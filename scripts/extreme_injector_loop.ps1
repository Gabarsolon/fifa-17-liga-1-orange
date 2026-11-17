. "$PSScriptRoot\Load-Env.ps1"

# Run from the FIFA 17 game dir (or set EXTREME_INJECTOR_PATH in .env).
$injector = if ($env:EXTREME_INJECTOR_PATH) { $env:EXTREME_INJECTOR_PATH } else { "Extreme Injector v3.exe" }

while ($true) {
    Start-Process -FilePath $injector -Wait
    Wait-Process -Name "FIFA17"
}
