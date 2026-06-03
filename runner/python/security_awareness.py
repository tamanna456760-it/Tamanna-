# Security education materials
class SecurityEducation:
    def __init__(self):
        self.lessons = {
            "phishing": self.phishing_awareness,
            "passwords": self.password_security,
            "social_engineering": self.social_engineering_defense,
        }

    def phishing_awareness(self):
        """Teach about phishing detection"""
        tips = [
            "Check sender email addresses carefully",
            "Look for spelling and grammar mistakes",
            "Hover over links before clicking",
            "Never give passwords via email",
            "Verify unexpected attachments",
        ]
        return tips

    def password_security(self):
        """Teach strong password practices"""
        guidelines = [
            "Use at least 12 characters",
            "Include numbers, symbols, uppercase and lowercase",
            "Don't reuse passwords across sites",
            "Use a password manager",
            "Enable two-factor authentication",
        ]
        return guidelines
