from dataclasses import dataclass, field
from datetime import datetime
from glob import glob
import hashlib
import joblib
import os
from typing import Optional
import shelve


@dataclass
class Model:
    path: str
    name: str
    digest: str
    uploaded_at: datetime
    loaded: bool = field(default=False, compare=False, hash=False)
    estimator: Optional[object] = field(default=None, compare=False, hash=False)

    def __init__(self, path: str, digest: str, uploaded_at: datetime):
        self.path = path
        self.name = os.path.basename(path)
        self.digest = digest
        self.uploaded_at = uploaded_at

    def load(self):
        self.estimator = joblib.load(self.path)

    def unload(self):
        self.estimator = None


class ModelManager:
    def __init__(self, model_path: str):
        model_path = os.path.abspath(model_path)
        self._model_matcher = os.path.join(model_path, "*.joblib")
        state = shelve.open(os.path.join(model_path, "models.db"), writeback=True)
        state["models"] = state["models"] if "models" in state else []
        state["active_model"] = state["active_model"] if "active_model" in state else None
        self._state = state

    @property
    def loaded_models(self):
        pre_existing = self._state["models"]

        not_seen = [(m.path, m.digest) for m in pre_existing]
        for model_file_path in glob(self._model_matcher):
            with open(model_file_path, 'rb', buffering=0) as model_file:
                uploaded_at = datetime.fromtimestamp(os.path.getmtime(model_file_path))
                digest = hashlib.file_digest(model_file, 'sha256').hexdigest()
                try:
                    not_seen.remove((model_file_path, digest))
                except ValueError:
                    pre_existing.append(Model(model_file_path, digest, uploaded_at))

        not_seen = (path for path,_ in not_seen)
        self._state["models"] = list(filter(lambda m: m.path not in not_seen, pre_existing))
        self.sync()
        return list(self._state["models"])

    @property
    def active_model(self):
        model = self._state["active_model"]
        if model is None:
            return None

        model = next(filter(lambda m: m.name == model, self._state["models"]), None)
        if model is not None:
            return model
        else:
            self._state["active_model"] = None
            return None

    @active_model.setter
    def active_model(self, value):
        old_model = self._state["active_model"]
        old_model = next(filter(lambda m: m.name == old_model, self._state["models"]), None)

        if value is None:
            self._state["active_model"] = None
            return
        else:
            assert(value in self._state["models"])
            value.load()
            self._state["active_model"] = value.name

        if old_model is not None:
            old_model.unload()

        self.sync()

    def sync(self):
        self._state.sync()

    def close(self):
        self._state.close()
