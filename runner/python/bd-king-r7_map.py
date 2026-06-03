# Specific test cases for BD-King-R7 fullmap
def test_bd_king_r7_specific():
    """Test specific BD-King-R7 functionality"""
    fullmap = BDKingR7Fullmap()

    # Test known key locations
    key_locations = [
        (100, 150),  # Replace with actual key coordinates
        (300, 400),
        (500, 600),
    ]

    for location in key_locations:
        # Test if locations are accessible
        assert fullmap.is_within_bounds(
            *location), f"Location {location} out of bounds"
        assert not fullmap.check_collision(
            location
        ), f"Location {location} has collision"

    # Test specific routes
    test_routes = [
        ((0, 0), (100, 100)),
        ((50, 50), (200, 200)),
        ((100, 100), (300, 300)),
    ]

    for start, end in test_routes:
        path = fullmap.find_path(start, end)
        assert path is not None, f"No path found from {start} to {end}"
        assert len(path) > 0, f"Empty path from {start} to {end}"


# Configuration validation
def test_configuration():
    """Test configuration parameters"""
    fullmap = BDKingR7Fullmap()

    required_attributes = [
        "width",
        "height",
        "grid",
        "obstacles",
        "start_position",
        "end_positions",
    ]

    for attr in required_attributes:
        assert hasattr(fullmap, attr), f"Missing required attribute: {attr}"

    # Validate specific BD-King-R7 requirements
    assert fullmap.width > 0, "Map width must be positive"
    assert fullmap.height > 0, "Map height must be positive"


# Run specific tests
if __name__ == "__main__":
    print("Running BD-King-R7 specific tests...")
    test_bd_king_r7_specific()
    test_configuration()
    print("All specific tests passed!")
