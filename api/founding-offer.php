<?php
declare(strict_types=1);

/**
 * Public aggregate-only bridge for the Darmaltoon Standard launch offer.
 * No direct SQLite access or exposure of the server-to-server import token.
 * Production opt-in: set private platform-offer.php outside the web root.
 */
header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('X-Robots-Tag: noindex, nofollow, noarchive');
header('Access-Control-Allow-Origin: https://darmaltoon.com');
header('Cache-Control: public, max-age=30');

function unavailable(): never {
    http_response_code(503);
    echo '{"ok":false,"message":"Live founding-customer availability is temporarily unavailable."}';
    exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'GET') {
    header('Allow: GET');
    http_response_code(405);
    echo '{"ok":false}';
    exit;
}

$config = dirname(__DIR__, 2).'/.darmaltoon-leads/platform-offer.php';
if (!is_file($config) || !is_readable($config)) unavailable();

$settings = require $config;
$url = is_array($settings) ? ($settings['url'] ?? '') : '';
if (!is_string($url) || !filter_var($url, FILTER_VALIDATE_URL)
    || !str_starts_with($url, 'https://')
    || parse_url($url, PHP_URL_USER) !== null
    || parse_url($url, PHP_URL_PASS) !== null
    || parse_url($url, PHP_URL_QUERY) !== null
    || parse_url($url, PHP_URL_FRAGMENT) !== null
    || parse_url($url, PHP_URL_PATH) !== '/api/v1/marketing/launch-offer'
    || !function_exists('curl_init')) unavailable();

$ch = curl_init($url);
if ($ch === false) unavailable();
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_CONNECTTIMEOUT => 3,
    CURLOPT_TIMEOUT => 6,
    CURLOPT_FOLLOWLOCATION => false,
    CURLOPT_SSL_VERIFYPEER => true,
    CURLOPT_SSL_VERIFYHOST => 2,
    CURLOPT_PROTOCOLS => CURLPROTO_HTTPS,
    CURLOPT_HTTPHEADER => ['Accept: application/json'],
]);
$response = curl_exec($ch);
$status = curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
curl_close($ch);
if (!is_string($response) || $status !== 200 || strlen($response) > 4096) unavailable();

$body = json_decode($response, true);
if (!is_array($body) || !isset($body['founding_remaining'], $body['founding_limit'], $body['founding_confirmed'])
    || !is_int($body['founding_remaining']) || !is_int($body['founding_confirmed'])
    || $body['founding_limit'] !== 10
    || $body['founding_remaining'] < 0 || $body['founding_remaining'] > 10
    || $body['founding_confirmed'] < 0 || $body['founding_confirmed'] > 10
    || $body['founding_remaining'] + $body['founding_confirmed'] !== 10
    || ($body['renewal_price_afn'] ?? null) !== '5000.00'
    || ($body['regular_first_year_price_afn'] ?? null) !== '7000.00'
    || !in_array($body['first_year_price_afn'] ?? '', ['5000.00', '7000.00'], true)) unavailable();

// Whitelisted aggregates ONLY; never proxy customer details.
echo json_encode([
    'ok' => true,
    'founding_remaining' => $body['founding_remaining'],
    'first_year_price_afn' => $body['first_year_price_afn'],
    'regular_first_year_price_afn' => $body['regular_first_year_price_afn'],
    'renewal_price_afn' => $body['renewal_price_afn'],
], JSON_THROW_ON_ERROR);
