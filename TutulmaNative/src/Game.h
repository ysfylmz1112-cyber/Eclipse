#pragma once

#include "Camera.h"
#include "Renderer.h"

class Game final {
public:
    bool Initialize(HWND window, int width, int height);
    void Resize(int width, int height);
    void Update(float dt);
    void Render();
    void OnMouseDelta(float dx, float dy);
    void OnKeyDown(WPARAM key);
    void OnKeyUp(WPARAM key);

private:
    Renderer renderer_;
    Camera camera_;
    bool keys_[256]{};
    float anomaly_ = 1.0f;
};
