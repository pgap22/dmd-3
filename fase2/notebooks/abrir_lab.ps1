[CmdletBinding()]
param(
    [switch]$Verificar
)

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$projectDir = Join-Path $repoRoot 'tmp\codigo'
$environmentDir = Join-Path $repoRoot 'tmp\entorno\notebook'
$projectFile = Join-Path $projectDir 'pyproject.toml'

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw 'No se encontró uv. Instálalo con: winget install --id=astral-sh.uv -e'
}

if (-not (Test-Path -LiteralPath $projectFile)) {
    throw "No se encontró la configuración del proyecto: $projectFile"
}

$env:UV_PROJECT_ENVIRONMENT = $environmentDir

Push-Location -LiteralPath $repoRoot
try {
    if ($Verificar) {
        $check = @'
import pandas
import numpy
import matplotlib
import seaborn
import sklearn
import nbformat
print("ENTORNO_OK")
print(f"pandas={pandas.__version__}")
print(f"scikit-learn={sklearn.__version__}")
print(f"seaborn={seaborn.__version__}")
'@
        & uv run --project $projectDir python -c $check
    }
    else {
        & uv run --project $projectDir jupyter lab
    }

    if ($LASTEXITCODE -ne 0) {
        throw "uv terminó con código $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
