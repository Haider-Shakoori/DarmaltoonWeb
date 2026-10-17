<?php
declare(strict_types=1);

/**
 * First-party, aggregated marketing analytics.
 * No visitor IDs, IPs, cookies, user agents, names, emails or form contents.
 * This file is not an HTTP endpoint.
 */
if (PHP_SAPI !== 'cli' && realpath((string)($_SERVER['SCRIPT_FILENAME'] ?? '')) === __FILE__) {
    http_response_code(404);
    exit;
}
function dal_analytics_db(): PDO {
    $root = dirname(__DIR__, 2) . '/.darmaltoon-analytics';
    if (!is_dir($root)) {
        umask(0077);
        if (!mkdir($root, 0700, true) && !is_dir($root)) throw new RuntimeException('Storage unavailable');
    }
    $file = $root . '/metrics.sqlite';
    $db = new PDO('sqlite:' . $file, null, null, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_TIMEOUT => 5,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ]);
    $db->exec('PRAGMA busy_timeout=5000');
    $db->exec('CREATE TABLE IF NOT EXISTS daily_metrics (
      day TEXT NOT NULL, event TEXT NOT NULL, path TEXT NOT NULL,
      language TEXT NOT NULL, source TEXT NOT NULL, referrer TEXT NOT NULL,
      campaign TEXT NOT NULL, device TEXT NOT NULL, count INTEGER NOT NULL DEFAULT 0,
      PRIMARY KEY (day,event,path,language,source,referrer,campaign,device)
    )');
    @chmod($file, 0600);
    return $db;
}
function dal_analytics_record(string $event, string $path, string $lang, string $source, string $campaign, string $device, string $referrer='none'): void {
    $events = ['page_view','demo_click','contact_click','whatsapp_click','email_click',
       'demo_received','contact_received'];
    if (!in_array($event, $events, true)) return;
    // Known site paths only. Query strings and fragments are never stored.
    $known = ['/','/about.html','/features.html',
       '/pharmadesktop.html','/demo.html','/contact.html','/privacy.html',
       '/fa/','/ps/','/fa/features.html','/ps/features.html',
       '/fa/pharmadesktop.html','/ps/pharmadesktop.html',
       '/fa/privacy.html','/ps/privacy.html',
       '/guides/','/fa/guides/','/ps/guides/',
       '/guides/pharmacy-inventory.html','/fa/guides/pharmacy-inventory.html','/ps/guides/pharmacy-inventory.html',
       '/guides/expiry-tracking.html','/fa/guides/expiry-tracking.html','/ps/guides/expiry-tracking.html',
       '/guides/offline-pharmacy-software.html','/fa/guides/offline-pharmacy-software.html','/ps/guides/offline-pharmacy-software.html'];
    if (!in_array($path, $known, true)) return;
    if (!in_array($lang,['en','fa','ps'], true)) $lang='en';
    if (!in_array($device,['mobile','tablet','desktop','server'], true)) $device='server';
    if (!in_array($source,['direct','organic','referral','ai_referral','campaign','internal','server'],true)) $source='direct';
    if (!preg_match('/^[A-Za-z0-9_-]{0,48}$/D',$campaign)) $campaign='';
    if (!in_array($referrer, ['none','google','bing','duckduckgo','yahoo','yandex','facebook','instagram','whatsapp','tiktok','youtube','linkedin','x','telegram','chatgpt','perplexity','gemini','copilot','claude','youcom','poe','other'],true)) $referrer='other';
    $db = dal_analytics_db();
    $q = $db->prepare('INSERT INTO daily_metrics
        (day,event,path,language,source,referrer,campaign,device,count)
        VALUES (:day,:event,:path,:language,:source,:referrer,:campaign,:device,1)
        ON CONFLICT(day,event,path,language,source,referrer,campaign,device)
        DO UPDATE SET count=count+1');
    $q->execute([
        ':day'=>gmdate('Y-m-d'), ':event'=>$event, ':path'=>$path,
        ':language'=>$lang, ':source'=>$source, ':referrer'=>$referrer, ':campaign'=>$campaign, ':device'=>$device
    ]);
    // Rolling 13-month aggregated retention.
    if (random_int(1,150) === 1) {
        $db->prepare('DELETE FROM daily_metrics WHERE day < :old')
           ->execute([':old'=>gmdate('Y-m-d',time()-400*86400)]);
    }
}
