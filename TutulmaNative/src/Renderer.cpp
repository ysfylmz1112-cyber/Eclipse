#include "Renderer.h"
#include <d3dcompiler.h>
#include <cmath>
#include <cstring>
#include <string>
#include <windows.h>

using namespace DirectX;
using Microsoft::WRL::ComPtr;

namespace {
const char* kVS=R"(
cbuffer CameraBuffer:register(b0){matrix worldViewProjection;float4 tint;};
struct VSIn{float3 position:POSITION;float3 normal:NORMAL;};
struct VSOut{float4 position:SV_POSITION;float3 normal:NORMAL;float3 worldPosition:TEXCOORD0;};
VSOut main(VSIn i){VSOut o;o.position=mul(float4(i.position,1),worldViewProjection);o.normal=i.normal;o.worldPosition=i.position;return o;}
)";
const char* kPS=R"(
cbuffer CameraBuffer:register(b0){matrix worldViewProjection;float4 tint;};
struct PSIn{float4 position:SV_POSITION;float3 normal:NORMAL;float3 worldPosition:TEXCOORD0;};
float4 main(PSIn i):SV_TARGET{
 float3 n=normalize(i.normal);float3 lightDir=normalize(float3(-0.35,0.85,-0.25));
 float sun=saturate(dot(n,lightDir));
 float altitude=saturate(0.5+i.worldPosition.y*0.045);
 float3 low=float3(0.035,0.11,0.045),high=float3(0.18,0.30,0.10);
 float3 c=lerp(low,high,altitude);
 float v=0.82+(0.5+0.5*sin(i.worldPosition.x*0.12+i.worldPosition.z*0.09))*0.18;
 c*=v*(0.42+sun*0.85);
 return float4(c,1);
}
)";

bool Compile(const char*s,const char*e,const char*t,ComPtr<ID3DBlob>&b){ComPtr<ID3DBlob>err;return SUCCEEDED(D3DCompile(s,std::strlen(s),nullptr,nullptr,nullptr,e,t,D3DCOMPILE_ENABLE_STRICTNESS,0,&b,&err));}
void LogHr(const char*stage,HRESULT hr){char b[64];sprintf_s(b,"%s HRESULT=0x%08lX\n",stage,(unsigned long)hr);OutputDebugStringA(b);}
}

bool Renderer::Initialize(HWND window,int width,int height){
 if(!window||width<=0||height<=0)return false;width_=width;height_=height;
 return CreateDevice(window)&&CreateTargets(width,height)&&CreateShaders()&&CreateRasterizerState()&&CreateGeometry();
}

bool Renderer::CreateDevice(HWND window){
 DXGI_SWAP_CHAIN_DESC d{};d.BufferCount=2;d.BufferDesc.Width=(UINT)width_;d.BufferDesc.Height=(UINT)height_;d.BufferDesc.Format=DXGI_FORMAT_R8G8B8A8_UNORM;d.BufferUsage=DXGI_USAGE_RENDER_TARGET_OUTPUT;d.OutputWindow=window;d.SampleDesc.Count=1;d.Windowed=TRUE;d.SwapEffect=DXGI_SWAP_EFFECT_FLIP_DISCARD;
 D3D_FEATURE_LEVEL levels[]={D3D_FEATURE_LEVEL_11_0,D3D_FEATURE_LEVEL_10_0};D3D_FEATURE_LEVEL chosen{};
 HRESULT hr=D3D11CreateDeviceAndSwapChain(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,levels,2,D3D11_SDK_VERSION,&d,&swapChain_,&device_,&chosen,&context_);
 if(SUCCEEDED(hr))return true;LogHr("Hardware D3D11",hr);device_.Reset();context_.Reset();swapChain_.Reset();
 hr=D3D11CreateDeviceAndSwapChain(nullptr,D3D_DRIVER_TYPE_WARP,nullptr,0,levels,2,D3D11_SDK_VERSION,&d,&swapChain_,&device_,&chosen,&context_);if(FAILED(hr))LogHr("WARP D3D11",hr);return SUCCEEDED(hr);
}

bool Renderer::CreateTargets(int width,int height){
 if(!swapChain_||!device_||width<=0||height<=0)return false;renderTarget_.Reset();depthView_.Reset();ComPtr<ID3D11Texture2D>back;
 HRESULT hr=swapChain_->GetBuffer(0,IID_PPV_ARGS(&back));if(FAILED(hr)){LogHr("GetBuffer",hr);return false;}hr=device_->CreateRenderTargetView(back.Get(),nullptr,&renderTarget_);if(FAILED(hr)){LogHr("CreateRTV",hr);return false;}
 D3D11_TEXTURE2D_DESC dd{};dd.Width=(UINT)width;dd.Height=(UINT)height;dd.MipLevels=1;dd.ArraySize=1;dd.Format=DXGI_FORMAT_D24_UNORM_S8_UINT;dd.SampleDesc.Count=1;dd.BindFlags=D3D11_BIND_DEPTH_STENCIL;ComPtr<ID3D11Texture2D>depth;
 hr=device_->CreateTexture2D(&dd,nullptr,&depth);if(FAILED(hr)){LogHr("CreateDepth",hr);return false;}hr=device_->CreateDepthStencilView(depth.Get(),nullptr,&depthView_);if(FAILED(hr)){LogHr("CreateDSV",hr);return false;}return true;
}

bool Renderer::CreateShaders(){
 ComPtr<ID3DBlob>vs,ps;if(!Compile(kVS,"main","vs_5_0",vs))return false;if(FAILED(device_->CreateVertexShader(vs->GetBufferPointer(),vs->GetBufferSize(),nullptr,&vertexShader_)))return false;
 D3D11_INPUT_ELEMENT_DESC l[]={{"POSITION",0,DXGI_FORMAT_R32G32B32_FLOAT,0,0,D3D11_INPUT_PER_VERTEX_DATA,0},{"NORMAL",0,DXGI_FORMAT_R32G32B32_FLOAT,0,12,D3D11_INPUT_PER_VERTEX_DATA,0}};
 if(FAILED(device_->CreateInputLayout(l,2,vs->GetBufferPointer(),vs->GetBufferSize(),&inputLayout_)))return false;if(!Compile(kPS,"main","ps_5_0",ps))return false;if(FAILED(device_->CreatePixelShader(ps->GetBufferPointer(),ps->GetBufferSize(),nullptr,&pixelShader_)))return false;
 D3D11_BUFFER_DESC b{};b.ByteWidth=sizeof(ConstantBufferData);b.Usage=D3D11_USAGE_DYNAMIC;b.BindFlags=D3D11_BIND_CONSTANT_BUFFER;b.CPUAccessFlags=D3D11_CPU_ACCESS_WRITE;return SUCCEEDED(device_->CreateBuffer(&b,nullptr,&constantBuffer_));
}

bool Renderer::CreateRasterizerState(){
 D3D11_RASTERIZER_DESC d{};d.FillMode=D3D11_FILL_SOLID;d.CullMode=D3D11_CULL_NONE;d.FrontCounterClockwise=FALSE;d.DepthClipEnable=TRUE;return SUCCEEDED(device_->CreateRasterizerState(&d,&rasterizerState_));
}

bool Renderer::CreateGeometry(){
 std::vector<Vertex>v;constexpr int grid=220;constexpr float size=1200.0f;v.reserve((grid-1)*(grid-1)*6);
 auto h=[](float x,float z){return std::sin(x*.012f)*5.5f+std::cos(z*.015f)*4.0f+std::sin((x+z)*.028f)*2.2f+std::sin(x*.075f+z*.041f)*.55f;};
 auto make=[&](float x,float z){float y=h(x,z),e=.35f,hx=(h(x+e,z)-h(x-e,z))/(2*e),hz=(h(x,z+e)-h(x,z-e))/(2*e);XMFLOAT3 n;XMStoreFloat3(&n,XMVector3Normalize(XMVectorSet(-hx,1,-hz,0)));return Vertex{{x,y,z},n};};
 for(int z=0;z<grid-1;++z)for(int x=0;x<grid-1;++x){float x0=-size*.5f+size*x/(grid-1),x1=-size*.5f+size*(x+1)/(grid-1),z0=-size*.5f+size*z/(grid-1),z1=-size*.5f+size*(z+1)/(grid-1);Vertex a=make(x0,z0),b=make(x1,z0),c=make(x1,z1),d=make(x0,z1);v.insert(v.end(),{a,b,c,a,c,d});}
 vertexCount_=(UINT)v.size();if(v.empty())return false;D3D11_BUFFER_DESC d{};d.ByteWidth=(UINT)(v.size()*sizeof(Vertex));d.Usage=D3D11_USAGE_DEFAULT;d.BindFlags=D3D11_BIND_VERTEX_BUFFER;D3D11_SUBRESOURCE_DATA data{};data.pSysMem=v.data();return SUCCEEDED(device_->CreateBuffer(&d,&data,&vertexBuffer_));
}

void Renderer::Resize(int width,int height){if(!swapChain_||!context_||width<=0||height<=0)return;context_->OMSetRenderTargets(0,nullptr,nullptr);renderTarget_.Reset();depthView_.Reset();width_=width;height_=height;if(SUCCEEDED(swapChain_->ResizeBuffers(0,(UINT)width,(UINT)height,DXGI_FORMAT_UNKNOWN,0)))CreateTargets(width,height);}
void Renderer::BeginFrame(){if(!context_||!renderTarget_||!depthView_)return;const float clear[]={0.045f,0.095f,0.17f,1};context_->ClearRenderTargetView(renderTarget_.Get(),clear);context_->ClearDepthStencilView(depthView_.Get(),D3D11_CLEAR_DEPTH|D3D11_CLEAR_STENCIL,1,0);context_->OMSetRenderTargets(1,renderTarget_.GetAddressOf(),depthView_.Get());D3D11_VIEWPORT vp{0,0,(float)width_,(float)height_,0,1};context_->RSSetViewports(1,&vp);context_->RSSetState(rasterizerState_.Get());}
void Renderer::Draw(const XMMATRIX&view,const XMMATRIX&projection,float sunScale){if(!context_||!constantBuffer_||!vertexBuffer_)return;D3D11_MAPPED_SUBRESOURCE m{};if(SUCCEEDED(context_->Map(constantBuffer_.Get(),0,D3D11_MAP_WRITE_DISCARD,0,&m))){auto*cb=(ConstantBufferData*)m.pData;cb->worldViewProjection=XMMatrixTranspose(view*projection);cb->tint=XMFLOAT4(.16f+sunScale*.01f,.28f,.20f,1);context_->Unmap(constantBuffer_.Get(),0);}UINT stride=sizeof(Vertex),offset=0;context_->IASetInputLayout(inputLayout_.Get());context_->IASetVertexBuffers(0,1,vertexBuffer_.GetAddressOf(),&stride,&offset);context_->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);context_->VSSetShader(vertexShader_.Get(),nullptr,0);context_->VSSetConstantBuffers(0,1,constantBuffer_.GetAddressOf());context_->PSSetShader(pixelShader_.Get(),nullptr,0);context_->PSSetConstantBuffers(0,1,constantBuffer_.GetAddressOf());context_->Draw(vertexCount_,0);}
void Renderer::EndFrame(){if(swapChain_)swapChain_->Present(1,0);}
