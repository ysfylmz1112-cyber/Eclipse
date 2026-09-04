# Tutulma Native

Unity kullanmadan geliştirilen Windows 3D prototipinin başlangıç noktasıdır.

## Teknoloji

- C++17
- Win32
- DirectX 11
- CMake
- MSVC

## İlk prototip

- Pencere ve DirectX 11 renderer
- CPU ile üretilen geniş arazi
- Birinci şahıs kamera
- WASD hareketi
- Sol mouse ile bakış
- Tutulma/anomali için temel runtime değişkeni

## Windows'ta derleme

Visual Studio Developer Command Prompt veya C++ araçları erişilebilir bir ortamda:

```powershell
Set-Location C:\Projects\Tutulma
Set-Location .\TutulmaNative
.\build.ps1
```

Çıktı:

```text
TutulmaNative\build\TutulmaNative.exe
```

ESC oyundan çıkar. WASD hareket eder. Sol mouse basılıyken kamera döner.

## Mimari hedef

Bu klasör, eski Unity projesinden bağımsızdır. İlerleyen aşamalarda renderer, dünya, oyuncu, atmosfer, Güneş anomalisi, uzay, kayıt sistemi ve oyun akışı burada büyütülecektir.
