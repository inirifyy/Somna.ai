from flask import Blueprint, render_template, request, jsonify

# Blueprint untuk mengelompokkan halaman
main_bp = Blueprint('main', __name__)

# 1. Halaman utama (form input kebiasaan tidur)
@main_bp.route('/')
def index():
    return render_template('index.html')

# 2. Halaman tentang Somna.ai
@main_bp.route('/about')
def about():
    return render_template('about.html')

# 3. Endpoint saat tombol analisis ditekan (mengirim data form)
@main_bp.route('/analyze', methods=['POST'])
def analyze():
    # Ambil data dari form
    durasi_tidur = float(request.form.get("durasi_tidur", 7.0))
    kualitas_tidur = int(request.form.get("kualitas_tidur", 8))
    tingkat_stres = int(request.form.get("tingkat_stres", 6))
    aktivitas_fisik = int(request.form.get("aktivitas_fisik", 60))
    layar_sebelum_tidur = request.form.get("layar_sebelum_tidur", "Jarang")
    konsumsi_kafein = request.form.get("konsumsi_kafein", "Jarang")
    kesulitan_tidur = request.form.get("kesulitan_tidur", "Jarang")

    # Proses prediksi menggunakan model AI
    from backend.prediction import preprocess_inputs
    results = preprocess_inputs(
        durasi_tidur=durasi_tidur,
        kualitas_tidur=kualitas_tidur,
        aktivitas_fisik=aktivitas_fisik,
        tingkat_stres=tingkat_stres,
        layar_sebelum_tidur=layar_sebelum_tidur,
        konsumsi_kafein=konsumsi_kafein,
        kesulitan_tidur=kesulitan_tidur,
    )

    # Kirim hasil ke result.html via Jinja2
    return render_template("result.html", **results)
