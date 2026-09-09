import test from 'node:test'
import assert from 'node:assert/strict'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import './tsxLoader.mjs'
const { NearbyBusinessEvidence, NearbyResults } = await import('../src/features/marketAnalysis/NearbyBusinessEvidence.tsx')
const { UiContext } = await import('../src/i18n/uiContextValue.ts')
const { translations } = await import('../src/i18n/translations.ts')
const { localizeText, formatDate } = await import('../src/i18n/localize.ts')
const { runtimeMessages } = await import('../src/i18n/runtimeMessages.ts')
const { initialNearbyState, nearbyReducer, validBusinessQuery, normalizeBusinessQuery } = await import('../src/features/marketAnalysis/nearbyState.ts')
const render = (element, language='en') => renderToStaticMarkup(React.createElement(UiContext.Provider,{value:{language,t:translations[language],text:v=>localizeText(v,language),date:v=>formatDate(v,language)}},React.createElement(MemoryRouter,null,element)))
const evidence = provider => {
 const poi = {provider,external_type:provider==='GOOGLE_PLACES'?'place':'node',external_id:'safe-id',name:'Hari OM',latitude:19,longitude:73,classification:'DIRECT_COMPETITOR',distance_km:'1.00',distance_meters:1000,matching_evidence:[{key:'shop',value:'general'}],normalized_address:{formatted_address:'Original Address'}}
 return {business_query:'Kirana Store',business:{slug:null,display_name:'Kirana Store'},location:{latitude:19,longitude:73,display_name:'Original Village'},radius:{selected_km:5,selected_meters:5000},competitors:[poi],related_businesses:[],summary:{direct_competitors:1,related_businesses:0,nearest_direct_competitor:poi},source:{provider,mode:'LIVE',cache_status:'FRESH_FETCH',fetched_at:'2026-09-09',expires_at:'2026-09-09'},quality:{attribution:provider==='GOOGLE_PLACES'?'Google Maps':'OSM',warnings:[]}}
}
test('free text, optional suggestions, blank disabled and all ten radii',()=>{
 const html=render(React.createElement(NearbyBusinessEvidence))
 assert.match(html, /<input[^>]*id="nearby-business"[^>]*type="text"/)
 assert.doesNotMatch(html, /<select[^>]*id="nearby-business"/)
 assert.match(html, /<datalist/)
 assert.match(html, /disabled=""/)
 for(let n=1;n<=10;n++) assert.match(html,new RegExp(`<option value="${n}"`))
 for(const value of ['', ' ', 'a']) assert.equal(validBusinessQuery(value),false)
 assert.equal(normalizeBusinessQuery('  Agricultural   Equipment Rental '),'Agricultural Equipment Rental')
})
test('arbitrary query and loaded evidence survive language and radius changes',()=>{
 const result=evidence('GOOGLE_PLACES')
 let state=nearbyReducer(initialNearbyState,{type:'query',value:'Kirana Store'})
 state=nearbyReducer(state,{type:'result',value:result})
 for(const language of ['en','hi','mr']) {
   const html=render(React.createElement(NearbyResults,{result:state.result}),language)
   assert.match(html,/Kirana Store/); assert.match(html,/Hari OM/); assert.match(html,/Original Address/)
   assert.match(html,/Google Places/); assert.doesNotMatch(html,/openstreetmap.org|shop=general/)
   assert.match(html,/query_place_id=safe-id/)
   assert.ok(html.includes(localizeText(runtimeMessages.marketText.coverage.en,language)))
 }
 const changed=nearbyReducer(state,{type:'radius',value:10})
 assert.equal(changed.query,'Kirana Store'); assert.equal(changed.result,result)
 const arbitrary=nearbyReducer(changed,{type:'query',value:'Agricultural Equipment Rental'})
 assert.equal(arbitrary.query,'Agricultural Equipment Rental'); assert.equal(arbitrary.result,result)
})
test('Overpass retains OSM link and tag evidence',()=>{
 const html=render(React.createElement(NearbyResults,{result:evidence('OPENSTREETMAP_OVERPASS')}))
 assert.match(html,/openstreetmap.org\/node\/safe-id/); assert.match(html,/shop=general/)
 assert.doesNotMatch(html,/query_place_id/)
})
test('every new message translates in Hindi and Marathi',()=>{
 for(const row of Object.values(runtimeMessages.marketText)) for(const language of ['en','hi','mr']) {
   assert.ok(row[language]); assert.equal(localizeText(row.en,language),row[language])
 }
 for(const code of ['overpass_catalog_required','business_query_mismatch','spatial_query_failed','google_history_unavailable']) for(const language of ['hi','mr']) {
   const row=runtimeMessages.errors[code]; assert.notEqual(localizeText(row.en,language),row.en)
 }
})

const { NearbySearchControls } = await import('../src/features/marketAnalysis/NearbySearchControls.tsx')
const { readFileSync } = await import('node:fs')
const findElement = (node, predicate) => {
 if (!node || typeof node !== 'object') return undefined
 if (predicate(node)) return node
 for (const child of React.Children.toArray(node.props?.children)) {
   const match = findElement(child, predicate)
   if (match) return match
 }
}
test('control events update query, enable submission and preserve state across locales/radii',()=>{
 let state={...initialNearbyState}
 let touched=false
 let language='en'
 let running=false
 const controls=()=>NearbySearchControls({
   ...state, businesses:[], running, queryInvalid:touched&&!validBusinessQuery(state.query),
   labels:translations[language].nearbyMarket, textUi:v=>localizeText(v,language),
   onQueryBlur:()=>{touched=true},
   onQueryChange:value=>{state=nearbyReducer(state,{type:'query',value})},
   onRadiusChange:value=>{state=nearbyReducer(state,{type:'radius',value})}, onRun:()=>{},
 })
 const input=()=>findElement(controls(),e=>e.props.id==='nearby-business')
 const button=()=>findElement(controls(),e=>e.props.className==='nearby-submit')
 assert.equal(input().type,'input')
 assert.equal(input().props.disabled,undefined)
 assert.equal(input().props.readOnly,undefined)
 assert.equal(input().props.tabIndex,undefined)
 assert.equal(button().props.disabled,true)
 for(const query of ['Kirana Store','Tea Stall','Mobile Repair Shop','Medical Store','Hardware Shop','Bakery','Beauty Parlour']) {
   input().props.onChange({target:{value:query}})
   assert.equal(state.query,query)
   assert.equal(input().props.value,query)
   assert.equal(button().props.disabled,false)
 }
 input().props.onChange({target:{value:'Kirana Store'}})
 findElement(controls(),e=>e.props.id==='nearby-radius').props.onChange({target:{value:'5'}})
 for(language of ['en','hi','mr']) {
   assert.equal(input().props.value,'Kirana Store')
   assert.equal(state.radius,5)
   assert.equal(button().props.disabled,false)
   assert.match(render(controls(),language),/<label for="nearby-business">/)
 }
 running=true; assert.equal(button().props.disabled,true); running=false
 input().props.onChange({target:{value:' '}}); input().props.onBlur()
 assert.equal(button().props.disabled,true)
 assert.equal(input().props['aria-invalid'],true)
 assert.equal(input().props['aria-describedby'],'nearby-business-hint nearby-business-error')
 const html=render(controls(),'mr')
 assert.ok(html.includes(localizeText('Enter a business idea with 2–200 characters.','mr')))
 input().props.onChange({target:{value:'Bakery'}})
 assert.equal(input().props['aria-invalid'],false)
})
test('grouped controls retain responsive sizing and visible input/focus styles',()=>{
 const html=render(React.createElement(NearbyBusinessEvidence))
 assert.match(html,/class="nearby-field nearby-field--business"/)
 assert.match(html,/class="nearby-field nearby-field--radius"/)
 assert.match(html,/<label for="nearby-business">/)
 const css=readFileSync(new URL('../src/index.css',import.meta.url),'utf8')
 assert.match(css,/\.nearby-field--business\s*\{[^}]*flex:1 1 320px/)
 assert.match(css,/\.nearby-field input,\s*\.nearby-field select\s*\{[^}]*width:100%[^}]*min-width:0[^}]*border:1px[^}]*background:#fff/)
 assert.match(css,/\.nearby-field input:focus-visible/)
 assert.match(css,/@media \(max-width:767px\)\s*\{\s*\.nearby-controls\s*\{[^}]*flex-direction:column/)
})
