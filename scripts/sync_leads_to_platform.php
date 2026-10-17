<?php
declare(strict_types=1);

/**
 * Darmaltoon -> Platform Admin private lead synchronization.
 *
 * Run from cPanel cron / PHP CLI. Never expose customer details in stdout,
 * query strings, website analytics, or a publicly readable export file.
 * The source of truth remains the existing private website SQLite store.
 */
if (PHP_SAPI !== 'cli') {
    http_response_code(404);
    exit;
}

umask(0077);

$privateDir = dirname(__DIR__, 2).'/.darmaltoon-leads';
$dbFile = $privateDir.'/leads.sqlite';
$configFile = $privateDir.'/platform-sync.php';
$cursorFile = $privateDir.'/platform-sync.cursor';
$lockFile = $privateDir.'/platform-sync.lock';

if (!is_file($dbFile) || !is_readable($dbFile)) {
    fwrite(STDERR, "No readable private website lead database found.\n");
    exit(1);
}

if (!is_file($configFile) || !is_readable($configFile)) {
    fwrite(STDERR, "Private platform synchronization configuration is missing.\n");
    exit(1);
}
$settings = require $configFile;
if (!is_array($settings)) {
    fwrite(STDERR, "Invalid private platform synchronization configuration.\n");
    exit(1);
}
$url = $settings['url'] ?? '';
$token = $settings['token'] ?? '';
if (!is_string($url) || !is_string($token) || strlen($token) < 32
    || !filter_var($url, FILTER_VALIDATE_URL)
    || !str_starts_with($url, 'https://')
    || parse_url($url, PHP_URL_USER) !== null
    || parse_url($url, PHP_URL_PASS) !== null
    || parse_url($url, PHP_URL_FRAGMENT) !== null
    || parse_url($url, PHP_URL_QUERY) !== null) {
    fwrite(STDERR, "Invalid HTTPS destination or synchronization credential.\n");
    exit(1);
}
if (!function_exists('curl_init')) {
    fwrite(STDERR, "The PHP curl extension is required for secure synchronization.\n");
    exit(1);
}

$lock = fopen($lockFile, 'c');
if ($lock === false || !flock($lock, LOCK_EX | LOCK_NB)) {
    fwrite(STDERR, "A website lead sync is already in progress.\n");
    exit(1);
}
@chmod($lockFile, 0600);

try {
    $db = new PDO('sqlite:'.$dbFile, null, null, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_TIMEOUT => 5,
    ]);

    // New setup imports all previously saved leads from ID 1 onward.
    // Only advance after an acknowledged batch. Restart/replay is idempotent.
    $cursor = is_file($cursorFile) ? trim((string) file_get_contents($cursorFile)) : '0';
    if (!preg_match('/^(0|[1-9][0-9]{0,18})$/', $cursor)) {
        throw new RuntimeException('Invalid private sync cursor.');
    }
    $lastId = (int) $cursor;
    $processed = 0;
    $new = 0;

    $select = $db->prepare('SELECT id, created_at, kind, language, name, phone,
        email, pharmacy, message, details_json
        FROM leads WHERE id > :id ORDER BY id ASC LIMIT 50');

    while (true) {
        $select->bindValue(':id', $lastId, PDO::PARAM_INT);
        $select->execute();
        $rows = $select->fetchAll();
        if ($rows === []) {
            break;
        }

        $leads = [];
        foreach ($rows as $row) {
            $details = json_decode((string) ($row['details_json'] ?? '{}'), true);
            if (!is_array($details)) {
                $details = [];
            }
            // The website stores only string-valued optional metadata.
            // Do not transmit the visitor IP hash or mail queue flags.
            $safeDetails = [];
            foreach ($details as $key => $value) {
                if (is_string($key) && is_string($value) && count($safeDetails) < 12) {
                    $safeDetails[$key] = mb_substr($value, 0, 150);
                }
            }
            $leads[] = [
                'id' => (int) $row['id'],
                'created_at' => (int) $row['created_at'],
                'kind' => (string) $row['kind'],
                'language' => (string) $row['language'],
                'name' => (string) $row['name'],
                'phone' => (string) $row['phone'],
                'email' => (string) ($row['email'] ?? ''),
                'pharmacy' => (string) ($row['pharmacy'] ?? ''),
                'message' => (string) ($row['message'] ?? ''),
                'details' => $safeDetails,
            ];
        }

        $json = json_encode(['leads' => $leads], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR);
        $handle = curl_init($url);
        if ($handle === false) {
            throw new RuntimeException('Cannot initialize secure transfer.');
        }
        curl_setopt_array($handle, [
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $json,
            CURLOPT_HTTPHEADER => [
                'Content-Type: application/json',
                'Accept: application/json',
                'Authorization: Bearer '.$token,
            ],
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_CONNECTTIMEOUT => 10,
            CURLOPT_TIMEOUT => 35,
            CURLOPT_FOLLOWLOCATION => false,
            CURLOPT_SSL_VERIFYPEER => true,
            CURLOPT_SSL_VERIFYHOST => 2,
            CURLOPT_MAXREDIRS => 0,
            CURLOPT_PROTOCOLS => CURLPROTO_HTTPS,
        ]);
        $reply = curl_exec($handle);
        $http = curl_getinfo($handle, CURLINFO_RESPONSE_CODE);
        curl_close($handle);

        if (!is_string($reply) || $http !== 200) {
            throw new RuntimeException('Platform import was not accepted (HTTP '.(int) $http.').');
        }
        $receipt = json_decode($reply, true);
        if (!is_array($receipt) || ($receipt['ok'] ?? false) !== true
            || ((int) ($receipt['imported'] ?? -1) + (int) ($receipt['already_present'] ?? -1)) !== count($rows)) {
            throw new RuntimeException('Platform did not acknowledge the full lead batch.');
        }

        $lastId = (int) end($rows)['id'];
        $temp = $cursorFile.'.tmp.'.getmypid();
        if (file_put_contents($temp, (string) $lastId."\n", LOCK_EX) === false) {
            throw new RuntimeException('Cannot checkpoint imported leads.');
        }
        @chmod($temp, 0600);
        if (!rename($temp, $cursorFile)) {
            @unlink($temp);
            throw new RuntimeException('Cannot atomically update the private sync checkpoint.');
        }
        $processed += count($rows);
        $new += (int) $receipt['imported'];
    }

    // Report only safe counts; never disclose names, phone numbers or email.
    fwrite(STDOUT, "Lead sync complete: {$processed} processed, {$new} new, last ID {$lastId}.\n");
} catch (Throwable $exception) {
    error_log('Darmaltoon lead sync failed: '.get_class($exception));
    fwrite(STDERR, "Lead sync failed. Existing source data and the last valid checkpoint are preserved.\n");
    exit(1);
} finally {
    flock($lock, LOCK_UN);
    fclose($lock);
}
