# Start NATS Server with JetStream using local nats-server binary
# If nats-server is not installed, the script will print instructions to download it.

$conf = Join-Path $PSScriptRoot 'nats.conf'
$exe = Get-Command nats-server -ErrorAction SilentlyContinue

function Start-NatsServer($exePath, $confPath) {
    Write-Host "Starting nats-server ($exePath) with config $confPath"
    Start-Process powershell -ArgumentList "-NoExit","-Command","& '$exePath' -c '$confPath'"
}

if (-not $exe) {
    Write-Host "nats-server not found in PATH. Will attempt to download a nats-server Windows binary into $PSScriptRoot\bin"
    $binDir = Join-Path $PSScriptRoot 'bin'
    if (-not (Test-Path $binDir)) { New-Item -ItemType Directory -Path $binDir | Out-Null }

    # Choose a stable release tag; update if you need a specific version
    $tag = 'v2.10.4'
    $zipName = "nats-server-$tag-windows-amd64.zip"
    $downloadUrl = "https://github.com/nats-io/nats-server/releases/download/$tag/$zipName"
    $zipPath = Join-Path $binDir $zipName
    $exePath = Join-Path $binDir 'nats-server.exe'

    if (-not (Test-Path $exePath)) {
        Write-Host "Downloading nats-server from $downloadUrl ..."
        try {
            Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath -UseBasicParsing -ErrorAction Stop
            Write-Host "Extracting $zipPath to $binDir"
            Expand-Archive -LiteralPath $zipPath -DestinationPath $binDir -Force
            Remove-Item $zipPath -Force
        } catch {
            Write-Host "Automatic download failed: $_"
            Write-Host "Please download nats-server manually from: https://github.com/nats-io/nats-server/releases and place nats-server.exe in $binDir or in your PATH."
            exit 1
        }
    } else {
        Write-Host "Found downloaded nats-server at $exePath"
    }

    Start-NatsServer $exePath $conf
    return
}

$exePath = $exe.Source
Start-NatsServer $exePath $conf
