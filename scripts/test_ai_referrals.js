/* Lightweight dependency-free first-party AI attribution regression checks. */
const fs=require('fs'),vm=require('vm'),assert=require('assert').strict;
const code=fs.readFileSync(require('path').join(__dirname,'../assets/js/first-party-analytics.js'),'utf8');
async function check(label,ref,search,expectedSource,expectedProvider){
  const payloads=[];
  const scope={
    URL,URLSearchParams,Blob,
    location:{pathname:'/guides/pharmacy-inventory.html',hostname:'darmaltoon.com',search},
    document:{referrer:ref,documentElement:{lang:'en'},addEventListener(){}},
    navigator:{globalPrivacyControl:false,doNotTrack:'0',sendBeacon:(_path,blob)=>{payloads.push(blob);return true;}},
    window:{innerWidth:1200,doNotTrack:'0'},
    fetch:async()=>({}),
  };
  vm.runInNewContext(code,scope);
  assert.equal(payloads.length,1,label+' page event');
  const payload=JSON.parse(await payloads[0].text());
  assert.equal(payload.source,expectedSource,label+' source');
  assert.equal(payload.referrer,expectedProvider,label+' provider');
}
(async()=>{
 await check('ChatGPT referral','https://chatgpt.com/c/example','','ai_referral','chatgpt');
 await check('Perplexity referral','https://www.perplexity.ai/search/something','','ai_referral','perplexity');
 await check('Copilot referral','https://copilot.microsoft.com/','','ai_referral','copilot');
 await check('Google organic','https://www.google.com/search?q=pharmacy','','organic','google');
 await check('Direct', '', '', 'direct','none');
 await check('Explicit AI UTM','','?utm_source=chatgpt&utm_campaign=guides','ai_referral','chatgpt');
 await check('Unrecognized referral','https://example.net/','','referral','other');
 console.log('PASS: AI attribution vs organic/direct, UTM, and other-referrer tests');
})().catch(e=>{console.error(e);process.exitCode=1;});
