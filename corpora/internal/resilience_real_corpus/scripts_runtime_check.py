from resilience_poc.runtime_checks import observe_cpython_gil

if __name__ == "__main__":
    import json
    print(json.dumps(observe_cpython_gil(), indent=2))
