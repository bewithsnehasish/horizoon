// Track user behavior patterns
const adminNavHistory = [];
const PREDICTION_THRESHOLD = 0.7;

// Store the current page content
let cachedPages = {};

// Background fetch with proper headers
async function backgroundFetch(url) {
  try {
    const response = await fetch(url, {
      credentials: 'include',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-Prefetch': 'true'
      }
    });
    if (response.ok) {
      return await response.text();
    }
  } catch (e) {
    console.log('Background fetch failed silently');
  }
  return null;
}

// Predict next likely page
function predictNextPage() {
  const currentPath = window.location.pathname;
  const similarPaths = adminNavHistory.filter(p => p.from === currentPath);
  
  if (similarPaths.length > 3) {
    const nextPages = {};
    similarPaths.forEach(entry => {
      nextPages[entry.to] = (nextPages[entry.to] || 0) + 1;
    });
    
    const sorted = Object.entries(nextPages).sort((a, b) => b[1] - a[1]);
    if (sorted[0][1] / similarPaths.length > PREDICTION_THRESHOLD) {
      return sorted[0][0];
    }
  }
  return null;
}

// Main prediction logic
async function runPredictionEngine() {
  const nextPage = predictNextPage();
  if (nextPage && !cachedPages[nextPage]) {
    console.log('Predictively loading:', nextPage);
    cachedPages[nextPage] = await backgroundFetch(nextPage);
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  // Record navigation history
  window.addEventListener('popstate', () => {
    adminNavHistory.push({
      from: document.referrer,
      to: window.location.pathname
    });
  });

  // Setup link tracking
  document.body.addEventListener('click', (e) => {
    const link = e.target.closest('a[href^="/admin/"]');
    if (link) {
      adminNavHistory.push({
        from: window.location.pathname,
        to: link.getAttribute('href')
      });
    }
  }, true);

  // Run prediction every 30s
  setInterval(runPredictionEngine, 30000);
  
  // Also run on mouse movement patterns
  document.addEventListener('mousemove', _.debounce(runPredictionEngine, 1000));
});

// Instant page switch for predicted pages
document.addEventListener('click', async (e) => {
  const link = e.target.closest('a[href^="/admin/"]');
  if (link && cachedPages[link.href]) {
    e.preventDefault();
    document.documentElement.style.opacity = '0.7';
    document.body.innerHTML = cachedPages[link.href];
    history.pushState({}, '', link.href);
    document.documentElement.style.opacity = '1';
  }
}, true);