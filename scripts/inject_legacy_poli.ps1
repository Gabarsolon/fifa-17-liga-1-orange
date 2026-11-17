. "$PSScriptRoot\Load-Env.ps1"

$FrostyCmd = $env:FROSTYCLI_PATH
$RepoRoot = Split-Path $PSScriptRoot -Parent
$Project = Join-Path $RepoRoot "Liga1Orange.fbproject"
$AssetsDir = Join-Path $RepoRoot "assets\teams\poli"

$legacyMap = @{
    "data/ui/imgAssets/crest/dark/l1443.dds" = "$AssetsDir\team_130022_crest_standard.dds"
    "data/ui/imgAssets/crest/light/l1443.dds" = "$AssetsDir\team_130022_crest_standard.dds"
    "data/ui/imgAssets/crest16x16/dark/l1443.dds" = "$AssetsDir\team_130022_crest_16x16.dds"
    "data/ui/imgAssets/crest16x16/light/l1443.dds" = "$AssetsDir\team_130022_crest_16x16.dds"
    "data/ui/imgAssets/crest32x32/dark/l1443.dds" = "$AssetsDir\team_130022_crest_32x32.dds"
    "data/ui/imgAssets/crest32x32/light/l1443.dds" = "$AssetsDir\team_130022_crest_32x32.dds"
    "data/ui/imgAssets/crest50x50/dark/l1443.dds" = "$AssetsDir\team_130022_crest_50x50.dds"
    "data/ui/imgAssets/crest50x50/light/l1443.dds" = "$AssetsDir\team_130022_crest_50x50.dds"
    "data/ui/imgAssets/kits/j0_1443_0.dds" = "$AssetsDir\team_130022_kit_0_minikit.dds"
    "data/ui/imgAssets/kits/j1_1443_0.dds" = "$AssetsDir\team_130022_kit_1_minikit.dds"
    "data/ui/imgAssets/kits/j2_1443_0.dds" = "$AssetsDir\team_130022_kit_2_minikit.dds"
}

# FrostyCmd must run from its own folder (it loads sibling DLLs).
Set-Location -Path (Split-Path $FrostyCmd -Parent)

foreach ($key in $legacyMap.Keys) {
    $payload = $legacyMap[$key]
    if (Test-Path $payload) {
        Write-Host "Injecting $payload -> $key"
        & $FrostyCmd "FIFA17" "import-legacy" $Project $key $payload
    } else {
        Write-Host "Missing file: $payload"
    }
}
