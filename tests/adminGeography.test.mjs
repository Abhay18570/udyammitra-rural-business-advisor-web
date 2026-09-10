import './tsxLoader.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { readFileSync } from 'node:fs'
const { UiContext } = await import('../src/i18n/uiContextValue.ts')
const { AuthContext } = await import('../src/context/authContextValue.ts')
const { translations } = await import('../src/i18n/translations.ts')
const { localizeText, formatDate } = await import('../src/i18n/localize.ts')
const { StateAnalyticsView } = await import('../src/features/admin/GeographicAnalyticsPage.tsx')
const { DistrictAnalyticsView } = await import('../src/features/admin/StateAnalyticsPage.tsx')
const { GeographyChart } = await import('../src/features/admin/GeographyChart.tsx')
const { AdminDataFeedback } = await import('../src/features/admin/AdminData.tsx')
const { EntrepreneurListView, EntrepreneurFilters } = await import('../src/features/admin/EntrepreneursPage.tsx')
const { entrepreneurQuery, filtersQuery, pageQuery } = await import('../src/features/admin/entrepreneurFilters.ts')
const { statePath, entrepreneursPath, getAdminData } = await import('../src/services/adminService.ts')
const { AdminProtectedRoute } = await import('../src/routes/AdminProtectedRoute.tsx')
const { apiClient } = await import('../src/services/apiClient.ts')
const { tokenStorage } = await import('../src/services/tokenStorage.ts')

function render(element, language='en') {
 return renderToStaticMarkup(React.createElement(UiContext.Provider,{value:{language,t:translations[language],text:v=>localizeText(v,language),date:v=>formatDate(v,language)}},React.createElement(MemoryRouter,null,element)))
}
function capture(Component, props) {let tree;function Capture(){tree=Component(props);return tree}render(React.createElement(Capture));return tree}
function find(tree,predicate) {if(!tree||typeof tree!=='object')return; if(predicate(tree))return tree; for(const child of React.Children.toArray(tree.props?.children)){const match=find(child,predicate);if(match)return match}}
const states={total_entrepreneurs:4,located_entrepreneurs:3,missing_state_count:1,states_count:1,districts_count:2,states:[{state:'Test State',state_key:'test state',entrepreneur_count:3,percentage:'100.00',districts_count:2,new_enterprises:2,existing_enterprises:1}]}
const districts={state:'Test State',state_key:'test state',total_entrepreneurs:3,districts_count:2,missing_district_count:0,new_enterprises:2,existing_enterprises:1,districts:[{district:'North & East',district_key:'north & east',entrepreneur_count:2,percentage:'66.67',new_enterprises:1,existing_enterprises:1},{district:'South',district_key:'south',entrepreneur_count:1,percentage:'33.33',new_enterprises:1,existing_enterprises:0}]}
const row={full_name:'Test Entrepreneur',email:'test-list@example.com',mobile_number:'8765432101',state:'Test State',district:'North & East',taluka:null,village:'Example village',enterprise_status:'new',proposed_business:'Test shop',preferred_language:'en',created_at:'2025-01-02T00:00:00Z',profile_status:'complete'}

test('single API state produces one chart datum and one table row',()=>{
 const tree=capture(StateAnalyticsView,{data:states});const chart=find(tree,e=>e.type===GeographyChart)
 assert.equal(chart.props.rows.length,1);assert.equal(chart.props.rows[0].entrepreneur_count,3)
 const html=render(React.createElement(StateAnalyticsView,{data:states}));assert.match(html,/100.00%/);assert.match(html,/View Districts/);assert.match(html,/test%20state/)
 assert.match(html,/Some entrepreneur profiles do not have state information/)
 assert.ok(!html.includes('Maharashtra'))
})
test('bar click passes API key and accessible table provides matching route',()=>{
 let selected; const tree=capture(GeographyChart,{rows:[{key:'test state',name:'Test State',entrepreneur_count:3,percentage:'100.00'}],title:'Entrepreneurs by State',axis:'State',onSelect:key=>selected=key})
 const bar=find(tree,e=>e.props?.dataKey==='entrepreneur_count'&&typeof e.props.onClick==='function')
 bar.props.onClick({payload:{key:'test state'}});assert.equal(selected,'test state')
 assert.equal(statePath(selected),'/admin/analytics/geography/state/test%20state')
})
test('district table and chart preserve counts and encode navigation',()=>{
 const tree=capture(DistrictAnalyticsView,{data:districts});assert.equal(find(tree,e=>e.type===GeographyChart).props.rows.length,2)
 const html=render(React.createElement(DistrictAnalyticsView,{data:districts}));assert.match(html,/66.67%/);assert.match(html,/North &amp; East/);assert.match(html,/View Entrepreneurs/)
 const path=entrepreneursPath('test state','north & east');const url=new URL(path,'http://localhost');assert.equal(url.searchParams.get('state'),'test state');assert.equal(url.searchParams.get('district'),'north & east');assert.ok(html.includes('district=north+%26+east'))
})
test('geography and district empty/missing states contain no fake locations',()=>{
 assert.match(render(React.createElement(StateAnalyticsView,{data:{...states,states:[],states_count:0}})),/No entrepreneur location data/)
 assert.match(render(React.createElement(DistrictAnalyticsView,{data:{...districts,districts:[],missing_district_count:3}})),/Some entrepreneur profiles do not have district information/)
})
test('loading skeleton and safe errors',()=>{
 assert.match(render(React.createElement(AdminDataFeedback,{state:{status:'loading'},retry:()=>{},error:'Unable to load geographic analytics.'})),/aria-busy="true"/)
 for(const error of ['Unable to load geographic analytics.','Unable to load district data.','Unable to load entrepreneurs.'])assert.ok(render(React.createElement(AdminDataFeedback,{state:{status:'error'},retry:()=>{},error})).includes(error))
 assert.match(render(React.createElement(AdminDataFeedback,{state:{status:'error',code:403},retry:()=>{},error:'x'})),/You do not have permission/)
})
test('query filters are visible and preserved during pagination',()=>{
 const params=new URLSearchParams({state:'Test State',district:'North & East',search:'shop'})
 const html=render(React.createElement(EntrepreneurFilters,{params,apply:()=>{},clear:()=>{}}));assert.match(html,/value="Test State"/);assert.match(html,/value="North &amp; East"/)
 const next=pageQuery(params,2);assert.equal(next.get('page'),'2');assert.equal(next.get('district'),'North & East')
 const form=new FormData();form.set('state',' Test State ');form.set('enterprise_status','new');form.set('sort','created_asc')
 assert.equal(filtersQuery(form).get('state'),'Test State');assert.equal(filtersQuery(form).get('page'),'1');assert.equal(filtersQuery(form).get('enterprise_status'),'new')
 assert.equal(entrepreneurQuery(new URLSearchParams('page=-1')).get('page'),'1')
})
test('clear filter and pagination button events work at boundaries',()=>{
 let cleared=false;const filters=capture(EntrepreneurFilters,{params:new URLSearchParams('state=Test'),apply:()=>{},clear:()=>cleared=true});find(filters,e=>e.type==='button'&&e.props.type==='button').props.onClick();assert.ok(cleared)
 let page;const tree=capture(EntrepreneurListView,{data:{items:[row],total:21,page:1,page_size:20,total_pages:2},onPage:value=>page=value})
 const previous=find(tree,e=>e.type==='button'&&e.props.children==='Previous');assert.equal(previous.props.disabled,true)
 find(tree,e=>e.type==='button'&&e.props.children==='Next').props.onClick();assert.equal(page,2)
 const last=capture(EntrepreneurListView,{data:{items:[row],total:21,page:2,page_size:20,total_pages:2},onPage:()=>{}});assert.equal(find(last,e=>e.type==='button'&&e.props.children==='Next').props.disabled,true)
})
test('list displays operational fields, business name and profile status',()=>{
 const html=render(React.createElement(EntrepreneurListView,{data:{items:[row],total:1,page:1,page_size:20,total_pages:1},onPage:()=>{}}))
 for(const value of ['Test Entrepreneur','test-list@example.com','Test shop','Complete','Example village'])assert.ok(html.includes(value))
 assert.ok(!html.includes('password_hash'));assert.match(html,/Not Provided/)
 assert.match(render(React.createElement(EntrepreneurListView,{data:{items:[],total:0,page:1,page_size:20,total_pages:0},onPage:()=>{}})),/No entrepreneurs match these filters/)
})
test('service forwards geographic and filtered list paths through shared client',async()=>{
 const old=apiClient.defaults.adapter,oldGet=tokenStorage.get;tokenStorage.get=()=>null
 let seen;apiClient.defaults.adapter=async config=>{seen=config.url;return{data:states,status:200,statusText:'OK',headers:{},config}}
 try{assert.deepEqual(await getAdminData('analytics/states'),states);assert.equal(seen,'/admin/analytics/states');await getAdminData('entrepreneurs?state=Test&page=2');assert.equal(seen,'/admin/entrepreneurs?state=Test&page=2')}finally{apiClient.defaults.adapter=old;tokenStorage.get=oldGet}
})
for(const language of ['en','hi','mr'])test(`geographic labels translated, proper names retained: ${language}`,()=>{
 const html=render(React.createElement(StateAnalyticsView,{data:states}),language);assert.ok(html.includes('Test State'));assert.ok(html.includes(localizeText('View Districts',language)))
 for(const label of ['Entrepreneurs by District','Clear Filters','Registered Date','Profile Status','Unable to load geographic analytics.']) {assert.ok(localizeText(label,language));if(language!=='en')assert.notEqual(localizeText(label,language),label)}
})
for(const path of ['/admin/analytics/geography','/admin/entrepreneurs'])test(`USER cannot render ${path}`,()=>{
 const html=render(React.createElement(AuthContext.Provider,{value:{user:{role:'USER'},isAuthenticated:true,isLoading:false}},React.createElement(Routes,null,React.createElement(Route,{element:React.createElement(AdminProtectedRoute)},React.createElement(Route,{path:'/',element:React.createElement('p',null,'Restricted geography')})))))
 assert.ok(!html.includes('Restricted geography'))
})
test('routes, constrained mobile scrolling and stale-request cancellation wired',()=>{
 const read=name=>readFileSync(new URL('../src/'+name,import.meta.url),'utf8')
 const router=read('routes/AppRouter.tsx');for(const path of ['analytics/geography','analytics/geography/state/:stateKey','entrepreneurs'])assert.ok(router.includes(`path="${path}"`))
 const css=read('features/admin/admin.css');assert.match(css,/overflow-x:auto/);assert.match(css,/@media\(max-width:480px\)/)
 const hook=read('features/admin/useAdminData.ts');assert.match(hook,/controller.abort\(\)/);assert.match(hook,/result.path === path/)
})
