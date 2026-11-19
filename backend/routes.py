from flask import Blueprint, render_template

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
    # Nanti hasil prediksi AI akan dikirim ke halaman result.html
    return render_template('result.html')
