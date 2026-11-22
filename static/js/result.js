function buildDefaultFactors(input) {
  if (!input) {
    return [
      { judul: "Durasi & Latensi Tidur", deskripsi: "Rata-rata durasi tidur per malam dan waktu hingga mulai tertidur." },
      { judul: "Kualitas Tidur & Stres", deskripsi: "Penilaian kualitas tidur (1–5) dan tingkat stres harian (1–5)." },
      { judul: "Aktivitas Fisik", deskripsi: "Durasi aktivitas fisik harian yang mendukung ritme tidur." },
      { judul: "Penggunaan Ponsel Sebelum Tidur", deskripsi: "Durasi paparan layar dalam 1 jam sebelum tidur (maks. 60 menit)." },
    ];
  }

  return [
    {
      judul: "Durasi Tidur",
      deskripsi: `${Number(input.durasi_tidur).toFixed(1)} jam/malam (rata-rata 7 hari terakhir).`,
    },
    {
      judul: "Kesulitan Memulai Tidur",
      deskripsi: `${input.kesulitan_memulai_tidur} menit hingga tertidur.`,
    },
    {
      judul: "Kualitas Tidur & Tingkat Stres",
      deskripsi: `Kualitas tidur ${input.kualitas_tidur}/5 dengan tingkat stres ${input.tingkat_stres}/5.`,
    },
    {
      judul: "Aktivitas Fisik & Ponsel",
      deskripsi: `Aktivitas fisik ${input.aktivitas_fisik} menit/hari dan penggunaan ponsel sebelum tidur ${input.penggunaan_ponsel} menit.`,
    },
  ];
}

function renderSomnaResult() {
  const resultView = document.getElementById("resultView");
  const emptyState = document.getElementById("emptyState");
  if (!resultView) return;

  const stored = window.SomnaStorage ? window.SomnaStorage.getResult() : null;

  const jinjaProdLabel = resultView.dataset.jinjaProdLabel?.trim();
  const jinjaProdConf = resultView.dataset.jinjaProdConf?.trim();
  const jinjaInsomniaLabel = resultView.dataset.jinjaInsomniaLabel?.trim();
  const jinjaInsomniaConf = resultView.dataset.jinjaInsomniaConf?.trim();
  const jinjaAnalysis = resultView.dataset.jinjaAnalysis?.trim();

  const hasJinjaData = Boolean(jinjaProdLabel || jinjaInsomniaLabel || jinjaAnalysis);

  if (!stored && !hasJinjaData) {
    resultView.classList.add("hidden");
    if (emptyState) emptyState.classList.remove("hidden");
    return;
  }

  resultView.classList.remove("hidden");
  if (emptyState) emptyState.classList.add("hidden");

  const data = stored || {};

  const prodLabel = String(jinjaProdLabel || data.produktivitas?.label || "Sedang");
  const prodConfRaw = jinjaProdConf !== "" && jinjaProdConf !== undefined
    ? Number(jinjaProdConf)
    : Number(data.produktivitas?.confidence ?? 80);
  const prodConf = Math.max(0, Math.min(100, Number.isNaN(prodConfRaw) ? 80 : prodConfRaw));

  document.getElementById("prodBadge").textContent = prodLabel;
  document.getElementById("prodConfText").textContent = `${prodConf.toFixed(1)}%`;
  document.getElementById("prodConfBar").style.width = `${prodConf}%`;

  document.querySelectorAll("#prodLevels .level-chip").forEach((chip) => {
    const match = chip.textContent.trim().toLowerCase() === prodLabel.trim().toLowerCase();
    chip.classList.toggle("active", match);
  });

  const insomniaLabel = String(jinjaInsomniaLabel || data.indikasi_gangguan_tidur?.label || "Indikasi ringan");
  const insomniaConfRaw = jinjaInsomniaConf !== "" && jinjaInsomniaConf !== undefined
    ? Number(jinjaInsomniaConf)
    : Number(data.indikasi_gangguan_tidur?.confidence ?? 78);
  const insomniaConf = Math.max(0, Math.min(100, Number.isNaN(insomniaConfRaw) ? 78 : insomniaConfRaw));

  document.getElementById("insomniaBadge").textContent = insomniaLabel;
  document.getElementById("insomniaConfText").textContent = `${insomniaConf.toFixed(1)}%`;
  document.getElementById("insomniaConfBar").style.width = `${insomniaConf}%`;

  document.querySelectorAll("#insomniaLevels .level-chip").forEach((chip) => {
    const match = chip.textContent.trim().toLowerCase() === insomniaLabel.trim().toLowerCase();
    chip.classList.toggle("active", match);
  });

  const factorsGrid = document.getElementById("factorsGrid");
  if (factorsGrid) {
    factorsGrid.innerHTML = "";
    const factors = Array.isArray(data.faktor_utama) && data.faktor_utama.length > 0
      ? data.faktor_utama
      : buildDefaultFactors(data.input);

    factors.forEach((f, idx) => {
      const card = document.createElement("div");
      card.className = "rec-card";
      if (typeof f === "string") {
        card.innerHTML = `<h3>Faktor ${idx + 1}</h3><p>${f}</p>`;
      } else {
        card.innerHTML = `<h3>${f.judul || `Faktor ${idx + 1}`}</h3><p>${f.deskripsi || ""}</p>`;
      }
      factorsGrid.appendChild(card);
    });
  }

  document.getElementById("unifiedAnalysis").textContent =
    jinjaAnalysis ||
    data.analisis_terpadu ||
    "Belum ada ringkasan analisis terpadu.";

  const recGrid = document.getElementById("recommendationGrid");
  recGrid.innerHTML = "";
  const recs = Array.isArray(data.rekomendasi) ? data.rekomendasi : [];

  recs.forEach((item, idx) => {
    const card = document.createElement("div");
    card.className = "rec-card";
    if (typeof item === "string") {
      card.innerHTML = `<h3>Saran ${idx + 1}</h3><p>${item}</p>`;
    } else {
      card.innerHTML = `<h3>${item.judul || `Saran ${idx + 1}`}</h3><p>${item.deskripsi || ""}</p>`;
    }
    recGrid.appendChild(card);
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", renderSomnaResult);
} else {
  renderSomnaResult();
}