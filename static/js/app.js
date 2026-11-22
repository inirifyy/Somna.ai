/**
 * Somna.ai - Client Interaction & Event Controller
 * Mengatur seluruh interaksi klik tombol, slider, navigasi floating, dan kalkulasi hasil inferensi
 */
document.addEventListener("DOMContentLoaded", () => {
  // ==========================================
  // 1. DUAL-BUTTON & SCALE TOGGLE (CLICK EVENTS)
  // ==========================================
  const toggleGroups = document.querySelectorAll(".btn-group-toggle");

  toggleGroups.forEach((group) => {
    const targetInputId = group.dataset.target;
    const hiddenInput = targetInputId ? document.getElementById(targetInputId) : null;
    const type = group.dataset.type;
    const suffix = group.dataset.suffix || "";

    const buttons = group.querySelectorAll(".btn-toggle");

    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        // Matikan tombol aktif sebelumnya dalam grup ini
        buttons.forEach((b) => {
          b.classList.remove("bg-teal-500", "text-white", "outline-teal-500", "shadow-sm");
          b.classList.add("bg-gray-100", "text-gray-900", "outline-slate-200", "hover:bg-slate-200");
        });

        // Aktifkan tombol yang diklik
        btn.classList.remove("bg-gray-100", "text-gray-900", "outline-slate-200", "hover:bg-slate-200");
        btn.classList.add("bg-teal-500", "text-white", "outline-teal-500", "shadow-sm");

        const val = btn.dataset.val;

        // Simpan nilai ke hidden input form
        if (hiddenInput) {
          hiddenInput.value = val;
        }

        // Update badge tampilan secara real-time
        if (type === "kualitas") {
          const num = parseInt(val, 10);
          let label = "Cukup";
          if (num <= 3) label = "Buruk";
          else if (num <= 6) label = "Cukup";
          else if (num <= 8) label = "Baik";
          else label = "Sangat Baik";

          const badge = document.getElementById("kualitasBadge");
          if (badge) badge.textContent = `${label} (${num}/10)`;
        } else if (type === "stres") {
          const num = parseInt(val, 10);
          let label = "Sedang";
          if (num <= 3) label = "Rendah";
          else if (num <= 6) label = "Sedang";
          else if (num <= 8) label = "Tinggi";
          else label = "Sangat Tinggi";

          const badge = document.getElementById("stresBadge");
          if (badge) badge.textContent = `${label} (${num}/10)`;
        } else if (targetInputId === "input_aktivitas_fisik") {
          const badge = document.getElementById("aktivitasBadge");
          if (badge) badge.textContent = `${val}${suffix}`;
        } else if (targetInputId === "input_layar_sebelum_tidur") {
          const badge = document.getElementById("layarBadge");
          if (badge) badge.textContent = val;
        } else if (targetInputId === "input_konsumsi_kafein") {
          const badge = document.getElementById("kafeinBadge");
          if (badge) badge.textContent = val;
        }
      });
    });
  });

  // ==========================================
  // 2. SLIDER DURASI TIDUR (INPUT EVENT)
  // ==========================================
  const durasiSlider = document.getElementById("durasi_tidur");
  const durasiDisplay = document.getElementById("durasiValueDisplay");

  if (durasiSlider && durasiDisplay) {
    durasiSlider.addEventListener("input", (e) => {
      const val = parseFloat(e.target.value).toFixed(1);
      durasiDisplay.textContent = `${val} jam`;
    });
  }

  // ==========================================
  // 3. SMOOTH SCROLL & ACTIVE NAVBAR STATE
  // ==========================================
  const navLinks = document.querySelectorAll("#navLinks a.nav-link");

  function setActiveNavLink(targetHref) {
    navLinks.forEach((link) => {
      if (link.getAttribute("href") === targetHref) {
        link.className =
          "nav-link text-teal-600 text-sm sm:text-base font-semibold font-['Inter'] border-b-2 border-teal-600 pb-0.5 transition-colors";
      } else {
        link.className =
          "nav-link text-slate-600 hover:text-teal-600 text-sm sm:text-base font-medium font-['Inter'] transition-colors";
      }
    });
  }

  const anchorLinks = document.querySelectorAll('a[href^="#"]');

  anchorLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      const targetId = link.getAttribute("href");
      if (targetId && targetId !== "#") {
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
          e.preventDefault();

          // Jika link atau target sesuai dengan menu navbar, update highlight seketika
          const matchingNavLink = document.querySelector(`#navLinks a[href="${targetId}"]`);
          if (matchingNavLink) {
            setActiveNavLink(targetId);
          }

          const navOffset = 90; // offset untuk navbar floating
          const elementPosition = targetElement.getBoundingClientRect().top;
          const offsetPosition = elementPosition + window.pageYOffset - navOffset;

          window.scrollTo({
            top: offsetPosition,
            behavior: "smooth",
          });
        }
      }
    });
  });

  // ==========================================
  // 4. FLOATING NAVBAR SCROLLSPY
  // ==========================================
  const navSections = [
    { id: "hero", target: "#hero" },
    { id: "fitur", target: "#fitur" },
    { id: "caraKerja", target: "#caraKerja" },
    { id: "formAnalisis", target: "#formAnalisis" },
  ];

  function updateNavbarScrollSpy() {
    const scrollPosition = window.scrollY || window.pageYOffset;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;

    // Jika sudah mendekati bagian bawah halaman (form/hasil/tips), pastikan 'Analisis' aktif
    if (windowHeight + scrollPosition >= documentHeight - 100) {
      setActiveNavLink("#formAnalisis");
      return;
    }

    let currentTarget = "#hero";
    navSections.forEach(({ id, target }) => {
      const section = document.getElementById(id);
      if (section) {
        const sectionTop = section.offsetTop - 140;
        if (scrollPosition >= sectionTop) {
          currentTarget = target;
        }
      }
    });

    setActiveNavLink(currentTarget);
  }

  window.addEventListener("scroll", updateNavbarScrollSpy, { passive: true });
  updateNavbarScrollSpy();

  // ==========================================
  // 5. TOMBOL SUBMIT ANALISIS & REAKTIVITAS HASIL
  // ==========================================
  const sleepForm = document.getElementById("sleepForm");

  if (sleepForm) {
    sleepForm.addEventListener("submit", (e) => {
      // Kita cegah reload halaman penuh agar pengguna tetap merasakan pengalaman 1-page yang mulus
      e.preventDefault();

      // Ambil nilai dari input form
      const durasi = parseFloat(document.getElementById("durasi_tidur").value) || 7.0;
      const kesulitan = document.getElementById("input_kesulitan_tidur").value || "Jarang";
      const kualitas = parseInt(document.getElementById("input_kualitas_tidur").value, 10) || 8;
      const stres = parseInt(document.getElementById("input_tingkat_stres").value, 10) || 6;
      const aktivitas = parseInt(document.getElementById("input_aktivitas_fisik").value, 10) || 60;
      const layar = document.getElementById("input_layar_sebelum_tidur").value || "Sering";

      // 1. Hitung perkiraan Latensi Onset Tidur
      let latencyMin = 20;
      if (kesulitan === "Tidak") latencyMin = 10;
      else if (kesulitan === "Jarang") latencyMin = 20;
      else if (kesulitan === "Sering") latencyMin = 35;
      else if (kesulitan === "Selalu") latencyMin = 50;

      // 2. Hitung perkiraan Waktu Layar Pra-Tidur
      let screenMin = 30;
      if (layar === "Tidak") screenMin = 0;
      else if (layar === "Jarang") screenMin = 15;
      else if (layar === "Sering") screenMin = 40;
      else if (layar === "Selalu") screenMin = 60;

      // 3. Logika Klasifikasi Produktivitas (Rendah / Sedang / Tinggi)
      // Ideal: durasi 7-9 jam, kualitas >= 7, stres <= 5, aktivitas >= 45
      let prodScore = 0;
      if (durasi >= 7.0 && durasi <= 9.0) prodScore += 3;
      else if (durasi >= 6.0 && durasi < 7.0) prodScore += 2;
      else prodScore += 1;

      if (kualitas >= 8) prodScore += 3;
      else if (kualitas >= 5) prodScore += 2;
      else prodScore += 1;

      if (stres <= 4) prodScore += 3;
      else if (stres <= 7) prodScore += 2;
      else prodScore += 1;

      if (aktivitas >= 45) prodScore += 2;
      else prodScore += 1;

      let prodStatus = "Sedang";
      if (prodScore >= 10) prodStatus = "Tinggi";
      else if (prodScore <= 5) prodStatus = "Rendah";

      // 4. Logika Skrining Gejala Insomnia
      let insomniaScore = 0;
      if (kesulitan === "Selalu") insomniaScore += 4;
      else if (kesulitan === "Sering") insomniaScore += 3;
      else if (kesulitan === "Jarang") insomniaScore += 1;

      if (latencyMin > 30) insomniaScore += 2;
      if (screenMin >= 40) insomniaScore += 1;
      if (stres >= 8) insomniaScore += 2;
      if (kualitas <= 4) insomniaScore += 2;

      let insomniaStatus = "Tidak Ada Gejala";
      if (insomniaScore >= 7) insomniaStatus = "Berat";
      else if (insomniaScore >= 4) insomniaStatus = "Sedang";
      else if (insomniaScore >= 2) insomniaStatus = "Subthreshold";

      // ==========================================
      // UPDATE UI SECTION HASIL INFERENSI
      // ==========================================
      // A. Update Metrik Analisis Terpadu
      const metricLatency = document.getElementById("metricLatency");
      if (metricLatency) metricLatency.textContent = `${latencyMin} menit`;

      const metricScreen = document.getElementById("metricScreenTime");
      if (metricScreen) metricScreen.textContent = `${screenMin} menit`;

      const metricDuration = document.getElementById("metricDuration");
      if (metricDuration) metricDuration.textContent = `${durasi.toFixed(1)} jam`;

      const durationBadge = document.getElementById("metricDurationBadge");
      if (durationBadge) {
        if (durasi >= 7.0 && durasi <= 9.0) {
          durationBadge.textContent = "(Rentang Optimal)";
          durationBadge.className = "text-teal-700 font-semibold text-xs";
        } else if (durasi < 6.0) {
          durationBadge.textContent = "(Kurang Tidur)";
          durationBadge.className = "text-rose-600 font-semibold text-xs";
        } else {
          durationBadge.textContent = "(Cukup)";
          durationBadge.className = "text-amber-600 font-semibold text-xs";
        }
      }

      // B. Update Kartu Produktivitas
      const badgeProd = document.getElementById("badgeProductivity");
      if (badgeProd) badgeProd.textContent = prodStatus;

      const descProd = document.getElementById("descProductivity");
      const summaryProd = document.getElementById("summaryProductivity");
      if (summaryProd) summaryProd.textContent = prodStatus;

      const barProdR = document.getElementById("barProdRendah");
      const barProdS = document.getElementById("barProdSedang");
      const barProdT = document.getElementById("barProdTinggi");

      const labelProdR = document.getElementById("labelProdRendah");
      const labelProdS = document.getElementById("labelProdSedang");
      const labelProdT = document.getElementById("labelProdTinggi");

      // Reset bars & labels
      [barProdR, barProdS, barProdT].forEach((b) => {
        if (b) b.className = "flex-1 bg-slate-200 rounded-sm transition-colors duration-300";
      });
      [labelProdR, labelProdS, labelProdT].forEach((l) => {
        if (l) l.className = "flex-1 text-center text-slate-500";
      });

      if (prodStatus === "Tinggi") {
        if (barProdT) barProdT.className = "flex-1 bg-teal-600 rounded-sm transition-colors duration-300";
        if (labelProdT) labelProdT.className = "flex-1 text-center text-teal-700 font-bold";
        if (descProd)
          descProd.textContent =
            "Pola tidur Anda sangat teratur dan mendukung pemulihan fungsi kognitif maksimal untuk produktivitas optimal sepanjang hari.";
      } else if (prodStatus === "Rendah") {
        if (barProdR) barProdR.className = "flex-1 bg-amber-500 rounded-sm transition-colors duration-300";
        if (labelProdR) labelProdR.className = "flex-1 text-center text-amber-700 font-bold";
        if (descProd)
          descProd.textContent =
            "Pola tidur Anda saat ini belum optimal dalam menunjang stamina kognitif harian. Diperlukan penyesuaian jam tidur dan pengurangan stres.";
      } else {
        if (barProdS) barProdS.className = "flex-1 bg-teal-600 rounded-sm transition-colors duration-300";
        if (labelProdS) labelProdS.className = "flex-1 text-center text-teal-700 font-bold";
        if (descProd)
          descProd.textContent =
            "Pola tidur Anda saat ini mendukung tingkat produktivitas yang cukup stabil, namun variasi durasi tidur dan aktivitas malam dapat ditingkatkan.";
      }

      // C. Update Kartu Insomnia
      const badgeInsom = document.getElementById("badgeInsomnia");
      if (badgeInsom) badgeInsom.textContent = insomniaStatus;

      const descInsom = document.getElementById("descInsomnia");
      const summaryInsom = document.getElementById("summaryInsomnia");
      if (summaryInsom) summaryInsom.textContent = insomniaStatus;

      const barInsomNone = document.getElementById("barInsomNone");
      const barInsomSub = document.getElementById("barInsomSub");
      const barInsomSedang = document.getElementById("barInsomSedang");
      const barInsomBerat = document.getElementById("barInsomBerat");

      const labelInsomNone = document.getElementById("labelInsomNone");
      const labelInsomSub = document.getElementById("labelInsomSub");
      const labelInsomSedang = document.getElementById("labelInsomSedang");
      const labelInsomBerat = document.getElementById("labelInsomBerat");

      [barInsomNone, barInsomSub, barInsomSedang, barInsomBerat].forEach((b) => {
        if (b) b.className = "flex-1 bg-slate-200 rounded-sm transition-colors duration-300";
      });
      [labelInsomNone, labelInsomSub, labelInsomSedang, labelInsomBerat].forEach((l) => {
        if (l) l.className = "flex-1 text-center text-slate-500";
      });

      if (insomniaStatus === "Tidak Ada Gejala") {
        if (barInsomNone) barInsomNone.className = "flex-1 bg-teal-600 rounded-sm transition-colors duration-300";
        if (labelInsomNone) labelInsomNone.className = "flex-1 text-center text-teal-700 font-bold";
        if (descInsom)
          descInsom.textContent =
            "Tidak ditemukan indikasi signifikan gangguan insomnia. Ritme sirkadian dan waktu latensi onset tidur Anda berada dalam batas sehat.";
      } else if (insomniaStatus === "Subthreshold") {
        if (barInsomSub) barInsomSub.className = "flex-1 bg-teal-600 rounded-sm transition-colors duration-300";
        if (labelInsomSub) labelInsomSub.className = "flex-1 text-center text-teal-700 font-bold";
        if (descInsom)
          descInsom.textContent =
            "Indikasi awal menunjukkan adanya gejala subthreshold (ringan) yang umumnya dipicu oleh sleep latency di atas 20 menit dan paparan layar malam.";
      } else if (insomniaStatus === "Sedang") {
        if (barInsomSedang) barInsomSedang.className = "flex-1 bg-amber-500 rounded-sm transition-colors duration-300";
        if (labelInsomSedang) labelInsomSedang.className = "flex-1 text-center text-amber-700 font-bold";
        if (descInsom)
          descInsom.textContent =
            "Terdapat indikasi gejala insomnia tingkat sedang yang mulai mempengaruhi kenyamanan istirahat Anda. Disarankan menerapkan jadwal tidur konsisten.";
      } else {
        if (barInsomBerat) barInsomBerat.className = "flex-1 bg-rose-500 rounded-sm transition-colors duration-300";
        if (labelInsomBerat) labelInsomBerat.className = "flex-1 text-center text-rose-700 font-bold";
        if (descInsom)
          descInsom.textContent =
            "Menunjukkan indikasi gejala insomnia tingkat tinggi dengan beban stres dan latensi onset tinggi. Disarankan berkonsultasi ke tenaga kesehatan profesional.";
      }

      // D. Smooth Scroll langsung ke Bagian Hasil
      const hasilSection = document.getElementById("hasilInferensi");
      if (hasilSection) {
        const navOffset = 80;
        const targetPos = hasilSection.getBoundingClientRect().top + window.pageYOffset - navOffset;
        window.scrollTo({
          top: targetPos,
          behavior: "smooth",
        });
      }
    });
  }

  // Bersihkan sisa state dark mode dari browser jika ada
  try {
    localStorage.removeItem("somna_theme");
    document.documentElement.classList.remove("dark");
  } catch (e) {}
});
