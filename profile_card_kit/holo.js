/* Runs only when the SVG is opened directly / hosted (GitHub Pages, <object>, browser tab).
   GitHub README embeds SVG as <img>, where scripts are disabled - the card then uses the CSS auto-sway instead. */
(function () {
  var g = document.getElementById('holo'), s = document.getElementById('hstack'),
      a = document.getElementById('gA'), b = document.getElementById('gB');
  if (!g || !s) return;
  function move(e) {
    var r = g.getBoundingClientRect();
    var nx = ((e.clientX - r.left) / r.width) * 2 - 1, ny = ((e.clientY - r.top) / r.height) * 2 - 1;
    nx = Math.max(-1, Math.min(1, nx)); ny = Math.max(-1, Math.min(1, ny));
    s.style.animation = a.style.animation = b.style.animation = 'none';
    s.style.transform = 'scale(' + (1.12 - 0.08 * Math.abs(nx)) + ',' + (1.08 + 0.02 * Math.abs(ny)) + ') skewY(' + (nx * -2.2) + 'deg)';
    a.style.transform = 'translate(' + (nx * -7) + 'px,' + (ny * -4) + 'px)';
    b.style.transform = 'translate(' + (nx * 7) + 'px,' + (ny * 4) + 'px)';
  }
  function leave() {
    s.style.animation = a.style.animation = b.style.animation = '';
    s.style.transform = a.style.transform = b.style.transform = '';
  }
  g.addEventListener('mousemove', move);
  g.addEventListener('mouseleave', leave);
})();
