from flask import Flask
from config import Config
from backend.routes import main_bp

def create_app():
    # 1. Buat aplikasi Flask
    app = Flask(__name__)
    
    # 2. Masukkan pengaturan dari file config.py
    app.config.from_object(Config)
    
    # 3. Daftarkan route/halaman dari folder backend
    app.register_blueprint(main_bp)
    
    return app

# Inisialisasi aplikasi
app = create_app()

# Jalankan server jika file ini dijalankan langsung
if __name__ == '__main__':
    app.run(debug=True)
