#include <windows.h>
#include <chrono>
#include <string>
#include "Game.h"

namespace {
Game* g_game = nullptr;
POINT g_mouseCenter{};
bool g_mouseCaptured = false;
bool g_ignoreMouseMove = false;

void ShowStartupError(const wchar_t* title, const std::wstring& message) {
    MessageBoxW(nullptr, message.c_str(), title, MB_OK | MB_ICONERROR);
}

void CenterMouse(HWND hwnd) {
    RECT client{};
    GetClientRect(hwnd, &client);
    POINT center{
        (client.right - client.left) / 2,
        (client.bottom - client.top) / 2
    };
    ClientToScreen(hwnd, &center);
    g_mouseCenter = center;
    g_ignoreMouseMove = true;
    SetCursorPos(center.x, center.y);
}

void CaptureMouse(HWND hwnd) {
    SetCapture(hwnd);
    ShowCursor(FALSE);
    g_mouseCaptured = true;
    CenterMouse(hwnd);
}

void ReleaseMouse() {
    if (!g_mouseCaptured) return;
    ReleaseCapture();
    ShowCursor(TRUE);
    g_mouseCaptured = false;
    g_ignoreMouseMove = false;
}

LRESULT CALLBACK WindowProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
    case WM_SIZE:
        if (g_game) g_game->Resize(LOWORD(lParam), HIWORD(lParam));
        if (g_mouseCaptured) CenterMouse(hwnd);
        return 0;

    case WM_SETFOCUS:
        if (g_mouseCaptured) CenterMouse(hwnd);
        return 0;

    case WM_KILLFOCUS:
        ReleaseMouse();
        return 0;

    case WM_KEYDOWN:
        if (g_game) g_game->OnKeyDown(wParam);
        if (wParam == VK_ESCAPE) {
            PostQuitMessage(0);
        }
        return 0;

    case WM_KEYUP:
        if (g_game) g_game->OnKeyUp(wParam);
        return 0;

    case WM_LBUTTONDOWN:
        CaptureMouse(hwnd);
        return 0;

    case WM_LBUTTONUP:
        return 0;

    case WM_MOUSEMOVE:
        if (g_mouseCaptured && g_game) {
            if (g_ignoreMouseMove) {
                g_ignoreMouseMove = false;
                return 0;
            }

            POINT p;
            GetCursorPos(&p);
            const float dx = static_cast<float>(p.x - g_mouseCenter.x);
            const float dy = static_cast<float>(p.y - g_mouseCenter.y);

            if (dx != 0.0f || dy != 0.0f) {
                g_game->OnMouseDelta(dx, dy);
                CenterMouse(hwnd);
            }
        }
        return 0;

    case WM_DESTROY:
        ReleaseMouse();
        PostQuitMessage(0);
        return 0;

    default:
        return DefWindowProcW(hwnd, msg, wParam, lParam);
    }
}
}

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE, PWSTR, int) {
    const wchar_t* className = L"TutulmaNativeWindow";

    WNDCLASSW wc{};
    wc.hInstance = instance;
    wc.lpfnWndProc = WindowProc;
    wc.lpszClassName = className;
    wc.hCursor = LoadCursorW(nullptr, IDC_ARROW);
    wc.hbrBackground = nullptr;
    wc.style = CS_HREDRAW | CS_VREDRAW;

    if (!RegisterClassW(&wc)) {
        const DWORD error = GetLastError();
        ShowStartupError(L"Tutulma - Baslatma Hatasi",
            L"Pencere sinifi olusturulamadi. Windows hata kodu: " + std::to_wstring(error));
        return 10;
    }

    // Start as a real borderless fullscreen game window instead of a desktop-style window.
    const HMONITOR monitor = MonitorFromPoint(POINT{0, 0}, MONITOR_DEFAULTTOPRIMARY);
    MONITORINFO monitorInfo{sizeof(MONITORINFO)};
    GetMonitorInfoW(monitor, &monitorInfo);
    const RECT fullscreen = monitorInfo.rcMonitor;
    const int width = fullscreen.right - fullscreen.left;
    const int height = fullscreen.bottom - fullscreen.top;

    HWND window = CreateWindowExW(
        WS_EX_APPWINDOW,
        className, L"TUTULMA",
        WS_POPUP | WS_VISIBLE,
        fullscreen.left, fullscreen.top,
        width, height,
        nullptr, nullptr, instance, nullptr);

    if (!window) {
        const DWORD error = GetLastError();
        ShowStartupError(L"Tutulma - Baslatma Hatasi",
            L"Oyun penceresi olusturulamadi. Windows hata kodu: " + std::to_wstring(error));
        return 12;
    }

    Game game;
    g_game = &game;

    ShowWindow(window, SW_SHOW);
    UpdateWindow(window);

    RECT client{};
    GetClientRect(window, &client);
    const int clientWidth = client.right - client.left;
    const int clientHeight = client.bottom - client.top;

    if (clientWidth <= 0 || clientHeight <= 0) {
        DestroyWindow(window);
        g_game = nullptr;
        ShowStartupError(L"Tutulma - Baslatma Hatasi", L"Gecerli bir pencere boyutu alinamadi.");
        return 13;
    }

    if (!game.Initialize(window, clientWidth, clientHeight)) {
        DestroyWindow(window);
        g_game = nullptr;
        ShowStartupError(L"Tutulma - DirectX Hatasi",
            L"DirectX 11 baslatilamadi. Donanim/WARP denemesi ve shader asamasi basarisiz oldu.\n\n"
            L"Oyun bu nedenle sessizce kapanmak yerine artik hatayi gosterecek.");
        return 14;
    }

    auto previous = std::chrono::steady_clock::now();
    MSG msg{};

    while (msg.message != WM_QUIT) {
        while (PeekMessageW(&msg, nullptr, 0, 0, PM_REMOVE)) {
            TranslateMessage(&msg);
            DispatchMessageW(&msg);
        }

        if (msg.message == WM_QUIT) break;

        auto now = std::chrono::steady_clock::now();
        float dt = std::chrono::duration<float>(now - previous).count();
        previous = now;
        if (dt > 0.1f) dt = 0.1f;

        game.Update(dt);
        game.Render();
    }

    ReleaseMouse();
    g_game = nullptr;
    return static_cast<int>(msg.wParam);
}
