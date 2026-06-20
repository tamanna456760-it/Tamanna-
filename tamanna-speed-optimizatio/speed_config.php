// আউটপুট বাফারিং চালু (পেজ লোড টাইম কমায়)
ob_start();

// ডিফল্ট টাইমআউট বাড়ান (দীর্ঘ অপারেশনের জন্য)
set_time_limit(300);

// মেমোরি লিমিট বাড়ান (প্রয়োজনে)
ini_set('memory_limit', '256M');

// Gzip আউটপুট কম্প্রেশন (PHP থেকেও)
if (substr_count($_SERVER['HTTP_ACCEPT_ENCODING'], 'gzip')) {
    ob_start('ob_gzhandler');
} else {
    ob_start();
}