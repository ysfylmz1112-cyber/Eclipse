#include "Game.h"
#include <cmath>
bool Game::Initialize(HWND w,int width,int height){camera_.SetAspect((float)width/(float)height);return renderer_.Initialize(w,width,height);}
void Game::Resize(int w,int h){if(h<=0)return;camera_.SetAspect((float)w/(float)h);renderer_.Resize(w,h);}
void Game::Update(float dt){float f=0,r=0;if(keys_['W'])f+=1;if(keys_['S'])f-=1;if(keys_['D'])r+=1;if(keys_['A'])r-=1;camera_.Update(dt,f,r,0,0);anomaly_+=dt*.035f;if(anomaly_>12)anomaly_=0;float p=anomaly_;eclipse_=p>5.0f&&p<8.0f?std::sin((p-5.0f)/3.0f*3.14159265f):0.0f;}
void Game::Render(){renderer_.BeginFrame(eclipse_);renderer_.Draw(camera_.View(),camera_.Projection(),anomaly_,eclipse_);renderer_.EndFrame();}
void Game::OnMouseDelta(float dx,float dy){camera_.Update(0,0,0,dx,dy);}
void Game::OnKeyDown(WPARAM k){if(k<256)keys_[k]=true;}
void Game::OnKeyUp(WPARAM k){if(k<256)keys_[k]=false;}
