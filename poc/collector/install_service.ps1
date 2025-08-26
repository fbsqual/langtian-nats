# Publish collector and register as Windows Service (example)
# This script publishes a self-contained exe for win-x64 and registers it as a service.
# Requires: dotnet SDK

$proj = Join-Path $PSScriptRoot 'UdpCollector.csproj'
$out = Join-Path $PSScriptRoot 'publish'

if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) { Write-Error "dotnet not found"; exit 1 }

Write-Host "Publishing self-contained exe (win-x64) to $out ..."
dotnet publish $proj -c Release -r win-x64 -o $out /p:PublishSingleFile=true --self-contained true

$exe = Get-ChildItem -Path $out -Filter '*.exe' | Select-Object -First 1
if (-not $exe) { Write-Error "Publish did not produce an exe"; exit 1 }

$svcName = 'UdpCollector'
$svcDisplay = 'UDP Collector Service'
$exePath = $exe.FullName

# Create service
if (Get-Service -Name $svcName -ErrorAction SilentlyContinue) {
    Write-Host "Service $svcName already exists - attempting to stop and remove"
    Stop-Service $svcName -Force -ErrorAction SilentlyContinue
    sc.exe delete $svcName | Out-Null
    Start-Sleep -Seconds 2
}

Write-Host "Creating service $svcName -> $exePath"
sc.exe create $svcName binPath= "`"$exePath`"" DisplayName= "$svcDisplay" start= auto
Write-Host "Service created. Start with: Start-Service $svcName"
