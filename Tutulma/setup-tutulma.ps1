$ErrorActionPreference = 'Stop'

$root = 'C:\Projects\Tutulma'
$base = 'https://raw.githubusercontent.com/ysfylmz1112-cyber/Eclipse/main/Tutulma/UnityProject'

if (-not (Test-Path $root)) {
    throw "Unity project bulunamadi: $root"
}

$files = @{
    'Assets\Scripts\Core\GameBootstrap.cs' = "$base/Assets/Scripts/Core/GameBootstrap.cs"
    'Assets\Scripts\Player\PlayerController.cs' = "$base/Assets/Scripts/Player/PlayerController.cs"
    'Assets\Scripts\Player\PlayerCamera.cs' = "$base/Assets/Scripts/Player/PlayerCamera.cs"
    'Assets\Scripts\World\SunAnomaly.cs' = "$base/Assets/Scripts/World/SunAnomaly.cs"
    'Assets\Scripts\World\WorldBootstrap.cs' = "$base/Assets/Scripts/World/WorldBootstrap.cs"
    'Assets\Editor\AutoBuild.cs' = "$base/Assets/Editor/AutoBuild.cs"
}

foreach ($item in $files.GetEnumerator()) {
    $out = Join-Path $root $item.Key
    New-Item -ItemType Directory -Force -Path (Split-Path $out) | Out-Null
    Invoke-WebRequest -Uri $item.Value -OutFile $out
}

$unityRoots = @(
    (Join-Path $env:ProgramFiles 'Unity\Hub\Editor'),
    (Join-Path ${env:ProgramFiles(x86)} 'Unity\Hub\Editor')
)

$unity = $null
foreach ($unityRoot in $unityRoots) {
    if (Test-Path $unityRoot) {
        $unity = Get-ChildItem $unityRoot -Filter 'Unity.exe' -Recurse -ErrorAction SilentlyContinue |
            Sort-Object FullName -Descending |
            Select-Object -First 1 -ExpandProperty FullName
        if ($unity) { break }
    }
}

if (-not $unity) {
    throw 'Unity.exe bulunamadi. Unity Hub ile bir Unity Editor kurulumu oldugunu kontrol et.'
}

$log = Join-Path $root 'Tutulma-AutoBuild.log'
Write-Host "Unity bulundu: $unity" -ForegroundColor Cyan
Write-Host 'Tutulma dosyalari aktariliyor ve sahne otomatik uretiliyor...' -ForegroundColor Yellow

& $unity -batchmode -quit -projectPath $root -executeMethod Tutulma.Editor.AutoBuild.BuildScene -logFile $log
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Host "Unity otomatik kurulum hatasi. Log: $log" -ForegroundColor Red
    Get-Content $log -Tail 80 -ErrorAction SilentlyContinue
    exit $exitCode
}

Write-Host ''
Write-Host 'TUTULMA OTOMATIK KURULUM TAMAMLANDI.' -ForegroundColor Green
Write-Host "Sahne: $root\Assets\Scenes\MainScene.unity"
Write-Host "Log:   $log"
