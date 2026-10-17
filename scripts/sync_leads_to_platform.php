<?php
declare(strict_types=1);

/**
 * Cron-only website lead replay. Backfills all historical demo and contact
 * requests and continuously retries unsent items without duplicating them.
 *
 * Example cPanel cron (set real PHP path):
 *   /usr/local/bin/php /home/darmaltoon/public_html/scripts/sync_leads_to_platform.php
 *
 * Keep the secret in a private file (0600) or PHP environment; never in Git.
 */
if (PHP_SAPI !== 'cli') {
    http_response_code(404);
    exit;
}

$privateDir = dirname(__DIR__, 2).'/.darmaltoon-leads';
$dbFile = $privateDir.'/leads.sqlite';
if (!is_file($dbFile)) {
    fwrite(STDERR, "No existing website lead database at configured private location.\n");
    exit(1);
}
require_once __DIR__.'/platform-lead-sync.php';

try {
    $db = new PDO('sqlite:'.$dbFile, null, null, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_TIMEOUT => 5
    ]);
    $db->exec('PRAGMA busy_timeout=5000');
    $total = 0;
    $attempts = 0;

    for ($batch = 0; $batch < 20; $batch++) {
        $result = dal_platform_sync_batch($db, $privateDir, 25);
        if (!$result['configured']) {
            fwrite(STDERR, "Lead integration is not configured; no records changed.\n");
            exit(2);
        }
        $total += $result['delivered'];
        $attempts += $result['attempted'];
        if ($result['attempted'] === 0) break;
        if ($result['delivered'] !== $result['attempted']) {
            fwrite(STDERR, "Lead integration failed: pending leads preserved for next retry.\n");
            exit(3);
        }
    }

    fwrite(STDOUT, "Imported/acknowledged {$total} website requests.\n");
} catch (Throwable $e) {
    error_log('Darmaltoon lead replay error: '.get_class($e));
    fwrite(STDERR, "Unable to sync requests; source records remain intact.\n");
    exit(4);
}
