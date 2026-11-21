/* ==========================================================================
   ARTSY_2000 PRESS KIT — INTERACTIVE CONTROLS
   Copy-to-clipboard, screenshot filtering, lightbox viewer, logo swatches,
   active TOC scroll-spy, and file:// YouTube preview fallback.
   ========================================================================== */

(function () {
  "use strict";

  // ------------------------------------------------------------------------
  // Toast helper
  // ------------------------------------------------------------------------
  let toastTimer = null;
  function showToast(message) {
    const toast = document.getElementById("pressToast");
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("show");
    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toast.classList.remove("show");
    }, 2200);
  }

  // ------------------------------------------------------------------------
  // Copy-to-clipboard buttons
  // ------------------------------------------------------------------------
  function copyTextToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise((resolve, reject) => {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      try {
        const ok = document.execCommand("copy");
        document.body.removeChild(ta);
        if (ok) resolve();
        else reject(new Error("Copy failed"));
      } catch (err) {
        document.body.removeChild(ta);
        reject(err);
      }
    });
  }

  function initCopyButtons() {
    document.querySelectorAll("[data-copy-target], [data-copy-text]").forEach((btn) => {
      btn.addEventListener("click", () => {
        let text = "";
        const targetId = btn.getAttribute("data-copy-target");
        if (targetId) {
          const el = document.getElementById(targetId);
          if (el) text = el.innerText.trim();
        } else {
          text = btn.getAttribute("data-copy-text") || "";
        }
        if (!text) return;

        copyTextToClipboard(text)
          .then(() => {
            const orig = btn.getAttribute("data-orig-label") || btn.textContent;
            btn.setAttribute("data-orig-label", orig);
            btn.classList.add("copied");
            btn.textContent = "✓ Copied";
            const label = btn.getAttribute("data-copy-label") || "Text";
            showToast(label + " copied to clipboard");
            setTimeout(() => {
              btn.classList.remove("copied");
              btn.textContent = orig;
            }, 1800);
          })
          .catch(() => {
            showToast("Unable to copy automatically — please select and copy");
          });
      });
    });
  }

  // ------------------------------------------------------------------------
  // Tabbed Copy Switcher (Short Blurb / Full Description / One-Line Pitch)
  // ------------------------------------------------------------------------
  function initCopyTabs() {
    const buttons = document.querySelectorAll(".copy-tab-btn[data-copy-panel]");
    const panels = document.querySelectorAll(".copy-panel");
    const activeCopyBtn = document.getElementById("activeCopyBtn");
    if (!buttons.length || !panels.length) return;

    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const panelId = btn.getAttribute("data-copy-panel");
        const label = btn.getAttribute("data-copy-label") || "Copy";
        buttons.forEach((b) => {
          const isMatch = b === btn;
          b.classList.toggle("active", isMatch);
          b.setAttribute("aria-selected", isMatch ? "true" : "false");
        });
        panels.forEach((p) => {
          p.classList.toggle("active", p.id === panelId);
        });
        if (activeCopyBtn) {
          activeCopyBtn.setAttribute("data-copy-target", panelId);
          activeCopyBtn.setAttribute("data-copy-label", label);
        }
      });
    });
  }

  // ------------------------------------------------------------------------
  // Screenshot category filtering, Expand-All toggle & Lightbox viewer
  // ------------------------------------------------------------------------
  let activeShotIndex = 0;
  let shotsExpanded = false;
  let activeFilter = "all";

  function applyScreenshotVisibility() {
    const cards = Array.from(document.querySelectorAll(".shot-card"));
    const expandRow = document.getElementById("shotsExpandRow");
    const expandBtn = document.getElementById("shotsExpandBtn");

    let extraHiddenCount = 0;
    cards.forEach((card, idx) => {
      const cat = card.getAttribute("data-category");
      const matchesFilter = activeFilter === "all" || cat === activeFilter;
      card.classList.toggle("hidden", !matchesFilter);

      const shouldCollapse = activeFilter === "all" && !shotsExpanded && idx >= 9;
      card.classList.toggle("collapsed-extra", shouldCollapse);
      if (shouldCollapse) extraHiddenCount++;
    });

    if (expandRow) {
      expandRow.classList.toggle("hidden", activeFilter !== "all");
    }
    if (expandBtn) {
      expandBtn.textContent = shotsExpanded
        ? "Show fewer screenshots (top 9)"
        : `Show all ${cards.length} screenshots (+${extraHiddenCount} more)`;
      expandBtn.setAttribute("aria-expanded", shotsExpanded ? "true" : "false");
    }
  }

  function getVisibleShotCards() {
    return Array.from(document.querySelectorAll(".shot-card:not(.hidden):not(.collapsed-extra)"));
  }

  function initScreenshotFilters() {
    const buttons = document.querySelectorAll(".filter-btn[data-filter]");
    const expandBtn = document.getElementById("shotsExpandBtn");
    const cards = document.querySelectorAll(".shot-card");
    if (!buttons.length || !cards.length) return;

    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        activeFilter = btn.getAttribute("data-filter") || "all";
        buttons.forEach((b) => {
          b.classList.toggle("active", b === btn);
          b.setAttribute("aria-pressed", b === btn ? "true" : "false");
        });
        applyScreenshotVisibility();
      });
    });

    if (expandBtn) {
      expandBtn.addEventListener("click", () => {
        shotsExpanded = !shotsExpanded;
        applyScreenshotVisibility();
      });
    }

    applyScreenshotVisibility();
  }

  function renderLightbox(index) {
    const cards = getVisibleShotCards();
    if (!cards.length) return;
    activeShotIndex = (index + cards.length) % cards.length;
    const card = cards[activeShotIndex];

    const imgSrc = card.getAttribute("data-full-src");
    const title = card.getAttribute("data-title") || "";
    const caption = card.getAttribute("data-caption") || "";
    const res = card.getAttribute("data-res") || "";
    const filename = card.getAttribute("data-filename") || "artsy_2000_screenshot.png";

    const lbImg = document.getElementById("lightboxImg");
    const lbTitle = document.getElementById("lightboxTitle");
    const lbCaption = document.getElementById("lightboxCaption");
    const lbCounter = document.getElementById("lightboxCounter");
    const lbRes = document.getElementById("lightboxRes");
    const lbDl = document.getElementById("lightboxDownload");

    if (lbImg) {
      lbImg.src = imgSrc;
      lbImg.alt = title;
    }
    if (lbTitle) lbTitle.textContent = title;
    if (lbCaption) lbCaption.textContent = caption;
    if (lbCounter) lbCounter.textContent = `${activeShotIndex + 1} / ${cards.length}`;
    if (lbRes) lbRes.textContent = res;
    if (lbDl) {
      lbDl.href = imgSrc;
      lbDl.setAttribute("download", filename);
    }
  }

  function openLightboxForCard(card) {
    const cards = getVisibleShotCards();
    const idx = cards.indexOf(card);
    if (idx === -1) return;
    const lb = document.getElementById("pressLightbox");
    if (!lb) return;
    renderLightbox(idx);
    lb.classList.add("open");
    lb.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    const closeBtn = document.getElementById("lightboxClose");
    if (closeBtn) closeBtn.focus();
  }

  function closeLightbox() {
    const lb = document.getElementById("pressLightbox");
    if (!lb || !lb.classList.contains("open")) return;
    lb.classList.remove("open");
    lb.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  function initLightbox() {
    document.querySelectorAll(".shot-card .shot-thumb-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const card = btn.closest(".shot-card");
        if (card) openLightboxForCard(card);
      });
    });

    const lb = document.getElementById("pressLightbox");
    const closeBtn = document.getElementById("lightboxClose");
    const prevBtn = document.getElementById("lightboxPrev");
    const nextBtn = document.getElementById("lightboxNext");

    if (closeBtn) closeBtn.addEventListener("click", closeLightbox);
    if (prevBtn) prevBtn.addEventListener("click", () => renderLightbox(activeShotIndex - 1));
    if (nextBtn) nextBtn.addEventListener("click", () => renderLightbox(activeShotIndex + 1));

    if (lb) {
      lb.addEventListener("click", (e) => {
        if (e.target === lb) closeLightbox();
      });
    }

    document.addEventListener("keydown", (e) => {
      if (!lb || !lb.classList.contains("open")) return;
      if (e.key === "Escape") closeLightbox();
      else if (e.key === "ArrowLeft") renderLightbox(activeShotIndex - 1);
      else if (e.key === "ArrowRight") renderLightbox(activeShotIndex + 1);
    });
  }

  // ------------------------------------------------------------------------
  // Logo stage background switcher (Dark / Light / Checkerboard)
  // ------------------------------------------------------------------------
  function initLogoSwatches() {
    const buttons = document.querySelectorAll(".bg-swatch-btn[data-stage]");
    const stages = document.querySelectorAll("[data-logo-stage]");
    if (!buttons.length || !stages.length) return;

    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const mode = btn.getAttribute("data-stage");
        buttons.forEach((b) => b.classList.toggle("active", b === btn));
        stages.forEach((stage) => {
          stage.classList.remove("stage-light", "stage-checker");
          if (mode === "light") stage.classList.add("stage-light");
          else if (mode === "checker") stage.classList.add("stage-checker");
        });
      });
    });
  }

  // ------------------------------------------------------------------------
  // Active TOC scroll-spy
  // ------------------------------------------------------------------------
  function initScrollSpy() {
    const links = Array.from(document.querySelectorAll(".toc-list a[href^='#']"));
    const sections = links
      .map((a) => document.querySelector(a.getAttribute("href")))
      .filter(Boolean);

    if (!links.length || !sections.length || !("IntersectionObserver" in window)) return;

    const setActive = (id) => {
      links.forEach((a) => {
        a.classList.toggle("active", a.getAttribute("href") === "#" + id);
      });
    };

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible.length) {
          setActive(visible[0].target.id);
        }
      },
      { rootMargin: "-18% 0px -68% 0px", threshold: 0.01 }
    );

    sections.forEach((sec) => observer.observe(sec));
  }

  // ------------------------------------------------------------------------
  // Local file:// fallback for YouTube embeds (avoids YouTube Error 153)
  // ------------------------------------------------------------------------
  function initLocalYouTubeFallback() {
    if (window.location.protocol !== "file:") return;
    document.querySelectorAll(".video-frame[data-yt-id]").forEach((frame) => {
      const ytId = frame.getAttribute("data-yt-id");
      const ytUrl = frame.getAttribute("data-yt-url") || `https://youtu.be/${ytId}`;
      const ytTitle = frame.getAttribute("data-yt-title") || "Watch on YouTube";
      frame.innerHTML =
        `<a class="video-file-fallback" href="${ytUrl}" target="_blank" rel="noopener noreferrer" ` +
        `style="background-image: linear-gradient(rgba(8,11,18,0.45), rgba(8,11,18,0.65)), url('https://i.ytimg.com/vi/${ytId}/hqdefault.jpg');">` +
        `<span class="video-file-fallback-btn">&#9658; WATCH ON YOUTUBE &mdash; ${ytTitle}</span>` +
        `</a>`;
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initCopyButtons();
    initCopyTabs();
    initScreenshotFilters();
    initLightbox();
    initLogoSwatches();
    initScrollSpy();
    initLocalYouTubeFallback();
  });
})();
