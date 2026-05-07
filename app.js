// SceneSeed — main app entry
// v0.1.0: landing page only. Auth + dashboard land in v0.2.0.

import { auth } from './firebase-config.js';
import { onAuthStateChanged } from 'https://www.gstatic.com/firebasejs/12.12.1/firebase-auth.js';

const ctaBtn = document.getElementById('cta-signin');

onAuthStateChanged(auth, (user) => {
  if (!ctaBtn) return;
  if (user) {
    ctaBtn.textContent = 'Open dashboard';
    ctaBtn.dataset.signedIn = 'true';
  } else {
    ctaBtn.textContent = 'Sign in to host a show';
    ctaBtn.dataset.signedIn = 'false';
  }
});

ctaBtn?.addEventListener('click', (e) => {
  e.preventDefault();
  // Auth UI lands in v0.2.0
  alert('Sign-in is shipping in v0.2.0. Hold tight.');
});
