#!/usr/bin/env python3
"""
Test script for Tamanna AI commands
"""

def test_all_commands():
    """Test all Tamanna AI commands"""
    from tamanna_ai import TamannaAI
    
    ai = TamannaAI()
    
    print("🧪 Testing Tamanna AI Commands...")
    
    # Test 1: Help command
    print("\n1. Testing 'help' command:")
    ai.help_command()
    
    # Test 2: Tools command
    print("\n2. Testing 'tools' command:")
    ai.tools_command()
    
    # Test 3: Status command
    print("\n3. Testing 'status' command:")
    ai.status_command()
    
    # Test 4: Health command
    print("\n4. Testing 'health' command:")
    ai.health_command()
    
    print("\n✅ All basic commands tested successfully!")
    print("💡 Use the interactive mode for full functionality.")

if __name__ == "__main__":
    test_all_commands()