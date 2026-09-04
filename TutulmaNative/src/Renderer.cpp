#include "Renderer.h"

#include <d3dcompiler.h>
#include <cmath>
#include <cstring>

using namespace DirectX;
using Microsoft::WRL::ComPtr;

namespace {
const char* kVS = R"(
cbuffer CameraBuffer : register(b0) {
    matrix worldViewProjection;
    float4 tint;
};
struct VSIn { float3 position : POSITION; float3 normal : NORMAL; };
struct VSOut { float4 position : SV_POSITION; float3 normal : NORMAL; };
VSOut main(VSIn input) {
    VSOut output;
    output.position = mul(float4(input.position, 1.0), worldViewProjection);
    output.normal = input.normal;
    return output;
}
)";

const char* kPS = R"(
cbuffer CameraBuffer : register(b0) {
    matrix worldViewProjection;
    float4 tint;
};
struct PSIn { float4 position : SV_POSITION; float3 normal : NORMAL; };
float4 main(PSIn input) : SV_TARGET {
    float3 lightDir = normalize(float3(-0.35, 0.85, -0.25));
    float lighting = saturate(dot(normalize(input.normal), lightDir)) * 0.65 + 0.35;
    return float4(tint.rgb * lighting, 1.0);
}
)";

bool Compile(const char* source, const char* entry, const char* target, ComPtr<ID3DBlob>& blob) {
    ComPtr<ID3DBlob> errors;
    HRESULT hr = D3DCompile(source, std::strlen(source), nullptr, nullptr, nullptr,
                            entry, target, D3DCOMPILE_ENABLE_STRICTNESS, 0, &blob, &errors);
    return SUCCEEDED(hr);
}
}

bool Renderer::Initialize(HWND window, int width, int height) {
    width_ = width;
    height_ = height;
    return CreateDevice(window) && CreateTargets(width, height) && CreateShaders() && CreateGeometry();
}

bool Renderer::CreateDevice(HWND window) {
    DXGI_SWAP_CHAIN_DESC desc{};
    desc.BufferCount = 2;
    desc.BufferDesc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
    desc.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
    desc.OutputWindow = window;
    desc.SampleDesc.Count = 1;
    desc.Windowed = TRUE;
    desc.SwapEffect = DXGI_SWAP_EFFECT_FLIP_DISCARD;

    UINT flags = 0;
#ifdef _DEBUG
    flags |= D3D11_CREATE_DEVICE_DEBUG;
#endif
    D3D_FEATURE_LEVEL levels[] = { D3D_FEATURE_LEVEL_11_0, D3D_FEATURE_LEVEL_10_0 };
    D3D_FEATURE_LEVEL chosen{};
    return SUCCEEDED(D3D11CreateDeviceAndSwapChain(nullptr, D3D_DRIVER_TYPE_HARDWARE, nullptr,
        flags, levels, 2, D3D11_SDK_VERSION, &desc, &swapChain_, &device_, &chosen, &context_));
}

bool Renderer::CreateTargets(int width, int height) {
    renderTarget_.Reset();
    depthView_.Reset();

    ComPtr<ID3D11Texture2D> backBuffer;
    if (FAILED(swapChain_->GetBuffer(0, IID_PPV_ARGS(&backBuffer)))) return false;
    if (FAILED(device_->CreateRenderTargetView(backBuffer.Get(), nullptr, &renderTarget_))) return false;

    D3D11_TEXTURE2D_DESC depthDesc{};
    depthDesc.Width = static_cast<UINT>(width);
    depthDesc.Height = static_cast<UINT>(height);
    depthDesc.MipLevels = 1;
    depthDesc.ArraySize = 1;
    depthDesc.Format = DXGI_FORMAT_D24_UNORM_S8_UINT;
    depthDesc.SampleDesc.Count = 1;
    depthDesc.BindFlags = D3D11_BIND_DEPTH_STENCIL;

    ComPtr<ID3D11Texture2D> depth;
    if (FAILED(device_->CreateTexture2D(&depthDesc, nullptr, &depth))) return false;
    return SUCCEEDED(device_->CreateDepthStencilView(depth.Get(), nullptr, &depthView_));
}

bool Renderer::CreateShaders() {
    ComPtr<ID3DBlob> vsBlob;
    if (!Compile(kVS, "main", "vs_5_0", vsBlob)) return false;
    if (FAILED(device_->CreateVertexShader(vsBlob->GetBufferPointer(), vsBlob->GetBufferSize(), nullptr, &vertexShader_))) return false;

    D3D11_INPUT_ELEMENT_DESC layout[] = {
        {"POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 0, D3D11_INPUT_PER_VERTEX_DATA, 0},
        {"NORMAL", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 12, D3D11_INPUT_PER_VERTEX_DATA, 0}
    };
    if (FAILED(device_->CreateInputLayout(layout, 2, vsBlob->GetBufferPointer(), vsBlob->GetBufferSize(), &inputLayout_))) return false;

    ComPtr<ID3DBlob> psBlob;
    if (!Compile(kPS, "main", "ps_5_0", psBlob)) return false;
    if (FAILED(device_->CreatePixelShader(psBlob->GetBufferPointer(), psBlob->GetBufferSize(), nullptr, &pixelShader_))) return false;

    D3D11_BUFFER_DESC cb{};
    cb.ByteWidth = sizeof(ConstantBufferData);
    cb.Usage = D3D11_USAGE_DYNAMIC;
    cb.BindFlags = D3D11_BIND_CONSTANT_BUFFER;
    cb.CPUAccessFlags = D3D11_CPU_ACCESS_WRITE;
    return SUCCEEDED(device_->CreateBuffer(&cb, nullptr, &constantBuffer_));
}

bool Renderer::CreateGeometry() {
    std::vector<Vertex> vertices;
    constexpr int grid = 80;
    constexpr float size = 160.0f;
    vertices.reserve((grid - 1) * (grid - 1) * 6);

    auto height = [](float x, float z) {
        return std::sin(x * 0.055f) * 0.9f + std::cos(z * 0.047f) * 0.7f + std::sin((x + z) * 0.025f) * 1.4f;
    };
    auto make = [&](float x, float z) {
        float h = height(x, z);
        float e = 0.2f;
        float hx = (height(x + e, z) - height(x - e, z)) / (2.0f * e);
        float hz = (height(x, z + e) - height(x, z - e)) / (2.0f * e);
        XMVECTOR n = XMVector3Normalize(XMVectorSet(-hx, 1.0f, -hz, 0));
        XMFLOAT3 nf; XMStoreFloat3(&nf, n);
        return Vertex{{x, h, z}, nf};
    };

    for (int z = 0; z < grid - 1; ++z) {
        for (int x = 0; x < grid - 1; ++x) {
            float x0 = -size * 0.5f + size * x / (grid - 1);
            float x1 = -size * 0.5f + size * (x + 1) / (grid - 1);
            float z0 = -size * 0.5f + size * z / (grid - 1);
            float z1 = -size * 0.5f + size * (z + 1) / (grid - 1);
            Vertex a = make(x0, z0), b = make(x1, z0), c = make(x1, z1), d = make(x0, z1);
            vertices.insert(vertices.end(), {a, b, c, a, c, d});
        }
    }
    vertexCount_ = static_cast<UINT>(vertices.size());

    D3D11_BUFFER_DESC desc{};
    desc.ByteWidth = static_cast<UINT>(vertices.size() * sizeof(Vertex));
    desc.Usage = D3D11_USAGE_DEFAULT;
    desc.BindFlags = D3D11_BIND_VERTEX_BUFFER;
    D3D11_SUBRESOURCE_DATA data{};
    data.pSysMem = vertices.data();
    return SUCCEEDED(device_->CreateBuffer(&desc, &data, &vertexBuffer_));
}

void Renderer::Resize(int width, int height) {
    if (!swapChain_ || width <= 0 || height <= 0) return;
    context_->OMSetRenderTargets(0, nullptr, nullptr);
    renderTarget_.Reset();
    depthView_.Reset();
    width_ = width; height_ = height;
    swapChain_->ResizeBuffers(0, static_cast<UINT>(width), static_cast<UINT>(height), DXGI_FORMAT_UNKNOWN, 0);
    CreateTargets(width, height);
}

void Renderer::BeginFrame() {
    const float clear[] = {0.008f, 0.012f, 0.022f, 1.0f};
    context_->ClearRenderTargetView(renderTarget_.Get(), clear);
    context_->ClearDepthStencilView(depthView_.Get(), D3D11_CLEAR_DEPTH | D3D11_CLEAR_STENCIL, 1.0f, 0);
    context_->OMSetRenderTargets(1, renderTarget_.GetAddressOf(), depthView_.Get());
    D3D11_VIEWPORT vp{0, 0, static_cast<float>(width_), static_cast<float>(height_), 0, 1};
    context_->RSSetViewports(1, &vp);
}

void Renderer::Draw(const XMMATRIX& view, const XMMATRIX& projection, float sunScale) {
    XMMATRIX world = XMMatrixIdentity();
    XMMATRIX wvp = XMMatrixTranspose(world * view * projection);
    D3D11_MAPPED_SUBRESOURCE mapped{};
    if (SUCCEEDED(context_->Map(constantBuffer_.Get(), 0, D3D11_MAP_WRITE_DISCARD, 0, &mapped))) {
        auto* cb = static_cast<ConstantBufferData*>(mapped.pData);
        cb->worldViewProjection = wvp;
        cb->tint = XMFLOAT4(0.16f + sunScale * 0.01f, 0.28f, 0.20f, 1.0f);
        context_->Unmap(constantBuffer_.Get(), 0);
    }

    UINT stride = sizeof(Vertex), offset = 0;
    context_->IASetInputLayout(inputLayout_.Get());
    context_->IASetVertexBuffers(0, 1, vertexBuffer_.GetAddressOf(), &stride, &offset);
    context_->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
    context_->VSSetShader(vertexShader_.Get(), nullptr, 0);
    context_->VSSetConstantBuffers(0, 1, constantBuffer_.GetAddressOf());
    context_->PSSetShader(pixelShader_.Get(), nullptr, 0);
    context_->PSSetConstantBuffers(0, 1, constantBuffer_.GetAddressOf());
    context_->Draw(vertexCount_, 0);
}

void Renderer::EndFrame() {
    swapChain_->Present(1, 0);
}
