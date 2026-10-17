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
    // New tables are additive; existing daily_metrics and historic totals are untouched.
    $db->exec('CREATE TABLE IF NOT EXISTS visitor_days (
      day TEXT NOT NULL, visitor_hash TEXT NOT NULL,
      PRIMARY KEY(day,visitor_hash)
    )');
    $db->exec('CREATE TABLE IF NOT EXISTS visit_sessions (
      session_hash TEXT PRIMARY KEY, visitor_hash TEXT NOT NULL, day TEXT NOT NULL,
      landing_path TEXT NOT NULL, last_path TEXT NOT NULL,
      source TEXT NOT NULL, referrer TEXT NOT NULL, campaign TEXT NOT NULL,
      device TEXT NOT NULL, language TEXT NOT NULL, country TEXT NOT NULL DEFAULT "ZZ",
      pageviews INTEGER NOT NULL DEFAULT 0, engaged INTEGER NOT NULL DEFAULT 0,
      started_at INTEGER NOT NULL, last_seen_at INTEGER NOT NULL
    )');
    $db->exec('CREATE INDEX IF NOT EXISTS idx_visit_sessions_day ON visit_sessions(day)');
    $db->exec('CREATE TABLE IF NOT EXISTS country_metrics (
       day TEXT NOT NULL, country TEXT NOT NULL, source TEXT NOT NULL,
       event TEXT NOT NULL, count INTEGER NOT NULL DEFAULT 0,
       PRIMARY KEY(day,country,source,event)
    )');
    $db->exec('CREATE TABLE IF NOT EXISTS campaign_terms (
      day TEXT NOT NULL, term TEXT NOT NULL, campaign TEXT NOT NULL,
      path TEXT NOT NULL, count INTEGER NOT NULL DEFAULT 0,
      PRIMARY KEY(day,term,campaign,path)
    )');
    @chmod($file, 0600);
    return $db;
}
function dal_analytics_record(string $event, string $path, string $lang, string $source, string $campaign, string $device, string $referrer='none', string $visitorId='', string $sessionId='', string $utmTerm=''): void {
    if (($_COOKIE['dt_analytics_exclude'] ?? '') === '1') return;
    $events = ['page_view','engaged','demo_click','contact_click','whatsapp_click','email_click',
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
    require_once __DIR__.'/geo-country.php';
    // REMOTE_ADDR is set by the web server; never trust arbitrary browser-supplied country headers.
    $country=dal_geo_country((string)($_SERVER['REMOTE_ADDR'] ?? ''));
    if ($event==='page_view') {
        $db->prepare('INSERT INTO country_metrics(day,country,source,event,count) VALUES(?,?,?,?,1)
          ON CONFLICT(day,country,source,event) DO UPDATE SET count=count+1')
          ->execute([gmdate('Y-m-d'),$country,$source,$event]);
    }
    $q = $db->prepare('INSERT INTO daily_metrics
        (day,event,path,language,source,referrer,campaign,device,count)
        VALUES (:day,:event,:path,:language,:source,:referrer,:campaign,:device,1)
        ON CONFLICT(day,event,path,language,source,referrer,campaign,device)
        DO UPDATE SET count=count+1');
    $q->execute([
        ':day'=>gmdate('Y-m-d'), ':event'=>$event, ':path'=>$path,
        ':language'=>$lang, ':source'=>$source, ':referrer'=>$referrer, ':campaign'=>$campaign, ':device'=>$device
    ]);
    // Short-lived identity estimation. Hash random tokens with a server-only pepper.
    if (preg_match('/^[a-f0-9]{32}$/D',$visitorId) && preg_match('/^[a-f0-9]{32}$/D',$sessionId)
        && $device !== 'server' && in_array($event,['page_view','engaged'],true)) {
        $secretFile=dirname(__DIR__,2).'/.darmaltoon-analytics/identity-secret';
        if (!is_file($secretFile)) {
            $new=bin2hex(random_bytes(32));
            // Atomic single-file initial creation, never overwrite an existing secret.
            @file_put_contents($secretFile,$new,LOCK_EX);
            @chmod($secretFile,0600);
        }
        $secret=trim((string)@file_get_contents($secretFile));
        if (strlen($secret)>=64) {
            $visitor=hash_hmac('sha256',$visitorId,$secret);
            $session=hash_hmac('sha256',$visitorId.':'.$sessionId,$secret);
            $day=gmdate('Y-m-d');$ts=time();
            if ($event==='page_view') {
                $db->prepare('INSERT OR IGNORE INTO visitor_days(day,visitor_hash) VALUES(?,?)')->execute([$day,$visitor]);
                $db->prepare('INSERT INTO visit_sessions
                   (session_hash,visitor_hash,day,landing_path,last_path,source,referrer,campaign,device,language,country,pageviews,engaged,started_at,last_seen_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,1,0,?,?)
                   ON CONFLICT(session_hash) DO UPDATE SET last_path=excluded.last_path,
                   pageviews=pageviews+1,last_seen_at=excluded.last_seen_at')
                    ->execute([$session,$visitor,$day,$path,$path,$source,$referrer,$campaign,$device,$lang,$country,$ts,$ts]);
            } else {
                $db->prepare('UPDATE visit_sessions SET engaged=1,last_seen_at=? WHERE session_hash=?')
                    ->execute([$ts,$session]);
            }
        }
    }
    // Only self-declared campaign terms. Organic Google search keywords are not available from referrers.
    if ($event==='page_view' && $campaign!=='' && preg_match('/^[a-zA-Z0-9 _-]{1,90}$/D',$utmTerm)) {
        $db->prepare('INSERT INTO campaign_terms(day,term,campaign,path,count) VALUES(?,?,?,?,1)
         ON CONFLICT(day,term,campaign,path) DO UPDATE SET count=count+1')
          ->execute([gmdate('Y-m-d'),$utmTerm,$campaign,$path]);
    }
    // Rolling 13-month aggregated retention.
    if (random_int(1,150) === 1) {
        $db->prepare('DELETE FROM daily_metrics WHERE day < :old')
           ->execute([':old'=>gmdate('Y-m-d',time()-400*86400)]);
        // Never keep pseudonymous visitor/session hashes for longer than 35 days.
        $cutoff=gmdate('Y-m-d',time()-35*86400);
        $db->prepare('DELETE FROM visitor_days WHERE day < ?')->execute([$cutoff]);
        $db->prepare('DELETE FROM visit_sessions WHERE day < ?')->execute([$cutoff]);
        $db->prepare('DELETE FROM country_metrics WHERE day < ?')->execute([gmdate('Y-m-d',time()-400*86400)]);
        $db->prepare('DELETE FROM campaign_terms WHERE day < ?')->execute([gmdate('Y-m-d',time()-400*86400)]);
    }
}
