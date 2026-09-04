#include "Game.h"

bool Game::Initialize(HWND window, int width, int height) {
    camera_.SetAspect(static_cast<float>(width) / static_cast<float>(height));
    return renderer_.Initialize(window, width, height);
}

void Game::Resize(int width, int height) {
    if (height <= 0) return;
    camera_.SetAspect(static_cast<float>(width) / static_cast<float>(height));
    renderer_.Resize(width, height);
}

void Game::Update(float dt) {
    float forward = 0.0f;
    float right = 0.0f;
    if (keys_['W']) forward += 1.0f;
    if (keys_['S']) forward -= 1.0f;
    if (keys_['D']) right += 1.0f;
    if (keys_['A']) right -= 1.0f;
    camera_.Update(dt, forward, right, 0.0f, 0.0f);

    anomaly_ += dt * 0.02f;
    if (anomaly_ > 8.0f) anomaly_ = 8.0f;
}

void Game::Render() {
    renderer_.BeginFrame();
    renderer_.Draw(camera_.View(), camera_.Projection(), anomaly_);
    renderer_.EndFrame();
}

void Game::OnMouseDelta(float dx, float dy) {
    camera_.Update(0.0f, 0.0f, 0.0f, dx, dy);
}

void Game::OnKeyDown(WPARAM key) {
    if (key < 256) keys_[key] = true;
}

void Game::OnKeyUp(WPARAM key) {
    if (key < 256) keys_[key] = false;
}
