# Example of using the pattern recognition neural networks
async def example_usage():
    """Example usage of pattern recognition neural networks"""

    # Initialize CNN Pattern Detector
    cnn_detector = CNNPatternDetector()

    # Build and compile model
    cnn_detector.build_model()
    cnn_detector.compile_model()

    # Example training data (replace with actual data)
    X_train = np.random.random((1000, 100, 100, 3))
    y_train = tf.keras.utils.to_categorical(np.random.randint(0, 10, 1000), 10)

    # Train the model
    training_result = await cnn_detector.train(X_train, y_train)
    print(f"CNN Training Accuracy: {training_result['final_accuracy']:.4f}")

    # Save the model
    await cnn_detector.save_model("1.0.0")

    # Make predictions
    X_test = np.random.random((100, 100, 100, 3))
    predictions = await cnn_detector.predict(X_test)

    # Analyze patterns
    pattern_analysis = await cnn_detector.detect_patterns(
        X_test, confidence_threshold=0.8
    )
    print(
        f"High confidence patterns detected: {pattern_analysis['high_confidence_matches']}"
    )


# Run the example
if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
