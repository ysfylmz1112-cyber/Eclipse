#pragma once

class World final {
public:
    void Initialize();
    float SunAnomaly() const { return sunAnomaly_; }

private:
    float sunAnomaly_ = 1.0f;
};
