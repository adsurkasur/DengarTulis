@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title DengarTulis - Launcher
echo ==============================================
echo [DengarTulis] Mempersiapkan Virtual Env...
echo ==============================================

:: Cek apakah python terinstall
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan! Harap install Python terlebih dahulu.
    pause
    exit /b
)

:: Cek apakah venv sudah dibuat
if not exist venv (
    echo [INFO] Membuat Virtual Environment venv baru...
    python -m venv venv --system-site-packages
    if errorlevel 1 (
        echo [ERROR] Gagal membuat Virtual Environment.
        pause
        exit /b
    )
)

:: Aktifkan venv
echo [INFO] Mengaktifkan Virtual Environment...
call venv\Scripts\activate

:: Cek apakah dependencies sudah terinstall
if not exist venv\.installed_flag (
    echo [INFO] Menginstal dependensi, ini mungkin memakan waktu beberapa menit...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Gagal menginstal dependensi. Pastikan koneksi internet aktif.
        pause
        exit /b
    )
    echo. > venv\.installed_flag
    echo [INFO] Instalasi dependensi selesai!
)

echo [INFO] Menjalankan DengarTulis...
python main.py
if errorlevel 1 (
    echo [ERROR] Program keluar dengan error code.
    pause
)
