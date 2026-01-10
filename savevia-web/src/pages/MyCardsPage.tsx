import { useState, useRef, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { PlusOutlined, RightOutlined, CreditCardOutlined, DeleteOutlined, CheckOutlined } from '@ant-design/icons'
import { useOptimizerStore } from '../stores/useOptimizerStore'
import type { CreditCard } from '../types'
import { getCardImageUrl, failedImages, loadedImages } from '../utils/cardImages'

// Default card style fallback
const DEFAULT_CARD_STYLE = { gradient: 'linear-gradient(135deg, #374151 0%, #1f2937 100%)', textColor: 'white' }

// Bank fallback colors
const BANK_FALLBACK_COLORS: Record<string, { gradient: string; textColor: string }> = {
  'AMEX': { gradient: 'linear-gradient(135deg, #016fd0 0%, #004080 100%)', textColor: 'white' },
  'American Express': { gradient: 'linear-gradient(135deg, #016fd0 0%, #004080 100%)', textColor: 'white' },
  'TD': { gradient: 'linear-gradient(135deg, #34a853 0%, #1e7e34 100%)', textColor: 'white' },
  'RBC': { gradient: 'linear-gradient(135deg, #003168 0%, #001a3a 100%)', textColor: 'white' },
  'Scotiabank': { gradient: 'linear-gradient(135deg, #ec111a 0%, #b30d14 100%)', textColor: 'white' },
  'CIBC': { gradient: 'linear-gradient(135deg, #8b1538 0%, #6b1029 100%)', textColor: 'white' },
  'BMO': { gradient: 'linear-gradient(135deg, #0079c1 0%, #005a91 100%)', textColor: 'white' },
  'Rogers': { gradient: 'linear-gradient(135deg, #e31837 0%, #b8132c 100%)', textColor: 'white' },
  'Tangerine': { gradient: 'linear-gradient(135deg, #ff6600 0%, #cc5200 100%)', textColor: 'white' },
  'Neo': { gradient: 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)', textColor: 'white' },
  'PC Financial': { gradient: 'linear-gradient(135deg, #e31837 0%, #b8132c 100%)', textColor: 'white' },
  'Simplii': { gradient: 'linear-gradient(135deg, #ff6600 0%, #e65c00 100%)', textColor: 'white' },
  'MBNA': { gradient: 'linear-gradient(135deg, #1a1a1a 0%, #333333 100%)', textColor: 'white' },
  'National Bank': { gradient: 'linear-gradient(135deg, #e31837 0%, #b8132c 100%)', textColor: 'white' },
  'Home Trust': { gradient: 'linear-gradient(135deg, #1e3a5f 0%, #152a45 100%)', textColor: 'white' },
}

// Parse card style from imageUrl JSON or use fallback
function getCardStyle(card: CreditCard) {
  if (card.imageUrl) {
    try {
      const parsed = JSON.parse(card.imageUrl)
      if (parsed.gradient && parsed.textColor) {
        return { gradient: parsed.gradient, textColor: parsed.textColor }
      }
    } catch {
      // Not JSON, ignore
    }
  }
  return BANK_FALLBACK_COLORS[card.bank] || DEFAULT_CARD_STYLE
}

// Get max reward rate for a card
function getMaxRewardRate(card: CreditCard): number {
  if (!card.rewardRules || card.rewardRules.length === 0) {
    return card.baseRewardRate || 0
  }
  const maxRule = Math.max(...card.rewardRules.map(r => r.rewardRate))
  return Math.max(maxRule, card.baseRewardRate || 0)
}

// Use real card images setting
function useRealCardImages() {
  const stored = localStorage.getItem('sv_realCardImages')
  return stored === 'true'
}

// Swipeable card item component
function SwipeableCardItem({
  card,
  onRemove,
  realCardImages,
  isEditMode,
  isSelected,
  onToggleSelect
}: {
  card: CreditCard
  onRemove: (id: number) => void
  realCardImages: boolean
  isEditMode: boolean
  isSelected: boolean
  onToggleSelect: (id: number) => void
}) {
  const { t } = useTranslation()
  const [offsetX, setOffsetX] = useState(0)
  const [isSwiping, setIsSwiping] = useState(false)
  const contentRef = useRef<HTMLDivElement>(null)

  // Use refs to track touch state (avoid stale closure issues)
  const touchState = useRef({
    startX: 0,
    startY: 0,
    direction: null as 'horizontal' | 'vertical' | null,
    currentOffsetX: 0
  })

  const style = getCardStyle(card)
  const maxRate = getMaxRewardRate(card)
  const imageKey = `${card.bank}|${card.name}`
  const cardImageUrl = realCardImages && !failedImages.has(imageKey) ? getCardImageUrl(card.bank, card.name) : null

  const DELETE_THRESHOLD = 80
  const DIRECTION_LOCK_THRESHOLD = 10 // Minimum movement to determine direction

  const handleTouchStart = useCallback((e: TouchEvent) => {
    if (isEditMode) return
    touchState.current.startX = e.touches[0].clientX
    touchState.current.startY = e.touches[0].clientY
    touchState.current.direction = null
    setIsSwiping(true)
  }, [isEditMode])

  const handleTouchMove = useCallback((e: TouchEvent) => {
    if (isEditMode) return

    const currentX = e.touches[0].clientX
    const currentY = e.touches[0].clientY
    const diffX = touchState.current.startX - currentX
    const diffY = currentY - touchState.current.startY

    // Determine swipe direction if not yet locked
    if (touchState.current.direction === null) {
      const absDiffX = Math.abs(diffX)
      const absDiffY = Math.abs(diffY)

      // Only lock direction after moving past threshold
      if (absDiffX > DIRECTION_LOCK_THRESHOLD || absDiffY > DIRECTION_LOCK_THRESHOLD) {
        touchState.current.direction = absDiffX > absDiffY ? 'horizontal' : 'vertical'
      }
      return // Don't update offset until direction is determined
    }

    // If vertical swipe, let it scroll normally
    if (touchState.current.direction === 'vertical') {
      return
    }

    // Horizontal swipe - prevent vertical scroll and update offset
    if (touchState.current.direction === 'horizontal') {
      e.preventDefault() // This works because we set passive: false
      if (diffX > 0) {
        const newOffset = Math.min(diffX, DELETE_THRESHOLD)
        touchState.current.currentOffsetX = newOffset
        setOffsetX(newOffset)
      } else {
        touchState.current.currentOffsetX = 0
        setOffsetX(0)
      }
    }
  }, [isEditMode])

  const handleTouchEnd = useCallback(() => {
    if (isEditMode) return
    setIsSwiping(false)
    const finalOffset = touchState.current.currentOffsetX
    if (finalOffset >= DELETE_THRESHOLD * 0.6) {
      setOffsetX(DELETE_THRESHOLD)
    } else {
      setOffsetX(0)
    }
    touchState.current.direction = null
    touchState.current.currentOffsetX = 0
  }, [isEditMode])

  // Use native event listeners with passive: false to allow preventDefault
  useEffect(() => {
    const element = contentRef.current
    if (!element || isEditMode) return

    element.addEventListener('touchstart', handleTouchStart, { passive: true })
    element.addEventListener('touchmove', handleTouchMove, { passive: false })
    element.addEventListener('touchend', handleTouchEnd, { passive: true })

    return () => {
      element.removeEventListener('touchstart', handleTouchStart)
      element.removeEventListener('touchmove', handleTouchMove)
      element.removeEventListener('touchend', handleTouchEnd)
    }
  }, [isEditMode, handleTouchStart, handleTouchMove, handleTouchEnd])

  const handleDelete = () => {
    onRemove(card.id)
  }

  const resetSwipe = () => {
    setOffsetX(0)
  }

  const handleItemClick = () => {
    if (isEditMode) {
      onToggleSelect(card.id)
    } else if (offsetX > 0) {
      resetSwipe()
    }
  }

  return (
    <div className="sv-swipe-container">
      {/* Delete button behind */}
      {!isEditMode && (
        <div
          className="sv-swipe-delete"
          style={{ opacity: offsetX / DELETE_THRESHOLD }}
          onClick={handleDelete}
        >
          <DeleteOutlined />
          <span>{t('common.delete')}</span>
        </div>
      )}

      {/* Card content */}
      <div
        ref={contentRef}
        className="sv-swipe-content"
        style={{
          transform: isEditMode ? 'none' : `translateX(-${offsetX}px)`,
          transition: isSwiping ? 'none' : 'transform 0.2s ease'
        }}
        onClick={handleItemClick}
      >
        <div className="sv-mycards-row">
          {/* Edit mode checkbox - outside the card item */}
          {isEditMode && (
            <div className={`sv-mycards-checkbox ${isSelected ? 'checked' : ''}`}>
              {isSelected && <CheckOutlined />}
            </div>
          )}

          <div className={`sv-card-list-item ${isEditMode && isSelected ? 'editing-selected' : ''}`}>
            {/* Card thumbnail */}
          <div
            className="sv-card-list-thumbnail"
            style={{ background: style.gradient }}
          >
            {cardImageUrl && (
              <img
                src={cardImageUrl}
                alt={card.name}
                loading="lazy"
                onLoad={(e) => {
                  loadedImages.add(imageKey)
                  ;(e.target as HTMLImageElement).style.opacity = '1'
                }}
                onError={(e) => {
                  failedImages.add(imageKey)
                  ;(e.target as HTMLImageElement).style.display = 'none'
                }}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  opacity: loadedImages.has(imageKey) ? 1 : 0,
                  transition: 'opacity 0.2s ease'
                }}
              />
            )}
          </div>

          {/* Card info - click to go to detail (disabled in edit mode) */}
          {isEditMode ? (
            <div className="sv-card-list-info">
              <div className="sv-card-list-name">{card.name}</div>
              <div className="sv-card-list-meta">
                <span className="sv-card-list-fee">
                  {card.annualFee === 0 ? t('cardDetail.noFee') : `$${card.annualFee}${t('common.perYear')}`}
                </span>
                <span className="sv-card-list-type">
                  {card.rewardType === 'POINTS' ? t('cards.points') : t('cards.cashback')}
                </span>
                <span className="sv-card-list-best">
                  {t('myCards.upTo')} {(maxRate * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          ) : (
            <Link
              to={`/cards/${card.id}`}
              state={{ card }}
              className="sv-card-list-link"
              onClick={(e) => offsetX > 0 && e.preventDefault()}
            >
              <div className="sv-card-list-info">
                <div className="sv-card-list-name">{card.name}</div>
                <div className="sv-card-list-meta">
                  <span className="sv-card-list-fee">
                    {card.annualFee === 0 ? t('cardDetail.noFee') : `$${card.annualFee}${t('common.perYear')}`}
                  </span>
                  <span className="sv-card-list-type">
                    {card.rewardType === 'POINTS' ? t('cards.points') : t('cards.cashback')}
                  </span>
                  <span className="sv-card-list-best">
                    {t('myCards.upTo')} {(maxRate * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
              <RightOutlined className="sv-card-list-arrow" />
            </Link>
          )}
          </div>
        </div>
      </div>
    </div>
  )
}

function MyCardsPage() {
  const { t } = useTranslation()
  const { selectedCards, removeCard } = useOptimizerStore()
  const realCardImages = useRealCardImages()
  const [isEditMode, setIsEditMode] = useState(false)
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set())

  const toggleEditMode = () => {
    if (isEditMode) {
      setSelectedIds(new Set())
    }
    setIsEditMode(!isEditMode)
  }

  const toggleSelect = (id: number) => {
    setSelectedIds(prev => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  const selectAll = () => {
    if (selectedIds.size === selectedCards.length) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(new Set(selectedCards.map(c => c.id)))
    }
  }

  const deleteSelected = () => {
    selectedIds.forEach(id => removeCard(id))
    setSelectedIds(new Set())
    if (selectedCards.length - selectedIds.size === 0) {
      setIsEditMode(false)
    }
  }

  // Empty state
  if (selectedCards.length === 0) {
    return (
      <div className="sv-mycards-page">
        <div className="sv-mycards-empty">
          <CreditCardOutlined className="sv-mycards-empty-icon" />
          <h2>{t('myCards.emptyTitle')}</h2>
          <p>{t('myCards.emptyDesc')}</p>
          <Link to="/cards" className="sv-mycards-add-btn">
            <PlusOutlined />
            {t('myCards.addCards')}
          </Link>
        </div>

        <style>{styles}</style>
      </div>
    )
  }

  const isAllSelected = selectedIds.size === selectedCards.length

  return (
    <div className="sv-mycards-page">
      {/* Header */}
      <div className="sv-mycards-header">
        <h1>{t('myCards.title')}</h1>
        <div className="sv-mycards-header-right">
          {!isEditMode && (
            <span className="sv-mycards-count">{selectedCards.length} {t('myCards.cards')}</span>
          )}
          <button className="sv-mycards-edit-btn" onClick={toggleEditMode}>
            {isEditMode ? t('common.done') : t('common.edit')}
          </button>
        </div>
      </div>

      {/* Select All - shown in edit mode above the list */}
      {isEditMode && (
        <button className="sv-mycards-select-all" onClick={selectAll}>
          <div className={`sv-mycards-checkbox ${isAllSelected ? 'checked' : ''}`}>
            {isAllSelected && <CheckOutlined />}
          </div>
          <span>{t('common.selectAll')}</span>
        </button>
      )}

      {/* Cards List */}
      <div className="sv-mycards-list">
        {selectedCards.map(card => (
          <SwipeableCardItem
            key={card.id}
            card={card}
            onRemove={removeCard}
            realCardImages={realCardImages}
            isEditMode={isEditMode}
            isSelected={selectedIds.has(card.id)}
            onToggleSelect={toggleSelect}
          />
        ))}
      </div>

      {/* Add More Button - hidden in edit mode */}
      {!isEditMode && (
        <Link to="/cards" className="sv-mycards-add-more">
          <PlusOutlined />
          {t('myCards.addMore')}
        </Link>
      )}

      {/* Edit mode bottom bar */}
      {isEditMode && (
        <div className="sv-mycards-edit-bar">
          <button
            className="sv-mycards-delete-btn"
            onClick={deleteSelected}
            disabled={selectedIds.size === 0}
          >
            <DeleteOutlined />
            <span>{t('common.delete')}{selectedIds.size > 0 ? ` (${selectedIds.size})` : ''}</span>
          </button>
        </div>
      )}

      <style>{styles}</style>
    </div>
  )
}

const styles = `
  .sv-mycards-page {
    padding: 20px;
    min-height: calc(100vh - 140px);
    background: var(--app-bg);
    max-width: 800px;
    margin: 0 auto;
    padding-bottom: 100px;
  }

  @media (max-width: 640px) {
    .sv-mycards-page {
      padding: 16px;
      padding-bottom: 100px;
      min-height: calc(100vh - 70px);
    }
  }

  .sv-mycards-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
  }

  .sv-mycards-header h1 {
    font-size: 24px;
    font-weight: 700;
    color: #111827;
    margin: 0;
  }

  .sv-mycards-header-right {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .sv-mycards-count {
    font-size: 14px;
    color: #6b7280;
    background: #f3f4f6;
    padding: 4px 12px;
    border-radius: 12px;
  }

  .sv-mycards-edit-btn {
    font-size: 14px;
    font-weight: 500;
    color: #6b7280;
    background: none;
    border: none;
    cursor: pointer;
    padding: 4px 8px;
  }

  /* Row wrapper for checkbox + card item */
  .sv-mycards-row {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .sv-mycards-row .sv-card-list-item {
    flex: 1;
  }

  /* .sv-mycards-row .sv-card-list-item.editing-selected {
    margin-left: -10px;
    padding-left: 10px;
  } */

  /* Checkbox - consistent with system style */
  .sv-mycards-checkbox {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    border: 2px solid #d1d5db;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    transition: all 0.15s ease;
  }

  .sv-mycards-checkbox.checked {
    background: #10b981;
    border-color: #10b981;
    color: white;
  }

  .sv-mycards-checkbox .anticon {
    font-size: 12px;
  }

  .sv-mycards-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 20px;
  }

  /* .sv-card-list-item.editing-selected {
    background: var(--gray-100, #f5f3f0);
    border-radius: 12px;
  }

  html.dark-mode .sv-card-list-item.editing-selected {
    background: var(--bg-tertiary);
  } */

  /* Swipe container */
  .sv-swipe-container {
    position: relative;
    overflow: hidden;
  }

  .sv-swipe-content {
    touch-action: pan-y;
    -webkit-user-select: none;
    user-select: none;
  }

  .sv-swipe-delete {
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 80px;
    background: #ef4444;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    color: white;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
  }

  .sv-swipe-delete .anticon {
    font-size: 18px;
  }

  .sv-swipe-content {
    position: relative;
    background: var(--app-bg, white);
    z-index: 1;
  }

  .sv-mycards-add-more {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    padding: 14px;
    border: 2px dashed #e5e7eb;
    border-radius: 12px;
    color: #6b7280;
    font-size: 14px;
    font-weight: 500;
    text-decoration: none;
    transition: all 0.2s;
  }

  .sv-mycards-add-more:hover {
    border-color: #d1d5db;
    color: #374151;
    background: #f9fafb;
  }

  /* Edit mode bottom bar */
  .sv-mycards-edit-bar {
    position: fixed;
    bottom: 70px;
    left: 0;
    right: 0;
    padding: 12px 20px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    z-index: 100;
  }

  @media (max-width: 640px) {
    .sv-mycards-edit-bar {
      bottom: calc(60px + env(safe-area-inset-bottom));
    }
  }

  .sv-mycards-select-all {
    display: flex;
    align-items: center;
    gap: 10px;
    background: none;
    border: none;
    font-size: 14px;
    color: #374151;
    cursor: pointer;
    padding: 8px 0;
    margin-bottom: 12px;
  }

  .sv-mycards-delete-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    background: #ef4444;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .sv-mycards-delete-btn:disabled {
    background: #fca5a5;
    cursor: not-allowed;
  }

  .sv-mycards-delete-btn:not(:disabled):hover {
    background: #dc2626;
  }

  /* Empty State */
  .sv-mycards-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    text-align: center;
  }

  .sv-mycards-empty-icon {
    font-size: 48px;
    color: #d1d5db;
    margin-bottom: 16px;
  }

  .sv-mycards-empty h2 {
    font-size: 18px;
    font-weight: 600;
    color: #111827;
    margin: 0 0 8px;
  }

  .sv-mycards-empty p {
    font-size: 14px;
    color: #6b7280;
    margin: 0 0 24px;
  }

  .sv-mycards-add-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 12px 24px;
    background: #111827;
    color: white;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.2s;
  }

  .sv-mycards-add-btn:hover {
    background: #1f2937;
  }

  /* Dark mode */
  html.dark-mode .sv-mycards-header h1 {
    color: var(--text-primary);
  }

  html.dark-mode .sv-mycards-count {
    background: #2a2a2a;
    color: #9ca3af;
  }

  html.dark-mode .sv-mycards-edit-btn {
    color: #9ca3af;
  }

  html.dark-mode .sv-mycards-checkbox {
    border-color: #4b5563;
  }

  html.dark-mode .sv-swipe-content {
    background: var(--app-bg);
  }

  html.dark-mode .sv-mycards-select-all {
    color: var(--text-primary);
  }

  html.dark-mode .sv-mycards-add-more {
    border-color: #333;
    color: #9ca3af;
  }

  html.dark-mode .sv-mycards-add-more:hover {
    border-color: #444;
    color: var(--text-primary);
    background: #1a1a1a;
  }

  html.dark-mode .sv-mycards-empty h2 {
    color: var(--text-primary);
  }

  html.dark-mode .sv-mycards-empty p {
    color: #9ca3af;
  }

  html.dark-mode .sv-mycards-empty-icon {
    color: #4b5563;
  }
`

export default MyCardsPage
