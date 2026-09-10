// Optional real-browser verification; no browser dependency is added to the app.
// PLAYWRIGHT_MODULE=/path/to/playwright/index.mjs node tests/governmentSchemes.browser.mjs
import assert from 'node:assert/strict'
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || 'playwright')
const origin = process.env.CATALOG_WEB_ORIGIN || 'http://127.0.0.1:5173'
const api = process.env.CATALOG_API_ORIGIN || 'http://127.0.0.1:8000/api/v1'
const browser = await chromium.launch({headless:true})
const page = await browser.newPage({viewport:{width:1440,height:1000}})
page.setDefaultTimeout(15000)
const errors=[]
page.on('pageerror',error=>errors.push(error.message))
const get = async path => { const response=await page.request.get(api+path);assert.equal(response.status(),200);return response.json() }
const waitList = () => page.locator('.gc-grid .gc-card').first().waitFor()
try {
 const all=await get('/government-schemes')
 await page.goto(origin+'/government-schemes')
 await waitList()
 assert.ok((await page.locator('.gc-explore [role=status]').innerText()).includes(String(all.total)))
 assert.equal(await page.locator('.gc-card').count(),all.items.length)
 assert.equal(await page.getByRole('heading',{name:'Your Financing Pathway',exact:true}).count(),1)
 const requests=[]
 page.on('request',request=>{const url=new URL(request.url());if(url.pathname.endsWith('/government-schemes')) requests.push(url)})
 const search=page.getByRole('searchbox',{name:'Search government schemes',exact:true})
 await search.fill('dai');await page.waitForTimeout(150);await search.fill('dairy')
 await page.waitForTimeout(200);assert.equal(requests.filter(u=>u.searchParams.has('search')).length,0)
 await page.waitForURL('**search=dairy**');await waitList()
 const dairy=await get('/government-schemes?search=dairy')
 await page.waitForFunction(total=>document.querySelector('.gc-explore [role=status]')?.textContent.includes(`of ${total} schemes`),dairy.total)
 assert.ok((await page.locator('.gc-explore [role=status]').innerText()).includes(String(dairy.total)))
 assert.equal(requests.filter(u=>u.searchParams.get('search')==='dairy').length,1)
 // Browser back must not replay a pending/stale draft search.
 await page.goBack();await waitList();await page.waitForTimeout(500)
 assert.equal(new URL(page.url()).search,'');assert.equal(await search.inputValue(),'')
 await page.getByLabel('Scheme Level',{exact:true}).selectOption('STATE')
 await page.getByLabel('State',{exact:true}).selectOption('Maharashtra')
 await waitList()
 const state=await get('/government-schemes?level=STATE&state=Maharashtra')
 await page.waitForFunction(total=>document.querySelector('.gc-explore [role=status]')?.textContent.includes(`of ${total} schemes`),state.total)
 assert.ok(state.items.every(s=>s.state==='Maharashtra'))
 assert.equal(await page.locator('.gc-card h3').first().innerText(),state.items[0].scheme_name)
 await page.getByRole('button',{name:'Next',exact:true}).click();await page.waitForURL('**page=2**');await page.waitForFunction(()=>document.querySelector('.gc-explore [role=status]')?.textContent.includes('Showing 21–'));await waitList()
 const before=page.url()
 const title=await page.locator('.gc-card h3').first().innerText()
 const href=await page.locator('.gc-card a').first().getAttribute('href')
 const slug=decodeURIComponent(new URL(href,origin).pathname.split('/').at(-1))
 const detail=await get('/government-schemes/'+encodeURIComponent(slug))
 await page.locator('.gc-card a').first().click()
 await page.locator('.gc-detail').getByRole('heading',{name:title,exact:true}).waitFor()
 const prose=await page.locator('.gc-prose').allTextContents()
 assert.deepEqual(prose.slice(0,3),[detail.details,detail.benefits,detail.eligibility])
 assert.equal(await page.getByRole('link',{name:'Apply Now',exact:true}).count(),0)
 assert.ok((await page.locator('.gc-detail').innerText()).includes('Official source link not available'))
 await page.goBack();await waitList();assert.equal(page.url(),before)
 await page.reload();await waitList();assert.equal(page.url(),before)
 await page.getByLabel('Scheme Level',{exact:true}).selectOption('CENTRAL');await waitList()
 assert.equal(await page.getByLabel('State',{exact:true}).isDisabled(),true)
 assert.equal(new URL(page.url()).searchParams.has('state'),false)
 for(const [label,value] of [['Category',all.items[0].categories[0]],['Verification Status','DATASET_ONLY'],['Sort','name_desc']]) {
  await page.getByLabel(label,{exact:true}).selectOption(value)
  await page.waitForTimeout(150)
 }
 await page.getByRole('button',{name:'Clear filters',exact:true}).click();await waitList()
 for(const width of [1440,768,390]) {
  await page.setViewportSize({width,height:1000})
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth <= window.innerWidth),`overflow at ${width}`)
  const columns=await page.locator('.gc-grid').evaluate(el=>getComputedStyle(el).gridTemplateColumns.split(' ').length)
  assert.equal(columns,width===1440?3:width===768?2:1)
 }
 await page.screenshot({path:'/private/tmp/government-schemes-mobile.png',fullPage:true})
 await page.setViewportSize({width:1440,height:1000})
 await page.screenshot({path:'/private/tmp/government-schemes-desktop.png',fullPage:true})
 // Controlled API failures/loading/empty responses exercise client states only.
 await page.route('**/api/v1/government-schemes?**',route=>route.fulfill({status:503,json:{detail:'internal marker'}}))
 await search.fill('failure')
 await page.getByText('Unable to load government schemes.',{exact:true}).waitFor()
 assert.equal(await page.getByText('internal marker').count(),0)
 await page.unroute('**/api/v1/government-schemes?**')
 await search.fill('zzzzunmatchablescheme')
 await page.getByText('No schemes match your filters.',{exact:true}).waitFor()
 assert.equal(await page.locator('.gc-card').count(),0)
 await page.route('**/api/v1/government-schemes?**',async route=>{await new Promise(resolve=>setTimeout(resolve,700));await route.continue()})
 await search.fill('dairy')
 await page.getByRole('status',{name:'Loading government schemes',exact:true}).waitFor()
 await waitList()
 await page.unroute('**/api/v1/government-schemes?**')
 for(const [language,label] of [['hi','सरकारी योजनाएँ खोजें'],['mr','शासकीय योजना शोधा']]) {
  await page.evaluate(language=>localStorage.setItem('udyammitra-language',language),language)
  await page.reload();await waitList()
  assert.equal(await page.getByRole('heading',{name:label,exact:true}).count(),1)
 }
 // Saved financial context is mocked only here; catalog data continues to use the real API.
 await page.route('**/api/v1/auth/me', route=>route.fulfill({json:{id:'catalog-browser-user',full_name:'Catalog Test',email:'catalog@example.test',mobile_number:'9000000000',preferred_language:'en',role:'USER',is_active:true}}))
 await page.route('**/api/v1/profile**', route=>route.fulfill({status:404,json:{detail:'Fixture has no profile'}}))
 const rules=[
  {type:'MICRO_FINANCE',displayName:'Micro Finance',projectCostMin:'0.00',projectCostMax:'140000.00',projectCostMinInclusive:false,projectCostMaxInclusive:true,maximumLoanAmount:'125000.00',annualInterestRatePercent:'6.50',tenureMonths:36,moratoriumMonths:3},
  {type:'TERM_LOAN',displayName:'Term Loan',projectCostMin:'140000.00',projectCostMax:'5000000.00',projectCostMinInclusive:false,projectCostMaxInclusive:true,maximumLoanAmount:'4500000.00',annualInterestRatePercent:'8.00',tenureMonths:84,moratoriumMonths:6},
 ]
 let chosen=rules[0]
 await page.route('**/api/v1/schemes/guidance', route=>route.fulfill({json:{source:'SAVED_FINANCIAL_PLAN',rules,sourceObservedAt:'2026-09-10T00:00:00Z',setupFundingGap:'0.00',fundingSharePercent:'90',contributionSharePercent:'10',result:{scheme:chosen,schemeStatus:'ELIGIBLE',projectCost:chosen.type==='MICRO_FINANCE'?'100000.00':'500000.00',beneficiaryContribution:chosen.type==='MICRO_FINANCE'?'10000.00':'50000.00',financingRequirement:chosen.type==='MICRO_FINANCE'?'90000.00':'450000.00',indicativeFinancedPrincipal:chosen.type==='MICRO_FINANCE'?'90000.00':'450000.00',schemeFinancingGap:'0.00',additionalContributionRequired:'0.00',eligibilityReasons:[],warnings:[],nextSteps:[]}}}))
 await page.evaluate(()=>{localStorage.setItem('udyammitra-language','en');sessionStorage.setItem('udyammitra_access_token','browser-fixture-only')})
 for(const rule of rules) {
  chosen=rule
  await page.goto(origin+'/schemes')
  await page.locator('.gc-pathway .scheme-panel--recommended').getByRole('heading',{name:rule.displayName,exact:true}).waitFor()
  assert.ok((await page.locator('.gc-pathway').innerText()).includes('Saved Financial Plan'))
  await waitList()
  assert.equal(await page.locator('.gc-explore').getByText('Eligible',{exact:true}).count(),0)
 }
 assert.deepEqual(errors,[])
 console.log(JSON.stringify({result:'PASS',total:all.total,dairy:dairy.total,maharashtra:state.total,checks:['real API totals','400ms debounce','browser back and refresh','all filters and sorting','pagination','detail/API prose parity','provenance','public route','loading/error/empty','EN/HI/MR','desktop/tablet/mobile overflow','saved Micro Finance and Term Loan rendering (mock guidance)']},null,2))
} catch(error) {
 console.log('Browser check context:', page.url(), (await page.locator('.gc-explore').innerText().catch(()=>'')).slice(0,700))
 throw error
} finally {await browser.close()}
