import { BarChart3, Bot, Calculator, FileCheck2, FileText, Landmark, MapPinned, Search, Store, TrendingUp, WalletCards } from 'lucide-react'
export const capabilities = [{ icon: MapPinned, title: 'Location-Aware Analysis' }, { icon: BarChart3, title: 'Explainable Recommendations' }, { icon: Calculator, title: 'Financial Planning' }, { icon: Landmark, title: 'Scheme Guidance' }]
export const problems = [
  { icon: MapPinned, title: 'Limited Local Market Information', text: 'Reliable demand and competition information is often difficult to find at village and taluka level.' },
  { icon: Search, title: 'Difficulty Choosing the Right Business', text: 'A promising idea elsewhere may not suit local needs, skills, resources or market access.' },
  { icon: WalletCards, title: 'Unclear Financial Requirements', text: 'Entrepreneurs need a realistic view of setup cost, working capital, loans and profitability.' },
  { icon: Landmark, title: 'Low Awareness of Support Schemes', text: 'Relevant assistance can be missed when eligibility rules and application paths are unclear.' },
  { icon: FileCheck2, title: 'Complicated Documentation', text: 'Registrations, licences and application documents can make a good idea feel overwhelming.' },
]
export const journeySteps = [
  { n: '01', title: 'Tell Us About You', text: 'Profile, location, skills, assets and available capital.' }, { n: '02', title: 'Analyse Your Local Market', text: 'Understand nearby businesses, competition and market indicators.' },
  { n: '03', title: 'Discover Business Opportunities', text: 'Get ranked, explainable business recommendations.' }, { n: '04', title: 'Build a Financial Plan', text: 'Estimate investment, working capital, EMI, profitability and risk.' },
  { n: '05', title: 'Explore Relevant Schemes', text: 'Understand potentially suitable government schemes and requirements.' }, { n: '06', title: 'Generate Your Business Report', text: 'Receive a consolidated feasibility report and next steps.' },
]
export const coreFeatures = [
  { icon: MapPinned, title: 'Local Market Intelligence', text: 'Analyse businesses and market conditions around the selected village, taluka or district.' }, { icon: TrendingUp, title: 'Business Opportunity Analysis', text: 'Compare suitable businesses using demand, competition, skills, financial fit and market access.' },
  { icon: Store, title: 'Existing Business Advisory', text: 'Evaluate whether to continue, improve, expand, diversify or switch an existing business.' }, { icon: Calculator, title: 'Financial Planning', text: 'Estimate project cost, working capital, loan requirement, profit, break-even and financial risk.' },
  { icon: Landmark, title: 'Government Scheme Router', text: 'Identify potentially relevant schemes using transparent rule-based eligibility checks.' }, { icon: FileCheck2, title: 'Documentation Assistance', text: 'Understand required documents, licences, registrations and application procedures.' },
  { icon: Bot, title: 'AI Business Advisor', text: "Ask contextual questions about the user's analysis, finances, schemes and next steps." }, { icon: FileText, title: 'Final Business Report', text: 'Bring market, opportunity, financial and scheme analysis into one consolidated report.' },
]
export type Opportunity = { title: string; score: number; capital: string; demand: 'High' | 'Medium'; competition: 'Low' | 'Medium' }
export const demoOpportunities: Opportunity[] = [
  { title: 'Mobile Repair & Accessories', score: 87, capital: '₹1.8L – ₹2.4L', demand: 'High', competition: 'Low' }, { title: 'Tailoring & Alteration Centre', score: 82, capital: '₹80K – ₹1.5L', demand: 'High', competition: 'Medium' },
  { title: 'Flour Mill', score: 76, capital: '₹3L – ₹5L', demand: 'Medium', competition: 'Medium' }, { title: 'Dairy Enterprise', score: 72, capital: '₹4L – ₹7L', demand: 'High', competition: 'Medium' },
]
export const financialMetrics = [['Project Cost', '₹2,40,000'], ['Own Contribution', '₹80,000'], ['Loan Requirement', '₹1,60,000'], ['Expected Monthly Revenue', '₹55,000'], ['Illustrative Net Profit', '₹18,000'], ['Estimated Break-even', '13 Months']]
export const financialChecks = ['Startup cost estimation', 'Working capital planning', 'EMI calculation', 'Cash-flow projection', 'Break-even analysis', 'Stress testing']
export const reportItems = ['Entrepreneur Profile', 'Location & Market Analysis', 'Recommended Business', 'Opportunity Score', 'Competitor Analysis', 'Financial Structure', 'Profitability', 'Risk Analysis', 'Scheme Matches', 'Required Documents', 'Final Recommendation']
export const principles = [['Explainable', 'Recommendations should show why a score or decision was produced.'], ['Local', "Analysis should focus on the entrepreneur's actual selected area."], ['Practical', 'Outputs should lead to actionable financial, scheme and documentation steps.'], ['Responsible', 'Official information should be source-backed and clearly distinguished from AI-generated explanation.']]
export const stateLabels = ['Continue', 'Improve', 'Expand', 'Diversify', 'Switch']
