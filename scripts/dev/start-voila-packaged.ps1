param(
    [switch]$Silent,
    [switch]$NoBrowser,
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"

Write-Output "VOILA_V0_8_37_PACKAGED_STARTUP_BOOTSTRAP_START"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PackageRoot = Resolve-Path (Join-Path $ScriptDir "..\..")
$PackageRoot = $PackageRoot.Path

$Python = Join-Path $PackageRoot ".venv\Scripts\python.exe"
$ApiDir = Join-Path $PackageRoot "services\api"
$WebApp = Join-Path $ApiDir "web_app.py"
$HostName = "127.0.0.1"
$Port = 8787

$RequirementCandidates = @(
    (Join-Path $PackageRoot "requirements.txt"),
    (Join-Path $PackageRoot "services\api\requirements.txt"),
    (Join-Path $PackageRoot "requirements-dev.txt")
)

$ExistingRequirementFiles = @()
foreach ($Candidate in $RequirementCandidates) {
    if (Test-Path -LiteralPath $Candidate) {
        $ExistingRequirementFiles += $Candidate
    }
}

$SystemPython = $null
try {
    $SystemPython = (Get-Command python -ErrorAction Stop).Source
} catch {
    $SystemPython = $null
}

$VenvExists = Test-Path -LiteralPath $Python
$WebAppExists = Test-Path -LiteralPath $WebApp
$ApiDirExists = Test-Path -LiteralPath $ApiDir

Write-Output "package_root=$PackageRoot"
Write-Output "venv_python=$Python"
Write-Output "venv_exists=$VenvExists"
Write-Output "api_dir_exists=$ApiDirExists"
Write-Output "web_app_exists=$WebAppExists"
Write-Output "system_python=$SystemPython"
Write-Output "requirements_found=$($ExistingRequirementFiles.Count)"
Write-Output "host=$HostName"
Write-Output "port=$Port"
Write-Output "check_only=$CheckOnly"
Write-Output "silent=$Silent"
Write-Output "no_browser=$NoBrowser"

if (-not $WebAppExists) {
    throw "Nu gasesc web_app.py: $WebApp"
}

if ($CheckOnly) {
    Write-Output "VOILA_V0_8_37_PACKAGED_STARTUP_BOOTSTRAP_CHECK_ONLY=PASS"
    Write-Output "venv_create_performed=False"
    Write-Output "dependency_install_performed=False"
    Write-Output "server_start_performed=False"
    Write-Output "browser_open_performed=False"
    exit 0
}

if (-not $VenvExists) {
    if (-not $SystemPython) {
        throw "Nu gasesc Python de sistem pentru a crea venv. Instaleaza Python 3.12+ si reincearca."
    }

    Write-Output "Creez .venv local in pachet..."
    & $SystemPython -m venv (Join-Path $PackageRoot ".venv")

    if (-not (Test-Path -LiteralPath $Python)) {
        throw "Nu s-a putut crea Python venv: $Python"
    }

    $VenvExists = $true
}

Write-Output "Actualizez pip..."
& $Python -m pip install --upgrade pip

if ($ExistingRequirementFiles.Count -gt 0) {
    foreach ($Req in $ExistingRequirementFiles) {
        Write-Output "Instalez dependinte din: $Req"
        & $Python -m pip install -r $Req
    }
} else {
    Write-Output "Nu am gasit requirements.txt; continui fara instalare dependinte."
}

Write-Output "Pornesc Voila packaged pe http://$HostName`:$Port/"
$UvicornArgs = @(
    "-m", "uvicorn",
    "web_app:app",
    "--app-dir", $ApiDir,
    "--host", $HostName,
    "--port", "$Port",
    "--log-level", "info"
)

if ($Silent) {
    Start-Process -FilePath $Python -ArgumentList $UvicornArgs -WorkingDirectory $PackageRoot -WindowStyle Hidden | Out-Null
} else {
    Start-Process -FilePath $Python -ArgumentList $UvicornArgs -WorkingDirectory $PackageRoot | Out-Null
}

if (-not $NoBrowser) {
    Start-Process "http://$HostName`:$Port/" | Out-Null
}

Write-Output "VOILA_V0_8_37_PACKAGED_STARTUP_BOOTSTRAP_STARTED=PASS"
Write-Output "venv_create_performed=$(-not $VenvExists)"
Write-Output "dependency_install_performed=$($ExistingRequirementFiles.Count -gt 0)"
Write-Output "server_start_performed=True"
Write-Output "browser_open_performed=$(-not $NoBrowser)"
