param(
    [Parameter(Mandatory=$true)]
    [string]$TargetDirectory
)

# Validate the provided directory path
if (-Not (Test-Path -Path $TargetDirectory -PathType Container)) {
    Write-Host "Error: The specified directory '$TargetDirectory' does not exist."
    exit
}

# texconv: TEXCONV_PATH from .env / environment, else PATH
if (-not $env:TEXCONV_PATH -and (Test-Path (Join-Path (Split-Path $PSScriptRoot -Parent) '.env'))) {
    . "$PSScriptRoot\Load-Env.ps1"
}
$texconv = if ($env:TEXCONV_PATH) { $env:TEXCONV_PATH } else { (Get-Command texconv -ErrorAction SilentlyContinue).Source }
if (-not $texconv -or -not (Test-Path $texconv)) {
    Write-Host "Error: texconv.exe not found. Set TEXCONV_PATH in .env or add it to PATH."
    exit
}

# Get all PNG files in the specified directory
$pngFiles = Get-ChildItem -Path $TargetDirectory -Filter *.png

# Check if there are any PNG files
if ($pngFiles.Count -eq 0) {
    Write-Host "No PNG files found in the specified directory."
    exit
}

# Loop through each PNG file and convert it
foreach ($file in $pngFiles) {
    $outputFile = [System.IO.Path]::ChangeExtension($file.FullName, ".dds")
    # FIFA 17 kit data maps (*_coeff, *_normal) are linear BC1 (DXT1); colour textures are sRGB BC3 (DXT5).
    if ($file.BaseName -match '_(coeff|normal)$') {
        $texArgs = @('-f', 'BC1_UNORM')
    } elseif ($file.BaseName -match '^p\d+$') {
        # player minifaces (data/ui/imgAssets/heads/p<id>.dds): 128x128 BC3 sRGB, single mip like the game's own files
        $texArgs = @('-f', 'BC3_UNORM', '-srgb', '-m', '1')
    } else {
        $texArgs = @('-f', 'BC3_UNORM', '-srgb')
    }
    Write-Host "Converting $($file.Name) to $outputFile ($($texArgs -join ' '))"
    & $texconv @texArgs -o $file.DirectoryName $file.FullName -y
}

Write-Host "Conversion complete!"
