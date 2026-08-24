import json
from pathlib import Path
from resilience_poc.validator import build_vector


def test_vector_emits_vsa(tmp_path):
    # This test exercises VSA creation through the real validator helper.
    # The repository's existing keypair is created lazily by other tests.
    from resilience_poc.security import ensure_keypair
    from resilience_poc.runtime_paths import KEYS
    keys = KEYS
    ensure_keypair(keys / 'poc_ed25519_private.pem', keys / 'poc_ed25519_public.pem')
    manifest = {
        'id': 'evmanifest-vsa-test',
        'generated_patch_ref': 'genpatch-vsa-test',
        'slsa_provenance_ref': 'link://slsa/provenance/abc123',
        'ai_evidence': {'target_repository': 'urn:test:repo'},
    }
    test_ev = {
        'id': 'testev-vsa',
        'unit_tests': {'failed': 0},
        'property_tests': {'violations': 0},
        'supply_chain_checks': {'signatures_valid': True, 'cve_policy_pass': True},
    }
    dep_ev = {
        'id': 'depev-vsa',
        'dependency_drift': {'count': 0},
        'supply_chain_checks': {'signatures_valid': True, 'cve_policy_pass': True},
    }
    repro = {'level': 'REPRODUCIBLE'}
    vector = build_vector(manifest, test_ev, dep_ev, repro, {'unexpected_gil_reactivation': False})
    assert vector['vsa_ref'].startswith('urn:uuid:vsa-')


def test_vector_emits_verifiable_dsse_vsa(tmp_path):
    from resilience_poc.security import ensure_keypair
    from resilience_poc.dsse import verify_dsse, ensure_ecdsa_p256_keypair
    from resilience_poc.runtime_paths import KEYS
    keys = KEYS
    ensure_keypair(keys / 'poc_ed25519_private.pem', keys / 'poc_ed25519_public.pem')
    ensure_ecdsa_p256_keypair(keys / 'poc_dsse_p256_private.pem', keys / 'poc_dsse_p256_public.pem')
    manifest = {
        'id': 'evmanifest-dsse-test',
        'generated_patch_ref': 'genpatch-dsse-test',
        'slsa_provenance_ref': 'link://slsa/provenance/dsse-test',
        'ai_evidence': {'target_repository': 'urn:test:repo'},
    }
    test_ev = {
        'id': 'testev-dsse',
        'unit_tests': {'failed': 0},
        'property_tests': {'violations': 0},
        'supply_chain_checks': {'signatures_valid': True, 'cve_policy_pass': True},
    }
    dep_ev = {
        'id': 'depev-dsse',
        'dependency_drift': {'count': 0},
        'supply_chain_checks': {'signatures_valid': True, 'cve_policy_pass': True},
    }
    repro = {'level': 'REPRODUCIBLE'}
    from resilience_poc.validator import build_vector
    from resilience_poc.storage import get_json
    vector = build_vector(manifest, test_ev, dep_ev, repro, {'unexpected_gil_reactivation': False})
    dsse_id = vector['vsa_dsse_ref'].split(':')[-1]
    envelope = get_json(dsse_id)
    ok, errors, statement = verify_dsse(envelope, keys / 'poc_dsse_p256_public.pem')
    assert ok, errors
    assert statement['predicateType'] == 'https://slsa.dev/verification_summary/v1'
