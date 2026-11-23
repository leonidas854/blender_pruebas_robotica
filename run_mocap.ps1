param([switch]$Synthetic, [int]$Camera = 0, [int]$Seconds = 0)
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$pythonExe = Join-Path $projectRoot '.venv/Scripts/python.exe'
if (!(Test-Path -LiteralPath $pythonExe)) { throw 'Crear .venv e instalar requirements-mocap.txt. Ver docs/mocap/GUIA_USO.md.' }
Push-Location -LiteralPath $projectRoot
try {
    $env:SSLKEYLOGFILE = ''
    if ($Synthetic) { & $pythonExe mocap_producer.py --synthetic --seconds $Seconds }
    else { & $pythonExe mocap_producer.py --camera $Camera --seconds $Seconds }
} finally { Pop-Location }
