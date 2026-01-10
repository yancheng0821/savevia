import { useLocation } from 'react-router-dom'
import { MessageOutlined } from '@ant-design/icons'
import { useAuthStore } from '../stores/useAuthStore'
import { useChatStore } from '../stores/useChatStore'
import { useHomePageStore } from '../stores/useHomePageStore'

interface ChatButtonProps {
  onAuthRequired?: () => void
}

// Pages where chat button should be hidden (conflicts with other floating elements or not needed)
const HIDDEN_PAGES = ['/cards', '/optimizer', '/result', '/share', '/my-cards']

export default function ChatButton({ onAuthRequired }: ChatButtonProps) {
  const location = useLocation()
  const { isAuthenticated } = useAuthStore()
  const { setOpen } = useChatStore()
  const { selectedCategory } = useHomePageStore()

  const handleClick = () => {
    if (isAuthenticated) {
      // User is logged in, open chat window
      setOpen(true)
    } else if (onAuthRequired) {
      // User not logged in, show auth panel
      onAuthRequired()
    }
  }

  // Don't show on pages with conflicting floating elements
  if (HIDDEN_PAGES.some(page => location.pathname === page || location.pathname.startsWith(page + '/'))) return null

  // On home page with floating result card, move button up
  const isHomePage = location.pathname === '/'
  const hasFloatingCard = isHomePage && selectedCategory !== null

  return (
    <button
      onClick={handleClick}
      className={`sv-chat-fab ${hasFloatingCard ? 'sv-chat-fab-high' : ''}`}
      aria-label="Ask SaveVia"
    >
      <MessageOutlined style={{ fontSize: 16 }} />
      <span className="sv-chat-fab-text">
        Ask <span className="sv-chat-fab-logo">SaveVia</span>
      </span>

      <style>{`
        .sv-chat-fab {
          position: fixed;
          bottom: calc(90px + env(safe-area-inset-bottom, 0px));
          right: 16px;
          height: 44px;
          padding: 0 18px;
          border-radius: 16px;
          border-bottom-right-radius: 4px;
          background: #ffffff;
          color: #1f2937;
          border: none;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          font-size: 14px;
          font-weight: 500;
          box-shadow:
            0 4px 12px rgba(0, 0, 0, 0.1),
            0 8px 24px rgba(0, 0, 0, 0.08);
          transition: all 0.2s ease;
          z-index: 9998;
        }

        .sv-chat-fab:active {
          transform: scale(0.96);
        }

        @media (hover: hover) {
          .sv-chat-fab:hover {
            background: #f9fafb;
            box-shadow:
              0 6px 16px rgba(0, 0, 0, 0.12),
              0 12px 32px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
          }
        }

        .sv-chat-fab-text {
          white-space: nowrap;
        }

        .sv-chat-fab-logo {
          background: linear-gradient(90deg, #2563eb 0%, #0d9488 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          font-weight: 600;
        }

        /* Mobile */
        @media (max-width: 640px) {
          .sv-chat-fab {
            padding: 0 16px;
            height: 40px;
            font-size: 13px;
          }
        }

        /* Higher position for home page (above floating result card) */
        .sv-chat-fab-high {
          bottom: calc(160px + env(safe-area-inset-bottom, 0px));
        }

        @media (max-width: 640px) {
          .sv-chat-fab-high {
            bottom: calc(150px + env(safe-area-inset-bottom, 0px));
          }
        }

        /* Dark mode */
        html.dark-mode .sv-chat-fab {
          background: #1f2937;
          color: #f3f4f6;
          box-shadow:
            0 4px 12px rgba(0, 0, 0, 0.3),
            0 8px 24px rgba(0, 0, 0, 0.2);
        }

        html.dark-mode .sv-chat-fab-logo {
          background: linear-gradient(90deg, #3b82f6 0%, #14b8a6 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        @media (hover: hover) {
          html.dark-mode .sv-chat-fab:hover {
            background: #374151;
          }
        }
      `}</style>
    </button>
  )
}
