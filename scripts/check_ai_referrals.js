const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const code=fs.readFileSync(__dirname+'/../assets/js/first-party-analytics.js','utf8');
function visit(path,ref,search=''){
 const out=[];
 const doc={documentElement:{lang:path.startsWith('/fa/')?'fa-AF':path.startsWith('/ps/')?'ps-AF':'en'},referrer:ref,cookie:'',visibilityState:'visible',prerendering:false,head:{appendChild(){}},createElement(){return {};},getElementById(){return null;},addEventListener(){}};
 const context={navigator:{globalPrivacyControl:false,doNotTrack:'0',userAgent:'Mozilla/5.0',sendBeacon:(url,blob)=>{out.push(JSON.parse(blob.parts[0]));return true;}},document:doc,window:{innerWidth:1280,doNotTrack:'0',dataLayer:[]},location:{pathname:path,hostname:'darmaltoon.com',search},URL,URLSearchParams,Blob:class{constructor(parts){this.parts=parts;}},fetch(){throw Error('unexpected fetch')}};
 vm.runInNewContext(code,context);return out[0];
}
for(const [ref,expected,source] of [
 ['https://chatgpt.com/c/test','chatgpt','ai_referral'],
 ['https://chat.openai.com/c/test','chatgpt','ai_referral'],
 ['https://www.perplexity.ai/search/x','perplexity','ai_referral'],
 ['https://gemini.google.com/app','gemini','ai_referral'],
 ['https://copilot.microsoft.com/','copilot','ai_referral'],
 ['https://claude.ai/','claude','ai_referral'],
 ['https://www.google.com/search?q=test','google','organic'],
 ['https://unknown.invalid/x','other','referral']
]){
 const row=visit('/guides/pharmacy-inventory.html',ref);
 assert.equal(row.referrer,expected);assert.equal(row.source,source);
}
assert.equal(visit('/fa/guides/expiry-tracking.html','','?utm_source=chatgpt').source,'ai_referral');
assert.equal(visit('/ps/guides/','', '?utm_source=perplexity').referrer,'perplexity');
assert.equal(visit('/','').source,'direct');
assert.equal(visit('/guides/','https://darmaltoon.com/').source,'internal');
assert.equal(visit('/','','?utm_source=newsletter').source,'campaign');
console.log('PASS: provider attribution, UTM, organic, referral, internal and direct traffic');
