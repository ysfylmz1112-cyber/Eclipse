#pragma once

#include <DirectXMath.h>

class Camera final {
public:
    Camera();

    void SetAspect(float aspect);
    void Update(float dt, float moveForward, float moveRight, float mouseDX, float mouseDY);

    DirectX::XMMATRIX View() const;
    DirectX::XMMATRIX Projection() const;
    DirectX::XMFLOAT3 Position() const { return position_; }

private:
    DirectX::XMFLOAT3 position_;
    float yaw_;
    float pitch_;
    float aspect_;
};
