import { useState } from 'react'
import { Pause, Play } from 'lucide-react'
import { useUi } from '../../i18n/uiContextValue'
import { landingMessages as m } from '../../i18n/landingMessages'
import { defaultHomeAlerts, type HomeAlert } from '../../data/homeAlerts'

export interface LatestUpdatesBarProps {
  alerts?: HomeAlert[]
}

/**
 * Multilingual Continuous News / Notification Alert Bar for the public landing page.
 *
 * Sits directly between the main public navigation header and the hero carousel.
 * Continuous smooth right-to-left scrolling track with seamless infinite loop.
 *
 * FUTURE-READY INTEGRATION:
 * When backend announcements API becomes available, pass the fetched alerts array
 * via the `alerts` prop (or replace `defaultHomeAlerts`).
 */
export function LatestUpdatesBar({ alerts = defaultHomeAlerts }: LatestUpdatesBarProps) {
  const { text } = useUi()
  const [paused, setPaused] = useState(false)

  const handleTogglePause = () => {
    setPaused(prev => !prev)
  }

  const renderAlertItems = (prefix: string) =>
    alerts.map((alert, index) => (
      <span key={`${prefix}-${alert.id}-${index}`} className="latest-updates-bar__item">
        <span className="latest-updates-bar__item-text">{text(alert.message.en)}</span>
        <span className="latest-updates-bar__bullet" aria-hidden="true">
          •
        </span>
      </span>
    ))

  return (
    <aside
      className="latest-updates-bar"
      role="region"
      aria-label={text(m.latestUpdatesRegion.en)}
    >
      <div className="portal-container latest-updates-bar__container">
        {/* Left Badge */}
        <div className="latest-updates-bar__badge">
          <span className="latest-updates-bar__tag">
            {text(m.latestUpdatesLabel.en)}
          </span>
          <span className="latest-updates-bar__divider" aria-hidden="true" />
        </div>

        {/* Center Continuous Scrolling Viewport */}
        <div className="latest-updates-bar__viewport">
          <div
            className={`latest-updates-bar__track ${paused ? 'is-paused' : ''}`}
            tabIndex={0}
          >
            {/* Primary group */}
            <div className="latest-updates-bar__group">
              {renderAlertItems('primary')}
            </div>
            {/* Duplicated group for seamless infinite loop */}
            <div className="latest-updates-bar__group" aria-hidden="true">
              {renderAlertItems('duplicate')}
            </div>
          </div>
        </div>

        {/* Right Pause / Play Control */}
        <div className="latest-updates-bar__actions">
          <button
            type="button"
            className={`latest-updates-bar__btn latest-updates-bar__btn--toggle ${
              paused ? 'is-paused' : ''
            }`}
            onClick={handleTogglePause}
            aria-label={text(paused ? m.resumeUpdates.en : m.pauseUpdates.en)}
            aria-pressed={paused}
          >
            {paused ? (
              <Play size={14} aria-hidden="true" />
            ) : (
              <Pause size={14} aria-hidden="true" />
            )}
          </button>
        </div>
      </div>
    </aside>
  )
}
