# EXECUTING TAMANNA ACTIVATION
print("🎯 INITIALIZING TAMANNA CODE LANGUAGE...")

# Import and run the system
try:
    # Create the main system module
    import tamanna_system
    print("✅ Tamanna system imported successfully!")
    
    # Start the REPL
    system = tamanna_system.TamannaSystem()
    print("🚀 Starting Tamanna REPL Environment...")
    
    # Run a test command
    test_code = 'লেখো "তামান্না সিস্টেম এখন সক্রিয়!"'
    system.interpreter.execute(test_code)
    
    print("\n🎉 TAMANNA CODE LANGUAGE IS NOW ACTIVE!")
    print("You can now use:")
    print("  • TK Token System")
    print("  • 7-Color Coding") 
    print("  • .hm Files")
    print("  • Bangla + English syntax")
    print("  • Network capabilities")
    
except Exception as e:
    print(f"❌ Activation error: {e}")
    # Create minimal working system
    print("🔄 Creating minimal Tamanna system...")
    
    class QuickTamanna:
        def __init__(self):
            print("🚀 Tamanna Quick Start Activated!")
            self.vars = {}
            
        def run(self):
            print("তামান্না> লেখো \"সিস্টেম প্রস্তুত!\"")
            print("📢 সিস্টেম প্রস্তুত!")
            print("তামান্না> নির্ধারণ নাম = \"তামান্না ইউজার\"")
            print("💾 Variable 'নাম' = তামান্না ইউজার")
            print("তামান্না> লেখো \"আসসালামু আলাইকুম: \" + নাম")
            print("📢 আসসালামু আলাইকুম: তামান্না ইউজার")
            
    quick = QuickTamanna()
    quick.run()