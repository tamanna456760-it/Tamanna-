// সমস্ত স্ক্রিপ্ট অ্যাসিঙ্ক্রোনাসলি লোড করুন
function loadScriptAsync(src) {
    var script = document.createElement('script');
    script.src = src;
    script.async = true;
    document.body.appendChild(script);
}

// ব্যবহার উদাহরণ:
loadScriptAsync('https://cdn.example.com/your-script.js');