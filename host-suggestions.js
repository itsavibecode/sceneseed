// SceneSeed — host-side suggestions data layer
//
// This module is the HOST counterpart to submissions.js (which is for the
// audience). Host can list every suggestion under a show, toggle favorite/
// hidden/used flags, and delete. All access is gated by the Firestore rules:
//   - list: requires authed event-owner
//   - update/delete: requires authed event-owner
//
// Suggestions live at /events/{publicCode}/suggestions/{hash}.

import { db } from './firebase-config.js';
import {
  collection, doc, onSnapshot, updateDoc, deleteDoc
} from 'https://www.gstatic.com/firebasejs/12.12.1/firebase-firestore.js';

// Live subscription to all suggestions under a show, sorted newest first
// client-side (avoids needing a composite index).
// Returns an unsubscribe function.
export function listSuggestions(publicCode, callback) {
  const ref = collection(db, 'events', publicCode, 'suggestions');
  return onSnapshot(
    ref,
    (snap) => {
      const list = snap.docs.map((d) => ({ id: d.id, ...d.data() }));
      list.sort((a, b) => {
        const aT = a.createdAt?.toMillis?.() ?? 0;
        const bT = b.createdAt?.toMillis?.() ?? 0;
        return bT - aT;
      });
      callback(list);
    },
    (err) => {
      console.error('Failed to load suggestions:', err);
      callback([]);
    }
  );
}

const ALLOWED_FLAGS = new Set(['isFavorite', 'isHidden', 'isUsed']);

export async function setSuggestionFlag(publicCode, hash, flag, value) {
  if (!ALLOWED_FLAGS.has(flag)) {
    throw new Error(`Unknown suggestion flag: ${flag}`);
  }
  await updateDoc(doc(db, 'events', publicCode, 'suggestions', hash), {
    [flag]: !!value
  });
}

export async function deleteSuggestion(publicCode, hash) {
  await deleteDoc(doc(db, 'events', publicCode, 'suggestions', hash));
}
