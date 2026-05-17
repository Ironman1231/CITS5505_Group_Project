function loadComponent(id, file) {
  fetch(file)
    .then(function(res) { return res.text(); })
    .then(function(html) {
      document.getElementById(id).innerHTML = html;
      // Highlight the active nav link based on the current page filename
      var page = window.location.pathname.split('/').pop() || 'index.html';
      var link = document.querySelector('#' + id + ' .nav-link[href="' + page + '"]');
      if (link) link.classList.add('active');
    });
}
