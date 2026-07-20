// Turns backend SCREAMING_SNAKE_CASE enum values (event types, risk levels,
// scenario types, commodity types, entity types, action priorities, etc.)
// into human-readable labels for display, without touching the raw values
// used for lookups/keys/CSS class selection.

// Acronyms and proper nouns that must not be title-cased word-by-word.
const WORD_OVERRIDES = {
  ais: 'AIS',
  spr: 'SPR',
  opec: 'OPEC+',
  lng: 'LNG',
  id: 'ID',
  us: 'US',
  uk: 'UK',
  uae: 'UAE',
  eu: 'EU',
}

function humanizeWord(word) {
  const lower = word.toLowerCase()
  return WORD_OVERRIDES[lower] ?? word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
}

// humanize('MARITIME_ATTACK') -> 'Maritime Attack'
// humanize('OPEC_SUPPLY_CUT') -> 'OPEC+ Supply Cut'
// humanize('SHIPPING_ROUTE') -> 'Shipping Route'
export function humanize(value) {
  if (value === null || value === undefined || value === '') return ''
  return String(value)
    .split(/[_\s]+/)
    .filter(Boolean)
    .map(humanizeWord)
    .join(' ')
}

// PascalCase graph labels (e.g. 'ShippingRoute', 'SupplierCountry') -> 'Shipping Route'
export function humanizeLabel(value) {
  if (!value) return ''
  return humanize(String(value).replace(/([a-z0-9])([A-Z])/g, '$1_$2').toUpperCase())
}
