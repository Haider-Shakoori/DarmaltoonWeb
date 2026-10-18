const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const code = fs.readFileSync(__dirname+'/../assets/js/first-party-analytics.js','utf8');

// Simulate browser cookies and storage across successive navigations, without
// actually sending a marketing or GA4 event to production.
function context(shared={}, {search='', webdriver=false, userAgent='Mozilla/5.0', dnt='0', gpc=false}={}) {
 const tags=[], beacons=[];
 const state=shared.state||(shared.state={cookie:{},storage:new Map()});
 const document={
  referrer:'',visibilityState:'visible',prerendering:false,
  documentElement:{lang:'en'},head:{appendChild:tag=>tags.push(tag)},
  createElement:()=>({}),getElementById:()=>null,addEventListener:()=>{}
 };
 Object.defineProperty(document,'cookie',{
  get:()=>Object.entries(state.cookie).map(([k,v])=>k+'='+v).join('; '),
  set:value=>{
   const kv=value.split(';',1)[0], i=kv.indexOf('='), key=kv.slice(0,i), val=kv.slice(i+1);
   if (value.includes('Max-Age=0') || val==='') delete state.cookie[key];
   else state.cookie[key]=val;
  }
 });
 const localStorage={
  getItem:k=>state.storage.get(k)||null,
  setItem:(k,v)=>state.storage.set(k,v),
  removeItem:k=>state.storage.delete(k)
 };
 const fakeWindow={innerWidth:1000,doNotTrack:dnt,dataLayer:[]};
 const fakeNavigator={
  globalPrivacyControl:gpc,doNotTrack:dnt,webdriver,userAgent,
  sendBeacon:(url,blob)=>{beacons.push(url);return true;}
 };
 vm.runInNewContext(code,{
   document,window:fakeWindow,navigator:fakeNavigator,localStorage,
   sessionStorage:localStorage,location:{pathname:'/',hostname:'darmaltoon.com',search},
   URL,URLSearchParams,Blob,crypto:require('node:crypto').webcrypto,setTimeout:()=>{}
 });
 return {tags,beacons,gaQueue:fakeWindow.dataLayer,shared};
}
function none(r, label) {
 assert.equal(r.tags.length,0,label+': no Google tag');
 assert.equal(r.beacons.length,0,label+': no first-party beacons');
}
function normal(r,label) {
 assert.equal(r.tags.length,1,label+': GA4 starts once');
 assert.equal(r.beacons.length,1,label+': first-party page view');
}
normal(context(), 'unmarked visitor');
none(context({}, {webdriver:true}), 'webdriver automation');
none(context({}, {userAgent:'HeadlessChrome/155.0'}), 'headless browser');
none(context({}, {gpc:true}), 'global privacy control');
none(context({}, {dnt:'1'}), 'Do Not Track');
const marked={};
none(context(marked,{search:'?dt_qa=1'}),'QA opt-out setup');
assert.equal(marked.state.cookie.dt_analytics_qa_exclude,'1','QA cookie persisted');
assert.equal(marked.state.storage.get('dt_analytics_qa_exclude'),'1','QA local storage persisted');
none(context(marked,{}),'next QA visit');
none(context(marked,{userAgent:'Mozilla/5.0 Chrome/155.0',webdriver:false}),'spoofed normal browser is still excluded');
normal(context(marked,{search:'?dt_qa=0'}),'QA opt-out deliberately cleared');
normal(context(marked,{}),'normal visit after clearing QA opt-out');
assert.equal(marked.state.cookie.dt_analytics_qa_exclude,undefined,'QA cookie removed');
const owner={state:{cookie:{dt_analytics_exclude:'1'},storage:new Map()}};
none(context(owner,{}),'existing owner exclusion');
none(context(owner,{search:'?dt_qa=0'}),'QA clearing does not override owner exclusion');
const php=fs.readFileSync(__dirname+'/../api/analytics.php','utf8');
assert.ok(php.includes("($_COOKIE['dt_analytics_qa_exclude'] ?? '') === '1'"),'server must reject QA-cookie events');
console.log('PASS: normal visitors measured, owner/privacy/automation/QA visits excluded, QA persistence and reset work, server guard present');
