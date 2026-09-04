#include <windows.h>
#include <chrono>
#include "Game.h"

namespace {
Game* g_game = nullptr;
POINT g_lastMouse{};
bool g_mouseCaptured = false;

LRESULT CALLBACK WindowProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
    case WM_SIZE:
        if (g_game) g_game->Resize(LOWORD(lParam), HIWORD(lParam));
        return 0;
    case WM_KEYDOWN:
        if (g_game) g_game->OnKeyDown(wParam);
        if (wParam == VK_ESCAPE) PostQuitMessage(0);
        return 0;
    case WM_KEYUP:
        if (g_game) g_game->OnKeyUp(wParam);
        return 0;
    case WM_LBUTTONDOWN:
        SetCapture(hwnd);
        ShowCursor(FALSE);
        GetCursorPos(&g_lastMouse);
        g_mouseCaptured = true;
        return 0;
    case WM_LBUTTONUP:
        ReleaseCapture();
        ShowCursor(TRUE);
        g_mouseCaptured = false;
        return 0;
    case WM_MOUSEMOVE:
        if (g_mouseCaptured && g_game) {
            POINT p;
            GetCursorPos(&p);
            g_game->OnMouseDelta(static_cast<float>(p.x - g_lastMouse.x),
                                 static_cast<float>(p.y - g_lastMouse.y));
            g_lastMouse = p;
        }
        return 0;
    case WM_DESTROY:
        PostQuitMessage(0);
        return 0;
    default:
        return DefWindowProcW(hwnd, msg, wParam, lParam);
    }
}
}

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE, PWSTR, int showCommand) {
    const wchar_t* className = L"TutulmaNativeWindow";
    WNDCLASSW wc{};
    wc.hInstance = instance;
    wc.lpfnWndProc = WindowProc;
    wc.lpszClassName = className;
    wc.hCursor = LoadCursorW(nullptr, IDC_ARROW);
    wc.style = CS_HREDRAW | CS_VREDRAW;
    RegisterClassW(&wc);

    RECT rect{0, 0, 1600, 900};
    AdjustWindowRect(&rect, WS_OVERLAPPEDWINDOW, FALSE);
    HWND window = CreateWindowExW(0, className, L"TUTULMA - Native Prototype",
        WS_OVERLAPPEDWINDOW, CW_USEDEFAULT, CW_USEDEFAULT,
        rect.right - rect.left, rect.bottom - rect.top,
        nullptr, nullptr, instance, nullptr);
    if (!window) return 1;

    Game game;
    g_game = &game;
    ShowWindow(window, showCommand);
    UpdateWindow(window);

    RECT client{};
    GetClientRect(window, &client);
    if (!game.Initialize(window, client.right - client.left, client.bottom - client.top)) {
        MessageBoxW(window, L"DirectX 11 baslatilamadi.", L"Tutulma", MB_ICONERROR);
        return 2;
    }

    auto previous = std::chrono::steady_clock::now();
    MSG msg{};
    while (msg.message != WM_QUIT) {
        while (PeekMessageW(&msg, nullptr, 0, 0, PM_REMOVE)) {
            TranslateMessage(&msg);
            DispatchMessageW(&msg);
        }

        auto now = std::chrono::steady_clock::now();
        float dt = std::chrono::duration<float>(now - previous).count();
        previous = now;
        if (dt > 0.1f) dt = 0.1f;

        game.Update(dt);
        game.Render();
    }

    g_game = nullptr;
    return static_cast<int>(msg.wParam);
}
