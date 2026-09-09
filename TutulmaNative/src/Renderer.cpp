#include "Renderer.h"
#include <d3dcompiler.h>
#include <cmath>
#include <cstring>
#include <algorithm>

using namespace DirectX;
using Microsoft::WRL::ComPtr;

namespace {
const char* vs = R"(
cbuffer C:register(b0){matrix wvp;float4 tint;float4 scene;};
struct I{float3 p:POSITION;float3 n:NORMAL;float4 c:COLOR;float e:TEXCOORD0;};
struct O{float4 p:SV_POSITION;float3 n:NORMAL;float4 c:COLOR;float e:TEXCOORD0;float3 world:TEXCOORD1;};
O main(I i){
 O o;float3 p=i.p;float t=scene.z;
 if(i.e>0.5&&i.e<1.5){
   float post=saturate((t-19.0)/6.0);float grow=1.0+post*2.15;float3 center=float3(0,78,230);
   p=center+(p-center)*grow;p.z-=post*42.0;
 }
 if(i.e>1.5&&i.e<2.5){
   float moonProgress=saturate(scene.y);float moonX=-14.0+14.0*moonProgress;
   float3 target=float3(moonX,78,222);p+=target-float3(0,78,222);
   float totality=smoothstep(0.72,1.0,moonProgress);
   p.y+=sin(totality*3.14159)*0.35;
 }
 if(i.e>2.5&&i.e<4.5){
   float panic=saturate(scene.w);float phase=i.e-2.5;float side=(phase<1.0)?-1.0:1.0;
   float speed=2.2+phase*0.8;p.x+=side*panic*(speed*t*.18+1.2*sin(t*3.5+p.z*.07));
   p.z+=panic*(0.8*sin(t*4.0+p.x*.09));
 }
 o.p=mul(float4(p,1),wvp);o.n=i.n;o.c=i.c;o.e=i.e;o.world=p;return o;
})";

const char* ps = R"(
cbuffer C:register(b0){matrix wvp;float4 tint;float4 scene;};
float hash21(float2 p){p=frac(p*float2(123.34,456.21));p+=dot(p,p+45.32);return frac(p.x*p.y);}
struct I{float4 p:SV_POSITION;float3 n:NORMAL;float4 c:COLOR;float e:TEXCOORD0;float3 world:TEXCOORD1;};
float4 main(I i):SV_TARGET{
 if(i.e>1.5&&i.e<2.5){
   float3 n=normalize(i.n);float rim=pow(1-saturate(dot(n,normalize(float3(-.25,.82,-.55)))),3.0);
   float crater=.90+.10*hash21(i.world.xz*.12);return float4(float3(.035,.040,.048)*crater+rim*.16,1);
 }
 if(i.e>.5&&i.e<1.5){
   float post=saturate((scene.z-19.0)/6.0);float pulse=1.0+.05*sin(scene.z*9.0);
   float3 sun=i.c.rgb*(4.8+post*6.0)*pulse;return float4(saturate(sun),1);
 }
 float3 n=normalize(i.n);float3 sunDir=normalize(float3(-.35,.82,-.45));
 float ndl=saturate(dot(n,sunDir));float ambient=.18+.12*saturate(n.y);
 float3 base=i.c.rgb;float noise=hash21(i.world.xz*.055);base*=lerp(.90,1.10,noise);
 float3 c=base*(ambient+.82*ndl)*tint.rgb;
 float3 viewDir=normalize(float3(0,5.2,-12)-i.world);float3 halfDir=normalize(sunDir+viewDir);
 c+=pow(saturate(dot(n,halfDir)),34)*.16;
 float dist=length(i.world-float3(0,5.8,-12));float fog=saturate((dist-280.0)/920.0);
 float3 daySky=lerp(float3(.24,.36,.52),float3(.10,.16,.23),saturate((i.world.y-1.0)/100.0));
 float3 nightSky=float3(.035,.055,.085);float3 fogColor=lerp(daySky,nightSky,saturate(scene.x));
 c=lerp(c,fogColor,fog*.58);
 return float4(saturate(c),1);
})";

bool comp(const char* s,const char* e,const char* t,ComPtr<ID3DBlob>& b){ComPtr<ID3DBlob> err;return SUCCEEDED(D3DCompile(s,strlen(s),nullptr,nullptr,nullptr,e,t,D3DCOMPILE_ENABLE_STRICTNESS,0,&b,&err));}

void tri(std::vector<Renderer::Vertex>&v,XMFLOAT3 a,XMFLOAT3 b,XMFLOAT3 c,XMFLOAT4 col,float em=0){
 XMVECTOR ab=XMLoadFloat3(&b)-XMLoadFloat3(&a),ac=XMLoadFloat3(&c)-XMLoadFloat3(&a);XMFLOAT3 n;XMStoreFloat3(&n,XMVector3Normalize(XMVector3Cross(ab,ac)));
 v.push_back({a,n,col,em});v.push_back({b,n,col,em});v.push_back({c,n,col,em});
}
void quad(std::vector<Renderer::Vertex>&v,XMFLOAT3 a,XMFLOAT3 b,XMFLOAT3 c,XMFLOAT3 d,XMFLOAT4 col,float em=0){tri(v,a,b,c,col,em);tri(v,a,c,d,col,em);}
void cube(std::vector<Renderer::Vertex>&v,float x,float y,float z,float sx,float sy,float sz,XMFLOAT4 c,float em=0){
 float x0=x-sx/2,x1=x+sx/2,z0=z-sz/2,z1=z+sz/2,y1=y+sy;
 quad(v,{x0,y,z0},{x1,y,z0},{x1,y1,z0},{x0,y1,z0},c,em);quad(v,{x1,y,z1},{x0,y,z1},{x0,y1,z1},{x1,y1,z1},c,em);
 quad(v,{x0,y,z1},{x0,y,z0},{x0,y1,z0},{x0,y1,z1},c,em);quad(v,{x1,y,z0},{x1,y,z1},{x1,y1,z1},{x1,y1,z0},c,em);
 quad(v,{x0,y1,z0},{x1,y1,z0},{x1,y1,z1},{x0,y1,z1},c,em);quad(v,{x0,y,z1},{x1,y,z1},{x1,y,z0},{x0,y,z0},c,em);
}
void sphere(std::vector<Renderer::Vertex>&v,float x,float y,float z,float r,XMFLOAT4 c,float em=0){
 const int R=32,S=20;for(int j=0;j<S;j++)for(int i=0;i<R;i++){float a=XM_2PI*i/R,b=XM_2PI*(i+1)/R,p=XM_PI*j/S-XM_PIDIV2,q=XM_PI*(j+1)/S-XM_PIDIV2;
 auto f=[&](float A,float P){return XMFLOAT3{x+r*cosf(P)*cosf(A),y+r*sinf(P),z+r*cosf(P)*sinf(A)};};auto A=f(a,p),B=f(b,p),C=f(b,q),D=f(a,q);quad(v,A,B,C,D,c,em);}
}
void ellipsoid(std::vector<Renderer::Vertex>&v,float x,float y,float z,float rx,float ry,float rz,XMFLOAT4 c,float em=0){
 const int R=28,S=18;for(int j=0;j<S;j++)for(int i=0;i<R;i++){float a=XM_2PI*i/R,b=XM_2PI*(i+1)/R,p=XM_PI*j/S-XM_PIDIV2,q=XM_PI*(j+1)/S-XM_PIDIV2;
 auto f=[&](float A,float P){return XMFLOAT3{x+rx*cosf(P)*cosf(A),y+ry*sinf(P),z+rz*cosf(P)*sinf(A)};};quad(v,f(a,p),f(b,p),f(b,q),f(a,q),c,em);}
}
float terrain(float x,float z){float h=1.2f*sinf(x*.018f)+.9f*cosf(z*.021f)+.65f*sinf((x+z)*.035f);float ridge=sinf(z*.010f)*sinf(x*.022f);return h+std::max(0.0f,ridge)*10.0f;}
void terrainMesh(std::vector<Renderer::Vertex>&v){const int NX=90,NZ=180;const float sx=8,sz=8;for(int z=0;z<NZ;z++)for(int x=0;x<NX;x++){float x0=(x-NX/2)*sx,x1=x0+sx,z0=-80+z*sz,z1=z0+sz;float y00=terrain(x0,z0),y10=terrain(x1,z0),y11=terrain(x1,z1),y01=terrain(x0,z1);float n=.5f+.5f*sinf(x0*.17f+z0*.13f);XMFLOAT4 grass={.11f+.07f*n,.25f+.10f*n,.075f+.045f*n,1};quad(v,{x0,y00,z0},{x1,y10,z0},{x1,y11,z1},{x0,y01,z1},grass);}}
void road(std::vector<Renderer::Vertex>&v,float x,float z,float w,float d){float y=terrain(x,z)+.045f;quad(v,{x-w*.5f,y,z-d*.5f},{x+w*.5f,y,z-d*.5f},{x+w*.5f,y,z+d*.5f},{x-w*.5f,y,z+d*.5f},{.045f,.05f,.055f,1});for(float zz=z-d*.5f+5;zz<z+d*.5f-4;zz+=12)cube(v,x,y+.012f,zz,.18f,.025f,5,{.95f,.80f,.32f,1},1);}
void building(std::vector<Renderer::Vertex>&v,float x,float z,float w,float h,float d,XMFLOAT4 c){float y=terrain(x,z);cube(v,x,y,z,w,h,d,c);cube(v,x,y+h,z,w+.5f,.28f,d+.5f,{.055f,.06f,.07f,1});for(int side=-1;side<=1;side+=2)for(int row=0;row<4;row++){float yy=y+2.2f+row*(h-3.2f)/4;cube(v,x+side*(w*.5f+.012f),yy,z,.035f,1.25f,2,{.30f,.55f,.68f,1},.2f);}for(int side=-1;side<=1;side+=2)for(int row=0;row<3;row++){float zz=z+side*(d*.5f+.012f);cube(v,x,y+3+row*3.4f,zz,2,1.1f,.035f,{.25f,.48f,.60f,1},.2f);}}
void car(std::vector<Renderer::Vertex>&v,float x,float z,XMFLOAT4 body){float y=terrain(x,z)+.25f;cube(v,x,y,z,3.4f,1,6.4f,body);cube(v,x,y+.82f,z-.15f,2.3f,.65f,3,{.08f,.12f,.16f,1});for(int s=-1;s<=1;s+=2)for(int q=-1;q<=1;q+=2)sphere(v,x+s*1.72f,y-.05f,z+q*2,.38f,{.015f,.018f,.02f,1});}

void human(std::vector<Renderer::Vertex>&v,float x,float z,float height,XMFLOAT4 shirt,XMFLOAT4 pants,XMFLOAT4 skin,XMFLOAT4 hair,float facingShift,float detail){
 float y=terrain(x,z);float s=height/1.8f;
 float legH=.78f*s, torsoH=.62f*s, headR=.20f*s;
 float shoeY=y+.035f, hipY=y+.76f*s, shoulderY=hipY+torsoH*.74f, neckY=hipY+torsoH*.96f, headY=y+1.61f*s;
 cube(v,x-.11f*s,shoeY,z,.20f*s,.10f*s,.31f*s,{.035f,.035f,.04f,1});cube(v,x+.11f*s,shoeY,z,.20f*s,.10f*s,.31f*s,{.035f,.035f,.04f,1});
 cube(v,x-.105f*s,y+.11f*s,z,.18f*s,legH,.22f*s,pants);cube(v,x+.105f*s,y+.11f*s,z,.18f*s,legH,.22f*s,pants);
 cube(v,x,y+.76f*s,z,.42f*s,torsoH,.24f*s,shirt);
 cube(v,x,y+.74f*s,z,.48f*s,.15f*s,.27f*s,shirt);
 ellipsoid(v,x-.29f*s,shoulderY-.02f*s,z,.10f*s,.34f*s,.11f*s,shirt);ellipsoid(v,x+.29f*s,shoulderY-.02f*s,z,.10f*s,.34f*s,.11f*s,shirt);
 ellipsoid(v,x-.30f*s,shoulderY-.30f*s,z,.085f*s,.12f*s,.085f*s,skin);ellipsoid(v,x+.30f*s,shoulderY-.30f*s,z,.085f*s,.12f*s,.085f*s,skin);
 cube(v,x,y+1.37f*s,z,.12f*s,.10f*s,.12f*s,skin);
 ellipsoid(v,x,headY,z,headR,headR*1.06f,headR*.92f,skin);
 ellipsoid(v,x,headY+headR*.50f,z+.01f,headR*1.03f,headR*.40f,headR*.94f,hair);
 if(detail>0.5f){
   cube(v,x-.075f*s,headY+.015f*s,z-headR*.91f,.045f*s,.032f*s,.035f*s,{.025f,.025f,.03f,1},0);
   cube(v,x+.075f*s,headY+.015f*s,z-headR*.91f,.045f*s,.032f*s,.035f*s,{.025f,.025f,.03f,1},0);
 }
 if(facingShift>0.5f) ellipsoid(v,x,headY-.02f*s,z-headR*.88f,.07f*s,.08f*s,.04f*s,skin);
}
void storyHuman(std::vector<Renderer::Vertex>&v,float x,float z,float height,XMFLOAT4 shirt,XMFLOAT4 pants,XMFLOAT4 jacket,XMFLOAT4 skin,XMFLOAT4 hair){
 human(v,x,z,height,jacket,pants,skin,hair,1,1);
 float y=terrain(x,z),s=height/1.8f;
 cube(v,x,y+1.02f*s,z-.125f,.27f*s,.28f*s,.035f*s,shirt,.05f);
}
void mountain(std::vector<Renderer::Vertex>&v,float x,float z,float r,float h){float y=terrain(x,z);XMFLOAT3 a{x-r,y,z-r*.7f},b{x+r,y,z-r*.7f},c{x+r,y,z+r*.7f},d{x-r,y,z+r*.7f},p{x,y+h,z};tri(v,a,b,p,{.10f,.13f,.15f,1});tri(v,b,c,p,{.13f,.16f,.18f,1});tri(v,c,d,p,{.16f,.18f,.19f,1});tri(v,d,a,p,{.08f,.11f,.13f,1});tri(v,a,d,c,{.07f,.09f,.10f,1});tri(v,a,c,b,{.07f,.09f,.10f,1});}
}

bool Renderer::Initialize(HWND w,int W,int H){width_=W;height_=H;return w&&W>0&&H>0&&CreateDevice(w)&&CreateTargets(W,H)&&CreateShaders()&&CreateRasterizerState()&&CreateGeometry();}
bool Renderer::CreateDevice(HWND w){DXGI_SWAP_CHAIN_DESC d{};d.BufferCount=2;d.BufferDesc.Width=width_;d.BufferDesc.Height=height_;d.BufferDesc.Format=DXGI_FORMAT_R8G8B8A8_UNORM;d.BufferUsage=DXGI_USAGE_RENDER_TARGET_OUTPUT;d.OutputWindow=w;d.SampleDesc.Count=1;d.Windowed=TRUE;d.SwapEffect=DXGI_SWAP_EFFECT_FLIP_DISCARD;D3D_FEATURE_LEVEL levels[]={D3D_FEATURE_LEVEL_11_0,D3D_FEATURE_LEVEL_10_0},out{};return SUCCEEDED(D3D11CreateDeviceAndSwapChain(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,D3D11_CREATE_DEVICE_BGRA_SUPPORT,levels,2,D3D11_SDK_VERSION,&d,&swapChain_,&device_,&out,&context_));}
bool Renderer::CreateTargets(int W,int H){ComPtr<ID3D11Texture2D>b;if(FAILED(swapChain_->GetBuffer(0,IID_PPV_ARGS(&b)))||FAILED(device_->CreateRenderTargetView(b.Get(),nullptr,&renderTarget_)))return false;D3D11_TEXTURE2D_DESC d{};d.Width=W;d.Height=H;d.MipLevels=1;d.ArraySize=1;d.Format=DXGI_FORMAT_D24_UNORM_S8_UINT;d.SampleDesc.Count=1;d.BindFlags=D3D11_BIND_DEPTH_STENCIL;ComPtr<ID3D11Texture2D>x;if(FAILED(device_->CreateTexture2D(&d,nullptr,&x)))return false;return SUCCEEDED(device_->CreateDepthStencilView(x.Get(),nullptr,&depthView_));}
bool Renderer::CreateShaders(){ComPtr<ID3DBlob>a,b;if(!comp(vs,"main","vs_5_0",a)||!comp(ps,"main","ps_5_0",b))return false;if(FAILED(device_->CreateVertexShader(a->GetBufferPointer(),a->GetBufferSize(),nullptr,&vertexShader_)))return false;D3D11_INPUT_ELEMENT_DESC e[]={{"POSITION",0,DXGI_FORMAT_R32G32B32_FLOAT,0,0,D3D11_INPUT_PER_VERTEX_DATA,0},{"NORMAL",0,DXGI_FORMAT_R32G32B32_FLOAT,0,12,D3D11_INPUT_PER_VERTEX_DATA,0},{"COLOR",0,DXGI_FORMAT_R32G32B32A32_FLOAT,0,24,D3D11_INPUT_PER_VERTEX_DATA,0},{"TEXCOORD",0,DXGI_FORMAT_R32_FLOAT,0,40,D3D11_INPUT_PER_VERTEX_DATA,0}};if(FAILED(device_->CreateInputLayout(e,4,a->GetBufferPointer(),a->GetBufferSize(),&inputLayout_))||FAILED(device_->CreatePixelShader(b->GetBufferPointer(),b->GetBufferSize(),nullptr,&pixelShader_)))return false;D3D11_BUFFER_DESC d{};d.ByteWidth=sizeof(ConstantBufferData);d.Usage=D3D11_USAGE_DYNAMIC;d.BindFlags=D3D11_BIND_CONSTANT_BUFFER;d.CPUAccessFlags=D3D11_CPU_ACCESS_WRITE;return SUCCEEDED(device_->CreateBuffer(&d,nullptr,&constantBuffer_));}
bool Renderer::CreateRasterizerState(){D3D11_RASTERIZER_DESC d{};d.FillMode=D3D11_FILL_SOLID;d.CullMode=D3D11_CULL_NONE;d.DepthClipEnable=TRUE;return SUCCEEDED(device_->CreateRasterizerState(&d,&rasterizerState_));}
bool Renderer::CreateGeometry(){
 std::vector<Vertex>v;v.reserve(320000);terrainMesh(v);road(v,0,235,11,620);road(v,92,250,9,520);
 for(int i=-5;i<=5;i++){float x=i*28;building(v,x,70,15,11+((i+5)%3)*4,15,{.27f,.29f,.31f,1});building(v,x,116,18,15+((i+5)%3)*5,18,{.20f,.27f,.33f,1});}
 for(int i=0;i<10;i++)car(v,-4,20+i*52,{.55f,.07f+.03f*(i%3),.035f,1});
 // Main character: about 1.86 m.
 storyHuman(v,0,28,1.86f,{.08f,.18f,.24f,1},{.10f,.12f,.14f,1},{.20f,.25f,.30f,1},{.58f,.38f,.25f,1},{.035f,.025f,.018f,1});
 // Three companions with natural height variation.
 storyHuman(v,-3.8f,31,1.78f,{.22f,.28f,.34f,1},{.16f,.18f,.20f,1},{.30f,.32f,.34f,1},{.47f,.30f,.20f,1},{.08f,.045f,.025f,1});
 storyHuman(v,3.6f,34,1.82f,{.30f,.15f,.12f,1},{.20f,.22f,.24f,1},{.35f,.32f,.28f,1},{.70f,.52f,.38f,1},{.12f,.07f,.035f,1});
 storyHuman(v,6.3f,37,1.74f,{.12f,.22f,.14f,1},{.20f,.16f,.13f,1},{.26f,.30f,.25f,1},{.36f,.24f,.18f,1},{.035f,.02f,.015f,1});
 // Civilians: close but varied heights, faces, hair and clothing.
 const XMFLOAT4 shirts[]={
  {.18f,.25f,.44f,1},{.42f,.16f,.10f,1},{.16f,.38f,.23f,1},{.42f,.34f,.13f,1},
  {.32f,.19f,.36f,1},{.10f,.34f,.38f,1},{.45f,.27f,.18f,1},{.24f,.24f,.24f,1}
 };
 const XMFLOAT4 pants[]={ {.08f,.09f,.12f,1},{.18f,.16f,.14f,1},{.10f,.15f,.20f,1},{.22f,.19f,.15f,1} };
 for(int i=0;i<24;i++){float x=-50.0f+(i%12)*9.0f;float z=52.0f+(i/12)*30.0f;float h=1.66f+0.16f*((i*7)%5)/4.0f;XMFLOAT4 skin={.32f+0.07f*(i%4),.22f+0.05f*(i%4),.16f+0.035f*(i%4),1};XMFLOAT4 hair={.025f+.015f*(i%3),.018f+.012f*(i%3),.012f,1};human(v,x,z,h,shirts[i%8],pants[i%4],skin,hair,(i%2)?1.0f:0.0f,(i%3)?1.0f:0.2f);}
 for(int i=-8;i<=8;i++)mountain(v,i*46.0f,430.0f+std::abs(i)*5.0f,34.0f+std::abs(i%3)*8.0f,48.0f+std::abs(i)*4.0f);
 sphere(v,0,78,230,14,{1.0f,.58f,.06f,1},1);sphere(v,0,78,222,11,{.06f,.065f,.075f,1},2);
 D3D11_BUFFER_DESC d{};d.ByteWidth=UINT(v.size()*sizeof(Vertex));d.Usage=D3D11_USAGE_DEFAULT;d.BindFlags=D3D11_BIND_VERTEX_BUFFER;D3D11_SUBRESOURCE_DATA s{};s.pSysMem=v.data();if(FAILED(device_->CreateBuffer(&d,&s,&vertexBuffer_)))return false;vertexCount_=UINT(v.size());return true;
}
void Renderer::Resize(int W,int H){if(!swapChain_||W<=0||H<=0)return;context_->OMSetRenderTargets(0,nullptr,nullptr);renderTarget_.Reset();depthView_.Reset();swapChain_->ResizeBuffers(0,W,H,DXGI_FORMAT_UNKNOWN,0);width_=W;height_=H;CreateTargets(W,H);}
void Renderer::BeginFrame(float eclipse){float e=std::clamp(eclipse,0.0f,1.0f);float clear[4]={.20f*(1-e)+.025f*e,.34f*(1-e)+.035f*e,.52f*(1-e)+.055f*e,1};context_->OMSetRenderTargets(1,renderTarget_.GetAddressOf(),depthView_.Get());context_->ClearRenderTargetView(renderTarget_.Get(),clear);context_->ClearDepthStencilView(depthView_.Get(),D3D11_CLEAR_DEPTH|D3D11_CLEAR_STENCIL,1,0);}
void Renderer::Draw(const XMMATRIX& view,const XMMATRIX& projection,float time,float eclipse){
 float moonProgress=0.0f;float panic=0.0f;float t=time;
 if(t>=7.0f&&t<15.0f)moonProgress=0.5f-0.5f*cosf(((t-7.0f)/8.0f)*XM_PI);else if(t>=15.0f&&t<19.0f)moonProgress=1.0f;else if(t>=19.0f&&t<25.0f)moonProgress=1.0f;else if(t>=25.0f)moonProgress=0.25f+0.75f*saturate((t-25.0f)/5.0f);
 if(t>=15.0f)panic=std::clamp((t-15.0f)/5.0f,0.0f,1.0f);
 ConstantBufferData cb{};cb.worldViewProjection=XMMatrixTranspose(view*projection);cb.tint=XMFLOAT4(1.0f-0.52f*eclipse,1.0f-0.48f*eclipse,1.0f-0.40f*eclipse,1);cb.scene=XMFLOAT4(eclipse,moonProgress,t,panic);
 D3D11_MAPPED_SUBRESOURCE m{};if(SUCCEEDED(context_->Map(constantBuffer_.Get(),0,D3D11_MAP_WRITE_DISCARD,0,&m))){std::memcpy(m.pData,&cb,sizeof(cb));context_->Unmap(constantBuffer_.Get(),0);}
 UINT stride=sizeof(Vertex),offset=0;context_->IASetInputLayout(inputLayout_.Get());context_->IASetVertexBuffers(0,1,vertexBuffer_.GetAddressOf(),&stride,&offset);context_->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);context_->VSSetShader(vertexShader_.Get(),nullptr,0);context_->PSSetShader(pixelShader_.Get(),nullptr,0);context_->VSSetConstantBuffers(0,1,constantBuffer_.GetAddressOf());context_->PSSetConstantBuffers(0,1,constantBuffer_.GetAddressOf());context_->RSSetState(rasterizerState_.Get());context_->Draw(vertexCount_,0);
}
void Renderer::EndFrame(){swapChain_->Present(1,0);}
