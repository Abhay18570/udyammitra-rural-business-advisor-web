import './tsxLoader.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
const { UiContext } = await import('../src/i18n/uiContextValue.ts')
const { AuthContext } = await import('../src/context/authContextValue.ts')
const { translations } = await import('../src/i18n/translations.ts')
const { localizeText } = await import('../src/i18n/localize.ts')
const { governmentSchemeMessages } = await import('../src/i18n/governmentSchemeMessages.ts')
const { GovernmentSchemeCatalogPage } = await import('../src/features/governmentSchemes/GovernmentSchemeCatalogPage.tsx')
const { SchemeCard, SchemeDetailContent, CatalogSkeleton, CatalogError } = await import('../src/features/governmentSchemes/CatalogViews.tsx')
const { readCatalogQuery, updateCatalogQuery, debounceCatalogSearch } = await import('../src/features/governmentSchemes/catalogState.ts')
const { governmentSchemeService } = await import('../src/services/governmentSchemeService.ts')
const { apiClient } = await import('../src/services/apiClient.ts')
const render = (component, language='en') => renderToStaticMarkup(React.createElement(UiContext.Provider,{value:{language,t:translations[language],text:v=>localizeText(v,language)}},React.createElement(AuthContext.Provider,{value:{isAuthenticated:false,user:null}},React.createElement(MemoryRouter,null,component))))
const scheme = {slug:'sample',scheme_name:'योजना ₹500',level:'STATE',state:'Maharashtra',categories:['Category 1','Category 2','Category 3'],tags:['Tag'],short_description:'Source preview',verification_status:'DATASET_ONLY',source_type:'DATASET',details:'Overview',benefits:'Benefit ₹500',eligibility:'Eligibility source text',application_process:'Application instructions',documents_required:'आधार',source_dataset:'fixture.csv',is_active:true,created_at:'2026-09-10',updated_at:'2026-09-10'}

test('catalog page and separate financing pathway render without login',()=>{
 const html=render(React.createElement(GovernmentSchemeCatalogPage))
 for(const label of ['Government Schemes','Your Financing Pathway','Explore Government Schemes','Search government schemes','Loading government schemes','Loading catalog filters']) assert.ok(html.includes(label),label)
})
test('card uses list preview, provenance and query-preserving detail link',()=>{
 const html=render(React.createElement(SchemeCard,{scheme,query:'state=Maharashtra&page=2'}))
 for(const label of ['योजना ₹500','Source preview','State','Maharashtra','Dataset Only','View Scheme','+1 more']) assert.ok(html.includes(label),label)
 assert.ok(html.includes('/government-schemes/sample?state=Maharashtra&amp;page=2'))
 for(const unwanted of ['Eligibility source text','Application instructions','Recommended','Approved','Apply Now']) assert.ok(!html.includes(unwanted))
})
test('Central cards omit State name and show Central badge',()=>{
 const html=render(React.createElement(SchemeCard,{scheme:{...scheme,level:'CENTRAL',state:null},query:''}))
 assert.ok(html.includes('Central'));assert.ok(!html.includes('Maharashtra'))
})
test('detail preserves prose and renders all sections without invented links',()=>{
 const html=render(React.createElement(SchemeDetailContent,{scheme}))
 for(const label of ['Scheme Overview','Benefits','Eligibility','Application Process','Documents Required','Source &amp; Verification','Benefit ₹500','आधार','fixture.csv','Official source link not available','Tag','Category 3']) assert.ok(html.includes(label),label)
 assert.ok(!html.includes('Apply Now'));assert.ok(!html.includes('href='))
})
test('verified detail adjusts disclaimer without claiming eligibility',()=>{
 const html=render(React.createElement(SchemeDetailContent,{scheme:{...scheme,verification_status:'VERIFIED'}}))
 assert.ok(html.includes('This record is marked verified.'));assert.ok(!html.includes('Eligible'))
})
test('loading and friendly retry render accessible status/alert',()=>{
 assert.ok(render(React.createElement(CatalogSkeleton,{label:'Loading scheme details'})).includes('role="status"'))
 const html=render(React.createElement(CatalogError,{label:'Unable to load government schemes.',retry:()=>{}}))
 assert.ok(html.includes('role="alert"'));assert.ok(html.includes('Retry'))
})
for(const language of ['en','hi','mr']) test(`${language} translates catalog chrome while preserving source data`,()=>{
 for(const row of Object.values(governmentSchemeMessages)) { assert.ok(row[language]); if(language!=='en') assert.notEqual(localizeText(row.en,language),row.en,row.en) }
 const html=render(React.createElement(SchemeCard,{scheme,query:''}),language)
 assert.ok(html.includes('योजना ₹500')); assert.ok(html.includes('Maharashtra'));assert.ok(html.includes(localizeText('Dataset Only',language)))
})
for(const key of ['level','state','category','verification_status','sort','search']) test(`${key} changes reset page and preserve other URL parameters`,()=>{
 const next=updateCatalogQuery(new URLSearchParams('page=9&category=Education'),key,key==='level'?'STATE':'test')
 assert.equal(next.get('page'),'1');if(key!=='category') assert.equal(next.get('category'),'Education')
})
test('Central removes state; malformed URL values normalize safely',()=>{
 const next=updateCatalogQuery(new URLSearchParams('state=Maharashtra&page=3'),'level','CENTRAL')
 assert.equal(next.has('state'),false)
 const query=readCatalogQuery(new URLSearchParams('level=CENTRAL&state=Maharashtra&page=-5&sort=unsafe&verification_status=unsafe'))
 assert.equal(query.state,undefined);assert.equal(query.page,1);assert.equal(query.sort,'name_asc');assert.equal(query.verification_status,undefined)
})
test('pagination retains filters and refresh URL reconstructs backend query',()=>{
 const params=updateCatalogQuery(new URLSearchParams('search=dairy&level=STATE&state=Maharashtra'),'page','2')
 const query=readCatalogQuery(params)
 assert.equal(query.page,2);assert.equal(query.search,'dairy');assert.equal(query.state,'Maharashtra');assert.equal(query.page_size,20)
})
test('search debounce waits 400ms and cancels superseded work',t=>{
 t.mock.timers.enable({apis:['setTimeout']})
 let calls=0
 const cancel=debounceCatalogSearch(()=>calls++)
 t.mock.timers.tick(399);assert.equal(calls,0);cancel();t.mock.timers.tick(1);assert.equal(calls,0)
 debounceCatalogSearch(()=>calls++);t.mock.timers.tick(400);assert.equal(calls,1)
})
test('service reuses API client with typed endpoints, params and abort signals',async()=>{
 const original=apiClient.get;const calls=[]
 apiClient.get=async (...args)=>{calls.push(args);return {data:{items:[]}}}
 try{
  const signal=new AbortController().signal;const query=readCatalogQuery(new URLSearchParams('search=dairy'))
  await governmentSchemeService.list(query,signal);await governmentSchemeService.filters(signal);await governmentSchemeService.detail('slug/value',signal)
  assert.deepEqual(calls.map(c=>c[0]),['/government-schemes','/government-schemes/filters','/government-schemes/slug%2Fvalue'])
  assert.equal(calls[0][1].params.search,'dairy');assert.ok(calls.every(c=>c[1].signal===signal))
 }finally{apiClient.get=original}
})
