#!/bin/bash
echo "=============================================="
echo "🎙️ Mempersiapkan DengarTulis (Virtual Env) 🎙️"
echo "=============================================="

# Cek python
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] Python3 tidak ditemukan! Harap install Python3 terlebih dahulu."
    exit 1
fi

# Cek venv
if [ ! -d "venv" ]; then
    echo "[INFO] Membuat Virtual Environment (venv) baru..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Gagal membuat Virtual Environment."
        exit 1
    fi
fi

# Aktifkan venv
echo "[INFO] Mengaktifkan Virtual Environment..."
source venv/bin/activate

# Cek flag
if [ ! -f "venv/.installed_flag" ]; then
    echo "[INFO] Menginstal dependensi..."
    python3 -m pip install --upgrade pip
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        touch venv/.installed_flag
        echo "[INFO] Instalasi dependensi selesai!"
    else
        echo "[ERROR] Gagal menginstal dependensi."
        exit 1
    fi
fi

echo "[INFO] Menjalankan DengarTulis..."
python3 main.py
