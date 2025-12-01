# Start server script for AgentSangam
# Usage: ./start_server.ps1

param(
    [string]$ApiKey = ""
)

# If API key not provided as parameter, prompt for it
if (-not $ApiKey) {
    $ApiKey = Read-Host -Prompt "Enter your GOOGLE_API_KEY"
}

# Set the environment variable
$env:GOOGLE_API_KEY = $ApiKey

# Start the server
cd 'd:\Kirubha\Repo\AgentSangam'
Write-Host "Starting AgentSangam server..." -ForegroundColor Green
Write-Host "Server will be available at http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

& '.\.venv\Scripts\python.exe' -m uvicorn app:app --host 127.0.0.1 --port 8000
