/* Tola storefront + platform interactions. No dependencies (Swiper optional). */
(function () {
  "use strict";

  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  // Mobile menu
  var menuBtn = $("[data-menu-toggle]");
  if (menuBtn) {
    menuBtn.addEventListener("click", function () {
      var open = document.body.classList.toggle("nav-open");
      menuBtn.setAttribute("aria-expanded", String(open));
    });
  }

  // Expanding search
  $$("[data-search-toggle]").forEach(function (btn) {
    var form = btn.closest("form");
    var input = form && form.querySelector("input");
    btn.addEventListener("click", function () {
      if (form.classList.contains("is-open") && input.value.trim()) {
        form.submit();
        return;
      }
      form.classList.toggle("is-open");
      if (form.classList.contains("is-open")) input.focus();
    });
    input && input.addEventListener("keydown", function (e) {
      if (e.key === "Escape") form.classList.remove("is-open");
    });
  });

  // Quantity steppers; in the cart they submit the line form on change
  $$("[data-qty]").forEach(function (box) {
    var input = box.querySelector("input");
    var form = box.closest("form[data-autosubmit]");
    var min = parseInt(input.min || "0", 10);
    var max = parseInt(input.max || "99", 10);
    box.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-step]");
      if (!btn) return;
      var next = Math.min(max, Math.max(min, (parseInt(input.value, 10) || 0) + parseInt(btn.dataset.step, 10)));
      if (String(next) === input.value) return;
      input.value = next;
      if (form) form.submit();
    });
    if (form) input.addEventListener("change", function () { form.submit(); });
  });

  // Flash toasts
  $$("[data-toast]").forEach(function (toast, i) {
    var dismiss = function () {
      toast.classList.add("is-leaving");
      setTimeout(function () { toast.remove(); }, 350);
    };
    var btn = toast.querySelector("[data-toast-close]");
    btn && btn.addEventListener("click", dismiss);
    setTimeout(dismiss, 4500 + i * 400);
  });

  // Copy-to-clipboard: <button data-copy="https://...">
  $$("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var text = btn.dataset.copy;
      var label = btn.querySelector("[data-copy-label]");
      var done = function () {
        btn.classList.add("is-copied");
        if (label) { label.dataset.orig = label.dataset.orig || label.textContent; label.textContent = "Copied!"; }
        setTimeout(function () {
          btn.classList.remove("is-copied");
          if (label) label.textContent = label.dataset.orig;
        }, 1800);
      };
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(done);
      } else {
        var ta = document.createElement("textarea");
        ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
        document.body.appendChild(ta); ta.select();
        try { document.execCommand("copy"); done(); } catch (e) { /* ignore */ }
        ta.remove();
      }
    });
  });

  // Reveal on scroll
  var reveals = $$(".reveal");
  if ("IntersectionObserver" in window && reveals.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    reveals.forEach(function (el, i) {
      el.style.transitionDelay = (i % 4) * 70 + "ms";
      io.observe(el);
    });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-in"); });
  }

  // Hero slider (only when the owner has more than one banner)
  window.addEventListener("load", function () {
    var hero = $(".hero-swiper");
    if (!hero || !window.Swiper || parseInt(hero.dataset.slides, 10) < 2) return;
    new window.Swiper(hero, {
      loop: true,
      effect: "fade",
      fadeEffect: { crossFade: true },
      speed: 900,
      autoplay: { delay: 6000, disableOnInteraction: false },
      pagination: { el: hero.querySelector(".swiper-pagination"), clickable: true }
    });
  });
})();
