# Somna.ai

Aplikasi web berbasis AI untuk **klasifikasi kebiasaan tidur terhadap tingkat produktivitas** dan **skrining awal indikasi insomnia** menggunakan Jaringan Saraf Tiruan (JST / MLP).

> **Disclaimer:** Somna.ai adalah alat skrining awal dan edukasi pola tidur, **bukan diagnosis medis**. Konsultasikan hasilnya dengan tenaga medis profesional.

---

## Daftar Isi

1. [Tentang Sistem](#tentang-sistem)
2. [Cara Kerja](#cara-kerja)
3. [Arsitektur Model](#arsitektur-model)
4. [Struktur Proyek](#struktur-proyek)
5. [Kebutuhan Sistem](#kebutuhan-sistem)
6. [Cara Mengambil Proyek](#cara-mengambil-proyek)
7. [Cara Menjalankan](#cara-menjalankan)
8. [Endpoint & Contoh Request](#endpoint--contoh-request)
9. [Kontrak Input Form](#kontrak-input-form)
10. [Keluaran Sistem](#keluaran-sistem)
11. [Dataset](#dataset)
12. [Troubleshooting](#troubleshooting)
13. [Tim](#tim)

---

## Tentang Sistem

Somna.ai menganalisis 7 variabel kebiasaan tidur dan gaya hidup pengguna, lalu menghasilkan dua keluaran sekaligus:

| Keluaran | Kelas |
| :--- | :--- |
| **Tingkat Produktivitas** | Rendah, Sedang, Tinggi |
| **Indikasi Insomnia** | Tidak Ada Gejala, Subthreshold, Sedang, Berat |

Setiap hasil disertai tingkat kepercayaan (*confidence*), analisis terpadu, faktor pemicu, dan rekomendasi perbaikan tidur. Sistem berjalan *real-time* dan **tidak menyimpan data pribadi pengguna**.

Stack: Python, Flask (Jinja2, server-side rendering), scikit-learn (MLP), Tailwind CSS (CDN), vanilla JavaScript.

---

## Cara Kerja

```
Pengguna isi form (7 variabel)
        │
        ▼
POST /analyze  ──►  backend/validators.py  (validasi + konversi tipe)
        │
        ▼
backend/prediction.py
   ├─ Model 1 (Insomnia)      : 4 fitur  ──► probabilitas ──► + adjustment ──► skor 0–100
   └─ Model 2 (Produktivitas) : 5 fitur  ──► kelas 3 kategori + confidence
        │
        ▼
Analisis terpadu + faktor pemicu
        │
        ▼
result.html  (render via Jinja2)
```

Detail:

1. **Validasi** — `validators.py` memeriksa tipe, rentang, dan pilihan tiap field. Input dari form maupun JSON diperlakukan sama (validasi JavaScript bisa dilewati, jadi backend wajib memeriksa ulang).
2. **Model 1 (Insomnia)** — input `[durasi_tidur, kualitas_tidur, aktivitas_fisik, tingkat_stres]` di-*clip* ke rentang data training, lalu di-*scale* dan diprediksi. Hasilnya probabilitas insomnia (0–100%).
3. **Hybrid Scoring** — probabilitas Model 1 ditambah *adjustment* dari frekuensi kesulitan tidur (variabel yang tidak ada di dataset publik):

   | Kesulitan tidur | Adjustment |
   | :--- | :--- |
   | Tidak / Jarang | +0% |
   | Sering | +10% |
   | Selalu | +20% |

   `skor_akhir = clip(prob_jst + adjustment, 0, 100)`

   Pemetaan kategori: `<25` Tidak Ada Gejala · `25–50` Subthreshold · `51–75` Sedang · `>75` Berat.
4. **Model 2 (Produktivitas)** — input `[sleep_hours, phone_usage_hours, coffee_intake_mg, exercise_minutes, stress_level]`, hasil berupa kelas + confidence.
5. **Analisis terpadu** — narasi gabungan kedua model beserta daftar pemicu (durasi tidur pendek, kualitas rendah, aktivitas minim, layar/kafein/kesulitan tidur sering).

---

## Arsitektur Model

Dua model dilatih terpisah dari dua dataset berbeda, lalu digabung di lapisan aplikasi (*Hybrid Multi-Model*), bukan digabung paksa di level data.

| | Model 1 — Insomnia | Model 2 — Produktivitas |
| :--- | :--- | :--- |
| Algoritma | MLP (`MLPClassifier`) | MLP (`MLPClassifier`) |
| Dataset | Sleep Health & Lifestyle (374 baris) | Student Productivity (16.000 baris) |
| Fitur | 4 | 5 |
| Target | Biner (Insomnia / bukan) | 3 kelas (Rendah/Sedang/Tinggi) |
| File | `models/sleep_model.keras` + `sleep_scaler.pkl` | `models/productivity_model.keras` + `productivity_scaler.pkl` |

> **Catatan penting:** meskipun berekstensi `.keras`, kedua file model sebenarnya adalah objek **scikit-learn** yang disimpan dengan `joblib`. Jangan dimuat dengan `keras.models.load_model()` — gunakan `joblib.load()` seperti di `backend/prediction.py`.

Fitur Model 1 di-*clip* ke rentang data training agar input ekstrem tetap stabil:

```python
SLEEP_FEATURE_BOUNDS = [(5.8, 8.5), (4, 9), (30, 90), (3, 8)]
# durasi tidur, kualitas tidur, aktivitas fisik, tingkat stres
```

Pemetaan pilihan form ke angka untuk Model 2:

| Pilihan | `phone_usage_hours` | `coffee_intake_mg` |
| :--- | :--- | :--- |
| Tidak | 0.0 | 0 |
| Jarang | 1.0 | 100 |
| Sering | 2.0 | 250 |
| Selalu | 3.0 | 400 |

---

## Struktur Proyek

```text
somna.ai/
├── app.py                      # Entry point (application factory)
├── config.py                   # Konfigurasi Flask (SECRET_KEY, DEBUG)
├── requirements.txt            # Dependensi Python
├── prd_somna_ai_final_v2_0.md  # Product Requirements Document
│
├── backend/
│   ├── routes.py               # Blueprint: /, /about, /analyze, /api/analyze
│   ├── validators.py           # Validasi + konversi input form
│   ├── prediction.py           # Load model, inferensi JST, hybrid scoring
│   ├── preprocessing.py        # Placeholder utilitas pra-pemodelan
│   └── recommendation.py       # Placeholder engine rekomendasi (rule-based)
│
├── models/                     # Model JST + scaler (joblib)
│   ├── sleep_model.keras
│   ├── sleep_scaler.pkl
│   ├── productivity_model.keras
│   └── productivity_scaler.pkl
│
├── dataset/
│   ├── raw/                    # CSV mentah (perlu diunduh dari Kaggle, lihat bawah)
│   └── processed/              # sleep_cleaned.csv, productivity_cleaned.csv
│
├── notebooks/                  # Eksplorasi data & training (Colab)
│   ├── 01_data_exploration.ipynb
│   ├── 02_data_preprocessing.ipynb
│   ├── 03_productivity_model.ipynb
│   ├── 04_sleep_model.ipynb
│   └── 05_model_evaluation.ipynb
│
├── templates/
│   ├── base.html               # Layout + Tailwind CDN + Google Fonts
│   ├── index.html              # Landing page (form analisis)
│   ├── result.html             # Halaman hasil inferensi
│   ├── about.html              # Tentang sistem
│   ├── 404.html / 500.html     # Halaman error
│   └── components/             # navbar, hero, features, steps, form,
│                               # results, tips, footer
│
├── static/
│   ├── css/                    # style.css, result.css, responsive.css, dashboard.css
│   ├── js/                     # app.js, form.js, main.js, result.js
│   └── images/
│
└── tests/                      # Placeholder pytest (belum berisi kasus uji)
```

---

## Kebutuhan Sistem

- Python **3.10 – 3.13** (proyek diuji pada Python 3.13)
- pip
- Git
- Koneksi internet (Tailwind CSS & Google Fonts dimuat via CDN)

> Python 3.14 belum diverifikasi. Jika memakai 3.14 dan muncul error aneh pada `scikit-learn`/`pandas`, gunakan Python 3.13.

---

## Cara Mengambil Proyek

```bash
git clone https://github.com/inirifyy/Somna.ai.git
cd Somna.ai
```

Atau unduh ZIP dari halaman GitHub → **Code → Download ZIP**, lalu ekstrak.

### Dataset mentah

File `dataset/raw/*.csv` di repo kosong (0 byte). Untuk melatih ulang model, unduh dataset:

1. **Sleep Health and Lifestyle Dataset** — Kaggle → simpan sebagai `dataset/raw/sleep_health_lifestyle.csv`
2. **Student Productivity Prediction Challenge** (`train.csv`) — Kaggle → simpan sebagai `dataset/raw/student_performance.csv`

Untuk **menjalankan aplikasi saja** dataset tidak diperlukan — cukup file model di `models/`.

---

## Cara Menjalankan

### 1. Buat virtual environment (disarankan)

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**

```bat
python -m venv venv
venv\Scripts\activate.bat
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependensi

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Verifikasi cepat

```bash
python -c "from app import create_app; create_app(); print('OK')"
```

### 4. Jalankan server

```bash
python app.py
```

Buka **http://127.0.0.1:5000** di browser.

Server berjalan dengan `debug=True` (auto-reload saat file berubah). Untuk produksi, matikan debug di `config.py` dan gunakan WSGI server (mis. `waitress` / `gunicorn`).

---

## Endpoint & Contoh Request

| Method | Path | Fungsi |
| :--- | :--- | :--- |
| GET | `/` | Landing page + form analisis |
| GET | `/about` | Halaman tentang sistem |
| POST | `/analyze` | Proses form → render `result.html` |
| POST | `/api/analyze` | Versi JSON (untuk testing / fetch) |

### Contoh `curl` (JSON API)

```bash
curl -X POST http://127.0.0.1:5000/api/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"durasi_tidur\":7,\"kualitas_tidur\":8,\"aktivitas_fisik\":60,\"tingkat_stres\":6,\"layar_sebelum_tidur\":\"Jarang\",\"konsumsi_kafein\":\"Jarang\",\"kesulitan_tidur\":\"Jarang\"}"
```

Contoh respons sukses:

```json
{
  "ok": true,
  "produktivitas_label": "Tinggi",
  "produktivitas_confidence": 49.1,
  "insomnia_label": "Tidak Ada Gejala",
  "insomnia_confidence": 1.31,
  "analisis_terpadu": "Produktivitas terprediksi Tinggi, indikasi insomnia: Tidak Ada Gejala. Pola tidur tergolong sehat, pertahankan kebiasaan baik."
}
```

Contoh respons gagal validasi (`400`):

```json
{
  "ok": false,
  "errors": {
    "durasi_tidur": "Durasi tidur (jam) harus antara 2 dan 12."
  }
}
```

> Pada `/analyze` (HTML), error validasi mengembalikan halaman form dengan pesan error dan isian sebelumnya tetap terisi.

---

## Kontrak Input Form

Nama field harus sama persis antara HTML dan backend.

| Field | Tipe | Rentang / Pilihan | Catatan |
| :--- | :--- | :--- | :--- |
| `durasi_tidur` | float | 2 – 12 jam | rata-rata 7 hari terakhir |
| `kualitas_tidur` | int | 1 – 10 | 1 = buruk, 10 = sangat baik |
| `tingkat_stres` | int | 1 – 10 | 1 = sangat rendah, 10 = sangat tinggi |
| `aktivitas_fisik` | int | 0 – 240 menit/hari | UI menyediakan 30/45/60/75/90 |
| `layar_sebelum_tidur` | pilihan | Tidak, Jarang, Sering, Selalu | → `phone_usage_hours` |
| `konsumsi_kafein` | pilihan | Tidak, Jarang, Sering, Selalu | → `coffee_intake_mg` |
| `kesulitan_tidur` | pilihan | Tidak, Jarang, Sering, Selalu | → adjustment hybrid scoring |

Angka desimal dengan koma (mis. `7,5`) otomatis dinormalkan menjadi `7.5`.

---

## Keluaran Sistem

Halaman `result.html` menampilkan:

1. **Kartu Klasifikasi Produktivitas** — kelas + confidence + deskripsi dampak.
2. **Kartu Skrining Insomnia** — kategori + confidence + catatan skrining.
3. **Analisis Terpadu** — narasi gabungan kedua model dan indikator faktor pemicu.
4. **Saran Perbaikan Tidur** — jadwal tidur konsisten, *digital sunset*, batas kafein, relaksasi, aktivitas fisik.

---

## Dataset

| Dataset | Baris | Kolom dipakai | Target |
| :--- | :--- | :--- | :--- |
| Sleep Health & Lifestyle | 374 | `Sleep Duration`, `Quality of Sleep`, `Physical Activity Level`, `Stress Level` | `Sleep Disorder` |
| Student Productivity | 16.000 | `sleep_hours`, `phone_usage_hours`, `coffee_intake_mg`, `exercise_minutes`, `stress_level` | `productivity_score` → 3 kelas |

Aturan preprocessing penting:

- `Sleep Disorder` yang kosong **tidak boleh** di-`dropna` — isi dengan `fillna('None')` karena merepresentasikan kategori normal.
- Target insomnia dikonversi biner: `Insomnia = 1`, lainnya `= 0`.
- `productivity_score` dibinning menjadi 3 kelas sebelum training.
- Split evaluasi: 80% train / 20% test (`train_test_split`).

Hasil pembersihan tersedia di `dataset/processed/` (`sleep_cleaned.csv`, `productivity_cleaned.csv`).

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'joblib'` (atau `flask`, `sklearn`)**

Penyebab hampir selalu: paket terinstal di interpreter yang berbeda dari yang menjalankan aplikasi. Cek interpreter aktif:

```bash
python -c "import sys; print(sys.executable)"
python -m pip -V
```

Path pada dua perintah di atas harus menunjuk Python yang sama. Lalu install ulang:

```bash
python -m pip install -r requirements.txt
```

Cara paling aman: aktifkan virtual environment (lihat [Cara Menjalankan](#cara-menjalankan)) sebelum install dan sebelum `python app.py`.

**Model gagal dimuat / `Invalid load key`**

File model adalah objek scikit-learn hasil `joblib.dump`. Muat dengan `joblib.load(...)`, bukan `keras.models.load_model(...)`. Pastikan juga versi `scikit-learn` tidak terlalu jauh berbeda dari versi saat model dilatih.

**Halaman tampil tanpa styling**

Tailwind dimuat dari CDN — butuh koneksi internet. Jika offline, styling tidak akan muncul.

**Port 5000 sudah dipakai**

```bash
python -c "from app import create_app; create_app().run(port=5001)"
```

## Tim

| Anggota | Peran |
| :--- | :--- |
| **Aidil** | AI & Arsitektur Sistem — arsitektur JST, training model, hybrid scoring, dokumentasi AI |
| **Rify** | Data & Backend Flask — pembersihan dataset, training model insomnia, backend & validasi |
| **Inri** | Frontend & Integrasi UI — desain UI, template Jinja2, CSS/JS, integrasi form |

Dokumen kebutuhan lengkap: [`prd_somna_ai_final_v2_0.md`](prd_somna_ai_final_v2_0.md)
