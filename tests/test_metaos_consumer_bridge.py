from pathlib import Path
import sys

from engine.metaos_consumer_bridge import adapter_manifest


def test_webnovel_bridge_manifest_exposes_metaos_consumer_surface():
    manifest = adapter_manifest()

    assert manifest["adapter_name"] == "web_novel"
    assert manifest["contract_version"] == "1.0.0"
    assert callable(manifest["material_from_source"])
    assert callable(manifest["artifact_from_output"])


def test_webnovel_bridge_registers_into_metaos_consumer_api():
    metaos_root = Path("/home/meta_os/metaos")
    if str(metaos_root) not in sys.path:
        sys.path.insert(0, str(metaos_root))

    from metaos.runtime.consumer_api import register_consumer, reset_consumers, resolve_consumer

    reset_consumers()
    register_consumer("web_novel", adapter_manifest)
    resolution = resolve_consumer("web_novel")

    assert resolution["verdict"] == "accept"
    assert resolution["adapter_manifest"]["adapter_name"] == "web_novel"
