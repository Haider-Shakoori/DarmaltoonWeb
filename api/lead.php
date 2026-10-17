<?php
declare(strict_types=1);

/**
 * Darmaltoon — publicly accessible lead intake, private storage outside document root.
 * Never exposes records or secrets through an HTTP GET or an admin URL.
 */
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, private');
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: no-referrer');
header('X-Robots-Tag: noindex, nofollow, noarchive');
header('Access-Control-Allow-Credentials: false');

function reply(int $status, array $payload): never {
    http_response_code($status);
    echo json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Allow: POST');
    reply(405, ['ok' => false, 'message' => 'POST required']);
}
$origin = (string)($_SERVER['HTTP_ORIGIN'] ?? '');
if ($origin !== '' && !hash_equals('https://web.darmaltoon.com', rtrim($origin, '/'))) {
    reply(403, ['ok' => false, 'message' => 'Origin not allowed']);
}
if (!str_starts_with(strtolower((string)($_SERVER['CONTENT_TYPE'] ?? '')), 'application/json')) {
    reply(415, ['ok' => false, 'message' => 'JSON required']);
}
$length = (int)($_SERVER['CONTENT_LENGTH'] ?? 0);
if ($length <= 0 || $length > 12000) reply(413, ['ok' => false, 'message' => 'Request too large or empty']);
$raw = file_get_contents('php://input', false, null, 0, 12001);
if ($raw === false || strlen($raw) > 12000) reply(413, ['ok' => false, 'message' => 'Request too large']);
$data = json_decode($raw, true);
if (!is_array($data)) reply(400, ['ok' => false, 'message' => 'Invalid JSON']);
if (!empty($data['website'])) reply(201, ['ok' => true]); // honeypot silently discards bots

function val(array $data, string $field, int $limit=200): string {
    $v = $data[$field] ?? '';
    if (!is_string($v)) return '';
    return trim(mb_substr(preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $v) ?? '', 0, $limit));
}
$kind = val($data, 'kind', 15);
if (!in_array($kind, ['demo', 'contact'], true)) reply(422, ['ok' => false, 'message' => 'Invalid request type']);
$name = val($data, 'name', 100);
$phone = val($data, 'phone', 40);
$email = val($data, 'email', 200);
$pharmacy = val($data, 'pharmacy', 160);
$message = val($data, 'message', 1200);
$lang = val($data, 'language', 8);
if (!in_array($lang, ['en', 'fa', 'ps'], true)) $lang = 'en';
if (mb_strlen($name) < 2 || mb_strlen($name) > 100) reply(422, ['ok' => false, 'message' => 'Valid name required']);
if (mb_strlen($phone) < 6 || mb_strlen($phone) > 40 || !preg_match('/^[+0-9 ()-]{6,40}$/', $phone)) reply(422, ['ok' => false, 'message' => 'Valid phone required']);
if ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL)) reply(422, ['ok' => false, 'message' => 'Invalid email']);
if ($kind === 'contact' && ($email === '' || mb_strlen($message) < 3)) reply(422, ['ok' => false, 'message' => 'Email and message required']);
if (($data['consent'] ?? false) !== true) reply(422, ['ok' => false, 'message' => 'Consent required']);

$optional = [];
foreach (['branches','city','province','computers','preferredContact','whatsapp','inquiryType','subject'] as $field) {
    $v = val($data, $field, 150);
    if ($v !== '') $optional[$field] = $v;
}
$siteRoot = dirname(__DIR__);
$privateDir = dirname($siteRoot) . '/.darmaltoon-leads';
try {
    if (!is_dir($privateDir)) {
        umask(0077);
        if (!mkdir($privateDir, 0700, true) && !is_dir($privateDir)) throw new RuntimeException('Cannot create private storage');
    }
    $secretFile = $privateDir . '/ip-key';
    if (!is_file($secretFile)) {
        $secret = bin2hex(random_bytes(32));
        if (file_put_contents($secretFile, $secret, LOCK_EX) === false) throw new RuntimeException('Cannot initialize private key');
        chmod($secretFile, 0600);
    }
    $secret = trim((string)file_get_contents($secretFile));
    if (strlen($secret) < 32) throw new RuntimeException('Bad private key');
    $dbFile = $privateDir . '/leads.sqlite';
    $db = new PDO('sqlite:' . $dbFile, null, null, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_TIMEOUT => 5
    ]);
    $db->exec('PRAGMA busy_timeout=5000');
    $db->exec('CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at INTEGER NOT NULL,
        kind TEXT NOT NULL,
        language TEXT NOT NULL,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        pharmacy TEXT,
        message TEXT,
        details_json TEXT NOT NULL,
        visitor_hash TEXT NOT NULL,
        notification_attempted INTEGER DEFAULT 0,
        notification_queued INTEGER DEFAULT 0
    )');
    $db->exec('CREATE INDEX IF NOT EXISTS lead_ip_time ON leads(visitor_hash, created_at)');
    @chmod($dbFile, 0600);
    $addr = (string)($_SERVER['REMOTE_ADDR'] ?? 'unknown');
    $ipHash = hash_hmac('sha256', $addr, $secret);
    $now = time();
    $db->beginTransaction();
    $limiter = $db->prepare('SELECT
        SUM(CASE WHEN created_at >= :hour THEN 1 ELSE 0 END) as in_hour,
        SUM(CASE WHEN created_at >= :day THEN 1 ELSE 0 END) as in_day,
        MAX(created_at) as last_lead
        FROM leads WHERE visitor_hash = :hash AND created_at >= :day2');
    $limiter->execute([':hash'=>$ipHash, ':hour'=>$now-3600, ':day'=>$now-86400, ':day2'=>$now-86400]);
    $recent = $limiter->fetch();
    if ((int)($recent['in_hour'] ?? 0) >= 5 || (int)($recent['in_day'] ?? 0) >= 16 ||
        $now - (int)($recent['last_lead'] ?? 0) < 45) {
        $db->rollBack();
        header('Retry-After: 60');
        reply(429, ['ok' => false, 'message' => 'Please wait and try again or contact us by email.']);
    }
    $insert = $db->prepare('INSERT INTO leads
      (created_at, kind, language, name, phone, email, pharmacy, message, details_json, visitor_hash)
      VALUES (:created,:kind,:language,:name,:phone,:email,:pharmacy,:message,:details,:hash)');
    $insert->execute([
      ':created'=>$now, ':kind'=>$kind, ':language'=>$lang, ':name'=>$name, ':phone'=>$phone,
      ':email'=>$email, ':pharmacy'=>$pharmacy, ':message'=>$message,
      ':details'=>json_encode($optional, JSON_UNESCAPED_UNICODE), ':hash'=>$ipHash
    ]);
    $id = (int)$db->lastInsertId();
    $db->commit();

    // Best-effort notification. Storage is the canonical record: mail() success only
    // confirms local queueing, never final email delivery.
    $subject = '[Darmaltoon] New ' . $kind . ' request #' . $id;
    $lines = ['Darmaltoon website request', 'ID: '.$id, 'Type: '.$kind,
      'Language: '.$lang, 'Name: '.$name, 'Phone: '.$phone,
      'Email: '.$email, 'Pharmacy: '.$pharmacy, 'Message: '.$message,
      'Details: '.json_encode($optional, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES),
      'Timestamp UTC: '.gmdate('c',$now)];
    $headers = [
        'From: Darmaltoon <noreply@darmaltoon.com>',
        'MIME-Version: 1.0',
        'Content-Type: text/plain; charset=UTF-8'
    ];
    if ($email !== '') $headers[] = 'Reply-To: ' . $email;
    $queued = @mail('info@businessos.af', $subject, implode("\n", $lines), implode("\r\n", $headers));
    $q = $db->prepare('UPDATE leads SET notification_attempted=1,notification_queued=:queued WHERE id=:id');
    $q->execute([':queued'=>$queued ? 1 : 0, ':id'=>$id]);
    reply(201, ['ok'=>true, 'received'=>true,
      'message'=>'Your request has been recorded. We will use your contact details to follow up.']);
} catch (Throwable $e) {
    if (isset($db) && $db->inTransaction()) $db->rollBack();
    error_log('Darmaltoon lead intake error: '.get_class($e)); // never log PII
    reply(503, ['ok'=>false, 'message'=>'Online submission is temporarily unavailable. Please use email or WhatsApp.']);
}
