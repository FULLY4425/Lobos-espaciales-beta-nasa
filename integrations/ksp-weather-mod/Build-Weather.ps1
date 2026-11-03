param([string]$KspPath, [switch]$Install)
$ErrorActionPreference = 'Stop'
if (-not $KspPath) {
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
    $dialog.Description = 'Selecciona la carpeta de KSP 1.12.x (contiene GameData)'
    if ($dialog.ShowDialog() -ne 'OK') { throw 'Seleccion cancelada.' }
    $KspPath = $dialog.SelectedPath
}
$managed = @('KSP_x64_Data','KSP_Data') | ForEach-Object { Join-Path $KspPath "$_\Managed" } | Where-Object { Test-Path (Join-Path $_ 'Assembly-CSharp.dll') } | Select-Object -First 1
if (-not $managed -or -not (Test-Path (Join-Path $KspPath 'GameData'))) { throw 'No se encontro una instalacion de KSP 1.' }
$csc = @("$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\csc.exe", "$env:WINDIR\Microsoft.NET\Framework\v4.0.30319\csc.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $csc) { throw 'Instala .NET Framework 4.x para disponer del compilador C# de Windows.' }
$build = Join-Path $PSScriptRoot 'build'
New-Item -ItemType Directory -Force -Path $build | Out-Null
$output = Join-Path $build 'LobosWeather.dll'
$references = @('Assembly-CSharp.dll','Assembly-CSharp-firstpass.dll','KSPUtil.dll','UnityEngine.dll','UnityEngine.CoreModule.dll','UnityEngine.IMGUIModule.dll','UnityEngine.UIModule.dll','UnityEngine.ParticleSystemModule.dll','UnityEngine.PhysicsModule.dll','UnityEngine.InputLegacyModule.dll') | ForEach-Object { Join-Path $managed $_ } | Where-Object { Test-Path $_ } | ForEach-Object { '/reference:' + $_ }
& $csc /nologo /target:library /optimize+ ("/out:" + $output) @references (Join-Path $PSScriptRoot 'LobosWeather.cs')
if ($LASTEXITCODE -ne 0) { throw 'La compilacion fallo; no se instala ningun archivo. Conserva la salida del compilador para revisar compatibilidad.' }
if ($Install) {
    $target = Join-Path $KspPath 'GameData\LobosWeather'
    New-Item -ItemType Directory -Force -Path $target | Out-Null
    Copy-Item $output (Join-Path $target 'LobosWeather.dll') -Force
    Write-Host "Instalado en $target. Reinicia KSP. Activar con la barra de mods o Alt+W."
} else { Write-Host "Compilado: $output" }
