$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Build = Join-Path $Root 'build'

Write-Host '=== TUTULMA NATIVE BUILD ===' -ForegroundColor Cyan

$vsDevCmd = 'C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat'
if (-not (Test-Path $vsDevCmd)) {
    throw "Visual Studio Developer Command Prompt bulunamadi: $vsDevCmd"
}

$cmd = @"
call "$vsDevCmd" -arch=x64
if errorlevel 1 exit /b 1
where cl
if errorlevel 1 exit /b 1
where cmake
if errorlevel 1 exit /b 1
cmake -S "$Root" -B "$Build" -G "NMake Makefiles" -DCMAKE_BUILD_TYPE=Release
if errorlevel 1 exit /b 1
cmake --build "$Build" --config Release --verbose
if errorlevel 1 exit /b 1
"@

cmd.exe /d /s /c $cmd
if ($LASTEXITCODE -ne 0) { throw "Build basarisiz. Cikis kodu: $LASTEXITCODE" }

$exeCandidates = @(
    (Join-Path $Build 'TutulmaNative.exe'),
    (Join-Path $Build 'Release\TutulmaNative.exe')
)
$exe = $exeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $exe) {
    Write-Host ''
    Write-Host 'Build klasoru:' -ForegroundColor Yellow
    if (Test-Path $Build) { Get-ChildItem $Build -Recurse -File | Select-Object FullName }
    throw "EXE olusturulamadi. Yukaridaki CMake/MSVC ciktisini kontrol et."
}

Write-Host ''
Write-Host 'BUILD BASARILI' -ForegroundColor Green
Write-Host "EXE: $exe" -ForegroundColor Green
