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
