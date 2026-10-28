// Email addresses are written as "user [at] domain" in the HTML so scrapers do not see a mailto link.
// Turn them into real mailto links in the browser.
document.querySelectorAll('.email').forEach(function (el) {
  var address = el.dataset.user + '@' + el.dataset.domain;
  var link = document.createElement('a');
  link.href = 'mailto:' + address;
  link.textContent = address;
  el.replaceWith(link);
});

// Open a collapsed section when the page is opened (or the link is followed) with its #id,
// e.g. /resources/#teaching.
function openSectionFromHash() {
  var el = location.hash && document.getElementById(location.hash.slice(1));
  if (el && el.tagName === 'DETAILS') { el.open = true; el.scrollIntoView(); }
}
openSectionFromHash();
window.addEventListener('hashchange', openSectionFromHash);

// Publications page: one search box over every BibTeX field. Every word typed must appear somewhere in a paper.
// Years with no matching paper (and their links at the top) are hidden. Without JavaScript the box stays hidden.
(function () {
  var input = document.getElementById('pub-q');
  if (!input) return;
  var form = input.form, clear = form.querySelector('.pub-clear');
  var papers = Array.prototype.slice.call(document.querySelectorAll('.pubs-page .pub'));
  var groups = Array.prototype.slice.call(document.querySelectorAll('.pubs-page .pub-year'));
  var count = document.getElementById('pub-count'), none = document.getElementById('pub-none');
  form.hidden = false;
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  function update() {
    var terms = input.value.toLowerCase().split(/\s+/).filter(Boolean), shown = 0;
    papers.forEach(function (li) {
      var text = li.dataset.search.toLowerCase();
      var match = terms.every(function (t) { return text.indexOf(t) !== -1; });
      li.hidden = !match;
      if (match) shown++;
    });
    groups.forEach(function (g) {
      var any = g.querySelector('.pub:not([hidden])') !== null;
      g.hidden = !any;
      var link = document.querySelector('.year-nav a[href="#' + g.id + '"]');
      if (link) link.hidden = !any;
    });
    clear.hidden = terms.length === 0;
    none.hidden = shown !== 0;
    count.textContent = terms.length ? shown + ' of ' + papers.length + ' papers' : papers.length + ' papers';
  }
  input.addEventListener('input', update);
  clear.addEventListener('click', function () { input.value = ''; update(); input.focus(); });
  update();
})();
