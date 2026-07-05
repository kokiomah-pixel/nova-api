from examples.agent_prepared_action.build_review_context_from_agent_package import (
    build_review_context_from_agent_package,
    load_agent_package,
)


def test_agent_prepared_action_package_preserves_non_authority_boundary() -> None:
    package = load_agent_package()

    assert package["prepared_by"]["actor_type"] == "agent"
    assert package["prepared_by"]["authority_scope"] == "preparation_only"
    assert package["prepared_action"]["execution_status"] == "not_executed"
    assert package["authority_context"]["nova_authority"] == "none"
    assert package["authority_context"]["local_authority_required"] is True


def test_agent_prepared_action_builds_review_context_only() -> None:
    package = load_agent_package()
    context = build_review_context_from_agent_package(package)

    assert context["context_type"] == "pre_action_review_context"
    assert context["local_authority"]["decision_responsibility"] == "local_authority"
    assert context["local_authority"]["nova_authority"] == "none"
    assert context["local_authority"]["execution_layer"] == "external"
    assert context["prepared_action"]["execution_status"] == "not_executed"


def test_agent_prepared_action_context_includes_reflex_memory_without_authority() -> None:
    package = load_agent_package()
    context = build_review_context_from_agent_package(package)

    reflex_context = context["reflex_memory_context"]
    assert reflex_context["present"] is True

    entry = reflex_context["entries"][0]
    assert entry["authority_effect"] == "none"


def test_agent_prepared_action_context_preserves_canonical_boundary() -> None:
    package = load_agent_package()
    context = build_review_context_from_agent_package(package)

    assert context["canonical_boundary"] == [
        "Agent prepares action.",
        "Nova structures review context.",
        "Local authority decides.",
        "Nova does not execute.",
    ]


def test_agent_prepared_action_context_is_review_ready_not_execution_ready() -> None:
    package = load_agent_package()
    context = build_review_context_from_agent_package(package)

    assert context["review_readiness"]["prepared_action_present"] is True
    assert context["review_readiness"]["source_context_present"] is True
    assert context["review_readiness"]["authority_context_present"] is True
    assert context["review_readiness"]["execution_status"] == "not_executed"
    assert "not approval" in context["non_authority_statement"]
