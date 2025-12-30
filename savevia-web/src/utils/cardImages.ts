/**
 * Card Image URL Generator
 * Automatically generates CDN image URLs based on bank + card name
 * Images hosted on: https://savevia.app/card-images/
 *
 * Naming convention: {bank}-{card-name}.png
 * Example: AMEX + Cobalt Card → amex-cobalt-card.png
 */

const CDN_BASE = 'https://savevia.app/card-images'

// Bank name normalization (for banks with different display names)
const BANK_ALIASES: Record<string, string> = {
  'American Express': 'amex',
  'PC Financial': 'pc-financial',
  'Home Trust': 'home-trust',
  'Canadian Tire': 'canadian-tire',
  'Coast Capital': 'coast-capital',
  'National Bank': 'national-bank',
}

// Special filename overrides (for non-.png files or special naming)
const FILENAME_OVERRIDES: Record<string, string> = {
  // Different file extensions
  'TD|Cash Back Visa Infinite': 'td-cash-back-visa-infinite.jpeg',
  'RBC|Avion Visa Infinite': 'rbc-avion-visa-infinite.webp',
  'RBC|Avion Visa Infinite Privilege': 'rbc-avion-visa-infinite-privilege.webp',
  'RBC|WestJet World Elite Mastercard': 'rbc-westjet-world-elite-mastercard.webp',
  'RBC|Cash Back Mastercard': 'rbc-cash-back-mastercard.webp',
  'Neo|World Elite Mastercard': 'neo-world-elite-mastercard.webp',
  'Neo|World Mastercard': 'neo-world-mastercard.webp',
  // Special character handling
  'Scotiabank|Scene+ Visa': 'scotiabank-scene-visa.png',
  'RBC|ION+ Visa': 'rbc-ion-plus-visa.png',
  'MBNA|Amazon.ca Rewards Mastercard': 'mbna-amazonca-rewards-mastercard.png',
}

/**
 * Generate filename from bank and card name
 * Converts to lowercase, replaces spaces with hyphens, removes special chars
 */
function generateFilename(bank: string, cardName: string): string {
  // Normalize bank name
  const normalizedBank = (BANK_ALIASES[bank] || bank)
    .toLowerCase()
    .replace(/\s+/g, '-')

  // Normalize card name: lowercase, replace spaces, handle special chars
  const normalizedCard = cardName
    .toLowerCase()
    .replace(/\+/g, '-plus')      // + → -plus
    .replace(/\./g, '')            // Remove dots
    .replace(/['']/g, '')          // Remove apostrophes
    .replace(/&/g, '-and-')        // & → -and-
    .replace(/\s+/g, '-')          // Spaces → hyphens
    .replace(/-+/g, '-')           // Multiple hyphens → single
    .replace(/[^a-z0-9-]/g, '')    // Remove other special chars

  return `${normalizedBank}-${normalizedCard}.png`
}

/**
 * Get card image URL from CDN
 * @param bank - Bank name (e.g., "AMEX", "TD")
 * @param cardName - Card name (e.g., "Cobalt Card", "Cash Back Visa Infinite")
 * @returns CDN URL (always returns a URL, CardImage component handles 404)
 */
export function getCardImageUrl(bank: string, cardName: string): string {
  const key = `${bank}|${cardName}`

  // Check for override first (special filenames or extensions)
  const override = FILENAME_OVERRIDES[key]
  if (override) {
    return `${CDN_BASE}/${override}`
  }

  // Generate filename automatically
  const filename = generateFilename(bank, cardName)
  return `${CDN_BASE}/${filename}`
}

/**
 * Check if card has an image available (always true now, actual check is done on load)
 */
export function hasCardImage(_bank: string, _cardName: string): boolean {
  return true // Always return true, let the image component handle 404
}

// Track failed and loaded card images
export const failedImages = new Set<string>()
export const loadedImages = new Set<string>()

/**
 * Clear card image cache (loaded and failed images tracking)
 */
export function clearCardImageCache(): void {
  failedImages.clear()
  loadedImages.clear()
}
