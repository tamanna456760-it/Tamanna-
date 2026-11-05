from tamanna_ai.features.feature_flags import FeatureFlags


def test_memory_and_personalization_are_enabled_by_default():
    flags = FeatureFlags()
    assert flags.is_enabled("memory")
    assert flags.is_enabled("personalization")


def test_optional_features_are_disabled_until_configured():
    flags = FeatureFlags()
    for name in ("web_search", "file_manager", "code_analysis", "voice", "backup"):
        assert not flags.is_enabled(name)


def test_feature_flag_snapshot_is_a_copy():
    flags = FeatureFlags()
    snapshot = flags.snapshot()
    snapshot["chat"] = False
    assert flags.is_enabled("chat")


def test_feature_flag_names_must_not_be_empty():
    flags = FeatureFlags()
    import pytest
    with pytest.raises(ValueError):
        flags.enable(" ")
