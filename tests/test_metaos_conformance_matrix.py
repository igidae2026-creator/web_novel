from engine.metaos_conformance import CONFORMANCE_CHECKS, conformance_matrix


def test_conformance_matrix_includes_registered_webnovel_adapter():
    rows = conformance_matrix()

    assert rows
    row = next(item for item in rows if item["project_type"] == "web_novel")
    assert row["adapter_name"] == "web_novel"
    assert row["status"] == "ready"
    assert row["verdict"] == "accept"
    assert row["checks_required"] == CONFORMANCE_CHECKS
