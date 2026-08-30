# Setup virtual environment (jika belum ada) lalu jalankan Drug Safety Platform API.
# Pakai: .\run.ps1            -> setup (jika perlu) + install deps + jalankan server
#        .\run.ps1 -SkipInstall -> lewati install deps, langsung jalankan server (lebih cepat)

param(
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$venvPath = Join-Path $root ".venv"
$pythonExe = Join-Path $venvPath "Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "Virtual environment belum ada, membuat .venv dengan Python 3.11..." -ForegroundColor Cyan

    if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
        Write-Error "Python launcher 'py' tidak ditemukan di PATH. Install Python dari https://www.python.org/ terlebih dahulu."
        exit 1
    }

    & py -3.11 -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Gagal membuat venv dengan Python 3.11. Pastikan Python 3.11 terinstal (winget install --id Python.Python.3.11)."
        exit 1
    }
}

if (-not $SkipInstall) {
    Write-Host "Menginstal dependencies dari requirements.txt..." -ForegroundColor Cyan

    & $pythonExe -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { exit 1 }

    & $pythonExe -m pip install -r (Join-Path $root "requirements.txt")
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

Write-Host ""
Write-Host "Menjalankan server di http://127.0.0.1:8000 (frontend) dan http://127.0.0.1:8000/docs (Swagger UI)" -ForegroundColor Green
Write-Host "Tekan CTRL+C untuk berhenti." -ForegroundColor Green
Write-Host ""

& $pythonExe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
