"""Parity tests: Text, Dict, and Protobuf envelopes produce identical results."""

from __future__ import annotations

from pathlib import Path

from dsl2wup import dispatch
from dsl2wup.pb_codec import encode_protobuf


def test_parity_validate_and_query(tmp_path: Path) -> None:
    config = tmp_path / "wup.yaml"
    config.write_text(
        "project:\n  name: demo\n  description: test\nwatch:\n  paths: []\nservices: []\n",
        encoding="utf-8",
    )
    
    # ------------------ VALIDATE Verb Parity ------------------
    # 1. Text format
    line_val = f"VALIDATE {config} PROJECT {tmp_path}"
    res_text_val = dispatch(line_val)
    
    # 2. Dict format
    dict_val = {"verb": "VALIDATE", "path": str(config), "project": str(tmp_path)}
    res_dict_val = dispatch(dict_val)
    
    # 3. Protobuf format
    proto_bytes_val = encode_protobuf(dict_val)
    res_proto_val = dispatch(proto_bytes_val)
    
    # Assertions for VALIDATE parity
    assert res_text_val.ok == res_dict_val.ok == res_proto_val.ok
    assert res_text_val.action == res_dict_val.action == res_proto_val.action == "validate"
    assert res_text_val.output == res_dict_val.output == res_proto_val.output
    assert res_text_val.error == res_dict_val.error == res_proto_val.error

    # ------------------ QUERY Verb Parity ------------------
    # 1. Text format
    line_query = f"QUERY wup://block/project FILE {config} PROJECT {tmp_path} FORMAT json"
    res_text_query = dispatch(line_query)
    
    # 2. Dict format
    dict_query = {
        "verb": "QUERY",
        "target": "wup://block/project",
        "file": str(config),
        "project": str(tmp_path),
        "format": "json",
    }
    res_dict_query = dispatch(dict_query)
    
    # 3. Protobuf format
    proto_bytes_query = encode_protobuf(dict_query)
    res_proto_query = dispatch(proto_bytes_query)
    
    # Assertions for QUERY parity
    assert res_text_query.ok == res_dict_query.ok == res_proto_query.ok
    assert res_text_query.action == res_dict_query.action == res_proto_query.action == "query"
    assert res_text_query.output == res_dict_query.output == res_proto_query.output
    assert res_text_query.error == res_dict_query.error == res_proto_query.error
    assert res_text_query.data == res_dict_query.data == res_proto_query.data
    
    # Verify the structure is correct
    assert isinstance(res_text_query.data, dict)
    assert res_text_query.data.get("data", {}).get("name") == "demo"
