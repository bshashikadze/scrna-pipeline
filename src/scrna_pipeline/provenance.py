"""Pipeline metadata provenance tracking (version, input hashes, timestamps)."""
import hashlib
import json
from datetime import datetime, timezone

from scrna_pipeline import __version__


def _hash_file(path, chunk_size=8192):
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def stamp(adata, step_name, params, input_path):
    """Append a provenance entry for one pipeline stage to adata.uns["provenance"].

    Stored as a JSON string, not a native list of dicts — anndata's h5ad writer
    can't serialize a list of dicts directly into .uns.
    """
    entry = {
        "step": step_name,
        "pipeline_version": __version__,
        "input_hash": _hash_file(input_path),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "params": params,
    }
    history = json.loads(adata.uns["provenance"]) if "provenance" in adata.uns else []
    history.append(entry)
    adata.uns["provenance"] = json.dumps(history)
