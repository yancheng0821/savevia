import { useState, useEffect, useRef } from 'react'
import { getCardImageUrl } from '../utils/cardImages'

interface CardImageProps {
  bank: string
  cardName: string
  style: { gradient: string; textColor: string }
  // Render function for fallback content (gradient style)
  fallbackContent: React.ReactNode
  // Optional: custom styles for the container
  containerStyle?: React.CSSProperties
  // Optional: timeout in ms (default 5000ms)
  timeout?: number
  // Optional: loading priority
  loading?: 'eager' | 'lazy'
}

type LoadState = 'loading' | 'loaded' | 'error'

/**
 * CardImage component with fallback to gradient style
 * - Shows real card image when available and loads successfully
 * - Falls back to gradient style on: no image URL, load error, or timeout
 */
export function CardImage({
  bank,
  cardName,
  style,
  fallbackContent,
  containerStyle,
  timeout = 5000,
  loading = 'lazy'
}: CardImageProps) {
  const cardImageUrl = getCardImageUrl(bank, cardName)
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    // Reset state when URL changes
    setLoadState('loading')

    // Set timeout for image loading
    timeoutRef.current = setTimeout(() => {
      setLoadState((prev) => prev === 'loading' ? 'error' : prev)
    }, timeout)

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [cardImageUrl, timeout])

  const handleLoad = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    setLoadState('loaded')
  }

  const handleError = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    setLoadState('error')
  }

  // Failed to load - show fallback
  if (loadState === 'error') {
    return (
      <div style={{
        position: 'relative',
        aspectRatio: '1.586',
        background: style.gradient,
        borderRadius: '12px',
        overflow: 'hidden',
        ...containerStyle
      }}>
        {fallbackContent}
      </div>
    )
  }

  // Image is loading or loaded
  return (
    <div style={{
      position: 'relative',
      aspectRatio: '1.586',
      borderRadius: '12px',
      overflow: 'hidden',
      // Show gradient as placeholder while loading
      background: loadState === 'loading' ? style.gradient : 'transparent',
      ...containerStyle
    }}>
      <img
        src={cardImageUrl}
        alt={`${bank} ${cardName}`}
        loading={loading}
        onLoad={handleLoad}
        onError={handleError}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          display: 'block',
          opacity: loadState === 'loaded' ? 1 : 0,
          transition: 'opacity 0.3s ease'
        }}
      />
      {/* Show fallback content while loading (as overlay) */}
      {loadState === 'loading' && (
        <div style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          {fallbackContent}
        </div>
      )}
    </div>
  )
}

/**
 * Simple version: just returns the image or null
 * Use this when you want to handle the fallback yourself
 */
export function useCardImage(bank: string, cardName: string) {
  const cardImageUrl = getCardImageUrl(bank, cardName)
  const [isLoaded, setIsLoaded] = useState(false)
  const [hasError, setHasError] = useState(false)

  useEffect(() => {
    setIsLoaded(false)
    setHasError(false)

    // Preload image
    const img = new Image()
    const timeoutId = setTimeout(() => {
      setHasError(true)
    }, 5000)

    img.onload = () => {
      clearTimeout(timeoutId)
      setIsLoaded(true)
    }
    img.onerror = () => {
      clearTimeout(timeoutId)
      setHasError(true)
    }
    img.src = cardImageUrl

    return () => {
      clearTimeout(timeoutId)
    }
  }, [cardImageUrl])

  return {
    imageUrl: cardImageUrl,
    isLoaded,
    hasError,
    showImage: isLoaded && !hasError
  }
}

export default CardImage
