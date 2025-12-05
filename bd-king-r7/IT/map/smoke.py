# Quick smoke test for basic functionality
def smoke_test():
    """Quick test to verify basic functionality"""
    try:
        from your_bd_king_r7_module import BDKingR7Fullmap
        
        # Basic initialization
        fullmap = BDKingR7Fullmap()
        print("✓ Initialization successful")
        
        # Basic operations
        path = fullmap.find_path((0, 0), (100, 100))
        print("✓ Pathfinding functional")
        
        # Coordinate check
        within_bounds = fullmap.is_within_bounds(50, 50)
        print("✓ Coordinate checking functional")
        
        print("🎉 Smoke test passed! Basic functionality is working.")
        return True
        
    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        return False

# Run smoke test
smoke_test()