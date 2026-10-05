from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .collector import collect
from .storage import get_json
from .validator import validate_manifest
from . import __version__

app = FastAPI(title="Software Resilience Stack Evidence PoC", version=__version__)


class PatchPayload(BaseModel):
    data: dict


@app.post("/collector/submit")
def collector_submit(payload: PatchPayload):
    return collect(payload.data)


@app.post("/validator/validate/{manifest_id}")
def validator_validate(manifest_id: str):
    result = validate_manifest(manifest_id)
    if result["status"] == "invalid":
        raise HTTPException(status_code=422, detail=result["errors"])
    return result


@app.get("/artifacts/{artifact_id}")
def artifact_get(artifact_id: str):
    try:
        return get_json(artifact_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="artifact not found")
