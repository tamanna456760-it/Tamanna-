# Example usage of the Learning System
async def example_usage():
    # Initialize learning system
    learning_system = AdaptiveLearningSystem()
    await learning_system.initialize()

    # Learn from an experience episode
    episode_data = {
        "mode": "reinforcement",
        "input": {
            "state": "high_traffic",
            "action_taken": "scale_resources",
            "features": {"cpu_usage": 0.85, "memory_usage": 0.75},
        },
        "predictions": {"expected_outcome": "improved_performance"},
        "outcomes": {"actual": {"performance_improvement": 0.15}},
        "reward": 0.8,
        "lessons": {"resource_scaling_effective": True},
        "metadata": {"domain": "system_optimization"},
    }

    learning_result = await learning_system.learn_from_experience(episode_data)
    print(f"Learning gain: {learning_result['learning_gain']}")

    # Get recommendations
    context = {"situation": "high_traffic", "resources": "constrained"}
    recommendations = await learning_system.get_recommendations(context)

    for rec in recommendations:
        print(
            f"Recommendation: {rec['recommendation']} (Confidence: {rec['confidence']})"
        )

    # Transfer learning between domains
    transfer_result = await learning_system.transfer_learning(
        "system_optimization", "security_optimization"
    )
    print(
        f"Transferred {transfer_result['transferred_units']} knowledge units")

    # Get learning metrics
    metrics = await learning_system.get_learning_metrics()
    print(f"Knowledge base size: {metrics['knowledge_base_size']}")

    # Save learning state
    await learning_system.save_learning_state()


# Run the example
if __name__ == "__main__":
    asyncio.run(example_usage())
