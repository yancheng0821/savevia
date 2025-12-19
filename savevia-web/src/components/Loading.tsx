import './Loading.css'

interface LoadingProps {
  size?: 'small' | 'default' | 'large'
  text?: string
}

export default function Loading({ size = 'default', text }: LoadingProps) {
  const sizeMap = {
    small: 24,
    default: 40,
    large: 56,
  }

  const dimension = sizeMap[size]

  return (
    <div className="sv-loading">
      <div className="sv-loading-spinner" style={{ width: dimension, height: dimension }}>
        <svg viewBox="0 0 50 50" className="sv-loading-svg">
          <defs>
            <linearGradient id="sv-loading-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#2563eb" />
              <stop offset="100%" stopColor="#0d9488" />
            </linearGradient>
          </defs>
          <circle
            className="sv-loading-track"
            cx="25"
            cy="25"
            r="20"
            fill="none"
            strokeWidth="4"
          />
          <circle
            className="sv-loading-progress"
            cx="25"
            cy="25"
            r="20"
            fill="none"
            strokeWidth="4"
            strokeLinecap="round"
            stroke="url(#sv-loading-gradient)"
          />
        </svg>
        {/* Card icon in center */}
        <div className="sv-loading-icon">
          <svg viewBox="0 0 24 24" fill="none" style={{ width: '50%', height: '50%' }}>
            <rect x="2" y="5" width="20" height="14" rx="2" stroke="currentColor" strokeWidth="1.5"/>
            <path d="M2 10h20" stroke="currentColor" strokeWidth="1.5"/>
          </svg>
        </div>
      </div>
      {text && <p className="sv-loading-text">{text}</p>}
    </div>
  )
}
