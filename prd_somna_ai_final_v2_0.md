  # Product Requirements Document (PRD): Somna.ai

**Versi:** 2.0 (Finalisasi Arsitektur, Dataset, & 7 Inputan)  
**Nama Sistem:** Somna.ai  
**Judul Proyek:** Klasifikasi Kebiasaan Tidur terhadap Tingkat Produktivitas dan Indikasi Gangguan Tidur Menggunakan Jaringan Saraf Tiruan (JST)  
**Tim Pengembang:** Aidil (AI & Arsitektur), Rify (Data & Backend), Inri (Frontend & UI/UX)  
**Tech Stack:** Python, Jaringan Saraf Tiruan (JST), Flask (Jinja2), HTML, CSS, JavaScript

---

## 1. Ringkasan Produk
**Somna.ai** adalah aplikasi web berbasis *Artificial Intelligence* yang menganalisis kebiasaan tidur dan gaya hidup pengguna untuk mengklasifikasikan **tingkat produktivitas** serta melakukan **skrining awal indikasi gangguan tidur (insomnia)** menggunakan metode Jaringan Saraf Tiruan (JST).

Sistem berjalan secara *real-time* tanpa menyimpan data pribadi pengguna secara permanen. Untuk menjaga validitas ilmiah tanpa melakukan penggabungan dataset secara paksa, Somna.ai menerapkan arsitektur **Hybrid Multi-Model (2 Model JST Terpisah + Hybrid Scoring & Rule-Based Engine)**.

> **Disclaimer Sistem:** Somna.ai dirancang sebagai alat skrining awal dan edukasi pola tidur, bukan pengganti diagnosis medis profesional.

---

## 2. Spesifikasi Input Pengguna (7 Variabel Final)

Seluruh input dikelompokkan dalam tata letak **2 Baris Simetris** pada halaman utama (`index.html`) agar tampilan tetap seimbang dan bebas dari input ekstrem di luar rentang data training.

### Baris 1 (Grid 2 Kolom Sejajar)
| Grup | No | Variabel Input | Komponen UI | Rentang / Pilihan | Pemrosesan di Backend (`utils.py` / `predictor.py`) |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **Grup 1: Pola Tidur** | 1 | **Durasi Tidur** | Slider + Badge nilai | $3.0$ – $12.0$ jam (default $7.0$) | Langsung masuk ke Model 1, Model 2, & Analisis Terpadu. |
| **Grup 1: Pola Tidur** | 2 | **Seberapa Sering Kesulitan Tidur (Malam Hari)** | 4 Tombol Pill | `Tidak Pernah`, `Jarang`, `Sering`, `Selalu` | Masuk ke **Hybrid Scoring** (penyesuai skor insomnia) & **Rule-Based Engine**. |
| **Grup 2: Kondisi Tidur** | 3 | **Kualitas Tidur** | 5 Tombol Skala | Skala $1$ – $5$ | Dikonversi ($\times 2$) menjadi skala $1$ – $10$ $\rightarrow$ masuk Model 1. |
| **Grup 2: Kondisi Tidur** | 4 | **Tingkat Stres** | 5 Tombol Skala | Skala $1$ – $5$ | Dikonversi ($\times 2$) menjadi skala $1$ – $10$ $\rightarrow$ masuk Model 1 & Model 2. |

### Baris 2 (1 Kartu Full-Width dengan 3 Kolom Sejajar)
| Grup | No | Variabel Input | Komponen UI | Rentang / Pilihan | Pemrosesan di Backend (`utils.py` / `predictor.py`) |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **Grup 3: Gaya Hidup** | 5 | **Aktivitas Fisik** | 5 Tombol Pilihan Cepat *(atau Slider $30$–$90$)* | `30`, `45`, `60`, `75`, `90` menit/hari | Langsung masuk ke Model 1 & Model 2 (sesuai distribusi dataset *Sleep Health*). |
| **Grup 3: Gaya Hidup** | 6 | **Frekuensi Penggunaan Ponsel Sebelum Tidur** | Dropdown / 4 Pill | `Tidak Pernah`, `Jarang`, `Sering`, `Selalu` | Dipetakan ke satuan jam (`phone_usage_hours`) $\rightarrow$ masuk Model 2 & Analisis Terpadu. |
| **Grup 3: Gaya Hidup** | 7 | **Frekuensi Konsumsi Kafein** | Dropdown / 4 Pill | `Tidak Pernah`, `Jarang`, `Sering`, `Selalu` | Dipetakan ke satuan mg (`coffee_intake_mg`, misal: $0, 100, 250, 400$ mg) $\rightarrow$ masuk Model 2 & Analisis Terpadu. |

---

## 3. Spesifikasi Output Sistem (`result.html`)

Setelah pengguna menekan tombol **Analisis Kebiasaan Tidur**, backend memproses data dan merender halaman hasil yang memuat 4 komponen utama:

1. **Kartu Klasifikasi Produktivitas:**
   * Menampilkan kelas hasil prediksi JST: **Rendah**, **Sedang**, atau **Tinggi**.
   * Menampilkan persentase tingkat kepercayaan (*confidence score*) dan deskripsi singkat dampak terhadap performa harian.
2. **Kartu Skrining Gejala Insomnia:**
   * Menampilkan tingkat indikasi hasil *Hybrid Scoring*: **Tidak Ada Gejala**, **Subthreshold**, **Sedang**, atau **Berat**.
   * Menampilkan persentase tingkat kepercayaan serta penjelasan singkat pemicu utama.
3. **Analisis Terpadu (Sintesis & Indikator Faktor Pemicu):**
   * **Narasi Sintesis:** Paragraf gabungan dari kedua model (termasuk deteksi pola unik, misalnya produktivitas tinggi yang ditopang konsumsi kafein tinggi di tengah kurang tidur).
   * **Kotak Indikator Status Warna (Hijau / Kuning / Merah):** Menampilkan status evaluasi dari **Durasi Tidur**, **Frekuensi Sulit Tidur**, **Konsumsi Kafein**, dan **Penggunaan Ponsel Pra-Tidur**.
4. **Rekomendasi Perbaikan Tidur Spesifik:**
   * Daftar saran praktis berbasis *rule-based* (`recommender.py`) yang langsung menargetkan kebiasaan terburuk pengguna (seperti *caffeine cut-off* $6$–$8$ jam sebelum tidur, *digital sunset* $30$–$60$ menit pra-tidur, teknik relaksasi, peningkatan aktivitas fisik, serta anjuran konsultasi medis untuk indikasi berat).

---

## 4. Strategi Dataset & Arsitektur AI

Sistem melatih **2 Model JST secara terpisah** dari 2 dataset publik yang berbeda. Hanya kolom yang sesuai dengan form input yang digunakan agar *input shape* JST konsisten dengan website dan bebas dari *noise*.

### A. Model 1: Skrining Gejala Insomnia
* **Dataset:** `Sleep_health_and_lifestyle_dataset.csv` (Kaggle, $374$ baris).
* **Kolom Fitur (`X` — 4 Kolom):**
  1. `Sleep Duration` (jam)
  2. `Quality of Sleep` (skala $1$–$10$)
  3. `Physical Activity Level` (menit/hari, rentang $30$–$90$)
  4. `Stress Level` (skala $1$–$10$)
* **Kolom Target (`y` — 1 Kolom):** `Sleep Disorder`.
* **Kolom yang Dibuang:** `Person ID`, `Gender`, `Age`, `Occupation`, `BMI Category`, `Blood Pressure`, `Heart Rate`, `Daily Steps`.
* **Aturan Preprocessing Khusus:**
  * Nilai kosong (`NaN`) pada kolom `Sleep Disorder` **tidak boleh dihapus (`dropna`)** karena merepresentasikan kategori `"None"` (Normal). Wajib diisi terlebih dahulu dengan `.fillna('None')`.
  * Target dikonversi menjadi klasifikasi biner: `Insomnia` $= 1$, selainnya (`None` / lainnya) $= 0$.
  * Ekspor model (`sleep_model.keras` / `.h5`) beserta scaler (`sleep_scaler.pkl`).

### B. Model 2: Klasifikasi Produktivitas
* **Dataset:** `train.csv` dari *Student Productivity Prediction Challenge* (Kaggle, $16.000$ baris).
* **Catatan File `test.csv`:** **Tidak digunakan** karena tidak memiliki kolom target (`productivity_score`). Data evaluasi/testing diperoleh dengan membagi `train.csv` menggunakan `train_test_split` ($80\%$ Training / $20\%$ Testing).
* **Kolom Fitur (`X` — 5 Kolom):**
  1. `sleep_hours` (jam)
  2. `phone_usage_hours` (jam)
  3. `coffee_intake_mg` (mg)
  4. `exercise_minutes` (menit/hari)
  5. `stress_level` (skala $1$–$10$)
* **Kolom Target (`y` — 1 Kolom):** `productivity_score`.
* **Kolom yang Dibuang:** `id`, `student_id`, `age`, `gender`, `study_hours_per_day`, `social_media_hours`, `youtube_hours`, `gaming_hours`, `breaks_per_day`, `assignments_completed`, `attendance_percentage`, `focus_score`, `final_grade`.
* **Aturan Preprocessing Khusus:**
  * Kolom numerik `productivity_score` dikonversi menjadi $3$ kelas kategori (**Rendah**, **Sedang**, **Tinggi**) sebelum pelatihan JST.
  * Ekspor model (`productivity_model.keras` / `.h5`) beserta scaler (`productivity_scaler.pkl`).

### C. Mekanisme Hybrid Scoring (Post-Processing Insomnia)
Karena variabel **"Seberapa Sering Kesulitan Tidur"** tidak tersedia pada dataset publik, fitur klinis ini diintegrasikan pada lapisan *post-processing* di `predictor.py` untuk menyempurnakan probabilitas awal Model 1 (`prob_jst` dalam $0\%$–$100\%$):

$$\text{Skor Akhir} = \text{clip}\left(\text{prob\_jst} + \text{adjustment},\; 0,\; 100\right)$$

* **Nilai Penyesuaian (*Adjustment*):**
  * `Tidak Pernah` $\rightarrow +0\%$ (atau $-5\%$)
  * `Jarang` $\rightarrow +0\%$
  * `Sering` $\rightarrow +10\%$
  * `Selalu` $\rightarrow +20\%$
* **Pemetaan Skor Akhir ke 4 Kategori UI:**
  * $< 25\%$ $\rightarrow$ **Tidak Ada Gejala**
  * $25\%$ – $50\%$ $\rightarrow$ **Subthreshold**
  * $51\%$ – $75\%$ $\rightarrow$ **Sedang**
  * $> 75\%$ $\rightarrow$ **Berat**

---

## 5. Struktur Folder Proyek (Flask)

Struktur dirancang ramping dengan **Flask Blueprint** untuk mencegah *circular import* dan menggunakan **Jinja2 (Server-Side Rendering)** agar integrasi frontend-backend sederhana dan minim bug.

```text
somna-ai/
├── app.py                        # Entry point aplikasi Flask
├── config.py                     # Konfigurasi dasar aplikasi
├── requirements.txt              # Daftar dependensi Python
├── models/                       # Model JST & Scaler hasil training dari Colab
│   ├── productivity_model.keras
│   ├── productivity_scaler.pkl
│   ├── sleep_model.keras
│   └── sleep_scaler.pkl
├── notebooks/                    # Eksplorasi data & training JST (Google Colab)
│   ├── 01_data_preprocessing.ipynb
│   ├── 02_productivity_model.ipynb
│   ├── 03_sleep_model.ipynb
│   └── 04_model_evaluation.ipynb
├── core/                         # Modul logika backend
│   ├── routes.py                 # Endpoint & routing halaman (Blueprint)
│   ├── utils.py                  # Validasi, konversi skala (1-5 -> 1-10), & mapping frekuensi
│   ├── predictor.py              # Load model, inferensi JST, & Hybrid Scoring
│   └── recommender.py            # Rule-based engine untuk Analisis Terpadu & Rekomendasi
├── templates/                    # Template HTML (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   └── about.html
└── static/                       # Aset frontend
    ├── css/
    │   ├── style.css
    │   └── responsive.css
    └── js/
        └── form.js               # Interaksi slider, tombol pill/skala, & validasi ringan
```

---

## 6. Pembagian Tugas & Tanggung Jawab

| Anggota | Peran Utama | Tanggung Jawab & Deliverables |
| :--- | :--- | :--- |
| **Aidil** | AI & Arsitektur Sistem | • Setup kerangka awal Flask (`app.py`, `config.py`, `requirements.txt`, `routes.py`).<br>• Merancang arsitektur JST & melatih Model Produktivitas (`02_productivity_model.ipynb`).<br>• Berkolaborasi melatih Model Insomnia & menyimpan seluruh file model + scaler.<br>• Mengimplementasikan logika `recommender.py` dan *Hybrid Scoring*.<br>• Menyusun dokumentasi AI (grafik akurasi/loss, *confusion matrix*, & justifikasi metodologi Hybrid). |
| **Rify** | Data & Backend Flask | • Membersihkan & memfilter kolom dataset (`01_data_preprocessing.ipynb`).<br>• Membantu training & evaluasi Model Insomnia (`03_sleep_model.ipynb`).<br>• Menyelesaikan modul backend (`utils.py`, `predictor.py`, integrasi ke `routes.py`).<br>• Menguji endpoint `POST`, validasi input, dan pengiriman variabel ke Jinja2. |
| **Inri** | Frontend & Integrasi UI | • Memperbarui desain UI untuk 7 inputan (layout 2 baris simetris) & indikator output baru.<br>• Membangun `base.html`, `index.html`, `result.html`, `about.html`, CSS, & `form.js`.<br>• Menghubungkan atribut `name=""` pada form HTML sesuai kontrak backend dan merender hasil prediksi via Jinja2. |

---

## 7. Status Progres & Langkah Selanjutnya

- [x] Finalisasi konsep 7 inputan, 2 model JST, dan mekanisme *Hybrid Scoring*.
- [x] Pemilihan dataset dan pemetaan kolom final (`Sleep_health_and_lifestyle_dataset.csv` & `train.csv`).
- [x] Setup kerangka awal Flask (`app.py`, `config.py`, `requirements.txt`, `routes.py`).
- [ ] **Tahap Berikutnya (Prioritas):** Training kedua model JST di Google Colab dan ekspor file `.keras` serta `.pkl` ke folder `models/`.
- [ ] Implementasi penuh `utils.py`, `predictor.py`, dan `recommender.py` lalu lakukan *sanity check* dengan skenario input ekstrem.
- [ ] Pembaruan tampilan UI di Google Stitch dan implementasi HTML/CSS/Jinja2 (`index.html` & `result.html`).
- [ ] Uji coba *end-to-end* aplikasi secara lokal dan finalisasi materi presentasi.