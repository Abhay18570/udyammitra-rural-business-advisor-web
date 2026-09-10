import './tsxLoader.mjs'
import { registerHooks } from 'node:module'
registerHooks({load(url,context,next){return url.endsWith('.css')?{format:'module',source:'export default {}',shortCircuit:true}:next(url,context)}})
import test from 'node:test'
import assert from 'node:assert/strict'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { readFileSync } from 'node:fs'
const { SwotAnalysis, AnalysisSummary } = await import('../src/features/businessAnalysis/SwotAnalysis.tsx')
const { BusinessOverview } = await import('../src/features/businessAnalysis/BusinessOverview.tsx')
const { AnalysisResults } = await import('../src/features/businessAnalysis/BusinessAnalysisPage.tsx')
const { findingSources } = await import('../src/features/businessAnalysis/swotPresentation.ts')
const { UiContext } = await import('../src/i18n/uiContextValue.ts')
const { localizeText,formatDate } = await import('../src/i18n/localize.ts')
const { translations } = await import('../src/i18n/translations.ts')
function render(element,language='en'){return renderToStaticMarkup(React.createElement(UiContext.Provider,{value:{language,t:translations[language],text:v=>localizeText(v,language),date:v=>formatDate(v,language)}},React.createElement(MemoryRouter,null,element)))}
function finding(id,source='BUSINESS_BASELINE',evidence='catalog.baseline_swot'){return{id,rule_id:id,title:`Finding ${id}`,explanation:`Description ${id}`,source_type:source,importance:'LOW',evidence_ids:[evidence],finding_ids:[],limitations:['General guidance only.']}}
const swot=Object.fromEntries(['strengths','weaknesses','opportunities','threats'].map(key=>[key,Array.from({length:4},(_,i)=>finding(`${key}-${i}`))]))
swot.strengths.push(finding('profile-skill','PROFILE','profile.skills'))
swot.opportunities.push(finding('mapped-related','MARKET','market.related'))
swot.weaknesses.push({...finding('funding-gap','FINANCIAL','financial.setup'),importance:'HIGH'})
const result={id:'d96b514b-0dd0-48ab-a0ad-30b49846012a',created_at:'2026-09-10T12:00:00Z',business:{name:'Kirana / General Store'},swot,evidence:[{id:'catalog.baseline_swot',source_ref:'business-baseline-v1',source_kind:'BUSINESS_BASELINE',value:{},limitations:[]},{id:'market.related',source_ref:'OPENSTREETMAP',source_kind:'OBSERVED_LOCAL',radius_km:5,value:[],limitations:[]}],
 market_context:{radius:{selected_km:5,selected_meters:5000},source:{mode:'LIVE',cache_status:'FRESH_CACHE',provider:'OVERPASS',fetched_at:'2026-09-10T12:00:00Z'},location:{latitude:null,longitude:null,display_name:'Test locality'},quality:{warnings:[],attribution:'OpenStreetMap'},competitors:[],related_businesses:[]},
 competition:{selected_radius_km:5,direct_count:0,related_count:0,nearest:null,average_distance:null,mapped_density:0,classification:'NO_MAPPED_DIRECT_EVIDENCE',classification_basis:'No mapped records',distance_bands:[],evidence_ids:[]},
 local_threats:[{id:'threat.test',title:'Detailed test threat',description:'Detailed risk explanation',evidence_kind:'SELF_REPORTED',severity:'MEDIUM',likelihood:null,severity_reason:null,mitigation:'Check assumptions',evidence_ids:[],coverage_warnings:[]}],
 pricing:{status:'INSUFFICIENT_PRICING_ASSUMPTIONS',strategy:'Check assumptions',items:[],assumptions:[],missing_assumptions:[],warnings:[],demographic_status:'UNAVAILABLE',purchasing_power_status:'UNAVAILABLE',local_price_status:'UNAVAILABLE'},quality:{warnings:{},rule_versions:{swot:'swot-v2'},context_hash:'test-context'}}
for(const quadrant of ['strengths','weaknesses','opportunities','threats'])test(`${quadrant} semantic heading and accent class`,()=>{
 const html=render(React.createElement(SwotAnalysis,{result}));assert.ok(html.includes(`swot-quadrant--${quadrant}`));assert.ok(html.includes(`id="swot-${quadrant}"`));assert.match(html,/<ul class="swot-findings">/)
})
test('finding titles/descriptions and all provenance layers visible',()=>{
 const html=render(React.createElement(SwotAnalysis,{result}));for(const value of ['Finding strengths-0','Description strengths-0','Business baseline guidance','Profile evidence','Market evidence','Financial evidence','High priority'])assert.ok(html.includes(value))
 assert.ok(!html.includes('No supported finding for this quadrant.'));assert.ok(!html.includes('View threat finding'))
 assert.match(html,/<details class="swot-evidence"><summary>Evidence details/);assert.match(html,/profile.skills/);assert.match(html,/business-baseline-v1/)
})
test('disclosure distinguishes baseline from local evidence',()=>{
 const html=render(React.createElement(SwotAnalysis,{result}));assert.match(html,/Baseline findings describe common business characteristics/);assert.match(html,/lang="en"/)
})
test('snapshot identity is inside collapsed details, saved date and derived summary visible',()=>{
 const html=render(React.createElement(AnalysisSummary,{result}));assert.match(html,/Analysis saved/);assert.match(html,/2026/);assert.match(html,/<dd>19<\/dd>/)
 const details=html.match(/<details>[\s\S]*?<\/details>/)[0];assert.ok(details.includes(result.id));assert.ok(!html.replace(details,'').includes(result.id))
})
test('empty and old snapshot provenance fallbacks remain valid',()=>{
 const html=render(React.createElement(SwotAnalysis,{result:{...result,swot:{}}}));assert.equal((html.match(/No supported finding for this quadrant/g)||[]).length,4)
 const old={...finding('old'),source_type:undefined,evidence_ids:['profile.skills']};assert.deepEqual(findingSources(old),['PROFILE'])
 assert.deepEqual(findingSources({...old,evidence_ids:['catalog.risks']}),['CATALOG'])
})
test('detailed Threat Analysis retained without duplicated SWOT paragraphs',()=>{
 const dynamic={...finding('threat','MARKET','market.related'),finding_ids:['threat.test'],explanation:'Dynamic threat detail'}
 const html=render(React.createElement(AnalysisResults,{result:{...result,swot:{...swot,threats:[dynamic]}}}))
 assert.match(html,/Local Threats/);assert.match(html,/Detailed test threat/);assert.match(html,/Check assumptions/);assert.match(html,/href="#threat.test"/)
 assert.match(html,/<summary>Evidence details<\/summary><p>Dynamic threat detail/)
})
const financial={business:{name:'Kirana / General Store'},availableMarginCapital:'50000.25',feasibleProjectCost:'500002.50'}
test('business overview preserves exact INR formatting and generate/refresh labels',()=>{
 for(const hasAnalysis of [false,true]){
  const html=render(React.createElement(BusinessOverview,{financial,radius:5,running:false,hasAnalysis,onRadius:()=>{},onGenerate:()=>{}}))
  assert.ok(html.includes('₹50,000.25'));assert.ok(html.includes('₹5,00,002.50'));assert.ok(html.includes(hasAnalysis?'Refresh Business Analysis':'Generate Business Analysis'))
 }
})
function find(tree,predicate){if(!tree||typeof tree!=='object')return;if(predicate(tree))return tree;for(const child of React.Children.toArray(tree.props?.children)){const match=find(child,predicate);if(match)return match}}
test('generate and radius callbacks retain behavior; running disables controls',()=>{
 let called=false,radius,tree
 function Capture(){tree=BusinessOverview({financial,radius:5,running:false,hasAnalysis:true,onRadius:v=>radius=v,onGenerate:()=>called=true});return tree}
 render(React.createElement(Capture));find(tree,e=>typeof e.props?.onClick==='function').props.onClick();assert.ok(called)
 find(tree,e=>e.type==='select').props.onChange({target:{value:'7'}});assert.equal(radius,7)
 const html=render(React.createElement(BusinessOverview,{financial,radius:5,running:true,hasAnalysis:false,onRadius:()=>{},onGenerate:()=>{}}));assert.match(html,/<select disabled=""/);assert.match(html,/Analysing evidence/)
})
for(const language of ['en','hi','mr'])test(`SWOT chrome ${language}, curated prose remains English`,()=>{
 const html=render(React.createElement(SwotAnalysis,{result}),language);assert.ok(html.includes(localizeText('Business baseline guidance',language)));assert.ok(html.includes('Description strengths-0'))
 for(const label of ['Evidence details','Your Contribution','Analysis saved','SWOT Findings'])if(language!=='en')assert.notEqual(localizeText(label,language),label)
})
test('responsive grid, neutral cards and focus styles',()=>{
 const css=readFileSync(new URL('../src/features/businessAnalysis/swot.css',import.meta.url),'utf8');assert.match(css,/grid-template-columns:repeat\(2,minmax\(0,1fr\)\)/);assert.match(css,/@media\(max-width:700px\)/);assert.match(css,/overflow-wrap:anywhere/);assert.match(css,/:focus-visible/);assert.ok(!css.includes('min-height'))
})
