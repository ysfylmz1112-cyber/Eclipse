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
    O o; float3 p=i.p;
    float t=scene.z;
    // e=1: Sun. It grows after totality and moves slightly toward camera.
    if(i.e>0.5 && i.e<1.5){
        float grow=1.0 + scene.x*0.95;
        float3 center=float3(0,78,230);
        p=center+(p-center)*grow;
        p.z -= scene.x*18.0;
    }
    // e=2: Moon. It crosses from left to right in front of the Sun.
    if(i.e>1.5 && i.e<2.5){
        float moonX=0.0;
        if(scene.y < 0.999){
            float u=saturate(scene.y);
            moonX=-42.0 + 84.0*u;
        }
        float3 center=float3(moonX,78,222);
        p=center+(p-float3(0,78,222));
    }
    // e=3: NPCs panic and run when the eclipse reaches totality.
    if(i.e>2.5 && i.e<3.5){
        float panic=saturate(scene.w);
        float dir=(p.x>=0.0)?1.0:-1.0;
        p.x += dir*(panic*(4.0 + 2.0*sin(t*5.0+p.z*0.08)));
        p.z += panic*(1.5*sin(t*7.0+p.x*0.05));
    }
    o.p=mul(float4(p,1),wvp);o.n=i.n;o.c=i.c;o.e=i.e;o.world=p;return o;
})";

const char* ps = R"(
cbuffer C:register(b0){matrix wvp;float4 tint;float4 scene;};
struct I{float4 p:SV_POSITION;float3 n:NORMAL;float4 c:COLOR;float e:TEXCOORD0;float3 world:TEXCOORD1;};
float4 main(I i):SV_TARGET{
    if(i.e>1.5 && i.e<2.5){
        float3 moon=float3(0.055,0.06,0.07);
        float rim=pow(1.0-saturate(dot(normalize(i.n),normalize(float3(-.2,.8,-.5)))),3.0);
        return float4(moon+rim*float3(.12,.12,.14),1);
    }
    if(i.e>0.5 && i.e<1.5){
        float pulse=1.0+0.12*sin(scene.z*8.0);
        float3 sun=i.c.rgb*(4.0+scene.x*2.5)*pulse;
        return float4(saturate(sun),1);
    }
    float3 n=normalize(i.n);
    float3 sunDir=normalize(float3(-.35,.82,-.45));
    float diffuse=.24+.76*saturate(dot(n,sunDir));
    float3 c=i.c.rgb*diffuse*tint.rgb;
    // Simple distance fog gives the scene depth instead of a black horizon.
    float dist=length(i.world-float3(0,0,-12));
    float fog=saturate((dist-220.0)/700.0);
    float3 fogColor=float3(.16,.25,.36)*tint.rgb;
    c=lerp(c,fogColor,fog*0.72);
    return float4(saturate(c),1);
})";

bool comp(const char* s,const char* e,const char* t,ComPtr<ID3DBlob>& b){
    ComPtr<ID3DBlob> x;
    return SUCCEEDED(D3DCompile(s,strlen(s),nullptr,nullptr,nullptr,e,t,D3DCOMPILE_ENABLE_STRICTNESS,0,&b,&x));
}

void tri(std::vector<Renderer::Vertex>&v,XMFLOAT3 a,XMFLOAT3 b,XMFLOAT3 c,XMFLOAT4 col,float em=0){
    XMFLOAT3 n;
    XMVECTOR ab=XMLoadFloat3(&b)-XMLoadFloat3(&a);
    XMVECTOR ac=XMLoadFloat3(&c)-XMLoadFloat3(&a);
    XMStoreFloat3(&n,XMVector3Normalize(XMVector3Cross(ab,ac)));
    v.push_back({a,n,col,em});v.push_back({b,n,col,em});v.push_back({c,n,col,em});
}

void cube(std::vector<Renderer::Vertex>&v,float x,float y,float z,float sx,float sy,float sz,XMFLOAT4 c,float em=0){
    float x0=x-sx/2,x1=x+sx/2,z0=z-sz/2,z1=z+sz/2,y1=y+sy;
    tri(v,{x0,y,z0},{x1,y,z0},{x1,y1,z0},c,em);tri(v,{x0,y,z0},{x1,y1,z0},{x0,y1,z0},c,em);
    tri(v,{x1,y,z1},{x0,y,z1},{x0,y1,z1},c,em);tri(v,{x1,y,z1},{x0,y1,z1},{x1,y1,z1},c,em);
    tri(v,{x0,y,z1},{x0,y,z0},{x0,y1,z0},c,em);tri(v,{x0,y,z1},{x0,y1,z0},{x0,y1,z1},c,em);
    tri(v,{x1,y,z0},{x1,y,z1},{x1,y1,z1},c,em);tri(v,{x1,y,z0},{x1,y1,z1},{x1,y1,z0},c,em);
    tri(v,{x0,y1,z0},{x1,y1,z0},{x1,y1,z1},c,em);tri(v,{x0,y1,z0},{x1,y1,z1},{x0,y1,z1},c,em);
}

void sphere(std::vector<Renderer::Vertex>&v,float x,float y,float z,float r,XMFLOAT4 c,float em=0){
    for(int j=0;j<16;j++)for(int i=0;i<32;i++){
        float a=XM_2PI*i/32,b=XM_2PI*(i+1)/32,p=XM_PI*j/16-XM_PIDIV2,q=XM_PI*(j+1)/16-XM_PIDIV2;
        auto f=[&](float A,float P){return XMFLOAT3{x+r*cosf(P)*cosf(A),y+r*sinf(P),z+r*cosf(P)*sinf(A)};};
        auto A=f(a,p),B=f(b,p),C=f(b,q),D=f(a,q);
        tri(v,A,B,C,c,em);tri(v,A,C,D,c,em);
    }
}

float terrain(float x,float z){
    // Broad rolling hills + distant mountains, shared conceptually with camera height.
    float h=2.0f*sinf(x*0.018f)+1.5f*cosf(z*0.021f)+1.0f*sinf((x+z)*0.035f);
    float ridge=sinf(z*0.010f)*sinf(x*0.022f);
    h+=std::max(0.0f,ridge)*18.0f;
    float m=std::max(0.0f,(z-300.0f)/180.0f);
    h+=m*m*(14.0f+10.0f*sinf(x*0.025f));
    return h;
}

void terrainMesh(std::vector<Renderer::Vertex>&v){
    const int NX=70,NZ=150; const float sx=10.0f,sz=8.0f;
    for(int z=0;z<NZ;z++)for(int x=0;x<NX;x++){
        float x0=(x-NX/2)*sx,x1=x0+sx;
        float z0=-60.0f+z*sz,z1=z0+sz;
        float y00=terrain(x0,z0),y10=terrain(x1,z0),y11=terrain(x1,z1),y01=terrain(x0,z1);
        XMFLOAT4 grass={0.16f+0.03f*sinf(x0),0.34f,0.12f,1};
        tri(v,{x0,y00,z0},{x1,y10,z0},{x1,y11,z1},grass);
        tri(v,{x0,y00,z0},{x1,y11,z1},{x0,y01,z1},grass);
    }
}

void building(std::vector<Renderer::Vertex>&v,float x,float z,float w,float h,float d,XMFLOAT4 c){
    float y=terrain(x,z); cube(v,x,y,z,w,h,d,c);
    // roof slab and simple windows.
    cube(v,x,y+h,z,w+0.5f,0.45f,d+0.5f,{0.08f,0.09f,0.11f,1});
    for(int side=-1;side<=1;side+=2)for(int row=0;row<3;row++)
        cube(v,x+side*(w*0.5f+0.015f),y+3.0f+row*4.0f,z,0.05f,1.8f,2.4f,{0.35f,0.55f,0.68f,1});
}

void npc(std::vector<Renderer::Vertex>&v,float x,float z){
    float y=terrain(x,z);
    cube(v,x,y,z,0.62f,1.55f,0.38f,{0.16f,0.22f,0.42f,1},3);
    sphere(v,x,y+1.95f,z,0.38f,{0.72f,0.52f,0.38f,1},3);
}

bool Renderer::Initialize(HWND w,int W,int H){width_=W;height_=H;return w&&W>0&&H>0&&CreateDevice(w)&&CreateTargets(W,H)&&CreateShaders()&&CreateRasterizerState()&&CreateGeometry();}

bool Renderer::CreateDevice(HWND w){
    DXGI_SWAP_CHAIN_DESC d{};d.BufferCount=2;d.BufferDesc.Width=width_;d.BufferDesc.Height=height_;d.BufferDesc.Format=DXGI_FORMAT_R8G8B8A8_UNORM;d.BufferUsage=DXGI_USAGE_RENDER_TARGET_OUTPUT;d.OutputWindow=w;d.SampleDesc.Count=1;d.Windowed=TRUE;d.SwapEffect=DXGI_SWAP_EFFECT_FLIP_DISCARD;
    D3D_FEATURE_LEVEL l[]={D3D_FEATURE_LEVEL_11_0,D3D_FEATURE_LEVEL_10_0},q{};
    return SUCCEEDED(D3D11CreateDeviceAndSwapChain(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,l,2,D3D11_SDK_VERSION,&d,&swapChain_,&device_,&q,&context_));
}

bool Renderer::CreateTargets(int W,int H){
    ComPtr<ID3D11Texture2D>b;if(FAILED(swapChain_->GetBuffer(0,IID_PPV_ARGS(&b)))||FAILED(device_->CreateRenderTargetView(b.Get(),nullptr,&renderTarget_)))return false;
    D3D11_TEXTURE2D_DESC d{};d.Width=W;d.Height=H;d.MipLevels=1;d.ArraySize=1;d.Format=DXGI_FORMAT_D24_UNORM_S8_UINT;d.SampleDesc.Count=1;d.BindFlags=D3D11_BIND_DEPTH_STENCIL;
    ComPtr<ID3D11Texture2D>x;if(FAILED(device_->CreateTexture2D(&d,nullptr,&x)))return false;return SUCCEEDED(device_->CreateDepthStencilView(x.Get(),nullptr,&depthView_));
}

bool Renderer::CreateShaders(){
    ComPtr<ID3DBlob>a,b;if(!comp(vs,"main","vs_5_0",a)||!comp(ps,"main","ps_5_0",b))return false;
    if(FAILED(device_->CreateVertexShader(a->GetBufferPointer(),a->GetBufferSize(),nullptr,&vertexShader_)))return false;
    D3D11_INPUT_ELEMENT_DESC e[]={{"POSITION",0,DXGI_FORMAT_R32G32B32_FLOAT,0,0,D3D11_INPUT_PER_VERTEX_DATA,0},{"NORMAL",0,DXGI_FORMAT_R32G32B32_FLOAT,0,12,D3D11_INPUT_PER_VERTEX_DATA,0},{"COLOR",0,DXGI_FORMAT_R32G32B32A32_FLOAT,0,24,D3D11_INPUT_PER_VERTEX_DATA,0},{"TEXCOORD",0,DXGI_FORMAT_R32_FLOAT,0,40,D3D11_INPUT_PER_VERTEX_DATA,0}};
    if(FAILED(device_->CreateInputLayout(e,4,a->GetBufferPointer(),a->GetBufferSize(),&inputLayout_))||FAILED(device_->CreatePixelShader(b->GetBufferPointer(),b->GetBufferSize(),nullptr,&pixelShader_)))return false;
    D3D11_BUFFER_DESC d{};d.ByteWidth=sizeof(ConstantBufferData);d.Usage=D3D11_USAGE_DYNAMIC;d.BindFlags=D3D11_BIND_CONSTANT_BUFFER;d.CPUAccessFlags=D3D11_CPU_ACCESS_WRITE;
    return SUCCEEDED(device_->CreateBuffer(&d,nullptr,&constantBuffer_));
}

bool Renderer::CreateRasterizerState(){D3D11_RASTERIZER_DESC d{};d.FillMode=D3D11_FILL_SOLID;d.CullMode=D3D11_CULL_NONE;d.DepthClipEnable=TRUE;return SUCCEEDED(device_->CreateRasterizerState(&d,&rasterizerState_));}

bool Renderer::CreateGeometry(){
    std::vector<Vertex>v; v.reserve(150000);
    terrainMesh(v);

    // Main road, side street and lane markings.
    cube(v,0,terrain(0,120)+0.10f,250,10,0.16f,620,{0.035f,0.04f,0.045f,1});
    for(int z=-20;z<550;z+=14) cube(v,0,terrain(0,(float)z)+0.20f,(float)z,0.28f,0.03f,6,{0.92f,0.80f,0.28f,1});
    cube(v,75,terrain(75,250)+0.10f,250,150,0.16f,8,{0.035f,0.04f,0.045f,1});

    // City blocks.
    for(int i=-4;i<=4;i++){
        float x=i*34.0f;
        building(v,x,75.0f,16.0f,12.0f+(i%3)*5.0f,16.0f,{0.34f,0.32f,0.30f,1});
        building(v,x,125.0f,18.0f,18.0f+((i+4)%4)*5.0f,18.0f,{0.24f,0.30f,0.38f,1});
        building(v,x,175.0f,14.0f,10.0f+(i%2)*8.0f,14.0f,{0.40f,0.36f,0.30f,1});
    }

    // Cars with visible bodies, roofs and wheels.
    for(int i=0;i<8;i++){
        float z=20.0f+i*58.0f; float y=terrain(0,z)+0.25f;
        cube(v,0,y,z,3.2f,1.1f,6.2f,{0.55f,0.06f,0.04f,1});
        cube(v,0,y+1.0f,z-0.15f,2.2f,0.65f,3.0f,{0.12f,0.18f,0.23f,1});
        for(int s=-1;s<=1;s+=2) for(int w=-1;w<=1;w+=2) cube(v,s*1.7f,y-0.05f,z+w*2.0f,0.35f,0.55f,0.75f,{0.025f,0.025f,0.03f,1});
    }

    // NPCs are human-sized and become visibly displaced by the panic animation.
    for(int i=0;i<16;i++) npc(v,-45.0f+(i%8)*12.0f,40.0f+(i/8)*26.0f);

    // Distant mountain ridge made from large, solid pyramidal-looking blocks.
    for(int i=-7;i<=7;i++){
        float x=i*42.0f,z=430.0f+std::abs(i)*3.0f;
        float h=55.0f+18.0f*cosf(i*0.7f);
        float y=terrain(x,z);
        cube(v,x,y,z,38.0f,h,55.0f,{0.11f,0.16f,0.14f,1});
    }

    // Sun and Moon are intentionally separate depth layers so the Moon can pass in front.
    sphere(v,0,78,230,19,{1.0f,0.48f,0.025f,1},1);
    sphere(v,-42,78,222,19,{0.025f,0.027f,0.032f,1},2);

    vertexCount_=(UINT)v.size();
    D3D11_BUFFER_DESC d{};d.ByteWidth=(UINT)(v.size()*sizeof(Vertex));d.Usage=D3D11_USAGE_DEFAULT;d.BindFlags=D3D11_BIND_VERTEX_BUFFER;
    D3D11_SUBRESOURCE_DATA s{};s.pSysMem=v.data();
    return SUCCEEDED(device_->CreateBuffer(&d,&s,&vertexBuffer_));
}

void Renderer::Resize(int W,int H){
    if(!swapChain_||W<1||H<1)return;context_->OMSetRenderTargets(0,nullptr,nullptr);renderTarget_.Reset();depthView_.Reset();width_=W;height_=H;
    if(SUCCEEDED(swapChain_->ResizeBuffers(0,W,H,DXGI_FORMAT_UNKNOWN,0)))CreateTargets(W,H);
}

void Renderer::BeginFrame(float e){
    float k=1.0f-e*0.82f;
    float c[]={.08f*k,.18f*k,.34f*k,1};
    context_->ClearRenderTargetView(renderTarget_.Get(),c);
    context_->ClearDepthStencilView(depthView_.Get(),D3D11_CLEAR_DEPTH,1,0);
    context_->OMSetRenderTargets(1,renderTarget_.GetAddressOf(),depthView_.Get());
    D3D11_VIEWPORT p{0,0,(float)width_,(float)height_,0,1};context_->RSSetViewports(1,&p);context_->RSSetState(rasterizerState_.Get());
}

void Renderer::Draw(const XMMATRIX&view,const XMMATRIX&projection,float time,float eclipse){
    D3D11_MAPPED_SUBRESOURCE m{};
    if(SUCCEEDED(context_->Map(constantBuffer_.Get(),0,D3D11_MAP_WRITE_DISCARD,0,&m))){
        auto*c=(ConstantBufferData*)m.pData;
        c->worldViewProjection=XMMatrixTranspose(view*projection);
        float d=1.0f-eclipse*0.78f;c->tint={d,d*.98f,d*.94f,1};
        float grow=saturate(0.10f+eclipse*0.90f);
        float panic=saturate((eclipse-0.72f)*3.6f);
        c->scene={grow,eclipse,time,panic};
        context_->Unmap(constantBuffer_.Get(),0);
    }
    UINT s=sizeof(Vertex),o=0;context_->IASetInputLayout(inputLayout_.Get());context_->IASetVertexBuffers(0,1,vertexBuffer_.GetAddressOf(),&s,&o);context_->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
    context_->VSSetShader(vertexShader_.Get(),nullptr,0);context_->PSSetShader(pixelShader_.Get(),nullptr,0);context_->VSSetConstantBuffers(0,1,constantBuffer_.GetAddressOf());context_->PSSetConstantBuffers(0,1,constantBuffer_.GetAddressOf());context_->Draw(vertexCount_,0);
}

void Renderer::EndFrame(){swapChain_->Present(1,0);}
