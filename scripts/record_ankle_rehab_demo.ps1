param(
    [double]$DurationSeconds = 60.0,
    [bool]$Loop = $true,
    [double]$PublishRateHz = 50.0
)

$ErrorActionPreference = "Stop"

Write-Host "RH1 ankle rehab RViz video demo"
Write-Host "Make sure ROS 2 is sourced before running this script."
Write-Host "Example: .\install\setup.ps1"
Write-Host ""
Write-Host "After RViz opens, start OBS, Xbox Game Bar, or another screen recorder."
Write-Host ""

ros2 launch rh1 ankle_rehab_demo.launch.py `
    duration_s:=$DurationSeconds `
    loop:=$Loop `
    publish_rate_hz:=$PublishRateHz
