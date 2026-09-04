#include <windows.h>
#include <chrono>
#include <string>
#include "Game.h"

namespace {
Game* g_game = nullptr;
POINT g_lastMouse{};
bool g_mouseCaptured = false;

void ShowStartupError(const wchar_t* title, const std::wstring& message) {
    MessageBoxW(nullptr, message.c_str(), title, MB_OK | MB_ICONERROR);
}

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
        if (g_mouseCaptured) {
            ReleaseCapture();
            ShowCursor(TRUE);
            g_mouseCaptured = false;
        }
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
    wc.hbrBackground = nullptr;
    wc.style = CS_HREDRAW | CS_VREDRAW;

    if (!RegisterClassW(&wc)) {
        const DWORD error = GetLastError();
        ShowStartupError(L"Tutulma - Baslatma Hatasi",
            L"Pencere sinifi olusturulamadi. Windows hata kodu: " + std::to_wstring(error));
        return 10;
    }

    RECT rect{0, 0, 1600, 900};
    if (!AdjustWindowRect(&rect, WS_OVERLAPPEDWINDOW, FALSE)) {
        ShowStartupError(L"Tutulma - Baslatma Hatasi",
            L"Pencere boyutu ayarlanamadi. Windows hata kodu: " +
            std::to_wstring(GetLastError()));
        return 11;
    }

    HWND window = CreateWindowExW(
        0, className, L"TUTULMA - Native Prototype",
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT,
        rect.right - rect.left, rect.bottom - rect.top,
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
    const int width = client.right - client.left;
    const int height = client.bottom - client.top;

    if (width <= 0 || height <= 0) {
        DestroyWindow(window);
        g_game = nullptr;
        ShowStartupError(L"Tutulma - Baslatma Hatasi", L"Gecerli bir pencere boyutu alinamadi.");
        return 13;
    }

    if (!game.Initialize(window, width, height)) {
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

    g_game = nullptr;
    return static_cast<int>(msg.wParam);
}
