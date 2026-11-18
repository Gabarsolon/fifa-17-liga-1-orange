# Builds the launcher and assembles releases/Liga1OrangeLauncher-<version>.zip
#   pwsh scripts/package_launcher.ps1 [-Mod releases\Liga1Orange-v0.5.0.fbmod] [-Version 1.0.0]
# Layout of the zip (everything the player needs, no game files):
#   Liga1OrangeLauncher.exe          the launcher (asks for administrator rights: Frosty links ModData with a symlink)
#   tools\FrostyCmd.exe + libraries  headless Frosty (FrostyCLI, GPL-3), only the FIFA 17 profile; it builds its own cache on first use
#   mods\Liga1Orange-<tag>.fbmod     the mod (+ version.txt)
#   CITESTE-MA.txt                   short instructions, licences and where the sources are
# CryptBase.dll: tools\ThirdParty\CryptBase.dll is Frosty's loader; the executor copies it into the game folder on the first apply.
param(
    [string]$Mod = "",
    [string]$Version = "1.0.0"
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
. "$PSScriptRoot\Load-Env.ps1"

if (-not $Mod) {
    $latest = Get-ChildItem "$root\releases\Liga1Orange-v*.fbmod" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $latest) { throw "no mod in releases\ (build one with FrostyCmd build-mod)" }
    $Mod = $latest.FullName
}
$tag = [regex]::Match((Split-Path $Mod -Leaf), 'Liga1Orange-(v[\d\.]+)\.fbmod').Groups[1].Value
if (-not $tag) { throw "mod file name must look like Liga1Orange-v0.5.0.fbmod" }

$out = "$root\releases\_launcher_build"
$pkg = "$out\Liga1OrangeLauncher"
Remove-Item $out -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force "$pkg\tools\Profiles", "$pkg\tools\ThirdParty", "$pkg\tools\Plugins", "$pkg\mods" | Out-Null

Write-Host "1. build launcher $Version"
dotnet build "$root\launcher\Liga1OrangeLauncher.csproj" -c Release -p:Version=$Version -o "$out\bin" | Out-Null
if ($LASTEXITCODE -ne 0) { throw "launcher build failed" }
Copy-Item "$out\bin\Liga1OrangeLauncher.exe", "$out\bin\Liga1OrangeLauncher.exe.config" $pkg

Write-Host "2. headless Frosty (FIFA 17 profile only)"
$frostyDir = Split-Path -Parent $env:FROSTYCLI_PATH
Copy-Item "$frostyDir\*.dll", "$frostyDir\FrostyCmd.exe" "$pkg\tools"
# The zip comes from the internet: its files carry the Mark of the Web and .NET Framework refuses to Assembly.LoadFile them
# unless loadFromRemoteSources is on (the launcher also removes the marks). Reproduced and verified 2026-11-19.
@'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
    <startup>
        <supportedRuntime version="v4.0" sku=".NETFramework,Version=v4.8"/>
    </startup>
    <runtime>
        <loadFromRemoteSources enabled="true"/>
    </runtime>
</configuration>
'@ | Set-Content "$pkg\tools\FrostyCmd.exe.config" -Encoding UTF8
Copy-Item "$frostyDir\Profiles\Fifa17SDK.dll" "$pkg\tools\Profiles"
Copy-Item "$frostyDir\Plugins\*" "$pkg\tools\Plugins" -Recurse -Exclude "*.disabled"
$skip = "avcodec-58.dll", "avformat-58.dll", "avutil-56.dll", "swresample-3.dll", "GFSDK_Txaa.win64.dll"
Get-ChildItem "$frostyDir\ThirdParty" -File | Where-Object { $skip -notcontains $_.Name } | Copy-Item -Destination "$pkg\tools\ThirdParty"

Write-Host "3. mod $tag"
Copy-Item $Mod "$pkg\mods\Liga1Orange-$tag.fbmod"
Set-Content "$pkg\mods\version.txt" $tag -NoNewline

Write-Host "4. instructions"
@"
LIGA 1 ORANGE 2016/17 - LAUNCHER
================================
Mod pentru FIFA 17 (PC): Liga 1 Orange 2016/17 in locul ligii daneze, interfata in romana.

CE TREBUIE SA AI
 - FIFA 17 instalat pe PC (Windows 10/11).
 - Nimic altceva: Frosty copiaza singur CryptBase.dll (incarcatorul de mod) in folderul jocului la prima pornire.

CUM FOLOSESTI
 1. Dezarhiveaza intregul folder oriunde (nu in Program Files).
 1b. Daca Windows blocheaza fisierele descarcate: clic dreapta pe zip -> Proprietati -> Deblocare, inainte de dezarhivare
     (launcherul deblocheaza si singur fisierele din tools\ si mods\).
 2. Porneste Liga1OrangeLauncher.exe (cere drepturi de administrator; Frosty leaga fisierele moduluii de joc
    printr-un link simbolic).
 3. Launcherul gaseste FIFA 17; daca nu, apasa "Alege folderul..." si alege folderul cu FIFA17.exe.
 4. Apasa "JOACA LIGA 1 ORANGE".
 La prima pornire Frosty isi construieste singur un cache (~4 minute, o singura data). Dupa aceea porneste in cateva secunde.
 "Pornește jocul original" porneste FIFA 17 fara mod.

DESPRE ACTUALIZARI
 Launcherul poate descarca noile versiuni de pe GitHub Releases cand acestea sunt publice. Pana atunci foloseste
 modul din folderul mods\.

LICENTE SI SURSE
 - Launcherul si modul: proiect de fani, toate drepturile asupra jocului apartin EA Sports; datele provin din FIFA 16 +
   patch-ul FRLT V2 (echipa EFET).
 - Folderul tools\ contine Frosty Toolsuite (CadeEvs, GPL-3.0) in varianta FrostyCLI. Sursele corespunzatoare:
   https://github.com/CadeEvs/FrostyToolsuite si https://github.com/Gabarsolon/FrostyCLI
 - Sursele launcherului: folderul launcher\ din https://github.com/Gabarsolon/fifa-17-liga-1-orange
 Acest pachet nu contine fisiere ale jocului.
"@ | Set-Content "$pkg\CITESTE-MA.txt" -Encoding UTF8

Write-Host "5. zip"
$zip = "$root\releases\Liga1OrangeLauncher-$tag.zip"
Remove-Item $zip -ErrorAction SilentlyContinue
Compress-Archive -Path $pkg -DestinationPath $zip -CompressionLevel Optimal
$size = [math]::Round((Get-Item $zip).Length / 1MB, 1)
Write-Host "done: $zip ($size MB)"
