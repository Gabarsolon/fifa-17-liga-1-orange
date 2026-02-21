while ($true) {
    Start-Process -FilePath "Extreme Injector v3.exe" -Wait
    Wait-Process -Name "FIFA17"
}

