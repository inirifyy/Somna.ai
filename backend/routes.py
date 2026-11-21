from flask import Blueprint, jsonify, render_template, request

from backend.prediction import prediksi_semua
from backend.preprocessing import siapkan_fitur
from backend.recommendation import buat_rekomendasi
from backend.validators import validate_input

# Blueprint untuk mengelompokkan halaman
main_bp = Blueprint('main', __name__)


def _proses(form):
    """
    Seluruh alur dari input mentah sampai hasil.
    Mengembalikan (hasil, errors). Kalau ada error, hasil = None.
    """
    data, errors = validate_input(form)
    if errors:
        return None, errors

    fitur = siapkan_fitur(data)
    prediksi = prediksi_semua(fitur)
    analisis = buat_rekomendasi(data, prediksi)

    return {'input': data, 'prediksi': prediksi, 'analisis': analisis}, {}


# 1. Halaman utama (form input kebiasaan tidur)
@main_bp.route('/')
def index():
    return render_template('index.html', errors={}, nilai={})


# 2. Halaman tentang Somna.ai
@main_bp.route('/about')
def about():
    return render_template('about.html')


# 3. Endpoint saat tombol analisis ditekan (mengirim data form)
@main_bp.route('/analyze', methods=['POST'])
def analyze():
    hasil, errors = _proses(request.form)

    if errors:
        # Kembali ke form, bawa pesan error dan isian lama supaya tidak hilang
        return render_template('index.html', errors=errors, nilai=request.form), 400

    # Hasil prediksi AI dikirim ke halaman result.html
    return render_template('result.html', hasil=hasil)


# 4. Versi JSON, enak untuk testing endpoint (curl / Postman) atau fetch() dari JavaScript
@main_bp.route('/api/analyze', methods=['POST'])
def api_analyze():
    sumber = request.get_json(silent=True) or request.form
    hasil, errors = _proses(sumber)

    if errors:
        return jsonify({'ok': False, 'errors': errors}), 400

    return jsonify({'ok': True, **hasil})