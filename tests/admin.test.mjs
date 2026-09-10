import './tsxLoader.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { registerHooks } from 'node:module'
import { readFileSync } from 'node:fs'
registerHooks({ load(url, context, next) { return url.endsWith('.css') ? { format:'module', source:'export default {}', shortCircuit:true } : next(url,context) } })
const { AdminOverviewView } = await import('../src/features/admin/AdminDashboardPage.tsx')
const { AdminProtectedRoute } = await import('../src/routes/AdminProtectedRoute.tsx')
const { AdminDashboardLayout } = await import('../src/layouts/AdminDashboardLayout.tsx')
const { loginDestination } = await import('../src/routes/roleRouting.ts')
const { AuthContext } = await import('../src/context/authContextValue.ts')
const { UiContext } = await import('../src/i18n/uiContextValue.ts')
const { localizeText } = await import('../src/i18n/localize.ts')
const { translations } = await import('../src/i18n/translations.ts')
const { getAdminOverview } = await import('../src/services/adminService.ts')
const { apiClient } = await import('../src/services/apiClient.ts')
const { tokenStorage } = await import('../src/services/tokenStorage.ts')
function render(element, { role='ADMIN', loading=false, language='en' }={}) {
  return renderToStaticMarkup(React.createElement(UiContext.Provider,{value:{text:v=>localizeText(v,language), language,t:translations[language],setLanguage:()=>{}}},
    React.createElement(AuthContext.Provider,{value:{user:role?{role,email:'officer@example.com'}:null,isAuthenticated:!!role,isLoading:loading,logout:()=>{}}},React.createElement(MemoryRouter,null,element))))
}
const data={total_registered_users:19,total_entrepreneurs:13,profiles_pending:6,new_enterprises:8,existing_enterprises:5,states_count:3,districts_count:7}
const view=state=>React.createElement(AdminOverviewView,{state,retry:()=>{}})
for(const role of ['ADMIN','SUPER_ADMIN','USER',null]) test(`admin guard: ${role}`,()=>{
 const html=render(React.createElement(Routes,null,React.createElement(Route,{element:React.createElement(AdminProtectedRoute)},React.createElement(Route,{path:'/',element:React.createElement('p',null,'Protected officer content')}))),{role})
 assert.equal(html.includes('Protected officer content'),role==='ADMIN'||role==='SUPER_ADMIN')
})
test('guard renders no protected content while restoring',()=>{
 const html=render(React.createElement(AdminProtectedRoute),{loading:true});assert.match(html,/Restoring your session/)
})
test('login destinations preserve user flow and separate officers',()=>{
 assert.equal(loginDestination('USER'),'/dashboard');assert.equal(loginDestination('USER','/financial-plan'),'/financial-plan')
 assert.equal(loginDestination('USER','/admin/dashboard'),'/dashboard');assert.equal(loginDestination('USER','//example.com'),'/dashboard')
 for(const role of ['ADMIN','SUPER_ADMIN']) assert.equal(loginDestination(role,'/financial-plan'),'/admin/dashboard')
})
test('service reads overview through shared authenticated client',async()=>{
 const previous=apiClient.defaults.adapter
 const previousGet=tokenStorage.get;tokenStorage.get=()=>null
 apiClient.defaults.adapter=async config=>{assert.equal(config.url,'/admin/overview');return {data,status:200,statusText:'OK',headers:{},config}}
 try {assert.deepEqual(await getAdminOverview(),data)}finally{apiClient.defaults.adapter=previous;tokenStorage.get=previousGet}
})
test('KPI cards render returned API values',()=>{
 const html=render(view({status:'ready',data}));for(const value of Object.values(data))assert.ok(html.includes(`<strong>${value}</strong>`))
 assert.equal((html.match(/<article/g)||[]).length,7)
})
test('loading skeleton contains no fake numeric totals',()=>{
 const html=render(view({status:'loading'}));assert.match(html,/aria-busy="true"/);assert.match(html,/officer-skeleton/);assert.ok(!html.includes('<strong>0</strong>'))
})
test('empty and pending profiles have distinct messages',()=>{
 const zero=Object.fromEntries(Object.keys(data).map(k=>[k,0]))
 assert.match(render(view({status:'ready',data:zero})),/No entrepreneurs have registered yet/)
 assert.match(render(view({status:'ready',data:{...zero,total_registered_users:2,profiles_pending:2}})),/Registered users have not created entrepreneur profiles yet/)
})
test('safe error and permission states',()=>{
 assert.match(render(view({status:'error',forbidden:false})),/Unable to load entrepreneurship statistics/)
 assert.match(render(view({status:'error',forbidden:true})),/You do not have permission/)
})
for(const language of ['en','hi','mr'])test(`overview localized in ${language}`,()=>{
 const html=render(view({status:'ready',data}),{language});assert.ok(html.includes(localizeText('Total Registered Users',language)))
 if(language!=='en')assert.ok(!html.includes('Total Registered Users'))
})
test('dedicated sidebar has dashboard and logout without entrepreneur actions',()=>{
 const html=render(React.createElement(AdminDashboardLayout))
 assert.match(html,/UdyamMitra/)
 assert.match(html,/Rural Business Advisory Platform/)
 assert.match(html,/ग्रामीण उद्यम मार्गदर्शन/)
 assert.match(html,/Government Officer Portal/)
 assert.match(html,/Logout/)
 for(const label of ['My Financial Plan','Business Opportunities','Market Analysis'])assert.ok(!html.includes(label))
 const source=readFileSync(new URL('../src/layouts/AdminDashboardLayout.tsx',import.meta.url),'utf8')
 assert.match(source,/logout\(\); navigate\('\/login'/)
 assert.ok(!source.includes('userNavigation'))
})

test('admin layout header contains working language selector with all locales',()=>{
 const html=render(React.createElement(AdminDashboardLayout))
 assert.match(html,/<select[^>]*aria-label="[^"]*"[^>]*>/)
 assert.match(html,/<option value="en"[^>]*>English<\/option>/)
 assert.match(html,/<option value="hi"[^>]*>हिन्दी<\/option>/)
 assert.match(html,/<option value="mr"[^>]*>मराठी<\/option>/)
})

test('admin CSS styles high-contrast sidebar branding and header language selector',()=>{
 const css=readFileSync(new URL('../src/features/admin/admin.css',import.meta.url),'utf8')
 assert.match(css,/\.officer-sidebar\s+\.brand\s+strong\s*\{[^}]*color:\s*#ffffff/)
 assert.match(css,/\.officer-sidebar\s+\.brand\s+small\s*\{[^}]*color:\s*#dce8f2/)
 assert.match(css,/\.officer-sidebar\s+\.brand\s+em\s*\{[^}]*color:\s*#afd2bd/)
 assert.match(css,/\.officer-sidebar\s*>\s*p\s*\{[^}]*color:\s*#e2edf6/)
 assert.match(css,/\.officer-header\s+\.language-selector\s+select\s*\{[^}]*background-color:\s*#ffffff/)
 assert.match(css,/\.officer-header\s+\.language-selector\s+select\s*\{[^}]*color:\s*#17324d/)
 assert.match(css,/\.officer-header\s+\.language-selector\s+select\s*\{[^}]*min-height:\s*42px/)
 assert.match(css,/@media\(max-width:600px\)\s*\{[^}]*\.officer-header\s*\{[^}]*flex-direction:\s*column/)
})

