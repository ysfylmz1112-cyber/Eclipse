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
cmake -S "$Root" -B "$Build" -G "NMake Makefiles" -DCMAKE_BUILD_TYPE=Release
cmake --build "$Build" --config Release
"@

cmd.exe /d /s /c $cmd
if ($LASTEXITCODE -ne 0) { throw "Build basarisiz. Cikis kodu: $LASTEXITCODE" }

$exe = Join-Path $Build 'TutulmaNative.exe'
if (-not (Test-Path $exe)) { throw "EXE olusturulamadi: $exe" }

Write-Host ''
Write-Host 'BUILD BASARILI' -ForegroundColor Green
Write-Host "EXE: $exe" -ForegroundColor Green
