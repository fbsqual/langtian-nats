# Generate protobuf bindings for targets used in the PoC
# Requires: protoc in PATH

$proto = Join-Path $PSScriptRoot '..\proto\battery.proto'
$pyOut = Join-Path $PSScriptRoot '..\simulator'
$csOut = Join-Path $PSScriptRoot '..\collector\protos'

if (-not (Get-Command protoc -ErrorAction SilentlyContinue)) {
    Write-Error "protoc not found in PATH. Install protoc and retry."
    exit 1
}

Write-Host "Generating Python bindings to $pyOut"
protoc --python_out=$pyOut $proto

Write-Host "Generating C# bindings to $csOut"
if (-not (Test-Path $csOut)) { New-Item -ItemType Directory -Path $csOut | Out-Null }
protoc --csharp_out=$csOut $proto

Write-Host "PROTO generation complete. Add generated files to projects as needed."
