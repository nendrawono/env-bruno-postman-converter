# Environment Converter (Bruno <-> Postman)

Tool CLI Python untuk mengonversi file environment **Bruno (`.bru`)** ke **Postman Environment (`.postman_environment.json`)** dan sebaliknya secara dua arah.

---

## 1. Prasyarat
* **Python 3.9+** sudah terinstal di sistem Anda (`python --version` atau `python3 --version`).
* Tidak memerlukan instalasi library pihak ketiga (100% menggunakan *Python Standard Library*).

---

## 2. Instalasi & Setup Virtual Environment (`venv`)

Jalankan perintah berikut di terminal dari root folder repositori:

### Windows (PowerShell / CMD)
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### macOS / Linux / Git Bash
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

*(Pastikan folder `.venv/` sudah masuk ke `.gitignore` agar tidak ikut ter-commit ke GitHub).*

---

## 3. Cara Penggunaan

1. Pastikan virtual environment (`.venv`) dalam keadaan aktif.
2. Jalankan script converter:
   ```bash
   python env_converter.py
   ```
3. Pilih mode konversi di terminal:
   * Ketik **`1`** untuk mengonversi **`.bru` $\rightarrow$ `.postman_environment.json`**
   * Ketik **`2`** untuk mengonversi **`.postman_environment.json` $\rightarrow$ `.bru`**
4. Masukkan **full path file** yang akan dikonversi (Anda juga bisa *drag & drop* file ke terminal atau *Copy as path*), contoh:
   * Contoh input opsi `1`:
     `D:\Project\COLLECTION\environments\ShippingLine - Dev.bru`
   * Contoh input opsi `2`:
     `D:\Project\COLLECTION\environments\ShippingLine - Dev.postman_environment.json`
5. File hasil konversi akan otomatis tersimpan **di direktori yang sama dengan file input**.
