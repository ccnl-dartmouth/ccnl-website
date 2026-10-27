// Email addresses are written as "user [at] domain" in the HTML so scrapers do not see a mailto link.
// Turn them into real mailto links in the browser.
document.querySelectorAll('.email').forEach(function (el) {
  var address = el.dataset.user + '@' + el.dataset.domain;
  var link = document.createElement('a');
  link.href = 'mailto:' + address;
  link.textContent = address;
  el.replaceWith(link);
});
