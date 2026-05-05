$ErrorActionPreference = "SilentlyContinue"

$Port = 8787

Write-Host "Stopping Voila! local UI on port $Port..."

$Connections = @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)

foreach ($Connection in $Connections) {
    $PidToStop = $Connection.OwningProcess

    if ($PidToStop) {
        Write-Host "Stopping process PID $PidToStop"
        Stop-Process -Id $PidToStop -Force -ErrorAction SilentlyContinue
    }
}

Start-Sleep -Milliseconds 500

$StillOpen = @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)

if ($StillOpen.Count -gt 0) {
    Write-Host "Port $Port is still in use."
}
else {
    Write-Host "Voila! local UI stopped."
}
