(function () {
  "use strict";

  var HLS_SRC = "https://cdnjs.cloudflare.com/ajax/libs/hls.js/1.5.20/hls.light.min.js";
  var HLS_SRI = "sha384-GMRZjjumhWPywgLYrubnh5qVhHY0BpD+pxIL57uwAenrOEYDLZ/z+8s/rFIjS+yO";
  var STEAM_URL = "https://store.steampowered.com/app/5155360/Hood_Warfare_2/";
  var DISMISS_KEY = "hw2-lang-dismissed";

  function storageGet(key) {
    try { return window.localStorage.getItem(key); } catch (e) { return null; }
  }
  function storageSet(key, value) {
    try { window.localStorage.setItem(key, value); } catch (e) { /* storage unavailable */ }
  }

  // Map a browser language tag to one of the site's language codes.
  function matchLang(tag, available) {
    var t = String(tag || "").toLowerCase();
    if (t.indexOf("zh") === 0) {
      var traditional = /hant|tw|hk|mo/.test(t);
      return traditional ? "zh-tw" : "zh";
    }
    if (t.indexOf("pt") === 0) return "pt-br";
    var base = t.split("-")[0];
    return available.indexOf(base) >= 0 ? base : null;
  }

  // A manual language choice counts as an answer: stop suggesting another one.
  function rememberManualChoice() {
    var links = document.querySelectorAll(".lang-menu a, .foot-langs a");
    Array.prototype.forEach.call(links, function (link) {
      link.addEventListener("click", function () { storageSet(DISMISS_KEY, "1"); });
    });
  }

  function suggestLanguage() {
    var node = document.getElementById("lang-data");
    var bar = document.getElementById("lang-suggest");
    if (!node || !bar || storageGet(DISMISS_KEY)) return;
    var data;
    try { data = JSON.parse(node.textContent); } catch (e) { return; }
    var available = Object.keys(data.langs);
    var prefs = navigator.languages || [navigator.language];
    var best = null;
    for (var i = 0; i < prefs.length && !best; i++) best = matchLang(prefs[i], available);
    if (!best || best === data.current || !data.langs[best]) return;
    var target = data.langs[best];
    var wrap = document.createElement("div");
    wrap.className = "wrap";
    wrap.lang = target.html;
    var text = document.createElement("p");
    text.textContent = target.suggest.replace("{lang}", target.name);
    var link = document.createElement("a");
    link.href = target.url;
    link.hreflang = target.html;
    link.textContent = target.go.replace("{lang}", target.name);
    var close = document.createElement("button");
    close.type = "button";
    close.textContent = target.close;
    close.addEventListener("click", function () {
      storageSet(DISMISS_KEY, "1");
      bar.hidden = true;
    });
    link.addEventListener("click", function () { storageSet(DISMISS_KEY, "1"); });
    wrap.appendChild(text);
    wrap.appendChild(link);
    wrap.appendChild(close);
    bar.appendChild(wrap);
    bar.hidden = false;
  }

  // Show "3 hours ago" style times in the page language.
  function relativeTimes() {
    if (!window.Intl || !Intl.RelativeTimeFormat) return;
    var fmt = new Intl.RelativeTimeFormat(document.documentElement.lang, { numeric: "auto" });
    var nodes = document.querySelectorAll("time[data-rel]");
    Array.prototype.forEach.call(nodes, function (node) {
      var when = new Date(node.getAttribute("datetime"));
      var minutes = Math.round((when - Date.now()) / 60000);
      if (isNaN(minutes)) return;
      var abs = Math.abs(minutes);
      var label = abs < 60 ? fmt.format(minutes, "minute")
        : abs < 60 * 48 ? fmt.format(Math.round(minutes / 60), "hour")
        : fmt.format(Math.round(minutes / 1440), "day");
      node.title = node.textContent;
      node.textContent = label;
    });
  }

  function loadScript(src, integrity) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = src;
      s.integrity = integrity;
      s.crossOrigin = "anonymous";
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  function setupTrailer() {
    var box = document.querySelector(".trailer[data-hls]");
    if (!box) return;
    var button = box.querySelector(".play");
    button.addEventListener("click", function () {
      var src = box.getAttribute("data-hls");
      var video = document.createElement("video");
      video.controls = true;
      video.playsInline = true;
      video.setAttribute("aria-label", button.textContent.trim());
      box.innerHTML = "";
      box.appendChild(video);
      video.focus();
      if (video.canPlayType("application/vnd.apple.mpegurl")) {
        video.src = src;
        video.play().catch(function () {});
        return;
      }
      loadScript(HLS_SRC, HLS_SRI).then(function () {
        if (!window.Hls || !window.Hls.isSupported()) throw new Error("HLS unsupported");
        var hls = new window.Hls();
        hls.loadSource(src);
        hls.attachMedia(video);
        hls.on(window.Hls.Events.MANIFEST_PARSED, function () { video.play().catch(function () {}); });
        hls.on(window.Hls.Events.ERROR, function (event, data) {
          if (data && data.fatal) window.location.href = STEAM_URL;
        });
      }).catch(function () {
        window.location.href = STEAM_URL;
      });
    });
  }

  // Close the language menu when clicking elsewhere or pressing Escape.
  function setupMenus() {
    var menu = document.querySelector(".lang-menu");
    if (!menu) return;
    document.addEventListener("click", function (e) {
      if (menu.open && !menu.contains(e.target)) menu.open = false;
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.open) {
        menu.open = false;
        menu.querySelector("summary").focus();
      }
    });
  }

  rememberManualChoice();
  suggestLanguage();
  relativeTimes();
  setupTrailer();
  setupMenus();
})();
