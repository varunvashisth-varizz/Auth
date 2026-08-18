// Shared helpers used by login.html / register.html / dashboard.html.
// Kept framework-free per the "clean HTML/CSS/JS" requirement.

const TOKEN_KEY = "auth_access_token";

const AuthStore = {
  setToken(token) {
    sessionStorage.setItem(TOKEN_KEY, token);
  },
  getToken() {
    return sessionStorage.getItem(TOKEN_KEY);
  },
  clearToken() {
    sessionStorage.removeItem(TOKEN_KEY);
  },
};

function showMessage(el, text, type = "error") {
  el.textContent = text;
  el.className = `message ${type}`;
}

function hideMessage(el) {
  el.className = "message";
  el.textContent = "";
}

/**
 * Normalizes FastAPI's error shapes:
 * - {"detail": "Some string"}
 * - {"detail": [{"msg": "...", "loc": [...]}, ...]}  (422 validation errors)
 */
function extractErrorMessage(payload, fallback = "Something went wrong.") {
  if (!payload) return fallback;
  const detail = payload.detail;
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => (d && d.msg ? d.msg : JSON.stringify(d)))
      .join(" ");
  }
  return fallback;
}

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  let data = null;
  try {
    data = await res.json();
  } catch (e) {
    /* no body */
  }
  return { ok: res.ok, status: res.status, data };
}

async function postForm(url, formData) {
  const res = await fetch(url, {
    method: "POST",
    body: formData,
  });
  let data = null;
  try {
    data = await res.json();
  } catch (e) {
    /* no body */
  }
  return { ok: res.ok, status: res.status, data };
}
