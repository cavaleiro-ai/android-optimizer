$ErrorActionPreference = 'Stop'
$source = Join-Path $PSScriptRoot 'skills\android-optimizer'
$target = Join-Path $env:USERPROFILE '.claude\skills\android-optimizer'

if (Test-Path $target) {
    Write-Host "Ja existe uma instalacao em $target. Remova essa pasta para reinstalar."
    exit 1
}

New-Item -ItemType Directory -Force (Split-Path $target) | Out-Null
Copy-Item $source $target -Recurse
Remove-Item (Join-Path $target 'evals') -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Skill instalada em $target. Reinicie o Claude Code."
