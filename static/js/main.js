(() => {
  const STORAGE_KEY = "somna_latest_result_v1";
  const THEME_KEY = "somna_theme_mode_v1";

  window.SomnaStorage = {
    setResult(data) {
      try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      } catch (e) {
        console.warn("Penyimpanan lokal tidak tersedia:", e);
      }
    },
    getResult() {
      try {
        const rawSession = sessionStorage.getItem(STORAGE_KEY);
        if (rawSession) return JSON.parse(rawSession);
        const rawLocal = localStorage.getItem(STORAGE_KEY);
        return rawLocal ? JSON.parse(rawLocal) : null;
      } catch (e) {
        console.warn("Gagal membaca data hasil:", e);
        return null;
      }
    },
    clearResult() {
      try {
        sessionStorage.removeItem(STORAGE_KEY);
        localStorage.removeItem(STORAGE_KEY);
      } catch (e) {
        console.warn("Gagal menghapus data hasil:", e);
      }
    },
  };

  function getSavedTheme() {
    try {
      return localStorage.getItem(THEME_KEY) || "dark";
    } catch (e) {
      return "dark";
    }
  }

  function applyTheme(theme) {
    const mode = theme === "light" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", mode);
    if (document.body) {
      document.body.setAttribute("data-theme", mode);
    }

    const iconEl = document.getElementById("themeIcon");
    const labelEl = document.getElementById("themeLabel");
    if (iconEl) iconEl.textContent = mode === "dark" ? "☀" : "☾";
    if (labelEl) labelEl.textContent = mode === "dark" ? "Terang" : "Gelap";

    try {
      localStorage.setItem(THEME_KEY, mode);
    } catch (e) {
      // Abaikan jika penyimpanan dibatasi
    }
  }

  applyTheme(getSavedTheme());

  document.addEventListener("DOMContentLoaded", () => {
    applyTheme(getSavedTheme());

    const toggleBtn = document.getElementById("themeToggle");
    if (toggleBtn) {
      toggleBtn.addEventListener("click", (e) => {
        e.preventDefault();
        const current = document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
        applyTheme(current === "light" ? "dark" : "light");
      });
    }

    const navLinks = document.querySelectorAll('.nav-links a[href*="#"]');
    navLinks.forEach((link) => {
      link.addEventListener("click", () => {
        const hash = link.getAttribute("href").split("#")[1];
        if (!hash) return;
        const target = document.getElementById(hash);
        if (target) {
          target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
    });

    document.querySelectorAll(".btn-teal, .btn-outline-teal, .scale-btn, .step-card, .result-card, .rec-card").forEach((el) => {
      el.addEventListener("pointerdown", () => {
        el.classList.add("is-pressed");
      });
      ["pointerup", "pointerleave", "pointercancel"].forEach((evt) => {
        el.addEventListener(evt, () => {
          el.classList.remove("is-pressed");
        });
      });
    });
  });
})();