// Local-only demo session gate. There is no backend authentication
// endpoint in the API contract (docs/API_REFERENCE.md) - this exists so
// `Login.jsx` and route guarding have something real to do, not to
// simulate a genuine auth system. Never treat this as a security boundary.
const STORAGE_KEY = 'energyshield.analyst'

export function getAnalyst() {
  return localStorage.getItem(STORAGE_KEY)
}

export function isLoggedIn() {
  return Boolean(getAnalyst())
}

export function login(name) {
  localStorage.setItem(STORAGE_KEY, name || 'Analyst')
}

export function logout() {
  localStorage.removeItem(STORAGE_KEY)
}
