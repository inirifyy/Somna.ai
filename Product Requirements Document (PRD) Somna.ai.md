# Product Requirements Document (PRD): Somna.ai

Versi 1.1 (draft untuk di-review tim) | 19 November 2026

Tim: Aidil (AI & Arsitektur), Rify (Data & Backend), Inri (Frontend & UI/UX)

Tech stack: Python, Jaringan Saraf Tiruan (JST), Flask + Jinja2, HTML, CSS, JavaScript

## 0. Cara Membaca Dokumen Ini

Dokumen ini adalah PRD v1.0 yang diperkaya supaya semua anggota tim, termasuk yang baru pertama kali pakai Flask, bisa paham gambaran besar sekaligus detail teknisnya. Penanda yang dipakai:

- **\[Asli\]** isi PRD v1.0 yang dipertahankan.
- **\[Baru\]** tambahan penjelasan atau spesifikasi.
- **\[Usulan\]** perubahan dari v1.0 yang perlu disepakati tim sebelum dikunci.
- **\[Verifikasi\]** informasi yang sebaiknya dicek ulang ke sumber atau dataset aslinya sebelum dijadikan keputusan.

Ringkasan perubahan utama:

1. Ditambah penjelasan alur kerja sistem dari klik tombol sampai hasil tampil (bagian 2).
2. Ditambah rentang nilai valid untuk setiap input dan aturan validasi (bagian 3).
3. Ditambah kontrak data (format output antar modul) agar tiga orang bisa kerja paralel tanpa bentrok (bagian 4).
4. Ditambah catatan risiko dataset, metrik evaluasi, dan usulan perbaikan pemetaan probabilitas insomnia (bagian 5).
5. Ditambah panduan Flask untuk pemula, termasuk contoh kode kerangka (bagian 7).
6. Ditambah rencana pengujian, risiko, keputusan terbuka, dan glosarium (bagian 10 sampai 13).

## 1. Ringkasan Produk

### 1.1 Apa itu Somna.ai \[Asli\]

Somna.ai adalah aplikasi web berbasis Artificial Intelligence yang mengklasifikasikan kebiasaan tidur pengguna terhadap tingkat produktivitas dan indikasi gangguan tidur (insomnia) menggunakan Jaringan Saraf Tiruan (JST). Sistem berjalan secara real-time tanpa menyimpan data pribadi pengguna secara permanen.

Karena tidak ada dataset publik yang memuat semua variabel dalam satu tabel, Somna.ai memakai arsitektur Hybrid Multi-Model: 2 model JST terpisah ditambah 1 Rule-Based Engine. Dengan begitu semua fitur di antarmuka tetap valid tanpa menggabungkan dataset secara paksa.

### 1.2 Latar Belakang dan Masalah \[Baru\]

Banyak orang merasa tidurnya berantakan tetapi tidak tahu apakah pola tidurnya memang bermasalah dan apa hubungannya dengan produktivitas harian. Somna.ai memberi gambaran cepat dan mudah dipahami dari 6 pertanyaan singkat, lalu memberi saran praktis yang bisa langsung dicoba.

### 1.3 Tujuan \[Baru\]

- Pengguna bisa mengisi form dan mendapat hasil dalam hitungan detik.
- Hasil mudah dipahami orang awam: kategori, penjelasan singkat, dan saran konkret.
- Seluruh pipeline (data, training, backend, frontend) bisa dikerjakan tiga orang pemula dalam kira-kira 10 hari.
- Tidak ada data pengguna yang disimpan permanen.

### 1.4 Non-Tujuan (di luar cakupan versi 1.0) \[Baru\]

- Bukan alat diagnosis medis. Hasil hanya skrining awal dan edukasi.
- Tidak ada akun pengguna, login, atau riwayat hasil.
- Tidak ada database.
- Tidak ada integrasi perangkat wearable atau pelacak tidur.
- Tidak ada bahasa selain Indonesia.

### 1.5 Target Pengguna \[Usulan\]

Target awal: mahasiswa dan pelajar usia 17 sampai 25 tahun yang punya kebiasaan tidur tidak teratur. Alasannya, dataset produktivitas (Model 2) berasal dari konteks pelajar atau mahasiswa, sehingga hasilnya paling masuk akal untuk kelompok ini. Tim perlu memutuskan apakah cakupan diperluas (lihat bagian 12).

### 1.6 Disclaimer Wajib di UI \[Baru\]

Halaman hasil dan halaman About harus menampilkan pernyataan sejenis: Hasil ini adalah skrining awal berbasis model statistik, bukan diagnosis. Jika keluhan tidur berlangsung lama atau mengganggu aktivitas, konsultasikan dengan tenaga kesehatan profesional.

## 2. Cara Kerja Sistem (Gambaran Besar untuk Pemula) \[Baru\]

Alur satu kali analisis:

```
Pengguna isi form (index.html)
        |
        v  klik 'Analisis Kebiasaan Tidur' -> kirim data via POST
Flask route (core/routes.py)
        |
        v
Validasi input (core/utils.py)  --salah--> kembali ke form + pesan error
        |
        v benar
Persiapan fitur: konversi skala + normalisasi (utils.py)
        |
        v
Prediksi Model 1 & Model 2 (core/predictor.py)
        |
        v
Rule-Based Engine (core/recommender.py): analisis terpadu + rekomendasi
        |
        v
Render result.html dengan variabel hasil (Jinja2)
```

Penjelasan singkat tiap tahap:

1. **Form**: pengguna mengisi 6 input. Setiap input punya atribut name yang harus sama persis dengan nama variabel di backend.
2. **POST**: browser mengirim isi form ke server Flask. Data tidak muncul di URL sehingga lebih privat dibanding GET.
3. **Validasi**: backend memastikan semua input ada, berupa angka, dan berada di rentang wajar. Validasi di JavaScript hanya kemudahan untuk pengguna, bukan pengaman, karena bisa dilewati.
4. **Persiapan fitur**: input diubah ke skala dan urutan fitur yang sama persis dengan saat training, lalu dinormalisasi memakai scaler yang disimpan.
5. **Prediksi**: dua model menghasilkan probabilitas. Probabilitas diterjemahkan menjadi label dan confidence.
6. **Rule-Based Engine**: aturan if-else menyusun teks analisis dan saran berdasarkan hasil model dan input mentah.
7. **Render**: Flask mengisi template result.html dengan hasil, lalu mengirim halaman ke browser.

## 3. Spesifikasi Input

### 3.1 Daftar Input (6 Variabel) \[Asli + Baru\]

Semua input diisi di index.html dalam tiga grup. Kolom nama field di bawah adalah usulan nama untuk atribut name pada HTML dan kunci di Python. Nama ini harus dikunci di Hari 1 dan tidak boleh diubah sepihak.

| Grup | Variabel | Nama field \[Usulan\] | Format di UI | Peran di backend |
| --- | --- | --- | --- | --- |
| 1: Pola Tidur | Durasi Tidur | sleep\_duration | Slider (jam, langkah 0,5) | Model 1, Model 2, Analisis Terpadu |
| 1: Pola Tidur | Kesulitan Memulai Tidur (Onset) | sleep\_onset\_min | Angka (menit) | Analisis Terpadu dan Rekomendasi (rule-based, ambang batas <= 20 menit) |
| 2: Kondisi Tidur | Kualitas Tidur | sleep\_quality | Skala 1 sampai 5 | Dikonversi ke skala 1 sampai 10, masuk Model 1 |
| 2: Kondisi Tidur | Tingkat Stres | stress\_level | Skala 1 sampai 5 | Dikonversi ke skala 1 sampai 10, masuk Model 1 |
| 3: Gaya Hidup | Aktivitas Fisik | physical\_activity\_min | Angka (menit per hari) | Model 1 dan Model 2 |
| 3: Gaya Hidup | Penggunaan Ponsel Sebelum Tidur | phone\_before\_bed\_min | Angka (menit) | Model 2 dan Analisis Terpadu (rule-based, ambang batas <= 15 menit) |

### 3.2 Rentang Nilai Valid dan Validasi \[Usulan\]

Rentang di bawah adalah usulan awal yang masuk akal untuk antarmuka. Tim bisa menyesuaikan setelah melihat rentang data training.

| Field | Tipe | Minimum | Maksimum | Catatan |
| --- | --- | --- | --- | --- |
| sleep\_duration | desimal | 1,0 | 14,0 | Slider, langkah 0,5 |
| sleep\_onset\_min | bilangan bulat | 0 | 240 |  |
| sleep\_quality | bilangan bulat | 1 | 5 |  |
| stress\_level | bilangan bulat | 1 | 5 |  |
| physical\_activity\_min | bilangan bulat | 0 | 300 |  |
| phone\_before\_bed\_min | bilangan bulat | 0 | 300 |  |

Aturan validasi di backend (utils.py):

- Semua field wajib terisi.
- Nilai harus bisa diubah ke angka; teks, kosong, atau simbol ditolak.
- Nilai di luar rentang ditolak dengan pesan error yang ramah dan spesifik (contoh: Durasi tidur harus antara 1 sampai 14 jam).
- Jika ada error, tampilkan kembali form dengan nilai yang tadi diisi agar pengguna tidak mengetik ulang.

### 3.3 Konversi Skala 1 sampai 5 ke 1 sampai 10 \[Usulan, perlu disepakati\]

PRD v1.0 memakai rumus kali 2. Dampaknya, hanya nilai genap (2, 4, 6, 8, 10) yang pernah masuk ke model, padahal data training memakai skala 1 sampai 10 penuh dan tidak pernah memberi nilai 1 untuk pilihan terendah di UI. Alternatif: pemetaan linear 1 sampai 5 menjadi 1 sampai 10 dengan rumus: nilai\_10 = 1 + (nilai\_5 - 1) x 9 / 4, yang menghasilkan 1; 3,25; 5,5; 7,75; 10. Keduanya sama-sama pendekatan; yang penting satu rumus dipilih, ditulis di utils.py, dan diuji.

## 4. Spesifikasi Output

### 4.1 Isi Halaman Hasil (result.html) \[Asli\]

1. **Kartu Klasifikasi Produktivitas**: kategori Rendah, Sedang, atau Tinggi, penjelasan singkat, dan confidence score.
2. **Kartu Skrining Gejala Insomnia**: Tidak Ada Gejala, Subthreshold, Sedang, atau Berat, penjelasan pemicu, dan confidence score.
3. **Analisis Terpadu**: sintesis teks yang menggabungkan hasil kedua model, plus 3 kartu metrik: Latensi Onset Tidur, Waktu Layar Pra-Tidur, dan Durasi Efektif Harian.
4. **Rekomendasi Perbaikan Tidur**: saran praktis dari rule-based engine berdasarkan kombinasi hasil klasifikasi dan input yang melewati ambang batas.

### 4.2 Definisi Metrik Kartu Analisis Terpadu \[Usulan\]

Istilah Durasi Efektif Harian belum didefinisikan di v1.0. Usulan definisi: durasi tidur dikurangi waktu onset (sleep\_duration - sleep\_onset\_min / 60), karena waktu menunggu tidur bukan waktu tidur sebenarnya. Tim perlu menyetujui atau mengganti definisi ini.

### 4.3 Kontrak Data Antar Modul \[Baru\]

Supaya Rify (backend) dan Inri (frontend) tidak saling menunggu, fungsi predictor dan recommender mengembalikan satu dictionary dengan bentuk tetap seperti di bawah. Inri bisa membuat dummy dengan struktur ini sejak Hari 1.

```python
result = {
    'productivity': {
        'label': 'Sedang',            # Rendah / Sedang / Tinggi
        'confidence': 0.72,           # 0.0 - 1.0
        'description': 'teks singkat'
    },
    'insomnia': {
        'label': 'Subthreshold',      # 4 tingkat
        'probability': 0.38,          # probabilitas kelas insomnia
        'description': 'teks pemicu'
    },
    'metrics': {
        'onset_min': 35,
        'phone_min': 45,
        'effective_sleep_h': 6.4
    },
    'unified_analysis': 'paragraf sintesis',
    'recommendations': ['saran 1', 'saran 2']
}
```

Di Jinja2, nilai diakses dengan sintaks seperti `{{ result.productivity.label }}`.

## 5. Arsitektur AI dan Strategi Dataset

Sistem memakai 2 dataset terpisah untuk melatih 2 model JST terpisah.

### 5.1 Model 1: Skrining Gejala Insomnia

**\[Asli\]**

- Dataset: Sleep Health and Lifestyle Dataset (Kaggle).
- Fitur: Durasi Tidur, Kualitas Tidur, Tingkat Stres, Aktivitas Fisik.
- Strategi: klasifikasi biner (Normal vs Indikasi Insomnia). Probabilitas kelas Insomnia dipetakan ke 4 tingkat di UI.

**\[Baru\] Catatan penting tentang dataset ini \[Verifikasi semua poin di bawah dengan membuka datasetnya\]:**

- Ukurannya kecil (sekitar 374 baris, sepengetahuan penulis) sehingga model rawan overfitting dan hasil evaluasi bisa sangat bervariasi.
- Kolom gangguan tidur biasanya berisi tiga nilai: None, Insomnia, dan Sleep Apnea. Karena targetnya biner Normal vs Insomnia, tim harus memutuskan perlakuan baris Sleep Apnea (usulan: dikeluarkan dari training dan dicatat di notebook).
- Kelas Insomnia jauh lebih sedikit daripada Normal (tidak seimbang). Gunakan stratified split, class weight, atau teknik penyeimbangan lain, dan jangan menilai model hanya dari akurasi.
- Dataset ini sering dibahas komunitas sebagai kemungkinan sintetis (bukan data klinis nyata). Artinya, hasil model menggambarkan pola di dataset, bukan kebenaran medis.
- Rentang nilai di dataset cenderung sempit (contoh: durasi tidur sekitar 5,8 sampai 8,5 jam). Input ekstrem seperti tidur 3 jam berada di luar rentang training, sehingga prediksi model pada input itu adalah ekstrapolasi dan kurang bisa diandalkan. Cek rentang sebenarnya di Colab.

**\[Usulan\] Pemetaan probabilitas ke 4 tingkat:**

Batas v1.0 punya celah (antara 50% dan 51%). Usulan memakai interval setengah terbuka:

| Probabilitas kelas Insomnia | Tingkat di UI (v1.0) |
| --- | --- |
| di bawah 25% | Tidak Ada Gejala |
| 25% sampai di bawah 50% | Subthreshold |
| 50% sampai di bawah 75% | Sedang |
| 75% ke atas | Berat |

Catatan kritis: probabilitas model berarti seberapa mirip pola input dengan pola kelas Insomnia di data, bukan tingkat keparahan insomnia. Nama Subthreshold, Sedang, dan Berat mirip kategori keparahan pada kuesioner klinis (misalnya Insomnia Severity Index), padahal model ini tidak mengukur itu. Alternatif penamaan yang lebih jujur: Risiko Rendah, Waspada, Tinggi, Sangat Tinggi, atau Kemiripan Pola Insomnia: Rendah/Sedang/Tinggi. Keputusan ada di tim (lihat bagian 12).

**\[Baru\] Titik awal arsitektur JST (bukan final):**

- Input 4 fitur (sudah dinormalisasi), Dense 16 (ReLU), Dropout 0,2, Dense 8 (ReLU), Dense 1 (sigmoid).
- Loss: binary cross-entropy. Optimizer: Adam. Gunakan EarlyStopping pada validation loss.
- Bandingkan dengan baseline sederhana (misalnya logistic regression). Jika JST tidak lebih baik, tulis jujur di laporan; itu temuan yang valid.

### 5.2 Model 2: Klasifikasi Produktivitas

**\[Asli\]**

- Dataset: satu dataset utuh (Student Habits / Performance) yang punya kolom durasi tidur, aktivitas fisik, dan screen time beserta target performa.
- Strategi: target performa dikelompokkan menjadi 3 kelas (Rendah, Sedang, Tinggi).

**\[Baru\] Hal yang harus dicek sebelum dataset dikunci \[Verifikasi\]:**

- Pada dataset Student Habits vs Academic Performance di Kaggle (sepengetahuan penulis), aktivitas fisik tercatat sebagai frekuensi olahraga per minggu, bukan menit per hari, dan screen time tercatat sebagai jam media sosial atau hiburan per hari, bukan menit ponsel sebelum tidur. Jika benar, input form tidak sama dengan fitur training. Pilihan: (a) ubah input form agar cocok dengan dataset, (b) lakukan konversi satuan yang dijelaskan secara transparan, atau (c) pilih dataset lain.
- Target di dataset itu biasanya nilai ujian. Itu mengukur performa akademik, bukan produktivitas secara umum. Tulis ini jelas di halaman About agar tidak menyesatkan.
- Faktor lain seperti jam belajar biasanya jauh lebih berpengaruh pada nilai daripada tidur. Dengan hanya 3 fitur (tidur, aktivitas, layar), kemampuan prediksi bisa rendah. Jangan kaget jika akurasi tidak tinggi; laporkan apa adanya.

**\[Usulan\] Pembentukan 3 kelas:** tentukan aturan pengelompokan di notebook dan dokumentasikan alasannya, misalnya berdasarkan tiga kuantil (bagi sama banyak) atau ambang nilai tetap. Kuantil membuat kelas lebih seimbang. Ambang tetap lebih mudah dijelaskan. Pilih satu dan konsisten.

**\[Baru\] Titik awal arsitektur:** Dense 16 (ReLU), Dropout 0,2, Dense 8 (ReLU), Dense 3 (softmax), loss categorical atau sparse categorical cross-entropy.

### 5.3 Rule-Based Engine \[Asli + Baru\]

Mengolah input mentah (onset, waktu layar, durasi) dan hasil kedua model untuk menyusun Analisis Terpadu dan Rekomendasi. Berikut contoh kerangka aturan. Angka ambang di luar 20 dan 15 menit adalah \[Usulan\] dan sebaiknya dicocokkan dengan sumber yang bisa dikutip tim \[Verifikasi\].

| Kondisi | Status | Contoh isi rekomendasi |
| --- | --- | --- |
| onset <= 20 menit | Baik | Pertahankan rutinitas sebelum tidur yang sekarang. |
| onset 21 sampai 30 menit | Perlu diperhatikan | Coba rutinitas relaksasi singkat dan jam tidur yang konsisten. |
| onset > 30 menit | Tinggi | Kurangi kafein sore hari, redupkan cahaya, dan pantau apakah berlangsung berhari-hari. |
| ponsel sebelum tidur <= 15 menit | Baik | Kebiasaan layar sebelum tidur sudah terkendali. |
| ponsel 16 sampai 30 menit | Perlu diperhatikan | Coba batasi layar sebelum tidur secara bertahap. |
| ponsel > 30 menit | Tinggi | Taruh ponsel di luar jangkauan saat waktu tidur atau aktifkan mode fokus. |
| durasi tidur < 6 jam | Kurang | Naikkan durasi tidur bertahap, misalnya 15 menit lebih awal per hari. |
| durasi 6 sampai di bawah 7 jam | Sedikit kurang | Usahakan mendekati rentang 7 sampai 9 jam (umum dipakai untuk dewasa \[Verifikasi\]). |
| durasi 7 sampai 9 jam | Ideal | Pertahankan. |
| tingkat insomnia Sedang atau Berat, atau keluhan berlangsung lama | Peringatan | Pertimbangkan berkonsultasi dengan tenaga kesehatan profesional. |

Prinsip penulisan teks: bahasa ramah dan tidak menghakimi, tidak menyebut diagnosis, tidak menjanjikan hasil, dan selalu menyertakan saran profesional untuk kasus tingkat tinggi.

### 5.4 Standar Evaluasi dan Pencegahan Kesalahan Umum \[Baru\]

- Pisahkan data: train, validation, dan test. Gunakan stratified split karena kelas tidak seimbang.
- Fit scaler hanya pada data training, lalu terapkan ke validation, test, dan input pengguna (hindari data leakage).
- Laporkan: confusion matrix, precision, recall, F1 (bukan hanya akurasi). Untuk skrining insomnia, recall kelas Insomnia penting karena kasus yang terlewat lebih merugikan daripada peringatan berlebih.
- Simpan urutan fitur di satu tempat (misalnya konstanta FEATURE\_ORDER) dan pakai di training maupun Flask. Urutan fitur yang tertukar adalah bug yang diam-diam menghasilkan prediksi salah tanpa error.
- Catat versi library dari Colab (pip freeze untuk tensorflow, scikit-learn, numpy, pandas) dan pakai versi yang sama di requirements.txt agar model bisa dimuat di komputer lain.
- Format model: .h5 masih bisa dipakai, tetapi format .keras adalah format yang lebih baru di Keras \[Verifikasi sesuai versi TensorFlow yang dipakai\]. Pilih satu dan konsisten.
- Opsi alternatif: untuk data tabular kecil, MLPClassifier dari scikit-learn juga termasuk JST, lebih ringan dipasang, dan lebih mudah di-deploy. Keputusan library ada di tim (bagian 12).
- Hanya muat file .pkl yang dibuat sendiri oleh tim. File pickle dari sumber tidak dikenal berisiko menjalankan kode berbahaya.

## 6. Struktur Folder dan Fungsi Tiap File

Struktur ini dirampingkan untuk mencegah circular import dan memudahkan pengguna baru Flask \[Asli\].

```
somna-ai/
├── app.py                  # Entry point Flask
├── requirements.txt        # Daftar library + versi
├── README.md               # [Baru] cara install & menjalankan
├── .gitignore              # [Baru] abaikan venv/, __pycache__/, dll
├── models/
│   ├── productivity_model.h5
│   ├── sleep_model.h5
│   └── scalers.pkl
├── notebooks/
│   ├── 01_data_preprocessing.ipynb
│   ├── 02_productivity_model.ipynb
│   └── 03_sleep_model.ipynb
├── core/
│   ├── routes.py
│   ├── utils.py
│   ├── predictor.py
│   └── recommender.py
├── tests/                  # [Baru] tes sederhana untuk utils & recommender
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   └── about.html
└── static/
    ├── css/ (style.css, responsive.css)
    └── js/form.js
```

| File | Fungsi | Penanggung jawab utama |
| --- | --- | --- |
| app.py | Membuat aplikasi Flask dan mendaftarkan Blueprint | Aidil |
| core/routes.py | Endpoint: halaman form, proses analisis, halaman About | Rify |
| core/utils.py | Validasi input, konversi skala, normalisasi | Rify |
| core/predictor.py | Memuat model dan scaler sekali saat startup, lalu menjalankan prediksi | Rify (dibantu Aidil) |
| core/recommender.py | Aturan if-else untuk analisis terpadu dan rekomendasi | Rify (aturan dari Aidil) |
| models/ | Model dan scaler hasil training | Aidil |
| templates/ | Halaman HTML (Jinja2) | Inri |
| static/ | CSS dan JavaScript | Inri |
| tests/ | Tes otomatis sederhana | Rify |

## 7. Panduan Flask untuk Pemula \[Baru\]

### 7.1 Konsep Dasar yang Dipakai di Proyek Ini

- **Route**: pasangan alamat URL dengan fungsi Python. Contoh: alamat / menampilkan form.
- **Blueprint**: cara mengelompokkan route di file terpisah (routes.py) agar app.py tidak membengkak.
- **Template (Jinja2)**: file HTML yang bisa diisi variabel Python memakai kurung kurawal ganda.
- **request.form**: tempat Flask menyimpan data hasil kiriman form POST.
- **render\_template**: mengisi template dengan variabel lalu mengirimnya ke browser.

### 7.2 Menyiapkan Lingkungan

```
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\\Scripts\\activate           # Windows
pip install -r requirements.txt
flask --app app run --debug
```

Buka alamat yang tampil di terminal (biasanya http://127.0.0.1:5000). Mode debug hanya untuk pengembangan dan tidak boleh dipakai saat aplikasi dipublikasikan.

### 7.3 Kerangka Kode

```python
# app.py
from flask import Flask
from core.routes import main_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main_bp)
    return app

app = create_app()
```

```python
# core/routes.py
from flask import Blueprint, render_template, request
from core.utils import validate_input
from core.predictor import predict_all
from core.recommender import build_recommendation

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/analyze', methods=['POST'])
def analyze():
    data, errors = validate_input(request.form)
    if errors:
        return render_template('index.html', errors=errors, form=request.form), 400
    predictions = predict_all(data)
    result = build_recommendation(data, predictions)
    return render_template('result.html', result=result)
```

```html
<!-- templates/index.html (potongan) -->
<form action='/analyze' method='POST'>
  <input type='number' name='sleep_onset_min' min='0' max='240' required>
  <button type='submit'>Analisis Kebiasaan Tidur</button>
</form>
```

Catatan: potongan di atas hanya kerangka. Rify dan Inri bebas menyesuaikan selama nama field dan kontrak data di bagian 3 dan 4 dipatuhi.

### 7.4 Kesalahan Umum Pemula dan Cara Menghindarinya

| Masalah | Penyebab umum | Pencegahan |
| --- | --- | --- |
| TemplateNotFound | Folder tidak bernama templates atau salah lokasi | Ikuti struktur di bagian 6 |
| Nilai form tidak terbaca (None atau error 400) | Atribut name di HTML berbeda dengan kunci di Python | Kunci nama field di Hari 1 |
| Model tidak ditemukan | Path relatif berubah tergantung dari mana program dijalankan | Bangun path dari lokasi file (pathlib) |
| Aplikasi lambat tiap klik | Model dimuat ulang di setiap request | Muat model sekali saat startup |
| Error import melingkar | Dua file saling mengimpor | Pakai Blueprint dan pisahkan logika di core/ |
| Model gagal dimuat di komputer teman | Versi TensorFlow atau scikit-learn berbeda dari Colab | Catat dan kunci versi di requirements.txt |
| Prediksi aneh tanpa error | Urutan fitur atau skala berbeda dengan training | Satu sumber FEATURE\_ORDER, uji dengan contoh dari notebook |

### 7.5 Aturan Kerja Git Sederhana

- Branch utama (main) hanya berisi kode yang jalan.
- Setiap orang bekerja di branch sendiri (contoh: feat/frontend-result, feat/backend-routes) lalu membuat Pull Request.
- Minimal satu anggota lain meninjau sebelum merge.
- Jangan commit folder venv/. File model yang besar disimpan sesuai kesepakatan tim.

## 8. Pembagian Tugas dan Tanggung Jawab \[Asli + Baru\]

| Anggota | Fokus utama | Deliverables kunci |
| --- | --- | --- |
| Aidil | AI & Arsitektur Sistem | Inisialisasi repo Git, app.py, requirements.txt. Menyepakati kontrak data di Hari 1. Merancang arsitektur JST, melatih productivity\_model dan membantu sleep\_model. Menyimpan scaler agar preprocessing di Flask identik dengan training. Menyusun aturan logika recommender. |
| Rify | Data & Backend Flask | Membersihkan dataset (01\_data\_preprocessing) dan menyiapkan CSV bersih. Membantu training dan evaluasi sleep\_model. Membangun routes, utils, predictor, recommender. Menguji endpoint dengan input valid dan tidak valid. |
| Inri | Frontend & Integrasi UI | Membangun base, index, result, about sesuai desain. Styling CSS desktop dan mobile serta interaksi slider di form.js. Menghubungkan form ke endpoint dengan POST dan menampilkan hasil dengan Jinja2. |

Catatan \[Baru\]: beban Rify paling berat (data, backend, dan evaluasi model). Disarankan Aidil atau Inri membantu pada tahap preprocessing atau pengujian, dan Inri ikut menulis halaman About beserta disclaimer.

## 9. Roadmap Eksekusi dengan Kriteria Selesai

### Fase 1: Kontrak Data dan Setup (Hari 1 sampai 2)

- Aidil membuat repo dan struktur folder, lalu mengunci nama field name dan kontrak data (bagian 3 dan 4).
- Rify membersihkan kedua dataset dan memeriksa poin risiko di bagian 5.
- Inri membangun kerangka index.html dan result.html dengan data dummy sesuai kontrak.
- **Selesai jika**: semua anggota bisa menjalankan kerangka Flask di komputer masing-masing; dokumen keputusan terbuka (bagian 12) sudah dijawab.

### Fase 2: Pengembangan Paralel (Hari 3 sampai 6)

- Aidil dan Rify melatih kedua model di Google Colab dan mengekspor model serta scalers.pkl ke models/.
- Inri menyelesaikan seluruh UI dan tampilan dummy halaman hasil.
- **Selesai jika**: kedua model punya laporan evaluasi (confusion matrix, F1, recall), dan UI desktop serta mobile tampil rapi dengan data dummy.

### Fase 3: Integrasi Backend dan Frontend (Hari 7 sampai 9)

- Rify mengintegrasikan model ke predictor.py dan menghubungkan routes.py dengan template Inri.
- Aidil memverifikasi konversi skala dan pemetaan probabilitas insomnia.
- **Selesai jika**: satu kali alur lengkap (isi form sampai hasil tampil) berjalan tanpa error untuk input valid, dan input tidak valid menampilkan pesan error yang jelas.

### Fase 4: Testing dan Polishing (Hari 10 sampai selesai)

- Uji end-to-end (lihat bagian 10), perbaiki bug, rapikan teks rekomendasi, tulis README dan halaman About.
- **Selesai jika**: kriteria penerimaan di bagian 10.3 terpenuhi.

Saran \[Baru\]: jadwal 10 hari ketat untuk pemula. Sisihkan buffer 1 sampai 2 hari, terutama untuk Fase 3, karena masalah integrasi (versi library, urutan fitur, path) biasanya paling memakan waktu.

## 10. Rencana Pengujian \[Baru\]

### 10.1 Skenario Uji End-to-End

Tabel berikut menguji arah hasil, bukan angka pasti, karena nilai model bergantung pada training.

| No | Skenario | Contoh input | Hasil yang diharapkan masuk akal |
| --- | --- | --- | --- |
| 1 | Pola tidur sehat | tidur 8 jam, onset 10, kualitas 5, stres 1, aktivitas 60, ponsel 0 | Risiko insomnia rendah, produktivitas sedang sampai tinggi, rekomendasi bersifat mempertahankan |
| 2 | Pola tidur buruk | tidur 3 jam, onset 60, kualitas 1, stres 5, aktivitas 0, ponsel 120 | Risiko insomnia lebih tinggi, produktivitas lebih rendah, rekomendasi lengkap dan saran profesional muncul |
| 3 | Campuran | tidur cukup tetapi ponsel 90 menit | Rule layar muncul meskipun durasi tidur ideal |
| 4 | Nilai batas | semua minimum dan semua maksimum yang diizinkan | Tidak error, hasil tampil |
| 5 | Input tidak valid | kosong, teks, angka negatif, desimal pada kolom bulat, nilai di luar rentang | Pesan error jelas, form tampil kembali, tidak crash |
| 6 | Konsistensi | input yang sama dikirim dua kali | Hasil identik |

Catatan: skenario 2 kemungkinan berada di luar rentang data training (lihat bagian 5.1). Jika hasilnya aneh, catat sebagai keterbatasan, bukan sekadar bug.

### 10.2 Tes Otomatis Sederhana

- utils.py: tes konversi skala, validasi rentang, dan penolakan input salah.
- recommender.py: tes setiap ambang batas (contoh: onset 20 vs 21, ponsel 15 vs 16).
- Pemetaan probabilitas: tes nilai tepat di batas 0,25, 0,50, 0,75.
- Uji kesamaan preprocessing: ambil beberapa baris dari notebook, jalankan lewat predictor.py, dan pastikan hasilnya sama dengan hasil di notebook.

### 10.3 Kriteria Penerimaan (Definition of Done)

- Semua skenario di 10.1 berjalan tanpa crash.
- Target metrik model ditetapkan tim setelah baseline dihitung (jangan menetapkan angka sebelum melihat data) dan dicatat di notebook.
- Disclaimer tampil di halaman hasil dan About.
- Tidak ada input pengguna yang tersimpan di file, database, atau log aplikasi.
- Tampilan nyaman di layar ponsel dan desktop.
- README memungkinkan anggota baru menjalankan aplikasi dari nol.

## 11. Privasi, Etika, dan Keamanan \[Baru\]

- **Tanpa penyimpanan data**: tidak ada database, tidak ada file log berisi input, dan input dikirim lewat POST (tidak muncul di URL).
- **Transparansi**: halaman About menjelaskan data apa yang dipakai, bagaimana hasil dibuat, dan keterbatasannya (dataset terbatas, bukan diagnosis).
- **Bahasa yang aman**: hindari kata yang menakut-nakuti atau memberi label medis pasti. Gunakan frasa seperti indikasi pola atau kecenderungan.
- **Keadilan**: model dilatih pada kelompok data tertentu dan mungkin kurang akurat untuk kelompok lain. Tulis keterbatasan ini secara jujur.
- **Keamanan dasar saat dipublikasikan**: matikan mode debug, gunakan HTTPS, dan pertimbangkan perlindungan CSRF (misalnya Flask-WTF) setelah fungsi utama selesai.

## 12. Keputusan Terbuka (Harus Dijawab Tim di Fase 1)

1. Library JST: TensorFlow/Keras atau scikit-learn MLP?
2. Format model: .h5 atau .keras?
3. Rumus konversi 1 sampai 5 ke 1 sampai 10: kali 2 atau pemetaan linear?
4. Penamaan 4 tingkat insomnia: tetap Subthreshold/Sedang/Berat atau diganti tingkat risiko?
5. Definisi Durasi Efektif Harian.
6. Dataset final Model 2 dan cara menyesuaikan satuan input (aktivitas fisik dan layar).
7. Cara membentuk 3 kelas produktivitas (kuantil atau ambang tetap).
8. Target pengguna: khusus mahasiswa atau umum?
9. Perlakuan baris Sleep Apnea pada Model 1.
10. Target deployment (lokal untuk demo atau dipublikasikan online) dan batas ukuran aplikasi.

## 13. Glosarium

| Istilah | Arti sederhana |
| --- | --- |
| JST | Jaringan Saraf Tiruan: model yang belajar pola dari data lewat lapisan neuron buatan |
| Inferensi | Proses memakai model yang sudah dilatih untuk memprediksi data baru |
| Confidence score | Seberapa yakin model terhadap prediksinya (bukan jaminan benar) |
| Scaler | Alat untuk menyamakan skala angka input; harus sama persis dengan saat training |
| Normalisasi | Mengubah angka ke skala seragam agar model belajar lebih stabil |
| Overfitting | Model terlalu hafal data training sehingga buruk pada data baru |
| Data leakage | Informasi dari data uji bocor ke proses training sehingga evaluasi terlihat terlalu bagus |
| Recall | Dari semua kasus positif yang sebenarnya, berapa yang berhasil terdeteksi |
| Rule-based | Logika berbasis aturan if-else buatan manusia, bukan hasil belajar model |
| Blueprint | Fitur Flask untuk mengelompokkan route di file terpisah |
| Jinja2 | Mesin template Flask yang mengisi HTML dengan variabel Python |
| Route | Alamat URL yang terhubung ke fungsi Python |
| POST | Metode HTTP untuk mengirim data form ke server tanpa menampilkannya di URL |
| Circular import | Dua file Python saling mengimpor sehingga program error |

## 14. Sumber yang Perlu Dicantumkan Tim

Tim perlu mencari dan mencantumkan sendiri, dengan tautan dan tanggal akses, sumber berikut sebelum laporan final: (1) halaman dataset Sleep Health and Lifestyle dan dataset Student Habits vs Academic Performance di Kaggle, (2) rujukan resmi untuk ambang latensi tidur dan durasi tidur yang direkomendasikan, (3) dokumentasi resmi Flask dan Keras atau scikit-learn untuk versi yang dipakai.
