# retrain.py
# Tugas file ini: melatih ulang 2 model JST HANYA dari data riwayat pengguna
# (dataset/history/history.csv).
#
# PENTING: dataset/processed/*.csv adalah data referensi dari dataset publik dan
# TIDAK digabung dengan inputan/riwayat pengguna. Retraining memakai data riwayat
# saja, sehingga kedua file processed tetap bersih dan tidak berubah.
#
# Cara pakai (jalankan berkala via cron / Task Scheduler):
#     python retrain.py                     # default
#     python retrain.py --min-rows 500      # naikkan ambang batas data riwayat
#     python retrain.py --force             # tetap simpan walau akurasi turun
#
# Pengaman:
#   1. Skip kalau baris riwayat valid < min-rows (data belum cukup untuk latih).
#   2. Skip kalau riwayat cuma berisi 1 kelas (tidak bisa klasifikasi).
#   3. Model lama di-backup dulu ke models/backup/ sebelum ditimpa.
#   4. Skip kalau model baru lebih buruk dari model lama pada data riwayat (kecuali --force).
#
# Setelah retrain, restart server: backend/prediction.py meng-cache model di memori.

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(__file__).resolve().parent
HISTORY_PATH = BASE_DIR / "dataset" / "history" / "history.csv"
MODEL_DIR = BASE_DIR / "models"
BACKUP_DIR = MODEL_DIR / "backup"

# Hyperparameter HARUS sama dengan notebook 03 & 04.
SPECS = {
    "sleep": {
        "features": [
            "Sleep Duration",
            "Quality of Sleep",
            "Physical Activity Level",
            "Stress Level",
        ],
        "target": "target",
        "min_rows": 100,
        "params": dict(hidden_layer_sizes=(32, 16), alpha=0.01, max_iter=3000),
    },
    "productivity": {
        "features": [
            "sleep_hours",
            "phone_usage_hours",
            "coffee_intake_mg",
            "exercise_minutes",
            "stress_level",
        ],
        "target": "productivity_class",
        "min_rows": 300,
        "params": dict(hidden_layer_sizes=(64, 32), alpha=0.0001, max_iter=500),
    },
}


def _split(X, y):
    """80/20 split; fallback tanpa stratify kalau kelas terlalu sedikit."""
    try:
        return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    except ValueError:
        return train_test_split(X, y, test_size=0.2, random_state=42)


def _akurasi_lama(nama, X_test, y_test):
    """Akurasi model lama pada test set yang sama. None kalau file model belum ada."""
    try:
        model = joblib.load(MODEL_DIR / f"{nama}_model.keras")
        scaler = joblib.load(MODEL_DIR / f"{nama}_scaler.pkl")
        return accuracy_score(y_test, model.predict(scaler.transform(X_test)))
    except Exception:
        return None


def _backup(nama):
    """Simpan model + scaler lama ke models/backup/<nama>_<timestamp>/."""
    berkas = [MODEL_DIR / f"{nama}_model.keras", MODEL_DIR / f"{nama}_scaler.pkl"]
    if not all(p.exists() for p in berkas):
        return None
    tujuan = BACKUP_DIR / f"{nama}_{datetime.now():%Y%m%d_%H%M%S}"
    tujuan.mkdir(parents=True, exist_ok=True)
    for p in berkas:
        shutil.copy2(p, tujuan / p.name)
    return tujuan


def _train(nama, spec, history, min_rows, force):
    """Latih ulang satu model dari data riwayat. Return string status untuk dicetak."""
    kolom = spec["features"] + [spec["target"]]
    hilang = [k for k in kolom if k not in history.columns]
    if hilang:
        return f"SKIP {nama}: kolom riwayat tidak lengkap, kurang {hilang}"

    df = history.dropna(subset=kolom)[kolom].astype(float).drop_duplicates()
    if len(df) < min_rows:
        return f"SKIP {nama}: {len(df)} baris riwayat valid (< {min_rows})"
    if df[spec["target"]].nunique() < 2:
        return f"SKIP {nama}: hanya berisi 1 kelas"

    X = df[spec["features"]].to_numpy(dtype=float)
    y = df[spec["target"]].to_numpy(dtype=int)
    X_train, X_test, y_train, y_test = _split(X, y)

    scaler = StandardScaler()
    model = MLPClassifier(
        activation="relu",
        solver="adam",
        learning_rate_init=0.001,
        random_state=42,
        **spec["params"],
    )
    model.fit(scaler.fit_transform(X_train), y_train)
    acc_baru = accuracy_score(y_test, model.predict(scaler.transform(X_test)))
    acc_lama = _akurasi_lama(nama, X_test, y_test)

    if acc_lama is not None and acc_baru < acc_lama - 0.005 and not force:
        return (
            f"SKIP {nama}: model lama lebih baik pada data riwayat "
            f"({acc_lama:.4f} -> {acc_baru:.4f}), pakai --force untuk tetap menyimpan"
        )

    cadangan = _backup(nama)
    joblib.dump(model, MODEL_DIR / f"{nama}_model.keras")
    joblib.dump(scaler, MODEL_DIR / f"{nama}_scaler.pkl")

    lama = "belum ada" if acc_lama is None else f"{acc_lama:.4f}"
    info = f"OK   {nama}: akurasi {acc_baru:.4f} (lama {lama}), data riwayat {len(df)}"
    if cadangan:
        info += f", backup -> {cadangan.relative_to(BASE_DIR)}"
    return info


def main():
    parser = argparse.ArgumentParser(description="Latih ulang model Somna.ai dari data riwayat.")
    parser.add_argument("--history", type=Path, default=HISTORY_PATH, help="file CSV riwayat")
    parser.add_argument("--min-rows", type=int, default=None,
                        help="minimal baris riwayat valid (default: sleep 100, productivity 300)")
    parser.add_argument("--force", action="store_true",
                        help="tetap simpan walau model lama lebih baik")
    args = parser.parse_args()

    if not args.history.exists():
        print(f"Riwayat tidak ditemukan: {args.history}")
        print("Format kolom yang dibutuhkan (gabungan kedua model):")
        for nama, spec in SPECS.items():
            print(f"  {nama}: {', '.join(spec['features'] + [spec['target']])}")
        print("Kolom yang tidak relevan untuk suatu model boleh kosong (NaN).")
        return 1

    history = pd.read_csv(args.history)
    print(f"Riwayat: {args.history} ({len(history)} baris)")
    print("Data dasar dataset/processed/ tidak dipakai (tetap bersih).\n")

    for nama, spec in SPECS.items():
        batas = args.min_rows if args.min_rows is not None else spec["min_rows"]
        print(_train(nama, spec, history, batas, args.force))

    print("\nSelesai. Restart server Flask agar model baru dipakai.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
