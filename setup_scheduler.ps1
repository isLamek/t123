# ─────────────────────────────────────────────────────────────────────────────
#  Omugongo — register the daily 7:00 AM morning sweep in Windows Task Scheduler.
#
#  Run once, from the project folder:
#      powershell -ExecutionPolicy Bypass -File .\setup_scheduler.ps1
#
#  Re-running updates the existing task. To change the time, edit $RunTime below.
#  To remove it later:   Unregister-ScheduledTask -TaskName "Omugongo_Morning_Sweep"
# ─────────────────────────────────────────────────────────────────────────────

param(
    [string]$RunTime = "7:00AM"
)

$TaskName   = "Omugongo_Morning_Sweep"
$ProjectDir = $PSScriptRoot
$Script     = Join-Path $ProjectDir "run_sweep.py"

# Prefer a project virtualenv, then pythonw (no console window), then python.
$VenvPyW = Join-Path $ProjectDir ".venv\Scripts\pythonw.exe"
if (Test-Path $VenvPyW) {
    $PyExe = $VenvPyW
} else {
    $pw = Get-Command pythonw.exe -ErrorAction SilentlyContinue
    if ($pw) { $PyExe = $pw.Source } else {
        $p = Get-Command python.exe -ErrorAction SilentlyContinue
        if ($p) { $PyExe = $p.Source } else {
            Write-Host "ERROR: Could not find python. Install Python or create .venv first." -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host "Project : $ProjectDir"
Write-Host "Python  : $PyExe"
Write-Host "Script  : $Script"
Write-Host "Time    : $RunTime daily"

$Action = New-ScheduledTaskAction -Execute $PyExe -Argument "`"$Script`"" -WorkingDirectory $ProjectDir
$Trigger = New-ScheduledTaskTrigger -Daily -At $RunTime

# Run as the current user, only when logged on (no stored password needed).
$Principal = New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited

# Laptop-friendly: still run on battery; don't kill it mid-sweep.
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 1)

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
    -Principal $Principal -Settings $Settings `
    -Description "Omugongo: sweeps Namibian jobs/scholarships/events, scores them, and sends a digest." `
    -Force | Out-Null

Write-Host ""
Write-Host "Omugongo morning sweep registered for $RunTime daily." -ForegroundColor Green
Write-Host "Test it now with:  Start-ScheduledTask -TaskName `"$TaskName`"" -ForegroundColor Cyan
Write-Host "Watch results in:  data\sweep.log"
