$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Build = Join-Path $Root 'build'

Write-Host '=== TUTULMA NATIVE BUILD ===' -ForegroundColor Cyan

$vsDevCmd = 'C:\Program Files\Microsoft Visual Studio\18\Community\Common7\Tools\VsDevCmd.bat'
if (-not (Test-Path $vsDevCmd)) {
    throw "Visual Studio Developer Command Prompt bulunamadi: $vsDevCmd"
}

# VsDevCmd ortam degiskenlerini ayni CMD oturumunda yukle ve ardindan CMake'i calistir.
# Onceki surumde PowerShell -> cmd arguman aktarimi CMD komutlarini eksik calistirabiliyordu.
$cmdFile = Join-Path $env:TEMP 'TutulmaNativeBuild.cmd'
$cmdText = @"
@echo off
call "$vsDevCmd" -arch=x64
if errorlevel 1 exit /b 10

echo === CL ===
where cl
if errorlevel 1 exit /b 11
cl 2>&1 | findstr /C:"Compiler Version" /C:"Microsoft (R)"

echo === CMAKE ===
where cmake
if errorlevel 1 exit /b 12
cmake --version

if not exist "$Build" mkdir "$Build"

echo === CMAKE CONFIGURE ===
cmake -S "$Root" -B "$Build" -G "NMake Makefiles" -DCMAKE_BUILD_TYPE=Release
if errorlevel 1 exit /b 20

echo === CMAKE BUILD ===
cmake --build "$Build" --config Release --verbose
if errorlevel 1 exit /b 21

exit /b 0
"@

Set-Content -Path $cmdFile -Value $cmdText -Encoding ASCII
try {
    & cmd.exe /d /c $cmdFile
    $exitCode = $LASTEXITCODE
}
finally {
    Remove-Item $cmdFile -Force -ErrorAction SilentlyContinue
}

if ($exitCode -ne 0) {
    throw "Build basarisiz. CMD cikis kodu: $exitCode"
}

$exeCandidates = @(
    (Join-Path $Build 'TutulmaNative.exe'),
    (Join-Path $Build 'Release\TutulmaNative.exe')
)
$exe = $exeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $exe) {
    Write-Host ''
    Write-Host 'Build klasoru:' -ForegroundColor Yellow
    if (Test-Path $Build) { Get-ChildItem $Build -Recurse -File | Select-Object FullName }
    throw 'EXE olusturulamadi.'
}

Write-Host ''
Write-Host 'BUILD BASARILI' -ForegroundColor Green
Write-Host "EXE: $exe" -ForegroundColor Green
