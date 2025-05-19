// static/admin/js/prefetch.js
function prefetchPage(url) {
    if (!document.querySelector(`link[href="${url}"]`)) {
      const link = document.createElement('link');
      link.rel = 'prefetch';
      link.href = url;
      link.as = 'document';
      document.head.appendChild(link);
    }
  }
  
  // Prefetch all admin <a> tags on hover
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('a').forEach(link => {
      const href = link.getAttribute('href');
      if (href && href.startsWith('/') && !href.startsWith('#')) {
        link.addEventListener('mouseover', () => prefetchPage(href));
      }
    });
  });
  