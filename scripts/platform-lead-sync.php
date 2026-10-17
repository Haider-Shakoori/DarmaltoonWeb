<?php
declare(strict_types=1);

/**
 * Website -> central SaaS lead delivery.
 *
 * This file is a library. It does not expose a public HTTP endpoint.
 * The private source SQLite remains canonical until a platform 2xx ack.
 * Configure env DARMALTOON_PLATFORM_LEADS_URL + DARMALTOON_PLATFORM_LEADS_TOKEN,
 * or /home/darmaltoon/.darmaltoon-leads/platform-sync.json (0600) containing
 * {"url":"https://.../api/v1/marketing/leads/import","token":"..."}.
 */

function dal_platform_sync_config(string $privateDir): ?array
{
    $url = trim((string)getenv('DARMALTOON_PLATFORM_LEADS_URL'));
    $token = trim((string)getenv('DARMALTOON_PLATFORM_LEADS_TOKEN'));

    if ($url === '' && $token === '') {
        $configPath = $privateDir . '/platform-sync.json';
        if (is_file($configPath)) {
            $mode = fileperms($configPath) & 0777;
            if (($mode & 0077) !== 0) {
                error_log('Darmaltoon sync configuration file permissions are too broad');
                return null;
            }
            $config = json_decode((string)file_get_contents($configPath), true);
            if (is_array($config)) {
                $url = trim((string)($config['url'] ?? ''));
                $token = trim((string)($config['token'] ?? ''));
            }
        }
    }

    $parts = parse_url($url);
    if (!is_array($parts) || strtolower((string)($parts['scheme'] ?? '')) !== 'https'
        || empty($parts['host']) || !in_array((string)($parts['path'] ?? ''), ['/api/v1/marketing/leads/import'], true)
        || strlen($token) < 32 || !function_exists('curl_init')) {
        return null;
    }
    return ['url' => $url, 'token' => $token];
}

function dal_platform_sync_batch(PDO $db, string $privateDir, int $limit = 25): array
{
    $config = dal_platform_sync_config($privateDir);
    if ($config === null) {
        return ['configured' => false, 'delivered' => 0, 'attempted' => 0];
    }

    $db->exec('CREATE TABLE IF NOT EXISTS platform_lead_sync (
        lead_id INTEGER PRIMARY KEY,
        delivered_at INTEGER NOT NULL
    )');
    $limit = max(1, min(50, $limit));

    $query = $db->prepare('SELECT l.id, l.created_at, l.kind, l.language,
        l.name, l.phone, l.email, l.pharmacy, l.message, l.details_json
        FROM leads AS l LEFT JOIN platform_lead_sync AS s ON s.lead_id = l.id
        WHERE s.lead_id IS NULL ORDER BY l.id ASC LIMIT :limit');
    $query->bindValue(':limit', $limit, PDO::PARAM_INT);
    $query->execute();
    $rows = $query->fetchAll(PDO::FETCH_ASSOC);

    if (!$rows) return ['configured' => true, 'delivered' => 0, 'attempted' => 0];

    $leads = [];
    foreach ($rows as $row) {
        $details = json_decode((string)($row['details_json'] ?? '{}'), true);
        if (!is_array($details)) $details = [];
        $details = array_filter($details, static fn($v): bool => is_string($v));
        $leads[] = [
            'id' => (int)$row['id'],
            'created_at' => (int)$row['created_at'],
            'kind' => (string)$row['kind'],
            'language' => (string)$row['language'],
            'name' => (string)$row['name'],
            'phone' => (string)$row['phone'],
            'email' => (string)($row['email'] ?? ''),
            'pharmacy' => (string)($row['pharmacy'] ?? ''),
            'message' => (string)($row['message'] ?? ''),
            'details' => $details
        ];
    }

    $payload = json_encode(['leads' => $leads], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    if (!is_string($payload)) return ['configured' => true, 'delivered' => 0, 'attempted' => count($rows)];

    $curl = curl_init($config['url']);
    curl_setopt_array($curl, [
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => $payload,
        CURLOPT_HTTPHEADER => [
            'Authorization: Bearer '.$config['token'],
            'Content-Type: application/json',
            'Accept: application/json'
        ],
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CONNECTTIMEOUT => 2,
        CURLOPT_TIMEOUT => 5,
        CURLOPT_FOLLOWLOCATION => false,
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_SSL_VERIFYHOST => 2,
    ]);
    $response = curl_exec($curl);
    $code = (int)curl_getinfo($curl, CURLINFO_RESPONSE_CODE);
    curl_close($curl);

    $ack = is_string($response) ? json_decode($response, true) : null;
    if ($code < 200 || $code >= 300 || !is_array($ack) || ($ack['ok'] ?? null) !== true ||
        (int)($ack['imported'] ?? -1) + (int)($ack['already_present'] ?? -1) !== count($leads)) {
        // Do not log PII or tokens; next cron run retries the entire batch.
        error_log('Darmaltoon platform lead import failed (HTTP '.$code.')');
        return ['configured' => true, 'delivered' => 0, 'attempted' => count($leads)];
    }

    $stamp = time();
    $insert = $db->prepare('INSERT OR IGNORE INTO platform_lead_sync (lead_id, delivered_at) VALUES (?, ?)');
    foreach ($rows as $row) $insert->execute([(int)$row['id'], $stamp]);

    return ['configured' => true, 'delivered' => count($leads), 'attempted' => count($leads)];
}
