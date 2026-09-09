import { Link } from 'react-router-dom'
import { Button } from '../../components/ui/Button'
import { LocalizedText } from '../../i18n/LocalizedText'
import type { BusinessListItem } from '../../types/business'
import { validBusinessQuery } from './nearbyState'

type Props = {
  query: string
  radius: number
  queryInvalid: boolean
  running: boolean
  businesses: BusinessListItem[]
  labels: { radius: string; find: string; loading: string; profile: string }
  textUi: (value: string) => string
  onQueryChange: (value: string) => void
  onQueryBlur: () => void
  onRadiusChange: (value: number) => void
  onRun: () => void
}

export function NearbySearchControls({ query, radius, queryInvalid, running, businesses, labels, textUi, onQueryChange, onQueryBlur, onRadiusChange, onRun }: Props) {
  return (
    <div className="nearby-controls">
      <div className="nearby-field nearby-field--business">
      <label htmlFor="nearby-business">{textUi('Business')}</label>
      <input id="nearby-business" type="text" list="nearby-suggestions" value={query} minLength={2} maxLength={200}
        aria-invalid={queryInvalid} aria-describedby={queryInvalid ? 'nearby-business-hint nearby-business-error' : 'nearby-business-hint'}
        onBlur={() => onQueryBlur()} placeholder={textUi('Enter your business idea')}
        onChange={event => {
          onQueryChange(event.target.value)
        }} />
      <p id="nearby-business-hint" className="nearby-field-hint">{textUi('e.g. Tea Stall, Kirana Store, Mobile Repair Shop')}</p>
      <datalist id="nearby-suggestions">{businesses.map(business => <option key={business.id} value={business.name} />)}</datalist>
      {queryInvalid && <p id="nearby-business-error" className="nearby-field-error" role="status">{textUi('Enter a business idea with 2–200 characters.')}</p>}
      </div>
      <div className="nearby-field nearby-field--radius">
      <label htmlFor="nearby-radius">{labels.radius}</label>
      <select id="nearby-radius" value={radius} onChange={event => {
        onRadiusChange(Number(event.target.value))
      }}>{Array.from({ length: 10 }, (_, i) => i + 1).map(km => <option key={km} value={km}>{km}<LocalizedText value={" km"} /></option>)}</select>
      </div>
      <Button className="nearby-submit" type="button" disabled={!validBusinessQuery(query) || running} onClick={onRun}>{running ? labels.loading : labels.find}</Button>
      <Link className="nearby-profile-link" to="/profile">{labels.profile}</Link>
    </div>
  )
}
