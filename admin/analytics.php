<?php
declare(strict_types=1);
/* Owner-only first-party analytics. Password hash lives outside the web root. */
header('Cache-Control: no-store, private');
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: DENY');
header('Referrer-Policy: no-referrer');
header('X-Robots-Tag: noindex, nofollow, noarchive');
header("Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'");
ini_set('session.use_strict_mode','1');
session_name('darmaltoon_owner_analytics');
session_set_cookie_params(['httponly'=>true,'secure'=>true,'samesite'=>'Strict','path'=>'/admin/']);
session_start();
function e(string $s): string { return htmlspecialchars($s,ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8'); }
function page_start(string $title): void {
    echo '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>'.e($title).' | Darmaltoon</title>';
    echo '<style>:root{font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:#0d2b50;background:#f3f8ff}*{box-sizing:border-box}body{margin:0;padding:34px 18px}.wrap{max-width:1150px;margin:auto}.head{display:flex;align-items:center;justify-content:space-between;gap:18px;flex-wrap:wrap}.tag{font-size:12px;color:#2375cf;font-weight:800}h1{font-size:clamp(26px,4vw,40px);letter-spacing:-.05em;margin:8px 0}h2{font-size:19px}.intro{color:#5d7694;font-size:13px;line-height:1.7}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:13px;margin:25px 0}.card,.panel{background:#fff;border:1px solid #dceafa;border-radius:16px;padding:21px;box-shadow:0 7px 26px #267ab010}.card strong{display:block;font-size:28px;margin-top:12px;color:#0c60d1}.card small{font-size:12px;color:#5e7796}.tables{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,360px),1fr));gap:18px}.table-scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:13px}td,th{text-align:left;padding:11px 5px;border-bottom:1px solid #e5eef8}td:last-child,th:last-child{text-align:right}th{font-size:11px;text-transform:uppercase;color:#70869e}form.login{max-width:430px;margin:10vh auto;background:#fff;padding:35px;border:1px solid #dce9f7;border-radius:19px;box-shadow:0 20px 50px #2368a622}input{width:100%;padding:12px;border:1px solid #b5cfea;border-radius:10px;margin:10px 0 17px;font:inherit}button{background:#126be9;color:white;border:0;border-radius:10px;padding:11px 19px;font:inherit;font-weight:750;cursor:pointer}.logout{background:#e8f2ff;color:#1257ad}.error{color:#bd2645;font-size:13px}.notice{color:#5e7692;font-size:12px}.bar{height:8px;background:#eaf3ff;border-radius:5px;margin-top:6px}.bar i{display:block;background:#1585ee;height:100%;border-radius:5px}</style></head><body>';
}
$private=dirname(__DIR__,2).'/.darmaltoon-analytics';
$passFile=$private.'/admin-password.hash';
if (!is_file($passFile)) {
    http_response_code(503);
    page_start('Analytics unavailable');
    echo '<div class="wrap"><h1>Analytics not activated</h1><p class="intro">The site owner must set an admin password on the server before this private report can be used.</p></div>';
    exit;
}
$hash=trim((string)file_get_contents($passFile));
$csrf=$_SESSION['csrf'] ?? bin2hex(random_bytes(20));
$_SESSION['csrf']=$csrf;
if (($_SERVER['REQUEST_METHOD'] ?? '') === 'POST' && (isset($_POST['password']) || isset($_POST['logout']))) {
    if (!hash_equals($csrf,(string)($_POST['csrf'] ?? ''))) {
        http_response_code(403);exit('Invalid session');
    }
    if (isset($_POST['logout'])) {
        $_SESSION=[];session_regenerate_id(true);
        header('Location: /admin/analytics.php');exit;
    }
    $attempts=(int)($_SESSION['failures'] ?? 0);
    if ($attempts >= 5 && time() < (int)($_SESSION['blocked_until'] ?? 0)) {
        $error='Too many attempts. Wait 15 minutes.';
    } elseif (password_verify((string)($_POST['password'] ?? ''),$hash)) {
        session_regenerate_id(true);
        $_SESSION['logged_in']=true;$_SESSION['last_activity']=time();$_SESSION['failures']=0;
        header('Location: /admin/analytics.php');exit;
    } else {
        $_SESSION['failures']=$attempts+1;
        if ($attempts+1>=5) $_SESSION['blocked_until']=time()+900;
        $error='Incorrect password.';
    }
}
$authenticated=($_SESSION['logged_in'] ?? false) === true
    && time()-(int)($_SESSION['last_activity'] ?? 0)<1800;
if (!$authenticated) {
    unset($_SESSION['logged_in']);
    page_start('Private analytics');
    echo '<form class="login" method="post"><span class="tag">DARMALTOON · PRIVATE REPORTING</span><h1>Owner analytics</h1><p class="intro">This report is private. No pharmacy or patient data is collected here.</p>';
    if (isset($error)) echo '<p class="error">'.e($error).'</p>';
    echo '<input type="password" name="password" placeholder="Admin password" required autocomplete="current-password" aria-label="Admin password"><input type="hidden" name="csrf" value="'.e($csrf).'"><button type="submit">Sign in</button></form>';
    exit;
}
$_SESSION['last_activity']=time();
require_once dirname(__DIR__).'/api/analytics-store.php';
try {$db=dal_analytics_db();}catch(Throwable $e){http_response_code(503);exit('Metrics storage unavailable');}
// Private, explicitly human-checked AI answer observations. Never auto-invent a mention.
$db->exec('CREATE TABLE IF NOT EXISTS ai_mention_checks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  checked_at TEXT NOT NULL,
  engine TEXT NOT NULL,
  question TEXT NOT NULL,
  result TEXT NOT NULL,
  evidence_url TEXT NOT NULL DEFAULT ""
)');
$aiEngines=['ChatGPT','Perplexity','Gemini','Copilot','Claude','Other'];
$aiResults=['mentioned_with_link','mentioned_without_link','not_mentioned','unclear'];
if (($_SERVER['REQUEST_METHOD'] ?? '') === 'POST' && isset($_POST['save_ai_check'])) {
    if (!hash_equals($csrf,(string)($_POST['csrf'] ?? ''))) { http_response_code(403);exit('Invalid session'); }
    $engine=(string)($_POST['engine'] ?? '');
    $question=trim((string)($_POST['question'] ?? ''));
    $result=(string)($_POST['result'] ?? '');
    $evidence=trim((string)($_POST['evidence_url'] ?? ''));
    if (!in_array($engine,$aiEngines,true) || !in_array($result,$aiResults,true) ||
        strlen($question)<12 || strlen($question)>750 ||
        strlen($evidence)>500 || ($evidence!=='' && (!filter_var($evidence,FILTER_VALIDATE_URL) || strncmp($evidence,'https://',8)!==0))) {
        $ai_error='Enter an engine, a 12–250 character question, a result, and an optional HTTPS evidence URL.';
    } else {
        $q=$db->prepare('INSERT INTO ai_mention_checks (checked_at,engine,question,result,evidence_url) VALUES (?,?,?,?,?)');
        $q->execute([gmdate('Y-m-d H:i:s'),$engine,$question,$result,$evidence]);
        header('Location: /admin/analytics.php#ai-visibility');exit;
    }
}
// Aggregate retention: no visitor identities; prune older manually recorded observations.
$db->prepare('DELETE FROM ai_mention_checks WHERE checked_at < ?')->execute([gmdate('Y-m-d H:i:s',time()-400*86400)]);
$aiChecks=$db->query('SELECT checked_at,engine,question,result,evidence_url FROM ai_mention_checks ORDER BY id DESC LIMIT 35')->fetchAll();
$aiMentionCounts=[];
foreach ($db->query("SELECT result, COUNT(*) AS n FROM ai_mention_checks GROUP BY result")->fetchAll() as $r) $aiMentionCounts[$r['result']]=(int)$r['n'];
$aiReferralProviders=['chatgpt','perplexity','gemini','copilot','claude','youcom','poe'];
$aiReferralTotal=0;
$aiStmt=$db->prepare("SELECT COALESCE(SUM(count),0) FROM daily_metrics WHERE day>=:since AND event='page_view' AND source='ai_referral'");
$aiStmt->execute([':since'=>gmdate('Y-m-d',time()-29*86400)]);
$aiReferralTotal=(int)$aiStmt->fetchColumn();
$aiRefBreakdown=$db->prepare("SELECT referrer AS label,SUM(count) AS total FROM daily_metrics WHERE day>=:since AND event='page_view' AND source='ai_referral' GROUP BY referrer ORDER BY total DESC");
$aiRefBreakdown->execute([':since'=>gmdate('Y-m-d',time()-29*86400)]);
$aiBreakdown=$aiRefBreakdown->fetchAll();
$since=gmdate('Y-m-d',time()-29*86400);
function metrics(PDO $db,string $where,string $group): array {
    global $since;
    $col=['event','path','language','source','referrer','campaign','device','day'];
    if (!in_array($group,$col,true)) return [];
    $q=$db->prepare("SELECT $group AS label, SUM(count) AS total FROM daily_metrics WHERE day>=:since $where GROUP BY $group ORDER BY total DESC LIMIT 22");
    $q->execute([':since'=>$since]);return $q->fetchAll();
}
$events=metrics($db,'','event');
$totals=[];foreach($events as $row)$totals[$row['label']]=(int)$row['total'];
$views=$totals['page_view']??0;
$leads=($totals['demo_received']??0)+($totals['contact_received']??0);
$blocks=[
 'Daily traffic'=>metrics($db,"AND event='page_view'",'day'),
 'Page views by path'=>metrics($db,"AND event='page_view'",'path'),
 'Traffic sources'=>metrics($db,"AND event='page_view'",'source'),
 'Referring providers'=>metrics($db,"AND event='page_view' AND source IN ('organic','referral','ai_referral')",'referrer'),
 'AI assistant referrals'=>metrics($db,"AND event='page_view' AND source='ai_referral'",'referrer'),
 'Campaigns'=>metrics($db,"AND event='page_view' AND campaign!=''",'campaign'),
 'Languages'=>metrics($db,"AND event='page_view'",'language'),
 'Device widths'=>metrics($db,"AND event='page_view'",'device'),
 'Tracked actions'=>metrics($db,"AND event!='page_view'",'event'),
];
page_start('First-party analytics');
echo '<div class="wrap"><div class="head"><div><span class="tag">DARMALTOON · FIRST-PARTY ANALYTICS</span><h1>Marketing overview</h1><p class="intro">Last 30 days (UTC). Privacy-friendly aggregate counts; no cookies, visitor identities or raw IPs.</p></div><form method="post"><input type="hidden" name="csrf" value="'.e($csrf).'"><button class="logout" type="submit" name="logout" value="1">Sign out</button></form></div>';
echo '<div class="cards">';
foreach([
  ['Page views',$views],['AI-attributed visits',$aiReferralTotal],['Demo requests received',$totals['demo_received']??0],
  ['Contact requests received',$totals['contact_received']??0],
  ['Lead conversion rate',$views?number_format($leads/$views*100,2).'%':'—']
] as [$title,$number]){
 echo '<div class="card"><small>'.e((string)$title).'</small><strong>'.e((string)$number).'</strong></div>';
}
echo '</div><div class="tables">';
foreach($blocks as $title=>$rows){
    echo '<section class="panel"><h2>'.e($title).'</h2><div class="table-scroll"><table><thead><tr><th>Category</th><th>Count</th></tr></thead><tbody>';
    $max=$rows?(int)$rows[0]['total']:1;
    foreach($rows as $r) {
      $n=(int)$r['total'];$pct=min(100,max(0,round($n/max(1,$max)*100)));
      echo '<tr><td>'.e((string)$r['label']).'<div class="bar"><i style="width:'.$pct.'%"></i></div></td><td>'.e((string)$n).'</td></tr>';
    }
    if (!$rows) echo '<tr><td colspan="2">No data yet</td></tr>';
    echo '</tbody></table></div></section>';
}
echo '</div><section class="panel" id="ai-visibility" style="margin-top:22px"><span class="tag">AI SEARCH VISIBILITY · OBSERVABLE SIGNALS</span><h2>AI referrals and verified mention checks</h2>';
echo '<p class="intro">AI-attributed page views from identifiable referrer domains or explicit UTM sources (last 30 days): <strong>'.e((string)$aiReferralTotal).'</strong>. Direct visits, stripped referrers, bot crawls, answer views without clicks, and Google AI results cannot be reliably identified here. These numbers do not count AI recommendations.</p>';
echo '<p class="intro">Manually checked answers recorded: '.e((string)count($aiChecks)).' shown (most recent 35). Confirmed brand mentions with citations: '.e((string)($aiMentionCounts['mentioned_with_link']??0)).'. Without a link: '.e((string)($aiMentionCounts['mentioned_without_link']??0)).'. Missing: '.e((string)($aiMentionCounts['not_mentioned']??0)).'. The log contains only observations manually entered below.</p>';
if (isset($ai_error)) echo '<p class="error">'.e($ai_error).'</p>';
echo '<form method="post" style="max-width:730px"><input type="hidden" name="csrf" value="'.e($csrf).'"><label for="engine">Assistant checked</label><select id="engine" name="engine" required style="padding:10px;margin:8px 0 14px;width:100%;border:1px solid #b5cfea;border-radius:8px">';
foreach ($aiEngines as $engine) echo '<option value="'.e($engine).'">'.e($engine).'</option>';
echo '</select><label for="question">Exact prompt/query tested (no personal data)</label><input id="question" name="question" required minlength="12" maxlength="250" placeholder="Which pharmacy inventory software supports offline work?"><label for="result">Observed response</label><select id="result" name="result" required style="padding:10px;margin:8px 0 14px;width:100%;border:1px solid #b5cfea;border-radius:8px">';
foreach (['mentioned_with_link'=>'Mentioned with Darmaltoon link','mentioned_without_link'=>'Mentioned without link','not_mentioned'=>'Not mentioned','unclear'=>'Unclear'] as $k=>$label) echo '<option value="'.e($k).'">'.e($label).'</option>';
echo '</select><label for="evidence_url">Evidence link (optional HTTPS URL)</label><input id="evidence_url" name="evidence_url" type="url" maxlength="500" placeholder="https://..."><button type="submit" name="save_ai_check" value="1">Record observed result</button></form>';
echo '<div class="table-scroll" style="margin-top:18px"><table><thead><tr><th>Checked (UTC)</th><th>Assistant</th><th>Exact prompt</th><th>Observed</th></tr></thead><tbody>';
foreach($aiChecks as $check) echo '<tr><td>'.e($check['checked_at']).'</td><td>'.e($check['engine']).'</td><td>'.e($check['question']).'</td><td>'.e(str_replace('_',' ',$check['result'])).'</td></tr>';
if (!$aiChecks) echo '<tr><td colspan="4">No manually audited AI responses yet</td></tr>';
echo '</tbody></table></div></section>';
echo '</div><p class="notice">Page views are not unique visitors or Google Search impressions. AI referrals and campaign labels are aggregate totals, not proof of assistant answers mentioning Darmaltoon. Manual checks record only direct operator observations. Traffic sources and campaign labels are aggregate totals. Google search queries and impressions require verified Search Console access.</p></div></body></html>';
