from resilience_poc.vsa import build_vsa, validate_vsa, PREDICATE_TYPE, STATEMENT_TYPE


def test_vsa_build_and_validate():
    artifact = "sha256:" + "a" * 64
    policy = "sha256:" + "b" * 64
    vsa = build_vsa(
        artifact_name="artifact.bin",
        artifact_digest=artifact,
        resource_uri="urn:test:artifact",
        verifier_id="urn:test:verifier",
        verifier_version={"resilience-poc": "0.2.0"},
        policy_uri="urn:test:policy",
        policy_digest=policy,
        input_attestations=[{"uri": "urn:test:prov", "digest": {"sha256": "c" * 64}}],
        verification_result="PASSED",
        verified_levels=["SLSA_BUILD_LEVEL_1"],
    )
    assert vsa["_type"] == STATEMENT_TYPE
    assert vsa["predicateType"] == PREDICATE_TYPE
    ok, errors = validate_vsa(vsa, expected_artifact_digest=artifact, expected_resource_uri="urn:test:artifact")
    assert ok, errors


def test_vsa_rejects_subject_mismatch():
    vsa = build_vsa(
        artifact_name="artifact.bin",
        artifact_digest="sha256:" + "a" * 64,
        resource_uri="urn:test:artifact",
        verifier_id="urn:test:verifier",
        verifier_version={"resilience-poc": "0.2.0"},
        policy_uri="urn:test:policy",
        policy_digest="sha256:" + "b" * 64,
        input_attestations=[],
        verification_result="PASSED",
        verified_levels=["SLSA_BUILD_LEVEL_1"],
    )
    ok, errors = validate_vsa(vsa, expected_artifact_digest="sha256:" + "c" * 64)
    assert not ok
    assert "SUBJECT_DIGEST_MISMATCH" in errors
