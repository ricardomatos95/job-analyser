from app_agent.graph import build_graph


def test_graph_compiles():
    graph = build_graph()
    assert graph is not None
