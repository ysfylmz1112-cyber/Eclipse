#pragma once
#include "Camera.h"
#include "Renderer.h"
class Game final{
public:
 bool Initialize(HWND,int,int);void Resize(int,int);void Update(float);void Render();void OnMouseDelta(float,float);void OnKeyDown(WPARAM);void OnKeyUp(WPARAM);
private:
 Renderer renderer_;Camera camera_;bool keys_[256]{};float anomaly_=0;float eclipse_=0;
};
