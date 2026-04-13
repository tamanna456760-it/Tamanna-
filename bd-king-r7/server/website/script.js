function showMessage() {
    alert("আপনার ওয়েবসাইটটি সফলভাবে তৈরি হয়েছে!");
}

// নেভিগেশন স্মুথ স্ক্রল
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if(target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});