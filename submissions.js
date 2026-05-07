// SceneSeed — public audience-submission helpers
//
// The submission window is enforced server-side by Firestore rules, not by this
// code. Everything here is UX preview + a friendlier error story.
//
// Duplicate prevention works through deterministic doc IDs:
//   /events/{publicCode}/suggestions/{hash(textNormalized)}
// A duplicate write hits an existing doc, which the create rule won't authorize
// for unauthed clients — but we also do an optimistic getDoc first to surface
// a precise "duplicate" error.

import { db } from './firebase-config.js';
import {
  doc, getDoc, setDoc, serverTimestamp
} from 'https://www.gstatic.com/firebasejs/12.12.1/firebase-firestore.js';

// Normalize text for dedup key:
//   - lowercase
//   - strip punctuation/symbols (keep letters, numbers, spaces)
//   - collapse whitespace
//   - trim ends
export function normalize(text) {
  return String(text || '')
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s]/gu, '')
    .replace(/\s+/g, ' ')
    .trim();
}

// SHA-256 over the normalized text, returning the first 16 hex chars (64 bits).
// 64 bits of entropy gives a vanishing collision rate at any plausible scale.
export async function hashText(text) {
  const buf = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest('SHA-256', buf);
  return Array.from(new Uint8Array(digest))
    .slice(0, 8)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

// Submit a suggestion. Throws an Error with .code === 'duplicate' on dup,
// .code === 'denied' on any other rule rejection, .code === 'empty' on no text.
//
// Audience names: when the show's nameCollection is 'optional' or 'required',
// the audience page passes a submitterName. We always write the field as a
// string (empty if not provided) so the rule can validate it uniformly.
export async function submitSuggestion(publicCode, rawText, rawName = '') {
  const text = String(rawText || '').trim();
  if (!text) {
    const e = new Error('Empty suggestion');
    e.code = 'empty';
    throw e;
  }
  const textNormalized = normalize(text);
  if (!textNormalized) {
    const e = new Error('Suggestion is just punctuation');
    e.code = 'empty';
    throw e;
  }

  // Names are kept short and stripped of leading/trailing whitespace; the
  // rule caps total length at 50 chars but we trim earlier to be friendly.
  const submitterName = String(rawName || '').trim().slice(0, 50);

  const hash = await hashText(textNormalized);
  const ref = doc(db, 'events', publicCode, 'suggestions', hash);

  // Optimistic dup check (rule allows public get on suggestion docs).
  try {
    const existing = await getDoc(ref);
    if (existing.exists()) {
      const e = new Error('Duplicate suggestion');
      e.code = 'duplicate';
      throw e;
    }
  } catch (err) {
    if (err.code === 'duplicate') throw err;
    // Fall through — if the get failed for some other reason, still try the write.
  }

  try {
    await setDoc(ref, {
      text,
      textNormalized,
      submitterName,
      isFavorite: false,
      isHidden: false,
      isUsed: false,
      createdAt: serverTimestamp()
    });
  } catch (err) {
    // Firestore returns "permission-denied" for any rule failure (window closed,
    // length over limit, name required but empty, etc). We surface a single
    // generic state and let the UI tell the user the window state if relevant.
    const e = new Error(err.message || 'Submission rejected');
    e.code = 'denied';
    e.cause = err;
    throw e;
  }
}
