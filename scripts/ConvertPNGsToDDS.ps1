param(
    [Parameter(Mandatory=$true)]
    [string]$TargetDirectory
)

# Validate the provided directory path
if (-Not (Test-Path -Path $TargetDirectory -PathType Container)) {
    Write-Host "Error: The specified directory '$TargetDirectory' does not exist."
    exit
}

# Ensure texconv is available in the system PATH
if (-not (Get-Command texconv -ErrorAction SilentlyContinue)) {
    Write-Host "Error: texconv.exe is not found in the system PATH."
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
    $command = "texconv -f BC3_UNORM -m 1 -srgb -o $($file.DirectoryName) $($file.FullName)"
    
    Write-Host "Converting $($file.Name) to $outputFile"
    Invoke-Expression $command
}

Write-Host "Conversion complete!"
