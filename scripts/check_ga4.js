const fs = require('fs');
const vm = require('vm');
const code = fs.readFileSync(__dirname+'/../assets/js/first-party-analytics.js','utf8');
function check({cookie='', dnt='0', page='/fa/', visible='visible', webdriver=false}={}){
 const scripts=[];
 const listeners=[];
 const local=new Map();
 const localStore={getItem:k=>local.get(k)||null,setItem:(k,v)=>local.set(k,v)};
 const fakeWindow={innerWidth:1300,doNotTrack:dnt,dataLayer:[],addEventListener:()=>{}};
 const fakeDocument={
  cookie,visibilityState:visible,prerendering:false,referrer:'',
  documentElement:{lang:'fa-AF'},head:{appendChild:x=>scripts.push(x)},
  createElement: tag=>({tagName:tag}),getElementById:()=>null,
  addEventListener:(e,fn)=>listeners.push([e,fn])
 };
 const context={
  document:fakeDocument,window:fakeWindow, navigator:{globalPrivacyControl:false,doNotTrack:dnt,webdriver,userAgent:'Mozilla/5.0',sendBeacon:()=>true},
  localStorage:localStore,sessionStorage:localStore,
  location:{pathname:page,hostname:'darmaltoon.com',search:''}, URL, URLSearchParams,Blob,
  setTimeout:()=>{},crypto:require('crypto').webcrypto
 };
 vm.createContext(context);vm.runInContext(code,context);
 return {scripts,data:fakeWindow.dataLayer,events:listeners};
}
const normal=check();
if(normal.scripts.length!==1 || normal.scripts[0].src!=='https://www.googletagmanager.com/gtag/js?id=G-EYBZX45DX7')throw Error('GA4 not configured once');
if(normal.data.length!==2 || normal.data[1][0]!=='config'||normal.data[1][1]!=='G-EYBZX45DX7')throw Error('gtag config missing');
for(const obj of [{cookie:'dt_analytics_exclude=1'},{dnt:'1'},{webdriver:true},{page:'/does-not-exist'}]){
 if(check(obj).scripts.length)throw Error('Tracking should be suppressed '+JSON.stringify(obj));
}
if(check({page:'/fa/medicine-expiry-inventory-software.html'}).scripts.length!==1)throw Error('Missing product page');
if(check({visible:'hidden'}).scripts.length!==0)throw Error('Hidden tab should not track yet');
console.log('PASS GA4: visible public page and product page; owner, DNT, bot, irrelevant URL, and hidden-tab exclusions');