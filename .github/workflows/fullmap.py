import unittest
from your_bd_king_r7_module import BDKingR7Fullmap  # Replace with your actual import

class TestBDKingR7Fullmap(unittest.TestCase):
    
    def setUp(self):
        """Initialize the fullmap instance before each test"""
        self.fullmap = BDKingR7Fullmap()
    
    def test_initialization(self):
        """Test that the fullmap initializes correctly"""
        self.assertIsNotNone(self.fullmap)
        # Add more specific initialization tests
    
    def test_map_dimensions(self):
        """Test map dimensions are correct"""
        expected_width = 1920  # Replace with expected dimensions
        expected_height = 1080
        self.assertEqual(self.fullmap.width, expected_width)
        self.assertEqual(self.fullmap.height, expected_height)
    
    def test_coordinate_system(self):
        """Test coordinate system functionality"""
        # Test coordinate conversion
        test_x, test_y = 100, 200
        converted = self.fullmap.convert_coordinates(test_x, test_y)
        self.assertEqual(len(converted), 2)
    
    def test_pathfinding(self):
        """Test pathfinding algorithms"""
        start = (0, 0)
        end = (100, 100)
        path = self.fullmap.find_path(start, end)
        self.assertIsInstance(path, list)
        if path:  # If path exists
            self.assertEqual(path[0], start)
            self.assertEqual(path[-1], end)
    
    def test_collision_detection(self):
        """Test collision detection"""
        # Test non-colliding point
        free_point = (50, 50)
        self.assertFalse(self.fullmap.check_collision(free_point))
        
        # Test colliding point (if known)
        if hasattr(self.fullmap, 'obstacles'):
            obstacle_point = self.fullmap.obstacles[0] if self.fullmap.obstacles else (9999, 9999)
            self.assertTrue(self.fullmap.check_collision(obstacle_point))
    
    def test_boundary_conditions(self):
        """Test behavior at map boundaries"""
        # Test within bounds
        self.assertTrue(self.fullmap.is_within_bounds(10, 10))
        
        # Test outside bounds
        self.assertFalse(self.fullmap.is_within_bounds(-1, -1))
        self.assertFalse(self.fullmap.is_within_bounds(self.fullmap.width + 1, self.fullmap.height + 1))

# Performance testing
def test_performance():
    """Performance test for the fullmap"""
    import time
    
    fullmap = BDKingR7Fullmap()
    
    # Test initialization time
    start_time = time.time()
    fullmap = BDKingR7Fullmap()
    init_time = time.time() - start_time
    print(f"Initialization time: {init_time:.4f} seconds")
    
    # Test pathfinding performance
    start_time = time.time()
    for _ in range(100):  # Multiple pathfinding operations
        fullmap.find_path((0, 0), (100, 100))
    pathfinding_time = time.time() - start_time
    print(f"Average pathfinding time: {pathfinding_time/100:.4f} seconds")

# Visual testing (if applicable)
def visual_test():
    """Visual representation test"""
    try:
        fullmap = BDKingR7Fullmap()
        
        # If your fullmap has visualization capabilities
        if hasattr(fullmap, 'visualize'):
            fullmap.visualize()
            print("Visual test completed - check the generated visualization")
        else:
            print("No visualization method available")
            
    except Exception as e:
        print(f"Visual test failed: {e}")

if __name__ == "__main__":
    # Run unit tests
    unittest.main(verbosity=2)
    
    # Run performance tests
    print("\n" + "="*50)
    print("PERFORMANCE TESTS")
    print("="*50)
    test_performance()
    
    # Run visual test
    print("\n" + "="*50)
    print("VISUAL TEST")
    print("="*50)
    visual_test()