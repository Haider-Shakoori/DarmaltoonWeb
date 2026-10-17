#!/usr/bin/env python3
"""Generate reviewed-structure, multilingual Darmaltoon SEO guides. No fabricated data."""
from pathlib import Path
from html import escape as esc
import json
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
BASE="https://darmaltoon.com"
TOPICS=["pharmacy-inventory","expiry-tracking","offline-pharmacy-software"]
DATA={
"en":{
"label":"English","home":"Home","guides":"Guides","features":"Features","demo":"Request a demo","desktop":"Windows desktop",
"hub_title":"Pharmacy Management Guides | Inventory, Expiry & Offline Operations","hub_h1":"Practical pharmacy management guides",
"hub_description":"Practical guides for pharmacy inventory, medicine expiry tracking and evaluating offline pharmacy software. Available in English, Dari and Pashto.",
"hub_intro":"Clear, practical explanations of pharmacy workflows, plus questions to ask when evaluating software for your team.",
"updated":"Updated October 2026","next":"Explore another guide","choose":"Talk through your pharmacy workflow",
"note":"These guides describe general pharmacy operating practices. Confirm exact features and licensing arrangements during a Darmaltoon demonstration.",
"topics":{
"pharmacy-inventory":{
"title":"Pharmacy Inventory Management: Practical Checklist | Darmaltoon",
"h1":"Pharmacy inventory management: a practical checklist",
"desc":"How to organize medicine stock, record purchases and sales, avoid stock discrepancies and prepare a pharmacy inventory system for daily work.",
"intro":"Reliable pharmacy stock records begin with consistent product data and careful receiving, not with a complicated dashboard. This checklist helps pharmacy teams decide what to record and review.",
"sections":[
("1. Make every medicine easy to identify","Use a consistent medicine name, strength, form, pack size and unit of measure. Keep supplier and purchasing information linked to the relevant stock records. Similar names or strengths should be distinguishable before items reach checkout."),
("2. Record every stock movement","Record initial quantities, purchase receipts, sales, returns and authorized adjustments. Compare physical counts with system totals regularly; investigate shortages rather than making unexplained corrections."),
("3. Define reorder and audit routines","Review fast-moving items, low-stock alerts and slower products regularly. Set a clear person responsible for receiving, expiry checks and discrepancy approvals. Keep a backup of the stock database."),
],
"questions":[("What is a pharmacy inventory system?","It is a process and set of records for tracking medicines received, sold, returned and currently held in stock."),("Can inventory management work without a barcode scanner?","Yes. A product catalog and clear manual lookup process can support stock control; scanner support is optional and depends on the software.")],
"related":"Medicine expiry tracking is closely related to accurate inventory records."
},
"expiry-tracking":{
"title":"Medicine Expiry Tracking: FEFO and Stock Checks | Darmaltoon",
"h1":"Medicine expiry tracking and FEFO: a step-by-step guide",
"desc":"Learn how to record medicine expiry dates, review near-expiry stock and organize FEFO procedures for safe, accountable pharmacy operations.",
"intro":"Expiry control reduces the risk of selling unsuitable stock and helps teams identify products that need review. The important details are batch-level dates, careful dispensing and repeatable routines.",
"sections":[
("1. Record the relevant expiry information","Where applicable, record batch or lot identifiers and the printed expiration date when receiving medicines. Inspect labels and packaging; do not invent missing dates or reuse expiry information from a different batch."),
("2. Apply FEFO where appropriate","First-expiring, first-out (FEFO) means reviewing the shortest remaining shelf life first, while respecting storage conditions and the requirements for that medicine. Staff must not dispense expired products."),
("3. Review and segregate risk stock","Use routine reports or physical checks to find near-expiry and expired items. Segregate unsuitable products and document approved returns, quarantine or disposal according to applicable requirements."),
],
"questions":[("What is FEFO in a pharmacy?","FEFO is a stock handling method that gives priority to products with the earliest applicable expiration date."),("Is a low-stock report the same as an expiry report?","No. Stock quantity and remaining shelf life are different controls, and pharmacy teams should review both.")],
"related":"Accurate product and batch information makes expiry checks more dependable."
},
"offline-pharmacy-software":{
"title":"Offline Pharmacy Software: Evaluation Guide | Darmaltoon",
"h1":"How to evaluate offline pharmacy management software",
"desc":"A practical guide to choosing pharmacy software when internet access is intermittent: local sales, stock updates, backups and multi-device requirements.",
"intro":"An offline-capable system should keep critical pharmacy work available during internet disruption. Evaluate the specific offline mode before choosing a product, rather than assuming every web or mobile feature works without connectivity.",
"sections":[
("1. List the transactions that must work offline","Ask whether sales, medicine lookup, stock deductions, receiving and reports operate locally without a network connection. Test a realistic full shift with internet disconnected."),
("2. Plan local data protection","Clarify where the primary data is stored, who can restore a backup, how often backups run and how updates are installed. Test recovery on a spare machine rather than trusting an untested backup."),
("3. Understand multi-device and synchronization limits","If several terminals are needed, verify how they connect on the local network and how simultaneous stock updates are handled. Cloud sync, when offered, should be explained separately from the basic offline workflow."),
],
"questions":[("Does a website always work offline?","No. Many web applications require internet or a local server. The exact offline behavior depends on architecture and subscription options."),("What should I test in a demonstration?","Test checkout, inventory updates, power interruption recovery, backups, concurrent terminals and reconnection behavior against your actual requirements.")],
"related":"Inventory accuracy is especially important when multiple terminals can make sales."
}
}
},
"fa":{
"label":"دری","home":"خانه","guides":"راهنماها","features":"امکانات","demo":"درخواست نمایش","desktop":"نسخه ویندوز",
"hub_title":"راهنمای مدیریت دواخانه | موجودی، انقضا و کار آفلاین | درملتون",
"hub_h1":"راهنماهای کاربردی مدیریت دواخانه",
"hub_description":"راهنمای عملی موجودی ادویه، کنترول تاریخ انقضا و انتخاب نرم‌افزار دواخانه بدون نیاز دایمی به اینترنت.",
"hub_intro":"نکته‌های ساده برای تنظیم موجودی، جلوگیری از اشتباه در تاریخ انقضا و ارزیابی نرم‌افزار مناسب دواخانه.",
"updated":"به‌روزرسانی: اکتوبر ۲۰۲۶","next":"راهنمای مرتبط","choose":"در مورد کار دواخانه مشوره بگیرید",
"note":"این مطالب راهنمای عمومی هستند. امکانات دقیق نرم‌افزار و شرایط استفاده را هنگام نمایش درملتون بررسی کنید.",
"topics":{
"pharmacy-inventory":{
"title":"مدیریت موجودی دواخانه و ثبت ادویه | درملتون",
"h1":"چگونه موجودی ادویه را در دواخانه مدیریت کنیم؟",
"desc":"راهنمای ثبت خرید، فروش، موجودی ادویه و بررسی کمبود در دواخانه با روش‌های ساده و قابل اجرا.",
"intro":"مدیریت موجودی از ثبت دقیق نام و مقدار هر دوا آغاز می‌شود. یک روش منظم به کارمندان کمک می‌کند خرید، فروش و تفاوت موجودی را بهتر پیگیری کنند.",
"sections":[("۱. مشخصات هر دوا را دقیق ثبت کنید","نام دوا، مقدار، نوع بسته‌بندی و واحد شمارش باید روشن باشد. ادویه با نام یا دوز مشابه را جداگانه ثبت کنید تا اشتباه رخ ندهد."),
("۲. ورود و خروج موجودی را ثبت کنید","خرید از عرضه‌کننده، فروش، مرجوعی و اصلاح موجودی باید سند داشته باشد. تعداد واقعی ادویه را به‌صورت دوره‌ای با سیستم مقایسه کنید."),
("۳. کمبود و گزارش‌ها را بررسی کنید","ادویه پرفروش، موجودی کم و کالاهای کم‌گردش را مشخص کنید. برای بررسی و تأیید اصلاحات موجودی مسئول تعیین نمایید.")],
"questions":[("سیستم موجودی دواخانه چیست؟","سیستمی برای ثبت ادویه واردشده، فروخته‌شده و موجود در گدام یا قفسه‌ها است."),
("آیا بارکد حتمی است؟","خیر. ثبت درست نام و مشخصات ادویه و جستجوی دستی نیز می‌تواند برای مدیریت موجودی استفاده شود.")],
"related":"برای موجودی دقیق، تاریخ انقضای ادویه را نیز بررسی کنید."
},
"expiry-tracking":{
"title":"کنترول تاریخ انقضای ادویه در دواخانه | درملتون",
"h1":"کنترول تاریخ انقضای ادویه چگونه انجام می‌شود؟",
"desc":"مراحل ثبت تاریخ انقضا، بررسی ادویه نزدیک به انقضا و استفاده از روش FEFO در دواخانه.",
"intro":"تاریخ انقضا باید هنگام دریافت ادویه بررسی و ثبت شود. کنترول منظم از فروش اشتباهی ادویه تاریخ‌گذشته جلوگیری می‌کند.",
"sections":[("۱. تاریخ و بچ ادویه را ثبت کنید","در صورت موجود بودن، شماره بچ و تاریخ انقضای درج‌شده روی بسته را ثبت کنید. برای بچ‌های مختلف یک تاریخ فرضی استفاده نکنید."),
("۲. روش FEFO را در نظر بگیرید","در روش FEFO ادویه با نزدیک‌ترین تاریخ انقضا زودتر بررسی و در صورت مناسب بودن استفاده می‌شود. ادویه منقضی نباید فروخته شود."),
("۳. بررسی و جداسازی انجام دهید","ادویه نزدیک به انقضا و تاریخ‌گذشته را به‌طور منظم بررسی و موارد نامناسب را جدا کنید. مرجوعی یا امحا باید طبق مقررات مربوط ثبت شود.")],
"questions":[("FEFO چیست؟","روشی است که در آن ادویه با نزدیک‌ترین تاریخ انقضا اولویت بررسی و خروج از موجودی دارد."),
("آیا گزارش کمبود موجودی کافی است؟","خیر. تعداد موجودی و تاریخ انقضا دو موضوع متفاوت هستند و هر دو باید کنترول شوند.")],
"related":"موجودی دقیق، بررسی تاریخ انقضا را آسان‌تر می‌سازد."
},
"offline-pharmacy-software":{
"title":"انتخاب نرم‌افزار دواخانه آفلاین | درملتون",
"h1":"برای انتخاب نرم‌افزار دواخانه آفلاین چه چیزهایی را بررسی کنیم؟",
"desc":"راهنمای ارزیابی نرم‌افزار دواخانه هنگام قطع اینترنت: فروش محلی، موجودی، پشتیبان‌گیری و چند دستگاه.",
"intro":"در جایی که اینترنت همیشه در دسترس نیست، کارهای ضروری دواخانه باید قابل انجام باشند. پیش از خرید، امکانات آفلاین را عملاً آزمایش کنید.",
"sections":[("۱. کارهای ضروری بدون اینترنت را مشخص کنید","بررسی کنید فروش، جستجوی ادویه، کاهش موجودی و گزارش‌ها بدون اینترنت انجام می‌شوند یا خیر. یک روز کاری نمونه را آزمایش کنید."),
("۲. از اطلاعات پشتیبان بگیرید","محل نگهداری اطلاعات، روش گرفتن نسخه پشتیبان و امکان بازیابی آن باید روشن باشد. نسخه پشتیبان را واقعاً آزمایش کنید."),
("۳. شرایط چند دستگاه را بپرسید","اگر چند کمپیوتر دارید، روش اتصال در شبکه محلی و ثبت فروش همزمان را بررسی کنید. همگام‌سازی ابری موضوع جداگانه‌ای است.")],
"questions":[("آیا تمام وب‌سایت‌ها آفلاین کار می‌کنند؟","خیر. برخی سیستم‌ها به اینترنت یا سرور محلی نیاز دارند؛ این موضوع به نوع سیستم بستگی دارد."),
("در نمایش نرم‌افزار چه آزمایش کنیم؟","فروش، کاهش موجودی، بازیابی نسخه پشتیبان و کار چند دستگاه را مطابق نیاز دواخانه آزمایش کنید.")],
"related":"مدیریت موجودی در زمان کار چند دستگاه اهمیت زیادی دارد."
}
}
},
"ps":{
"label":"پښتو","home":"کورپاڼه","guides":"لارښودونه","features":"ځانګړتیاوې","demo":"د نندارې غوښتنه","desktop":"د وینډوز نسخه",
"hub_title":"د درملتون د مدیریت لارښود | موجودي، ختمېدونکې نېټه او آفلاین | درملتون",
"hub_h1":"د درملتون د مدیریت عملي لارښودونه",
"hub_description":"د درملو د موجودۍ، د ختمېدو نېټې او له انټرنېټ پرته د درملتون د سافټویر د ارزونې عملي لارښود.",
"hub_intro":"د درملتون د موجودۍ د سم ثبت، د درملو د نېټو د کتنې او د مناسب سافټویر د انتخاب لپاره ساده لارښوونې.",
"updated":"تازه شوی: اکتوبر ۲۰۲۶","next":"اړوند لارښود","choose":"د خپل درملتون د کار په اړه خبرې وکړئ",
"note":"دا عمومي لارښوونې دي. د درملتون سافټویر دقیقې ځانګړتیاوې او د کار شرایط د نندارې پر مهال تایید کړئ.",
"topics":{
"pharmacy-inventory":{
"title":"د درملتون د موجودۍ مدیریت او د درملو ثبت | درملتون",
"h1":"د درملتون د درملو موجودي څنګه مدیریت کړو؟",
"desc":"د درملو د پېرلو، پلورلو، موجودۍ او د کموالي د ثبت لپاره عملي لارښوونې.",
"intro":"د موجودۍ ښه مدیریت د هر درمل له سم نوم او شمېر څخه پیلېږي. منظم ثبت د پېر او پلور د تېروتنو په پېژندلو کې مرسته کوي.",
"sections":[("۱. د هر درمل معلومات روښانه وساتئ","د درمل نوم، اندازه، د بسته ډول او د شمېر واحد ثبت کړئ. ورته نومونه او بېلابېلې اندازې باید جلا وپېژندل شي."),
("۲. د موجودۍ هر بدلون ثبت کړئ","پېر، پلور، بېرته راګرځول او تایید شوي سمونونه ثبت کړئ. فزیکي شمېر له سیسټم سره وخت په وخت پرتله کړئ."),
("۳. د کموالي او راپورونو کتنه وکړئ","ډېر پلورل کېدونکي او کم پاتې درمل وڅارئ. د موجودۍ د توپیرونو د کتنې لپاره یو مسؤل وټاکئ.")],
"questions":[("د درملتون د موجودۍ سیسټم څه شی دی؟","هغه طریقه ده چې د درملو راتګ، پلور او پاتې شمېر ثبتوي."),
("آیا بارکوډ حتمي دی؟","نه. د درملو روښانه نومونه او لاسي لټون هم د موجودۍ د مدیریت لپاره کارېدلی شي.")],
"related":"د موجودۍ له سم ثبت سره د درملو د ختمېدو نېټه هم وڅارئ."
},
"expiry-tracking":{
"title":"د درملو د ختمېدو نېټې کنټرول او FEFO | درملتون",
"h1":"د درملو د ختمېدو نېټه څنګه وڅارو؟",
"desc":"د ختمېدو د نېټو ثبت، نېټې ته نږدې درملو کتنه او د FEFO طریقې تشریح.",
"intro":"د درملو د ترلاسه کولو پر مهال د ختمېدو نېټه وڅېړئ. منظمې کتنې د نېټه‌تېرو درملو د ناسم پلور خطر کموي.",
"sections":[("۱. د درملو نېټه او بچ ثبت کړئ","کله چې موجود وي، د بچ شمېره او پر بسته لیکل شوې د ختمېدو نېټه وساتئ. د بېلابېلو بچونو لپاره یوه اټکلي نېټه مه کاروئ."),
("۲. د FEFO اصول وکاروئ","په FEFO کې هغه درمل لومړی کتل کېږي چې د ختمېدو نېټه یې نږدې وي. نېټه‌تېر درمل باید ونه پلورل شي."),
("۳. نامناسب درمل بېل کړئ","نېټې ته نږدې او نېټه‌تېر درمل په منظم ډول وڅېړئ. بېرته ستنول او له منځه وړل د اړوندو مقرراتو له مخې ثبت کړئ.")],
"questions":[("FEFO څه مانا لري؟","هغه کړنلاره ده چې د نږدې ختمېدو نېټې لرونکو درملو ته لومړیتوب ورکوي."),
("آیا یوازې د کمې موجودۍ راپور بس دی؟","نه. د درملو شمېر او د ختمېدو نېټه دوه جلا کنټرولونه دي.")],
"related":"سمه موجودي د ختمېدو د نېټې کتنه اسانه کوي."
},
"offline-pharmacy-software":{
"title":"له انټرنېټ پرته د درملتون سافټویر انتخاب | درملتون",
"h1":"آفلاین درملتون سافټویر څنګه انتخاب کړو؟",
"desc":"د انټرنېټ د پرې کېدو پر مهال د پلور، موجودۍ، بیک اپ او څو کمپیوټرونو د کار ارزونې لارښود.",
"intro":"کله چې انټرنېټ پرې کېږي، د درملتون اړین کارونه باید دوام ومومي. د سافټویر د انتخاب مخکې آفلاین کار په عملي ډول وازمویئ.",
"sections":[("۱. مهم آفلاین کارونه معلوم کړئ","وګورئ چې پلور، د درملو لټون، د موجودۍ کمېدل او راپورونه له انټرنېټ پرته ترسره کېږي که نه."),
("۲. د معلوماتو خوندي ساتل وارزوئ","پوښتنه وکړئ چې معلومات چېرې ساتل کېږي، بیک اپ څنګه جوړېږي او بېرته څنګه راګرځي. د بېرته راګرځولو ازموینه وکړئ."),
("۳. د څو کمپیوټرونو کار تایید کړئ","که څو کمپیوټرونه کاروئ، د محلي شبکې اړیکه او هممهاله پلور وڅېړئ. د کلاوډ همغږي جلا ځانګړنه ده.")],
"questions":[("آیا هره ویبپاڼه آفلاین چلېږي؟","نه. ځینې سیسټمونه انټرنېټ یا محلي سرور ته اړتیا لري."),
("په ډیمو کې څه وازمویو؟","پلور، د موجودۍ بدلون، بیک اپ، بېرته رغونه او د څو کمپیوټرونو کار وازمویئ.")],
"related":"د څو کمپیوټرونو پر مهال سمه موجودي ډېره مهمه ده."
}
}
}
}
CSS="""*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f5faff;color:#10365c;font-family:system-ui,-apple-system,"Segoe UI",Tahoma,sans-serif;line-height:1.8}a{color:#1268cb}a:focus-visible{outline:3px solid #1480fc;outline-offset:3px}.shell{max-width:1120px;margin:auto;padding:0 22px}.header{border-bottom:1px solid #dceafa;background:#fff}.headerbar{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;min-height:82px}.brand img{display:block;max-width:200px;height:auto}.nav,.langs,.trail,.actions{display:flex;flex-wrap:wrap;align-items:center;gap:16px}.nav a,.langs a{text-decoration:none;font-size:14px;font-weight:650}.langs{gap:9px;border-inline-start:1px solid #cbdff5;padding-inline-start:15px}.hero{background:linear-gradient(120deg,#e4f5ff,#fff);padding:50px 0 44px;border-bottom:1px solid #dceafa}.eyebrow{text-transform:uppercase;color:#176dc6;letter-spacing:.09em;font-weight:750;font-size:12px}h1{font-size:clamp(29px,4.8vw,48px);line-height:1.18;max-width:880px;margin:13px 0 22px;letter-spacing:-.025em}.intro{font-size:18px;max-width:820px;color:#486683}.meta{font-size:13px;color:#66809e}.main{padding:38px 0 60px}.card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,285px),1fr));gap:17px}.card,.article,.sidebar,.cta{background:#fff;border:1px solid #dceafa;border-radius:18px;padding:23px;box-shadow:0 9px 28px #28669d0c}.card h2{font-size:21px;line-height:1.35;margin:8px 0}.card p{color:#52708d}.card a{font-weight:700}.article{max-width:790px}.article h2{margin-top:30px;font-size:23px}.article h3{font-size:17px;margin-top:18px}.article p,.article li{color:#365779}.layout{display:grid;grid-template-columns:minmax(0,780px) minmax(240px,1fr);gap:20px;align-items:start}.sidebar{position:sticky;top:20px}.sidebar h2{margin-top:0;font-size:19px}.sidebar a{display:block;padding:8px 0}.cta{background:#e9f5ff;margin:25px 0}.button{display:inline-block;border-radius:10px;background:#156be0;color:#fff;padding:11px 19px;text-decoration:none;font-weight:750}.small{font-size:13px;color:#627d98}.trail{font-size:13px;margin-bottom:16px}.footer{background:#edf6ff;padding:26px 0;font-size:13px}.footer .shell{display:flex;justify-content:space-between;flex-wrap:wrap;gap:14px}.footer a{margin-inline-start:15px}@media(max-width:760px){.layout{grid-template-columns:1fr}.sidebar{position:static}.nav{gap:12px}.hero{padding:36px 0}.brand img{max-width:170px}.shell{padding:0 17px}}"""
asset=ROOT/"assets/css/seo-guides.css"
asset.parent.mkdir(parents=True,exist_ok=True)
asset.write_text(CSS,encoding="utf-8")
def path(lang,topic=None):
    prefix=f"/{lang}" if lang!="en" else ""
    return prefix+"/guides/"+(topic+".html" if topic else "")
def url(lang,topic=None):return BASE+path(lang,topic)
def langlinks(topic=None):
    return "".join(f'<link rel="alternate" hreflang="{c}" href="{esc(url(l,topic))}">' for l,c in [("en","en"),("fa","fa-AF"),("ps","ps-AF")])+f'<link rel="alternate" hreflang="x-default" href="{url("en",topic)}">'
def linkset(lang):
    d=DATA[lang]
    return f'<nav class="nav" aria-label="Site navigation"><a href="/">{esc(d["home"])}</a><a href="{path(lang)}">{esc(d["guides"])}</a><a href="{("/"+lang if lang!="en" else "")+"/features.html"}">{esc(d["features"])}</a><a href="/demo.html?lang={lang}">{esc(d["demo"])}</a></nav>'
def layout(lang,title,description,h1,intro,body,topic=None):
    d=DATA[lang];dir="rtl" if lang!="en" else "ltr"
    canonical=url(lang,topic)
    langnav=''.join(f'<a href="{path(l,topic)}" hreflang="{code}" lang="{code}"'+(' aria-current="page"' if l==lang else '')+f'>{esc(DATA[l]["label"])}</a>' for l,code in [("en","en"),("fa","fa-AF"),("ps","ps-AF")])
    graph={"@context":"https://schema.org","@graph":[{"@type":"WebPage","name":title,"url":canonical,"description":description,"inLanguage":{"en":"en","fa":"fa-AF","ps":"ps-AF"}[lang],"isPartOf":{"@type":"WebSite","name":"Darmaltoon","url":BASE}},{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":d["home"],"item":BASE+"/"},{"@type":"ListItem","position":2,"name":d["guides"],"item":url(lang)}]+([{"@type":"ListItem","position":3,"name":h1,"item":canonical}] if topic else [])}]}
    if topic:graph["@graph"].append({"@type":"Article","headline":h1,"description":description,"inLanguage":{"en":"en","fa":"fa-AF","ps":"ps-AF"}[lang],"datePublished":"2026-10-17","dateModified":"2026-10-17","publisher":{"@type":"Organization","name":"Darmaltoon","url":BASE},"mainEntityOfPage":canonical})
    src=f'''<!doctype html><html lang="{("fa-AF" if lang=="fa" else "ps-AF" if lang=="ps" else "en")}" dir="{dir}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="robots" content="index,follow,max-image-preview:large"><meta property="og:type" content="article"><meta property="og:site_name" content="Darmaltoon"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><link rel="canonical" href="{canonical}">{langlinks(topic)}<link rel="icon" href="/assets/images/brand/darmaltoon-selected.png"><link rel="stylesheet" href="/assets/css/seo-guides.css?v=20261017-1"><script type="application/ld+json">{json.dumps(graph,ensure_ascii=False,separators=(",",":"))}</script></head><body><header class="header"><div class="shell headerbar"><a href="/" class="brand"><img width="200" height="42" src="/assets/images/brand/darmaltoon-merged-wordmark.png" alt="Darmaltoon logo"></a>{linkset(lang)}<nav class="langs" aria-label="Languages">{langnav}</nav></div></header><section class="hero"><div class="shell"><div class="eyebrow">Darmaltoon · {esc(d["guides"])}</div><h1>{esc(h1)}</h1><p class="intro">{esc(intro)}</p><p class="meta">{esc(d["updated"])}</p></div></section><main class="shell main">{body}</main><footer class="footer"><div class="shell"><span>© 2026 Darmaltoon · {esc(d["note"])}</span><div><a href="/privacy.html">Privacy</a><a href="/contact.html?lang={lang}">Contact</a></div></div></footer><script defer src="/assets/js/first-party-analytics.js?v=20261017-ai1"></script></body></html>'''
    return src
for lang,d in DATA.items():
    cards=[]
    for topic in TOPICS:
        t=d["topics"][topic]
        cards.append(f'<article class="card"><h2>{esc(t["h1"])}</h2><p>{esc(t["desc"])}</p><a href="{path(lang,topic)}">{esc(d["guides"])} →</a></article>')
    hub_body='<div class="card-grid">'+''.join(cards)+'</div><section class="cta"><h2>'+esc(d["choose"])+'</h2><p>'+esc(d["note"])+'</p><a class="button" href="/demo.html?lang='+lang+'">'+esc(d["demo"])+'</a></section>'
    folder=ROOT/path(lang).lstrip("/")
    folder.mkdir(parents=True,exist_ok=True)
    (folder/"index.html").write_text(layout(lang,d["hub_title"],d["hub_description"],d["hub_h1"],d["hub_intro"],hub_body),encoding="utf-8")
    for topic in TOPICS:
        t=d["topics"][topic]
        parts=[f'<section class="article"><nav class="trail"><a href="{path(lang)}">{esc(d["guides"])}</a> › {esc(t["h1"])}</nav>']
        for heading,paragraph in t["sections"]:parts.append(f'<section><h2>{esc(heading)}</h2><p>{esc(paragraph)}</p></section>')
        parts.append('<section><h2>FAQ</h2>')
        for q,a in t["questions"]:parts.append(f'<h3>{esc(q)}</h3><p>{esc(a)}</p>')
        parts.append('</section><p class="small">'+esc(d["note"])+'</p></section>')
        links=[t2 for t2 in TOPICS if t2!=topic]
        sidebar=f'<aside class="sidebar"><h2>{esc(d["next"])}</h2><p>{esc(t["related"])}</p>'+''.join(f'<a href="{path(lang,l)}">{esc(d["topics"][l]["h1"])} →</a>' for l in links)+f'<hr><p class="small">{esc(d["note"])}</p><a class="button" href="/demo.html?lang={lang}">{esc(d["demo"])}</a></aside>'
        (folder/f"{topic}.html").write_text(layout(lang,t["title"],t["desc"],t["h1"],t["intro"],'<div class="layout">'+''.join(parts)+sidebar+'</div>',topic),encoding="utf-8")
print('Generated 12 multilingual guide pages and shared light stylesheet')

