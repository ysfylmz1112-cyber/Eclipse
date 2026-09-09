#include "Game.h"
#include <cmath>

bool Game::Initialize(HWND w,int width,int height){camera_.SetAspect((float)width/(float)height);return renderer_.Initialize(w,width,height);}
void Game::Resize(int w,int h){if(h<=0)return;camera_.SetAspect((float)w/(float)h);renderer_.Resize(w,h);}
void Game::Update(float dt){
 float f=0,r=0;if(keys_['W'])f+=1;if(keys_['S'])f-=1;if(keys_['D'])r+=1;if(keys_['A'])r-=1;camera_.Update(dt,f,r,0,0);
 anomaly_+=dt*.28f;if(anomaly_>36.0f)anomaly_=0.0f;
 float t=anomaly_;
 if(t<7.0f)eclipse_=0.0f;
 else if(t<15.0f){float u=(t-7.0f)/8.0f;eclipse_=0.5f-0.5f*cosf(u*3.14159265f);}
 else if(t<19.0f)eclipse_=1.0f;
 else if(t<25.0f){float u=(t-19.0f)/6.0f;eclipse_=1.0f-0.35f*u;}
 else eclipse_=0.65f;
}
void Game::Render(){renderer_.BeginFrame(eclipse_);renderer_.Draw(camera_.View(),camera_.Projection(),anomaly_,eclipse_);renderer_.EndFrame();}
void Game::OnMouseDelta(float dx,float dy){camera_.Update(0,0,0,dx,dy);}
void Game::OnKeyDown(WPARAM k){if(k<256)keys_[k]=true;}
void Game::OnKeyUp(WPARAM k){if(k<256)keys_[k]=false;}
