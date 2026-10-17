<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit(1);
$root=rtrim((string)getenv('HOME'),'/').'/.darmaltoon-analytics';
if (!is_dir($root)) {umask(0077);mkdir($root,0700,true);}
$file=$root.'/admin-password.hash';
if (is_file($file) && !in_array('--rotate',$argv,true)) {
    echo "Password already configured. Use --rotate to change it.\n";exit(1);
}
// Print once to an authorized terminal. Never write/store plaintext password to disk.
$password=rtrim(strtr(base64_encode(random_bytes(24)),'+/','-_'),'=');
$hash=password_hash($password,PASSWORD_DEFAULT);
if (file_put_contents($file,$hash."\n",LOCK_EX)===false) exit(1);
chmod($file,0600);
echo "Darmaltoon owner analytics login\nURL: https://darmaltoon.com/admin/analytics.php\nUsername: not needed\nInitial password (copy now, shown only once): $password\n";
