#pragma once

#include <d3d11.h>
#include <DirectXMath.h>
#include <wrl/client.h>
#include <vector>

class Renderer final {
public:
    bool Initialize(HWND window, int width, int height);
    void Resize(int width, int height);
    void BeginFrame();
    void Draw(const DirectX::XMMATRIX& view, const DirectX::XMMATRIX& projection, float sunScale);
    void EndFrame();

private:
    struct Vertex {
        DirectX::XMFLOAT3 position;
        DirectX::XMFLOAT3 normal;
    };

    struct ConstantBufferData {
        DirectX::XMMATRIX worldViewProjection;
        DirectX::XMFLOAT4 tint;
    };

    bool CreateDevice(HWND window);
    bool CreateShaders();
    bool CreateGeometry();
    bool CreateTargets(int width, int height);
    bool CreateRasterizerState();

    Microsoft::WRL::ComPtr<ID3D11Device> device_;
    Microsoft::WRL::ComPtr<ID3D11DeviceContext> context_;
    Microsoft::WRL::ComPtr<IDXGISwapChain> swapChain_;
    Microsoft::WRL::ComPtr<ID3D11RenderTargetView> renderTarget_;
    Microsoft::WRL::ComPtr<ID3D11DepthStencilView> depthView_;
    Microsoft::WRL::ComPtr<ID3D11VertexShader> vertexShader_;
    Microsoft::WRL::ComPtr<ID3D11PixelShader> pixelShader_;
    Microsoft::WRL::ComPtr<ID3D11InputLayout> inputLayout_;
    Microsoft::WRL::ComPtr<ID3D11Buffer> vertexBuffer_;
    Microsoft::WRL::ComPtr<ID3D11Buffer> constantBuffer_;
    Microsoft::WRL::ComPtr<ID3D11RasterizerState> rasterizerState_;
    UINT vertexCount_ = 0;
    int width_ = 1;
    int height_ = 1;
};
