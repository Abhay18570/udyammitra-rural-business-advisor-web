import { Check, ChevronLeft, ChevronRight } from 'lucide-react'
import { useEffect, useState, type ChangeEvent, type ReactNode } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Button } from '../../components/ui/Button'
import { useAuth } from '../../context/authContextValue'
import { getApiErrorMessage } from '../../services/apiError'
import { profileService } from '../../services/profileService'
import type { EntrepreneurProfile, SelectionItem } from '../../types/profile'
import { formatValidationError, stepSchemas } from './onboardingSchemas'

const steps = ['Personal details', 'Location', 'Capital', 'Skills', 'Resources', 'Existing business']
const skills = [
  'Tailoring',
  'Repairing',
  'Farming',
  'Dairy',
  'Cooking',
  'Retail',
  'Machinery',
  'Computer',
  'Food Processing',
  'Driving',
  'Other',
]
const resources = [
  'Land',
  'Shop',
  'Vehicle',
  'Storage Space',
  'Machinery',
  'Livestock',
  'Electricity',
  'Water',
  'Internet',
  'Other',
]
const options = {
  age: [
    ['AGE_18_25', '18–25'],
    ['AGE_26_35', '26–35'],
    ['AGE_36_45', '36–45'],
    ['AGE_46_60', '46–60'],
    ['AGE_60_PLUS', '60+'],
  ],
  education: [
    ['', 'Prefer not to say'],
    ['NO_FORMAL', 'No formal education'],
    ['UP_TO_10TH', 'Up to 10th'],
    ['TWELFTH', '12th'],
    ['ITI_VOCATIONAL', 'ITI / Vocational'],
    ['DIPLOMA', 'Diploma'],
    ['GRADUATE', 'Graduate'],
    ['POSTGRADUATE', 'Postgraduate'],
    ['OTHER', 'Other'],
  ],
  experience: [
    ['NONE', 'No prior experience'],
    ['LESS_THAN_1_YEAR', 'Less than 1 year'],
    ['ONE_TO_THREE_YEARS', '1–3 years'],
    ['THREE_TO_FIVE_YEARS', '3–5 years'],
    ['FIVE_PLUS_YEARS', '5+ years'],
  ],
  capital: [
    ['UP_TO_50000', 'Up to ₹50,000'],
    ['RANGE_50000_TO_100000', '₹50,000–₹1 lakh'],
    ['RANGE_100000_TO_250000', '₹1–2.5 lakh'],
    ['RANGE_250000_TO_500000', '₹2.5–5 lakh'],
    ['RANGE_500000_TO_1000000', '₹5–10 lakh'],
    ['ABOVE_1000000', 'Above ₹10 lakh'],
  ],
}
const blankBusiness = {
  businessName: '',
  businessCategory: '',
  yearsOperating: 0,
  initialInvestment: '0',
  monthlyRevenue: '0',
  monthlyExpenses: '0',
  employeeCount: 0,
  estimatedMonthlyCustomers: 0,
  majorChallenges: '',
}

const initialProfile = (name: string, language: EntrepreneurProfile['preferredLanguage']): EntrepreneurProfile => ({
  fullName: name,
  preferredLanguage: language || 'en',
  state: 'Maharashtra',
  district: '',
  taluka: '',
  village: '',
  pincode: '',
  capitalRange: undefined,
  ownCapital: '',
  loanRequired: '',
  skills: [],
  resources: [],
  hasExistingBusiness: undefined,
  existingBusiness: undefined,
  onboardingStep: 1,
  onboardingCompleted: false,
})

function Field({ label, error, children }: { label: string; error?: string; children: ReactNode }) {
  return (
    <label className="profile-field">
      <span>{label}</span>
      {children}
      {error && <small className="field-error">{error}</small>}
    </label>
  )
}

function Select({
  value,
  onChange,
  items,
}: {
  value?: string
  onChange: (value: string) => void
  items: string[][]
}) {
  return (
    <select value={value ?? ''} onChange={e => onChange(e.target.value)}>
      <option value="" disabled>
        Select an option
      </option>
      {items.map(([val, label]) => (
        <option key={val || label} value={val}>
          {label}
        </option>
      ))}
    </select>
  )
}

function SelectionGrid({
  values,
  selected,
  onChange,
}: {
  values: string[]
  selected: SelectionItem[]
  onChange: (items: SelectionItem[]) => void
}) {
  const toggle = (name: string) =>
    onChange(
      selected.some(i => i.name === name)
        ? selected.filter(i => i.name !== name)
        : [...selected, { name, otherDescription: undefined }]
    )
  const other = selected.find(i => i.name === 'Other')

  return (
    <>
      <div className="selection-grid">
        {values.map(name => (
          <button
            type="button"
            className={selected.some(i => i.name === name) ? 'selection-chip selected' : 'selection-chip'}
            onClick={() => toggle(name)}
            key={name}
          >
            {selected.some(i => i.name === name) && <Check size={15} />}
            {name}
          </button>
        ))}
      </div>
      {other && (
        <Field label="Please describe Other">
          <input
            value={other.otherDescription ?? ''}
            maxLength={120}
            placeholder="Describe your skill/resource"
            onChange={e =>
              onChange(
                selected.map(i =>
                  i.name === 'Other' ? { ...i, otherDescription: e.target.value } : i
                )
              )
            }
          />
        </Field>
      )}
    </>
  )
}

export function OnboardingPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const [profile, setProfile] = useState<EntrepreneurProfile>(() =>
    initialProfile(user?.fullName ?? '', user?.preferredLanguage ?? 'en')
  )
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    void profileService
      .get()
      .then(saved => {
        if (saved) {
          if (saved.onboardingCompleted && params.get('mode') !== 'edit') {
            navigate('/dashboard', { replace: true })
            return
          }
          setProfile(saved)
          setStep(params.get('mode') === 'edit' ? 1 : saved.onboardingStep || 1)
        }
      })
      .catch(e => setError(getApiErrorMessage(e, 'Unable to load your profile.')))
      .finally(() => setLoading(false))
  }, [navigate, params])

  const set = <K extends keyof EntrepreneurProfile>(key: K, value: EntrepreneurProfile[K]) =>
    setProfile(current => ({ ...current, [key]: value }))

  const validate = () => {
    const schema = stepSchemas[step - 1]
    if (!schema) return true
    const result = schema.safeParse(profile)
    if (result.success) {
      setError('')
      return true
    }
    const firstIssue = result.error.issues[0]
    const message = formatValidationError(firstIssue)
    setError(message)
    return false
  }

  const next = async () => {
    if (!validate()) return
    setSaving(true)
    setError('')
    const completing = step === 6
    try {
      const saved = await profileService.update({
        ...profile,
        onboardingStep: completing ? 6 : step + 1,
        onboardingCompleted: completing,
      })
      setProfile(saved)
      if (completing) navigate('/dashboard', { replace: true })
      else setStep(step + 1)
    } catch (e) {
      setError(getApiErrorMessage(e, 'Your profile could not be saved. Please try again.'))
    } finally {
      setSaving(false)
    }
  }

  const input = (key: keyof EntrepreneurProfile) => (e: ChangeEvent<HTMLInputElement>) =>
    set(key, e.target.value as never)

  if (loading)
    return (
      <div className="onboarding-shell">
        <div className="profile-card">
          <p>Loading your profile…</p>
        </div>
      </div>
    )

  return (
    <div className="onboarding-shell">
      <section className="onboarding-heading">
        <span className="eyebrow">Entrepreneur profile</span>
        <h1>Tell us about your journey</h1>
        <p>This helps UdyamMitra personalise future business guidance. You can edit these details later.</p>
      </section>
      <div className="onboarding-layout">
        <aside className="onboarding-progress">
          <strong>Step {step} of 6</strong>
          <div className="progress-track">
            <i style={{ width: `${(step / 6) * 100}%` }} />
          </div>
          <ol>
            {steps.map((name, index) => (
              <li key={name} className={index + 1 === step ? 'active' : index + 1 < step ? 'done' : ''}>
                <span>{index + 1 < step ? <Check size={14} /> : index + 1}</span>
                {name}
              </li>
            ))}
          </ol>
        </aside>
        <main className="profile-card">
          <header>
            <small>
              STEP {step} OF 6
            </small>
            <h2>{steps[step - 1]}</h2>
          </header>
          {error && (
            <div className="profile-error" role="alert">
              {error}
            </div>
          )}
          <div className="profile-form">
            {step === 1 && (
              <div className="profile-grid">
                <Field label="Full name">
                  <input value={profile.fullName} onChange={input('fullName')} />
                </Field>
                <Field label="Age group">
                  <Select
                    value={profile.ageGroup}
                    onChange={v => set('ageGroup', v as EntrepreneurProfile['ageGroup'])}
                    items={options.age}
                  />
                </Field>
                <Field label="Education (optional)">
                  <Select
                    value={profile.education}
                    onChange={v => set('education', (v || undefined) as EntrepreneurProfile['education'])}
                    items={options.education}
                  />
                </Field>
                <Field label="Previous experience">
                  <Select
                    value={profile.previousExperience}
                    onChange={v => set('previousExperience', v as EntrepreneurProfile['previousExperience'])}
                    items={options.experience}
                  />
                </Field>
                <Field label="Preferred language">
                  <Select
                    value={profile.preferredLanguage}
                    onChange={v => set('preferredLanguage', v as EntrepreneurProfile['preferredLanguage'])}
                    items={[
                      ['en', 'English'],
                      ['mr', 'मराठी'],
                      ['hi', 'हिन्दी'],
                    ]}
                  />
                </Field>
              </div>
            )}
            {step === 2 && (
              <div className="profile-grid">
                <Field label="State">
                  <input value={profile.state ?? ''} onChange={input('state')} />
                </Field>
                <Field label="District">
                  <input value={profile.district ?? ''} onChange={input('district')} />
                </Field>
                <Field label="Taluka">
                  <input value={profile.taluka ?? ''} onChange={input('taluka')} />
                </Field>
                <Field label="Village / town">
                  <input value={profile.village ?? ''} onChange={input('village')} />
                </Field>
                <Field label="Pincode">
                  <input
                    inputMode="numeric"
                    maxLength={6}
                    value={profile.pincode ?? ''}
                    onChange={input('pincode')}
                  />
                </Field>
              </div>
            )}
            {step === 3 && (
              <div className="profile-grid">
                <Field label="Available capital range">
                  <Select
                    value={profile.capitalRange}
                    onChange={v => set('capitalRange', v as EntrepreneurProfile['capitalRange'])}
                    items={options.capital}
                  />
                </Field>
                <Field label="Your own capital (₹)">
                  <input
                    type="number"
                    min="0"
                    value={profile.ownCapital ?? ''}
                    onChange={input('ownCapital')}
                  />
                  <small>Amount you can invest without borrowing.</small>
                </Field>
                <Field label="Loan required (₹)">
                  <input
                    type="number"
                    min="0"
                    value={profile.loanRequired ?? ''}
                    onChange={input('loanRequired')}
                  />
                  <small>Enter 0 if you do not need a loan.</small>
                </Field>
              </div>
            )}
            {step === 4 && (
              <>
                <p>Select all skills that apply.</p>
                <SelectionGrid
                  values={skills}
                  selected={profile.skills}
                  onChange={v => set('skills', v)}
                />
              </>
            )}
            {step === 5 && (
              <>
                <p>Select resources already available to you.</p>
                <SelectionGrid
                  values={resources}
                  selected={profile.resources}
                  onChange={v => set('resources', v)}
                />
              </>
            )}
            {step === 6 && (
              <>
                <fieldset className="business-choice">
                  <legend>Do you currently run a business?</legend>
                  <label>
                    <input
                      type="radio"
                      name="hasExistingBusiness"
                      checked={profile.hasExistingBusiness === true}
                      onChange={() => {
                        set('hasExistingBusiness', true)
                        if (!profile.existingBusiness) set('existingBusiness', blankBusiness)
                      }}
                    />{' '}
                    Yes
                  </label>
                  <label>
                    <input
                      type="radio"
                      name="hasExistingBusiness"
                      checked={profile.hasExistingBusiness === false}
                      onChange={() => {
                        set('hasExistingBusiness', false)
                        set('existingBusiness', undefined)
                      }}
                    />{' '}
                    No
                  </label>
                </fieldset>
                {profile.hasExistingBusiness === false && (
                  <div className="profile-note">
                    That’s completely fine—UdyamMitra also supports first-time entrepreneurs.
                  </div>
                )}
                {profile.hasExistingBusiness && profile.existingBusiness && (
                  <BusinessFields
                    business={profile.existingBusiness}
                    onChange={b => set('existingBusiness', b)}
                  />
                )}
              </>
            )}
          </div>
          <footer>
            {step > 1 ? (
              <Button
                variant="outline"
                type="button"
                onClick={() => setStep(step - 1)}
                disabled={saving}
              >
                <ChevronLeft size={17} /> Back
              </Button>
            ) : (
              <span />
            )}
            <Button type="button" onClick={() => void next()} disabled={saving}>
              {saving ? 'Saving…' : step === 6 ? 'Complete profile' : 'Save & continue'}{' '}
              {!saving && <ChevronRight size={17} />}
            </Button>
          </footer>
        </main>
      </div>
    </div>
  )
}

function BusinessFields({
  business,
  onChange,
}: {
  business: NonNullable<EntrepreneurProfile['existingBusiness']>
  onChange: (business: NonNullable<EntrepreneurProfile['existingBusiness']>) => void
}) {
  const text =
    (key: keyof typeof business) =>
    (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      onChange({ ...business, [key]: e.target.value })
  const number =
    (key: keyof typeof business) => (e: ChangeEvent<HTMLInputElement>) =>
      onChange({ ...business, [key]: Number(e.target.value) })

  return (
    <div className="profile-grid business-fields">
      <Field label="Business name">
        <input value={business.businessName} onChange={text('businessName')} />
      </Field>
      <Field label="Category">
        <input value={business.businessCategory} onChange={text('businessCategory')} />
      </Field>
      <Field label="Years operating">
        <input
          type="number"
          min="0"
          value={business.yearsOperating}
          onChange={number('yearsOperating')}
        />
      </Field>
      <Field label="Initial investment (₹)">
        <input
          type="number"
          min="0"
          value={business.initialInvestment}
          onChange={text('initialInvestment')}
        />
      </Field>
      <Field label="Monthly revenue (₹)">
        <input
          type="number"
          min="0"
          value={business.monthlyRevenue}
          onChange={text('monthlyRevenue')}
        />
      </Field>
      <Field label="Monthly expenses (₹)">
        <input
          type="number"
          min="0"
          value={business.monthlyExpenses}
          onChange={text('monthlyExpenses')}
        />
      </Field>
      <Field label="Employees">
        <input
          type="number"
          min="0"
          value={business.employeeCount}
          onChange={number('employeeCount')}
        />
      </Field>
      <Field label="Estimated monthly customers">
        <input
          type="number"
          min="0"
          value={business.estimatedMonthlyCustomers}
          onChange={number('estimatedMonthlyCustomers')}
        />
      </Field>
      <Field label="Major challenges (optional)">
        <textarea
          rows={4}
          maxLength={2000}
          value={business.majorChallenges ?? ''}
          onChange={text('majorChallenges')}
        />
      </Field>
    </div>
  )
}

