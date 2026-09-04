#include "Camera.h"

#include <algorithm>
#include <cmath>

using namespace DirectX;

namespace {
float TerrainHeight(float x, float z) {
    float h = 2.0f * std::sin(x * 0.018f)
        + 1.5f * std::cos(z * 0.021f)
        + 1.0f * std::sin((x + z) * 0.035f);
    float ridge = std::sin(z * 0.010f) * std::sin(x * 0.022f);
    h += std::max(0.0f, ridge) * 18.0f;
    float m = std::max(0.0f, (z - 300.0f) / 180.0f);
    h += m * m * (14.0f + 10.0f * std::sin(x * 0.025f));
    return h;
}
}

Camera::Camera()
    : position_(0.0f, 5.8f, -12.0f), yaw_(0.0f), pitch_(0.0f), aspect_(16.0f / 9.0f) {}

void Camera::SetAspect(float aspect) {
    aspect_ = aspect > 0.0f ? aspect : 1.0f;
}

void Camera::Update(float dt, float moveForward, float moveRight, float mouseDX, float mouseDY) {
    constexpr float mouseSensitivity = 0.0025f;
    constexpr float moveSpeed = 8.0f;
    constexpr float eyeHeight = 2.0f;

    // Standard FPS convention: mouse up looks up, mouse down looks down.
    yaw_ += mouseDX * mouseSensitivity;
    pitch_ -= mouseDY * mouseSensitivity;

    const float limit = XMConvertToRadians(85.0f);
    pitch_ = std::clamp(pitch_, -limit, limit);

    XMVECTOR forward = XMVector3Normalize(XMVectorSet(std::sin(yaw_), 0.0f, std::cos(yaw_), 0.0f));
    XMVECTOR right = XMVector3Normalize(XMVector3Cross(XMVectorSet(0, 1, 0, 0), forward));
    XMVECTOR pos = XMLoadFloat3(&position_);
    pos += forward * (moveForward * moveSpeed * dt);
    pos += right * (moveRight * moveSpeed * dt);

    XMFLOAT3 candidate{};
    XMStoreFloat3(&candidate, pos);
    const float minimumY = TerrainHeight(candidate.x, candidate.z) + eyeHeight;
    if (candidate.y < minimumY) candidate.y = minimumY;
    XMStoreFloat3(&position_, XMLoadFloat3(&candidate));
}

XMMATRIX Camera::View() const {
    XMVECTOR pos = XMLoadFloat3(&position_);
    XMVECTOR forward = XMVectorSet(
        std::sin(yaw_) * std::cos(pitch_),
        std::sin(pitch_),
        std::cos(yaw_) * std::cos(pitch_),
        0.0f);
    return XMMatrixLookToLH(pos, XMVector3Normalize(forward), XMVectorSet(0, 1, 0, 0));
}

XMMATRIX Camera::Projection() const {
    return XMMatrixPerspectiveFovLH(XMConvertToRadians(70.0f), aspect_, 0.05f, 5000.0f);
}
