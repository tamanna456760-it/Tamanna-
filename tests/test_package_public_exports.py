"""Ensure newly generated modules are reachable through package boundaries."""
def test_analysis_backup_learning_and_brain_public_exports():
    from tamanna_ai.analysis import PerformanceMonitor, analyze_complexity, scan_python_source
    from tamanna_ai.backup import create_backup, inspect_backup, restore_backup
    from tamanna_ai.learning import LearningMemory, inspect_jsonl_dataset
    from tamanna_ai.brain import BrainLearning, analyze_source, choose_action, create_plan

    assert callable(analyze_complexity)
    assert callable(scan_python_source)
    assert PerformanceMonitor
    assert callable(create_backup)
    assert callable(inspect_backup)
    assert callable(restore_backup)
    assert LearningMemory
    assert callable(inspect_jsonl_dataset)
    assert BrainLearning
    assert callable(analyze_source)
    assert callable(choose_action)
    assert callable(create_plan)
