<?php
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');
header('Access-Control-Allow-Origin: https://darmaltoon.com');
header('Access-Control-Allow-Credentials: false');
header('X-Robots-Tag: noindex');
function dal_reply(int $code): never {
    http_response_code($code);
    echo json_encode(['ok'=>$code===202]);
    exit;
}
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Allow: POST');
    dal_reply(405);
}
$origin = (string)($_SERVER['HTTP_ORIGIN'] ?? '');
if ($origin !== '' && !hash_equals('https://darmaltoon.com',rtrim($origin,'/'))) dal_reply(403);
if (!str_starts_with(strtolower((string)($_SERVER['CONTENT_TYPE'] ?? '')),'application/json')) dal_reply(415);
if ((int)($_SERVER['CONTENT_LENGTH'] ?? 0) > 1024) dal_reply(413);
$raw=file_get_contents('php://input',false,null,0,1025);
$data=json_decode($raw ?: '',true);
if (!is_array($data)) dal_reply(400);
function tiny(array $d,string $key,int $max): string {
    $v=$d[$key] ?? '';
    return is_string($v) ? substr($v,0,$max) : '';
}
// Exclude signed-in platform-owner browser visits across *.darmaltoon.com.
if (($_COOKIE['dt_analytics_exclude'] ?? '') === '1') dal_reply(202);
if (!empty($data['optOut'])) dal_reply(202);
$event=tiny($data,'event',30);
$path=tiny($data,'path',100);
$lang=tiny($data,'language',8);
$src=tiny($data,'source',20);
$campaign=tiny($data,'campaign',60);
$device=tiny($data,'device',12);
$referrer=tiny($data,'referrer',20);
$visitorId=tiny($data,'visitorId',40);
$sessionId=tiny($data,'sessionId',40);
$utmTerm=tiny($data,'utmTerm',100);
// Public pages must not be able to forge successful lead conversions.
if (!in_array($event, ['page_view','engaged','demo_click','contact_click','whatsapp_click','email_click'], true)) dal_reply(422);
// Count only server-approved properties; ignore arbitrary client metadata entirely.
try {
    require_once __DIR__.'/analytics-store.php';
    dal_analytics_record($event,$path,$lang,$src,$campaign,$device,$referrer,$visitorId,$sessionId,$utmTerm);
    dal_reply(202);
} catch(Throwable $e) {
    error_log('Darmaltoon analytics: '.get_class($e));
    dal_reply(503);
}
