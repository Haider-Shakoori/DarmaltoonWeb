<?php
declare(strict_types=1);

/** Local DB-IP Lite (CC BY 4.0) lookup: no external requests and no IP storage. */
if (PHP_SAPI !== 'cli' && realpath((string)($_SERVER['SCRIPT_FILENAME'] ?? '')) === __FILE__) {
    http_response_code(404); exit;
}
function dal_geo_country(string $ip): string {
    if (!filter_var($ip,FILTER_VALIDATE_IP,FILTER_FLAG_NO_PRIV_RANGE|FILTER_FLAG_NO_RES_RANGE)) return 'ZZ';
    $bytes=@inet_pton($ip);
    if ($bytes===false) return 'ZZ';
    $file=dirname(__DIR__,2).'/.darmaltoon-analytics/geo-country.sqlite';
    if (!is_file($file) || !is_readable($file)) return 'ZZ';
    try {
        $db=new PDO('sqlite:file:'.$file.'?mode=ro',null,null,
            [PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION,PDO::ATTR_TIMEOUT=>2]);
        $table=strlen($bytes)===4?'v4':'v6';
        $q=$db->prepare("SELECT end_ip,country FROM $table WHERE start_ip <= ? ORDER BY start_ip DESC LIMIT 1");
        $q->bindValue(1,$bytes,PDO::PARAM_LOB);
        $q->execute();
        $row=$q->fetch(PDO::FETCH_ASSOC);
        if (!$row || strcmp($bytes,$row['end_ip'])>0) return 'ZZ';
        $c=$row['country'];
        return preg_match('/^[A-Z]{2}$/D',$c)?$c:'ZZ';
    } catch(Throwable $e) {
        error_log('Darmaltoon geo lookup failure: '.get_class($e));
        return 'ZZ';
    }
}
