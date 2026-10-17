<?php
declare(strict_types=1);
/* Optional cPanel cron task. Retries locally-rejected notification attempts;
   does not re-send anything that mail() already accepted for queueing. */
if (PHP_SAPI !== 'cli') exit(1);
$dir=rtrim((string)getenv('HOME'),'/').'/.darmaltoon-leads';
$file=$dir.'/leads.sqlite';
if (!is_file($file)) { echo "No lead records yet.\n"; exit(0); }
try {
    $db=new PDO('sqlite:'.$file,null,null,[
        PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION,PDO::ATTR_DEFAULT_FETCH_MODE=>PDO::FETCH_ASSOC
    ]);
    $q=$db->prepare('SELECT id,kind,language,name,phone,email,pharmacy,message,details_json
      FROM leads WHERE notification_queued=0 AND notification_attempted<3
      AND created_at<:minage ORDER BY id ASC LIMIT 15');
    $q->execute([':minage'=>time()-120]);
    $retry=$q->fetchAll();
    $update=$db->prepare('UPDATE leads SET notification_attempted=notification_attempted+1,
       notification_queued=:queued WHERE id=:id AND notification_queued=0 AND notification_attempted<3');
    foreach($retry as $lead) {
        $subject='[Darmaltoon] New '.$lead['kind'].' request #'.$lead['id'];
        $lines=['Darmaltoon website request','ID: '.$lead['id'],
            'Type: '.$lead['kind'],'Language: '.$lead['language'],
            'Name: '.$lead['name'],'Phone: '.$lead['phone'],
            'Email: '.$lead['email'],'Pharmacy: '.$lead['pharmacy'],
            'Message: '.$lead['message'],'Details: '.$lead['details_json']];
        $headers=['From: Darmaltoon <noreply@darmaltoon.com>',
          'MIME-Version: 1.0','Content-Type: text/plain; charset=UTF-8'];
        if (!empty($lead['email']) && filter_var($lead['email'],FILTER_VALIDATE_EMAIL))
            $headers[]='Reply-To: '.$lead['email'];
        $queued=@mail('info@businessos.af',$subject,implode("\n",$lines),implode("\r\n",$headers));
        $update->execute([':queued'=>$queued?1:0,':id'=>$lead['id']]);
    }
    echo count($retry)." notifications checked for retry.\n";
} catch(Throwable $e) {
    error_log('Darmaltoon retry notifier: '.get_class($e));
    exit(1);
}
