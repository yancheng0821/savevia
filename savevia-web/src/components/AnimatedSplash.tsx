import { useEffect, useState, useRef } from 'react'

interface AnimatedSplashProps {
  onComplete?: () => void
  duration?: number // Duration in ms before calling onComplete
}

export default function AnimatedSplash({ onComplete, duration = 2500 }: AnimatedSplashProps) {
  const [stage, setStage] = useState(0)
  const [cashbackValue, setCashbackValue] = useState(0)
  const [progressStarted, setProgressStarted] = useState(false)
  const cashbackAnimated = useRef(false)

  useEffect(() => {
    // Stage 0: Initial (cards start off-screen)
    // Stage 1: Back card flies in
    // Stage 2: Middle card flies in
    // Stage 3: Front card flies in
    // Stage 4: Chip appears, cashback animates
    // Stage 5: Text fades in
    // Stage 6: Complete

    const timers = [
      setTimeout(() => setStage(1), 100),
      setTimeout(() => setStage(2), 300),
      setTimeout(() => setStage(3), 500),
      setTimeout(() => setStage(4), 700),
      setTimeout(() => setStage(5), 1200),
      setTimeout(() => setStage(6), 1800),
    ]

    return () => timers.forEach(clearTimeout)
  }, [])

  // Animate cashback percentage - only once
  useEffect(() => {
    if (stage >= 4 && !cashbackAnimated.current) {
      cashbackAnimated.current = true
      const targetValue = 5
      const animationDuration = 500
      const steps = 20
      const stepValue = targetValue / steps
      const stepDuration = animationDuration / steps

      let currentStep = 0
      const interval = setInterval(() => {
        currentStep++
        setCashbackValue(Math.min(currentStep * stepValue, targetValue))
        if (currentStep >= steps) {
          clearInterval(interval)
        }
      }, stepDuration)

      return () => clearInterval(interval)
    }
  }, [stage])

  // Start progress bar animation when stage >= 6
  useEffect(() => {
    if (stage >= 6) {
      // Small delay to ensure the element is rendered before starting animation
      requestAnimationFrame(() => {
        setProgressStarted(true)
      })
    }
  }, [stage])

  // Call onComplete after animation
  useEffect(() => {
    if (onComplete) {
      const timer = setTimeout(onComplete, duration)
      return () => clearTimeout(timer)
    }
  }, [onComplete, duration])

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: '#FFFCF5',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      overflow: 'hidden',
    }}>
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 512 512"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ maxWidth: '400px', maxHeight: '100vh' }}
      >
        {/* Background base */}
        <rect width="512" height="512" fill="#FFFCF5"/>

        {/* Cards container - scaled down for mobile */}
        <g transform="translate(90, 50) scale(0.65)">
          {/* Background Card - slides in from top-right with rotation */}
          <g style={{
            transform: stage >= 1
              ? 'translate(0, 0) rotate(8deg)'
              : 'translate(100px, -150px) rotate(20deg)',
            transformOrigin: '236px 145px',
            opacity: stage >= 1 ? 1 : 0,
            transition: 'all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)',
          }}>
            <rect x="36" y="20" width="400" height="250" rx="26" fill="url(#splash1)"/>
          </g>

          {/* Middle Card - slides in from bottom-left with rotation */}
          <g style={{
            transform: stage >= 2
              ? 'translate(0, 0) rotate(-4deg)'
              : 'translate(-100px, 150px) rotate(-15deg)',
            transformOrigin: '216px 215px',
            opacity: stage >= 2 ? 1 : 0,
            transition: 'all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)',
          }}>
            <rect x="16" y="90" width="400" height="250" rx="26" fill="url(#splash2)"/>
          </g>

          {/* Front Card - slides up and settles */}
          <g style={{
            transform: stage >= 3
              ? 'translateY(0) scale(1)'
              : 'translateY(80px) scale(0.9)',
            opacity: stage >= 3 ? 1 : 0,
            transition: 'all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)',
          }}>
            <rect x="56" y="145" width="400" height="250" rx="26" fill="url(#splash3)"/>

          {/* Chip with glow animation */}
          <g style={{
            opacity: stage >= 4 ? 1 : 0,
            transition: 'opacity 0.3s ease',
          }}>
            <rect x="90" y="180" width="56" height="42" rx="6" fill="url(#chipGradient)">
              <animate
                attributeName="opacity"
                values="1;0.7;1"
                dur="2s"
                repeatCount="indefinite"
              />
            </rect>
            <line x1="90" y1="196" x2="146" y2="196" stroke="#c9a227" strokeWidth="1" opacity="0.5"/>
            <line x1="90" y1="209" x2="146" y2="209" stroke="#c9a227" strokeWidth="1" opacity="0.5"/>
            <line x1="118" y1="180" x2="118" y2="222" stroke="#c9a227" strokeWidth="1" opacity="0.5"/>
          </g>

          {/* CASHBACK label */}
          <text
            x="90"
            y="250"
            fill="rgba(255,255,255,0.7)"
            fontFamily="Inter, Arial, sans-serif"
            fontSize="12"
            fontWeight="600"
            letterSpacing="1"
            style={{
              opacity: stage >= 4 ? 1 : 0,
              transition: 'opacity 0.3s ease 0.1s',
            }}
          >
            CASHBACK
          </text>

          {/* Animated percentage */}
          <text
            x="90"
            y="295"
            fill="white"
            fontFamily="Inter, Arial, sans-serif"
            fontSize="40"
            fontWeight="700"
            style={{
              opacity: stage >= 4 ? 1 : 0,
              transition: 'opacity 0.3s ease 0.2s',
            }}
          >
            {cashbackValue.toFixed(0)}%
          </text>

          {/* Card number */}
          <text
            x="90"
            y="375"
            fill="rgba(255,255,255,0.5)"
            fontFamily="Inter, Arial, sans-serif"
            fontSize="16"
            style={{
              opacity: stage >= 4 ? 1 : 0,
              transition: 'opacity 0.3s ease 0.3s',
            }}
          >
            •••• •••• •••• 4242
          </text>
        </g>

          {/* Animated sparkles - gentle fade in/out */}
          <g style={{
            opacity: stage >= 4 ? 1 : 0,
            transition: 'opacity 0.5s ease',
          }}>
            {/* Main sparkle */}
            <path
              d="M420 175 L425 190 L440 195 L425 200 L420 215 L415 200 L400 195 L415 190 Z"
              fill="white"
            >
              <animate
                attributeName="opacity"
                values="0.5;1;0.5"
                dur="2s"
                repeatCount="indefinite"
              />
            </path>

            {/* Second sparkle */}
            <path
              d="M450 135 L453 145 L463 148 L453 151 L450 161 L447 151 L437 148 L447 145 Z"
              fill="white"
            >
              <animate
                attributeName="opacity"
                values="0.4;0.9;0.4"
                dur="2.5s"
                begin="0.7s"
                repeatCount="indefinite"
              />
            </path>

            {/* Third sparkle */}
            <path
              d="M380 130 L382 137 L389 139 L382 141 L380 148 L378 141 L371 139 L378 137 Z"
              fill="white"
            >
              <animate
                attributeName="opacity"
                values="0.3;0.8;0.3"
                dur="2.2s"
                begin="0.4s"
                repeatCount="indefinite"
              />
            </path>
          </g>
        </g>

        {/* SaveVia Text - fade in and slight rise */}
        <text
          x="256"
          y="365"
          textAnchor="middle"
          fontFamily="Inter, Arial, sans-serif"
          fontSize="42"
          fontWeight="700"
          letterSpacing="-1"
          fill="url(#splashText)"
          style={{
            opacity: stage >= 5 ? 1 : 0,
            transform: stage >= 5 ? 'translateY(0)' : 'translateY(20px)',
            transition: 'all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)',
          }}
        >
          SaveVia
        </text>

        {/* Tagline - fade in after title */}
        <text
          x="256"
          y="395"
          textAnchor="middle"
          fontFamily="Inter, Arial, sans-serif"
          fontSize="12"
          fontWeight="500"
          fill="#9ca3af"
          letterSpacing="1"
          style={{
            opacity: stage >= 5 ? 1 : 0,
            transition: 'opacity 0.5s ease 0.2s',
          }}
        >
          USE THE RIGHT CARD
        </text>

        {/* Progress bar */}
        <g style={{
          opacity: stage >= 6 ? 1 : 0,
          transition: 'opacity 0.3s ease',
        }}>
          {/* Background track */}
          <rect
            x="176"
            y="420"
            width="160"
            height="4"
            rx="2"
            fill="#e5e7eb"
          />
          {/* Progress fill - using CSS transform for smooth GPU-accelerated animation */}
          <rect
            x="176"
            y="420"
            width="160"
            height="4"
            rx="2"
            fill="url(#progressGradient)"
            style={{
              // @ts-ignore - transformBox is valid CSS but not in React types
              transformBox: 'fill-box',
              transformOrigin: 'left center',
              transform: progressStarted ? 'scaleX(1)' : 'scaleX(0)',
              transition: progressStarted ? 'transform 1s cubic-bezier(0.25, 0.1, 0.25, 1)' : 'none',
              willChange: 'transform',
            }}
          />
        </g>

        <defs>
          {/* Card gradients */}
          <linearGradient id="splash1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style={{ stopColor: '#dbeafe' }}/>
            <stop offset="100%" style={{ stopColor: '#ede9fe' }}/>
          </linearGradient>
          <linearGradient id="splash2" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style={{ stopColor: '#fef3c7' }}/>
            <stop offset="100%" style={{ stopColor: '#fce7f3' }}/>
          </linearGradient>
          <linearGradient id="splash3" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style={{ stopColor: '#1f2937' }}/>
            <stop offset="100%" style={{ stopColor: '#374151' }}/>
          </linearGradient>
          <linearGradient id="splashText" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style={{ stopColor: '#2563eb' }}/>
            <stop offset="100%" style={{ stopColor: '#0d9488' }}/>
          </linearGradient>
          <linearGradient id="chipGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style={{ stopColor: '#fbbf24' }}/>
            <stop offset="100%" style={{ stopColor: '#d97706' }}/>
          </linearGradient>
          <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style={{ stopColor: '#2563eb' }}/>
            <stop offset="100%" style={{ stopColor: '#0d9488' }}/>
          </linearGradient>
        </defs>
      </svg>
    </div>
  )
}
