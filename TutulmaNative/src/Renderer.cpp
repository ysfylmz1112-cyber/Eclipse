#include "Renderer.h"
#include <d3dcompiler.h>
#include <cmath>
#include <cstring>
using namespace DirectX; using Microsoft::WRL::ComPtr;
namespace {
const char* vs=R"(
cbuffer C:register(b0){matrix wvp;float4 tint;float4 scene;};
struct I{float3 p:POSITION;float3 n:NORMAL;float4 c:COLOR;float e:TEXCOORD0;};
struct O{float4 p:SV_POSITION;float3 n:NORMAL;float4 c:COLOR;float e:TEXCOORD0;};
O main(I i){
 O o; float3 p=i.p;
 if(i.e>0.5 && i.e<1.5){ float3 center=float3(0,70,170); p=center+(p-center)*scene.x; }
 if(i.e>1.5){ float t=saturate(scene.y); float3 center=float3(-38+76*t,70,166); p=center+(p-float3(0,70,166)); }
 o.p=mul(float4(p,1),wvp);o.n=i.n;o.c=i.c;o.e=i.e;return o;
})";
const char* ps=R"(
cbuffer C:register(b0){matrix wvp;float4 tint;float4 scene;};
struct I{float4 p:SV_POSITION;float3 n:NORMAL;float4 c:COLOR;float e:TEXCOORD0;};
float4 main(I i):SV_TARGET{
 float3 sunDir=normalize(float3(-.35,.8,-.45));
 float light=.30+.70*saturate(dot(normalize(i.n),sunDir));
 float eclipse=saturate(scene.y);
 float3 c=i.c.rgb;
 if(i.e>1.5){c*=0.035;return float4(c,1);}
 if(i.e>0.5){float glow=4.5+scene.x*1.5;c*=glow;return float4(saturate(c),1);}
 c*=light*tint.rgb;
 return float4(saturate(c),1);
})";
bool comp(const char*s,const char*e,const char*t,ComPtr<ID3DBlob>&b){ComPtr<ID3DBlob>x;return SUCCEEDED(D3DCompile(s,strlen(s),nullptr,nullptr,nullptr,e,t,D3DCOMPILE_ENABLE_STRICTNESS,0,&b,&x));}
void tri(std::vector<Renderer::Vertex>&v,XMFLOAT3 a,XMFLOAT3 b,XMFLOAT3 c,XMFLOAT4 col,float em=0){XMFLOAT3 n;XMVECTOR ab=XMLoadFloat3(&b)-XMLoadFloat3(&a);XMVECTOR ac=XMLoadFloat3(&c)-XMLoadFloat3(&a);XMStoreFloat3(&n,XMVector3Normalize(XMVector3Cross(ab,ac)));v.push_back({a,n,col,em});v.push_back({b,n,col,em});v.push_back({c,n,col,em});}
void cube(std::vector<Renderer::Vertex>&v,float x,float y,float z,float sx,float sy,float sz,XMFLOAT4 c){float x0=x-sx/2,x1=x+sx/2,z0=z-sz/2,z1=z+sz/2,y1=y+sy;tri(v,{x0,y,z0},{x1,y,z0},{x1,y1,z0},c);tri(v,{x0,y,z0},{x1,y1,z0},{x0,y1,z0},c);tri(v,{x1,y,z1},{x0,y,z1},{x0,y1,z1},c);tri(v,{x1,y,z1},{x0,y1,z1},{x1,y1,z1},c);tri(v,{x0,y,z1},{x0,y,z0},{x0,y1,z0},c);tri(v,{x0,y,z1},{x0,y1,z0},{x0,y1,z1},c);tri(v,{x1,y,z0},{x1,y,z1},{x1,y1,z1},c);tri(v,{x1,y,z0},{x1,y1,z1},{x1,y1,z0},c);tri(v,{x0,y1,z0},{x1,y1,z0},{x1,y1,z1},c);tri(v,{x0,y1,z0},{x1,y1,z1},{x0,y1,z1},c);}
void sphere(std::vector<Renderer::Vertex>&v,float x,float y,float z,float r,XMFLOAT4 c,float em=0){for(int j=0;j<12;j++)for(int i=0;i<24;i++){float a=XM_2PI*i/24,b=XM_2PI*(i+1)/24,p=XM_PI*j/12-XM_PIDIV2,q=XM_PI*(j+1)/12-XM_PIDIV2;auto f=[&](float A,float P){return XMFLOAT3{x+r*cosf(P)*cosf(A),y+r*sinf(P),z+r*cosf(P)*sinf(A)};};auto A=f(a,p),B=f(b,p),C=f(b,q),D=f(a,q);tri(v,A,B,C,c,em);tri(v,A,C,D,c,em);}}
}
bool Renderer::Initialize(HWND w,int W,int H){width_=W;height_=H;return w&&W>0&&H>0&&CreateDevice(w)&&CreateTargets(W,H)&&CreateShaders()&&CreateRasterizerState()&&CreateGeometry();}
bool Renderer::CreateDevice(HWND w){DXGI_SWAP_CHAIN_DESC d{};d.BufferCount=2;d.BufferDesc.Width=width_;d.BufferDesc.Height=height_;d.BufferDesc.Format=DXGI_FORMAT_R8G8B8A8_UNORM;d.BufferUsage=DXGI_USAGE_RENDER_TARGET_OUTPUT;d.OutputWindow=w;d.SampleDesc.Count=1;d.Windowed=TRUE;d.SwapEffect=DXGI_SWAP_EFFECT_FLIP_DISCARD;D3D_FEATURE_LEVEL l[]={D3D_FEATURE_LEVEL_11_0,D3D_FEATURE_LEVEL_10_0},q{};return SUCCEEDED(D3D11CreateDeviceAndSwapChain(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,l,2,D3D11_SDK_VERSION,&d,&swapChain_,&device_,&q,&context_));}
bool Renderer::CreateTargets(int W,int H){ComPtr<ID3D11Texture2D>b;if(FAILED(swapChain_->GetBuffer(0,IID_PPV_ARGS(&b)))||FAILED(device_->CreateRenderTargetView(b.Get(),nullptr,&renderTarget_)))return false;D3D11_TEXTURE2D_DESC d{};d.Width=W;d.Height=H;d.MipLevels=1;d.ArraySize=1;d.Format=DXGI_FORMAT_D24_UNORM_S8_UINT;d.SampleDesc.Count=1;d.BindFlags=D3D11_BIND_DEPTH_STENCIL;ComPtr<ID3D11Texture2D>x;if(FAILED(device_->CreateTexture2D(&d,nullptr,&x)))return false;return SUCCEEDED(device_->CreateDepthStencilView(x.Get(),nullptr,&depthView_));}
bool Renderer::CreateShaders(){ComPtr<ID3DBlob>a,b;if(!comp(vs,"main","vs_5_0",a)||!comp(ps,"main","ps_5_0",b))return false;if(FAILED(device_->CreateVertexShader(a->GetBufferPointer(),a->GetBufferSize(),nullptr,&vertexShader_)))return false;D3D11_INPUT_ELEMENT_DESC e[]={{"POSITION",0,DXGI_FORMAT_R32G32B32_FLOAT,0,0,D3D11_INPUT_PER_VERTEX_DATA,0},{"NORMAL",0,DXGI_FORMAT_R32G32B32_FLOAT,0,12,D3D11_INPUT_PER_VERTEX_DATA,0},{"COLOR",0,DXGI_FORMAT_R32G32B32A32_FLOAT,0,24,D3D11_INPUT_PER_VERTEX_DATA,0},{"TEXCOORD",0,DXGI_FORMAT_R32_FLOAT,0,40,D3D11_INPUT_PER_VERTEX_DATA,0}};if(FAILED(device_->CreateInputLayout(e,4,a->GetBufferPointer(),a->GetBufferSize(),&inputLayout_))||FAILED(device_->CreatePixelShader(b->GetBufferPointer(),b->GetBufferSize(),nullptr,&pixelShader_)))return false;D3D11_BUFFER_DESC d{};d.ByteWidth=sizeof(ConstantBufferData);d.Usage=D3D11_USAGE_DYNAMIC;d.BindFlags=D3D11_BIND_CONSTANT_BUFFER;d.CPUAccessFlags=D3D11_CPU_ACCESS_WRITE;return SUCCEEDED(device_->CreateBuffer(&d,nullptr,&constantBuffer_));}
bool Renderer::CreateRasterizerState(){D3D11_RASTERIZER_DESC d{};d.FillMode=D3D11_FILL_SOLID;d.CullMode=D3D11_CULL_NONE;d.DepthClipEnable=TRUE;return SUCCEEDED(device_->CreateRasterizerState(&d,&rasterizerState_));}
bool Renderer::CreateGeometry(){std::vector<Vertex>v;const float S=500;cube(v,0,-1,100,S,1,S,{.12f,.38f,.10f,1});cube(v,0,0,35,14,.25f,420,{.07f,.07f,.075f,1});cube(v,0,.13f,35,7,.03f,420,{.95f,.75f,.12f,1});cube(v,0,0,150,420,.25f,14,{.07f,.07f,.075f,1});for(int i=-4;i<=4;i++){float x=i*28;cube(v,x,0,85,18,18+(i&1)*10,18,{.35f+.02f*i,.28f,.20f,1});cube(v,x,0,125,14,26,14,{.20f,.32f,.48f,1});for(int w=-1;w<=1;w++)for(int h=1;h<=3;h++)cube(v,x+w*4,h*4,76,1.2f,1.8f,.15f,{.72f,.82f,.88f,1});}for(int i=0;i<9;i++){float x=-40+i*10;cube(v,x,.35f,35,4,1.5f,8,{.72f,.04f,.025f,1});cube(v,x,.85f,35,1.5f,.12f,4,{.08f,.08f,.08f,1});}for(int i=0;i<12;i++){float x=-35+(i%6)*14,z=18+(i/6)*12;cube(v,x,0,z,1.2f,2.0f,1.2f,{.10f,.20f,.65f,1});sphere(v,x,2.45f,z,.55f,{.75f,.55f,.38f,1});}for(int i=-5;i<=5;i++){float x=i*32;cube(v,x,0,205,8,28,8,{.10f+.015f*(i+5),.24f,.11f,1});}sphere(v,0,70,170,18,{1,.55f,.03f,1},1);sphere(v,-38,70,166,13,{.015f,.015f,.02f,1},2);vertexCount_=(UINT)v.size();D3D11_BUFFER_DESC d{};d.ByteWidth=(UINT)(v.size()*sizeof(Vertex));d.Usage=D3D11_USAGE_DEFAULT;d.BindFlags=D3D11_BIND_VERTEX_BUFFER;D3D11_SUBRESOURCE_DATA s{};s.pSysMem=v.data();return SUCCEEDED(device_->CreateBuffer(&d,&s,&vertexBuffer_));}
void Renderer::Resize(int W,int H){if(!swapChain_||W<1||H<1)return;context_->OMSetRenderTargets(0,nullptr,nullptr);renderTarget_.Reset();depthView_.Reset();width_=W;height_=H;if(SUCCEEDED(swapChain_->ResizeBuffers(0,W,H,DXGI_FORMAT_UNKNOWN,0)))CreateTargets(W,H);}
void Renderer::BeginFrame(float e){float k=1.0f-e*.78f;float c[]={.10f*k,.22f*k,.42f*k,1};context_->ClearRenderTargetView(renderTarget_.Get(),c);context_->ClearDepthStencilView(depthView_.Get(),D3D11_CLEAR_DEPTH,1,0);context_->OMSetRenderTargets(1,renderTarget_.GetAddressOf(),depthView_.Get());D3D11_VIEWPORT p{0,0,(float)width_,(float)height_,0,1};context_->RSSetViewports(1,&p);context_->RSSetState(rasterizerState_.Get());}
void Renderer::Draw(const XMMATRIX&view,const XMMATRIX&projection,float time,float eclipse){D3D11_MAPPED_SUBRESOURCE m{};if(SUCCEEDED(context_->Map(constantBuffer_.Get(),0,D3D11_MAP_WRITE_DISCARD,0,&m))){auto*c=(ConstantBufferData*)m.pData;c->worldViewProjection=XMMatrixTranspose(view*projection);float d=1-eclipse*.78f;c->tint={d,d*.97f,d*.92f,1};float grow=1.0f+0.75f*(0.5f+0.5f*sinf(time*0.7f));c->scene={grow,eclipse,0,0};context_->Unmap(constantBuffer_.Get(),0);}UINT s=sizeof(Vertex),o=0;context_->IASetInputLayout(inputLayout_.Get());context_->IASetVertexBuffers(0,1,vertexBuffer_.GetAddressOf(),&s,&o);context_->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);context_->VSSetShader(vertexShader_.Get(),nullptr,0);context_->PSSetShader(pixelShader_.Get(),nullptr,0);context_->VSSetConstantBuffers(0,1,constantBuffer_.GetAddressOf());context_->PSSetConstantBuffers(0,1,constantBuffer_.GetAddressOf());context_->Draw(vertexCount_,0);}
void Renderer::EndFrame(){swapChain_->Present(1,0);}
