#pragma once
#include <d3d11.h>
#include <DirectXMath.h>
#include <wrl/client.h>
#include <vector>
class Renderer final{
public:
 struct Vertex{DirectX::XMFLOAT3 position;DirectX::XMFLOAT3 normal;DirectX::XMFLOAT4 color;float emissive;};
 struct ConstantBufferData{DirectX::XMMATRIX worldViewProjection;DirectX::XMFLOAT4 tint;DirectX::XMFLOAT4 scene;};
 bool Initialize(HWND,int,int);void Resize(int,int);void BeginFrame(float);void Draw(const DirectX::XMMATRIX&,const DirectX::XMMATRIX&,float,float);void EndFrame();
private:
 bool CreateDevice(HWND);bool CreateShaders();bool CreateGeometry();bool CreateTargets(int,int);bool CreateRasterizerState();
 Microsoft::WRL::ComPtr<ID3D11Device> device_;Microsoft::WRL::ComPtr<ID3D11DeviceContext> context_;Microsoft::WRL::ComPtr<IDXGISwapChain> swapChain_;Microsoft::WRL::ComPtr<ID3D11RenderTargetView> renderTarget_;Microsoft::WRL::ComPtr<ID3D11DepthStencilView> depthView_;Microsoft::WRL::ComPtr<ID3D11VertexShader> vertexShader_;Microsoft::WRL::ComPtr<ID3D11PixelShader> pixelShader_;Microsoft::WRL::ComPtr<ID3D11InputLayout> inputLayout_;Microsoft::WRL::ComPtr<ID3D11Buffer> vertexBuffer_;Microsoft::WRL::ComPtr<ID3D11Buffer> constantBuffer_;Microsoft::WRL::ComPtr<ID3D11RasterizerState> rasterizerState_;UINT vertexCount_=0;int width_=1,height_=1;
};
