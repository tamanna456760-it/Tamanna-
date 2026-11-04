from tamanna_ai.integrations.project_catalog import (
    get_project,
    list_projects,
    search_project_knowledge,
)


def test_catalog_contains_all_recovered_submodule_references():
    projects = list_projects()
    assert len(projects) == 9
    assert all(project["upstream_commit"] for project in projects)
    assert all(project["status"] == "source_unverified" for project in projects)


def test_project_lookup_is_case_insensitive():
    project = get_project("AutoGen")
    assert project is not None
    assert project["feature"] == "multi_agent_coordination"


def test_project_knowledge_search_returns_relevant_entries():
    results = search_project_knowledge("workflow automation")
    assert results
    assert any(item["id"] in {"n8n", "dify"} for item in results)


def test_empty_query_returns_no_results():
    assert search_project_knowledge("   ") == []
