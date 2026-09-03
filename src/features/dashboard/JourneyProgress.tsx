import { Check } from 'lucide-react'

const journey = ['Profile Completed', 'Local Market Analysis', 'Business Opportunity Analysis', 'Financial Planning', 'Scheme Guidance', 'Final Report']
export function JourneyProgress() { return <section className="dashboard-card journey-progress" aria-labelledby="journey-title"><div className="card-heading-row"><div><span className="eyebrow">Your roadmap</span><h2 id="journey-title">Business analysis journey</h2></div></div><ol>{journey.map((name, index) => <li key={name} className={index === 0 ? 'complete' : ''}><span>{index === 0 ? <Check aria-hidden="true" /> : index + 1}</span><div><strong>{name}</strong><small>{index === 0 ? 'Complete' : 'Not started'}</small></div></li>)}</ol></section> }
