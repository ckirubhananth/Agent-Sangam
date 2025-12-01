# Start server script for AgentSangam
# Usage: ./start_server.ps1

param(
    [string]$ApiKey = "",
    [int]$Port = 8000,
    [string]$Host = "127.0.0.1"
)

# If API key not provided as parameter, prompt for it
if (-not $ApiKey) {
    $ApiKey = Read-Host -Prompt "Enter your GOOGLE_API_KEY"
}

# Set the environment variables
$env:GOOGLE_API_KEY = $ApiKey
$env:PORT = $Port
$env:HOST = $Host

# Start the server
cd 'd:\Kirubha\Repo\AgentSangam'
Write-Host "Starting AgentSangam server..." -ForegroundColor Green
Write-Host "Server will be available at http://$Host`:$Port" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

& '.\.venv\Scripts\python.exe' app.py
