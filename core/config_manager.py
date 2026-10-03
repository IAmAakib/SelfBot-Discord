import os
import threading
from typing import Any, Dict, Optional

try:
    import orjson
    HAS_ORJSON = True
except ImportError:
    import json
    HAS_ORJSON = False

class ConfigManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, config_path: str = "config.json"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ConfigManager, cls).__new__(cls)
                cls._instance._init(config_path)
            return cls._instance

    def _init(self, config_path: str) -> None:
        self.config_path = config_path
        self._data: Dict[str, Any] = {}
        self._file_lock = threading.Lock()
        self.reload()

    def reload(self) -> None:
        with self._file_lock:
            if not os.path.exists(self.config_path):
                self._data = {"prefix": "."}
                self._save()
                return

            try:
                if HAS_ORJSON:
                    with open(self.config_path, 'rb') as f:
                        self._data = orjson.loads(f.read())
                else:
                    with open(self.config_path, 'r', encoding='utf-8') as f:
                        import json
                        self._data = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                if not self._data:
                    self._data = {"prefix": "."}

    def _save(self) -> None:
        try:
            if HAS_ORJSON:
                with open(self.config_path, 'wb') as f:
                    f.write(orjson.dumps(self._data, option=orjson.OPT_INDENT_2))
            else:
                import json
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(self._data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        with self._file_lock:
            return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        with self._file_lock:
            self._data[key] = value
            self._save()

    @property
    def prefix(self) -> str:
        return self.get("prefix", ".")

# Global instance
config = ConfigManager()
