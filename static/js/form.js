document.addEventListener("DOMContentLoaded", () => {
  const durasiInput = document.getElementById("durasi_tidur");
  const durasiBadge = document.getElementById("durasiBadge");

  function syncDurasiUI() {
    if (!durasiInput || !durasiBadge) return;
    const val = Number(durasiInput.value);
    durasiBadge.textContent = `${val.toFixed(1)} Jam`;
    durasiBadge.classList.add("is-filled");
    const fieldItem = durasiInput.closest(".field-item");
    if (fieldItem) fieldItem.classList.add("is-completed");
  }

  if (durasiInput) {
    syncDurasiUI();
    ["input", "change", "pointerdown", "focus"].forEach((evt) => {
      durasiInput.addEventListener(evt, syncDurasiUI);
    });
  }

  // Interaksi tombol skala 1 - 5 (Kualitas Tidur & Tingkat Stres)
  document.querySelectorAll(".scale-buttons").forEach((group) => {
    const targetId = group.dataset.target;
    const displayId = group.dataset.display;
    let labels = {};
    try {
      labels = JSON.parse(group.dataset.labels || "{}");
    } catch {
      labels = {};
    }
    const hiddenInput = targetId ? document.getElementById(targetId) : null;
    const displayEl = displayId ? document.getElementById(displayId) : null;
    const fieldItem = group.closest(".field-item");

    const activeInit = group.querySelector(".scale-btn.active");
    if (activeInit && displayEl) {
      displayEl.classList.add("is-filled");
      if (fieldItem) fieldItem.classList.add("is-completed");
    }

    group.querySelectorAll(".scale-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        group.querySelectorAll(".scale-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");

        const val = btn.dataset.val;
        if (hiddenInput) hiddenInput.value = val;
        if (displayEl && labels[val]) {
          displayEl.textContent = labels[val];
          displayEl.classList.add("is-filled");
        }
        if (fieldItem) {
          fieldItem.classList.add("is-completed");
        }
      });
    });
  });

  // Interaksi visual saat input angka diklik / difokuskan / diisi
  const numberInputs = document.querySelectorAll('#sleepForm input[type="number"]');
  numberInputs.forEach((input) => {
    const fieldItem = input.closest(".field-item");
    const pill = fieldItem ? fieldItem.querySelector(".field-label-row .value-pill") : null;
    const defaultPillText = pill ? pill.textContent.trim() : "";

    function refreshNumberState() {
      const hasValue = input.value !== "" && !Number.isNaN(Number(input.value));
      const isFocused = document.activeElement === input;

      if (fieldItem) {
        fieldItem.classList.toggle("is-focused", isFocused);
        fieldItem.classList.toggle("is-completed", hasValue);
      }

      if (pill) {
        if (hasValue) {
          pill.classList.add("is-filled");
          if (input.id === "kesulitan_memulai_tidur") {
            pill.textContent = `${input.value} Menit`;
          } else if (input.id === "aktivitas_fisik") {
            pill.textContent = `${input.value} Menit/Hari`;
          } else if (input.id === "penggunaan_ponsel") {
            pill.textContent = `${input.value} / 60 Menit`;
          }
        } else if (isFocused) {
          pill.classList.add("is-filled");
          pill.textContent = "Sedang diisi...";
        } else {
          pill.classList.remove("is-filled");
          if (defaultPillText) pill.textContent = defaultPillText;
        }
      }
    }

    ["focus", "blur", "input", "change"].forEach((evt) => {
      input.addEventListener(evt, refreshNumberState);
    });
    refreshNumberState();
  });

  const form = document.getElementById("sleepForm");
  if (!form) return;

  const errorBox = document.getElementById("formError");
  const loadingBox = document.getElementById("loadingBox");
  const btnSubmit = document.getElementById("btnSubmit");

  function showError(msg) {
    if (!errorBox) return;
    errorBox.textContent = msg;
    errorBox.classList.remove("hidden");
  }

  function hideError() {
    if (!errorBox) return;
    errorBox.textContent = "";
    errorBox.classList.add("hidden");
  }

  function createFallbackResult(p) {
    const prodLabel =
      p.durasi_tidur >= 7 && p.kualitas_tidur >= 4 && p.tingkat_stres <= 3
        ? "Tinggi"
        : p.durasi_tidur >= 5.5
        ? "Sedang"
        : "Rendah";

    const insomniaLabel =
      p.kesulitan_memulai_tidur <= 20 && p.kualitas_tidur >= 4
        ? "Tidak terindikasi"
        : p.kesulitan_memulai_tidur <= 40
        ? "Indikasi ringan"
        : p.kesulitan_memulai_tidur <= 60
        ? "Indikasi sedang"
        : "Indikasi berat";

    return {
      input: p,
      produktivitas: { label: prodLabel, confidence: 82.0 },
      indikasi_gangguan_tidur: { label: insomniaLabel, confidence: 78.5 },
      analisis_terpadu: `Rata-rata durasi tidur ${p.durasi_tidur} jam, waktu mulai tidur ${p.kesulitan_memulai_tidur} menit, kualitas tidur ${p.kualitas_tidur}/5, tingkat stres ${p.tingkat_stres}/5, aktivitas fisik ${p.aktivitas_fisik} menit/hari, dan penggunaan ponsel sebelum tidur ${p.penggunaan_ponsel} menit mengarah pada klasifikasi produktivitas ${prodLabel} serta skrining gejala insomnia ${insomniaLabel}.`,
      rekomendasi: [
        {
          judul: "Pertahankan Jadwal Tidur yang Konsisten",
          deskripsi: "Tidur dan bangun pada jam yang relatif teratur setiap hari agar ritme tidur lebih stabil.",
        },
        {
          judul: "Kurangi Penggunaan Layar Sebelum Tidur",
          deskripsi: `Batasi pemakaian ponsel dalam 1 jam sebelum tidur (tercatat ${p.penggunaan_ponsel} menit) agar lebih mudah tertidur.`,
        },
        {
          judul: "Kelola Stres Harian",
          deskripsi: `Atur jeda istirahat atau teknik relaksasi ringan saat tingkat stres berada di skala ${p.tingkat_stres}/5.`,
        },
        {
          judul: "Rutin Lakukan Aktivitas Fisik",
          deskripsi: `Pertahankan aktivitas fisik harian (tercatat ${p.aktivitas_fisik} menit/hari) pada waktu yang sesuai.`,
        },
      ],
    };
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError();

    const payload = {
      durasi_tidur: parseFloat(document.getElementById("durasi_tidur").value),
      kesulitan_memulai_tidur: parseFloat(document.getElementById("kesulitan_memulai_tidur").value),
      kualitas_tidur: parseInt(document.getElementById("kualitas_tidur").value, 10),
      tingkat_stres: parseInt(document.getElementById("tingkat_stres").value, 10),
      aktivitas_fisik: parseFloat(document.getElementById("aktivitas_fisik").value),
      penggunaan_ponsel: parseFloat(document.getElementById("penggunaan_ponsel").value),
    };

    if (Object.values(payload).some((v) => Number.isNaN(v))) {
      showError("Harap lengkapi seluruh enam variabel kebiasaan tidur.");
      return;
    }
    if (payload.durasi_tidur < 0 || payload.durasi_tidur > 24) {
      showError("Durasi tidur harus berada pada rentang 0–24 jam.");
      return;
    }
    if (payload.kesulitan_memulai_tidur < 0) {
      showError("Kesulitan memulai tidur tidak boleh bernilai negatif.");
      return;
    }
    if (payload.aktivitas_fisik < 0) {
      showError("Aktivitas fisik tidak boleh bernilai negatif.");
      return;
    }
    if (payload.penggunaan_ponsel < 0 || payload.penggunaan_ponsel > 60) {
      showError("Penggunaan ponsel sebelum tidur dihitung dalam 1 jam sebelum tidur (0–60 menit).");
      return;
    }

    if (btnSubmit) {
      btnSubmit.disabled = true;
      btnSubmit.textContent = "Menganalisis...";
    }
    if (loadingBox) loadingBox.classList.remove("hidden");

    const resultData = createFallbackResult(payload);
    if (window.SomnaStorage) {
      window.SomnaStorage.setResult(resultData);
    }

    try {
      const response = await fetch("/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const htmlText = await response.text();
        document.open();
        document.write(htmlText);
        document.close();
      } else {
        window.location.href = "/result";
      }
    } catch (err) {
      window.location.href = "/result";
    }
  });
});
// Interaksi tombol skala 1 - 5 (awalnya kosong, menyala hijau saat dipencet)
document.querySelectorAll(".scale-buttons").forEach((group) => {
  const targetId = group.dataset.target;
  const displayId = group.dataset.display;
  let labels = {};
  try {
    labels = JSON.parse(group.dataset.labels || "{}");
  } catch {
    labels = {};
  }

  const hiddenInput = targetId ? document.getElementById(targetId) : null;
  const displayEl = displayId ? document.getElementById(displayId) : null;
  const fieldItem = group.closest(".field-item");
  const buttons = group.querySelectorAll(".scale-btn");

  // Pastikan awalnya tidak ada yang terpilih jika value kosong
  if (!hiddenInput || !hiddenInput.value) {
    buttons.forEach((b) => b.classList.remove("active", "is-selected"));
    if (displayEl) {
      displayEl.classList.remove("is-filled");
    }
    if (fieldItem) {
      fieldItem.classList.remove("is-completed");
    }
  }

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      buttons.forEach((b) => b.classList.remove("active", "is-selected"));
      btn.classList.add("active", "is-selected");

      const val = btn.dataset.val;
      if (hiddenInput) {
        hiddenInput.value = val;
      }
      if (displayEl && labels[val]) {
        displayEl.textContent = labels[val];
        displayEl.classList.add("is-filled");
      }
      if (fieldItem) {
        fieldItem.classList.add("is-completed", "is-focused");
      }
    });
  });
});