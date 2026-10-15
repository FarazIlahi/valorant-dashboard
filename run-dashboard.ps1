param([switch]$RefreshOnly,[switch]$GitHubSync)
$ErrorActionPreference = 'Stop'
$scriptFile = Join-Path $PSScriptRoot 'sync_workbook.py'
$bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$arguments = @($scriptFile)
if (-not $RefreshOnly) { $arguments += @('--watch', '--serve') }
if ($GitHubSync) { $arguments += '--push' }
if (Test-Path -LiteralPath $bundledPython) { & $bundledPython @arguments }
elseif (Get-Command py -ErrorAction SilentlyContinue) { & py -3 @arguments }
elseif (Get-Command python -ErrorAction SilentlyContinue) { & python @arguments }
else { throw 'Python 3 is required. No extra packages are needed.' }
if ($LASTEXITCODE -ne 0) { throw 'Dashboard refresh failed. The previous export was preserved.' }
