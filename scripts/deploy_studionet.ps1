$ErrorActionPreference = 'Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..'))
# Python runner uses the repo-local .cmd, never the globally installed rc CLI.
py -3 scripts/network_guard.py --deploy
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
