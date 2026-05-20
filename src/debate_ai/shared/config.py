"""Config loader — reads JSON from ``config/`` into typed Pydantic models.

Every config file declares ``version``. After parsing, the loader cross-checks
each file's version against ``versions.json``'s declared expectations and
raises ``ConfigVersionError`` on any mismatch. Tests pass a ``config_dir`` arg
pointing at a temp fixture dir.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from debate_ai.models.config_models import (
    DebateConfigJson,
    FactsConfig,
    LoggingConfig,
    ModelsConfig,
    RateLimitsConfig,
    SetupConfig,
    VersionsConfig,
)
from debate_ai.models.persona_models import Persona
from debate_ai.shared.exceptions import ConfigError, ConfigVersionError

T = TypeVar("T", bound=BaseModel)

_CONFIG_FILES: dict[str, tuple[str, type[BaseModel]]] = {
    "setup": ("setup.json", SetupConfig),
    "debate": ("debate.json", DebateConfigJson),
    "models": ("models.json", ModelsConfig),
    "rate_limits": ("rate_limits.json", RateLimitsConfig),
    "logging": ("logging.json", LoggingConfig),
    "facts": ("facts.json", FactsConfig),
}


class ConfigLoader:
    """One-stop loader. Construct once, query repeatedly."""

    def __init__(self, config_dir: Path | str = "config") -> None:
        self.config_dir = Path(config_dir)
        if not self.config_dir.is_dir():
            raise ConfigError(f"config dir not found: {self.config_dir.resolve()}")
        self._versions: VersionsConfig | None = None

    def _read(self, filename: str) -> dict:
        path = self.config_dir / filename
        if not path.is_file():
            raise ConfigError(f"missing config file: {path}")
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ConfigError(f"invalid JSON in {path}: {e}") from e

    def _parse(self, model: type[T], raw: dict, where: str) -> T:
        try:
            return model.model_validate(raw)
        except ValidationError as e:
            raise ConfigError(f"schema error in {where}: {e}") from e

    def versions(self) -> VersionsConfig:
        """Load + cache ``versions.json``."""
        if self._versions is None:
            raw = self._read("versions.json")
            self._versions = self._parse(VersionsConfig, raw, "versions.json")
        return self._versions

    def load(self, name: str) -> BaseModel:
        """Load one config by short name (``"setup"``, ``"debate"``, ...)."""
        if name not in _CONFIG_FILES:
            raise ConfigError(f"unknown config name: {name!r}")
        filename, model_cls = _CONFIG_FILES[name]
        raw = self._read(filename)
        parsed = self._parse(model_cls, raw, filename)
        self._check_version(name, parsed.version)  # type: ignore[attr-defined]
        return parsed

    def load_persona(self, persona_name: str) -> Persona:
        """Load one persona by name. Version is checked against the ``personas`` slot."""
        path = self.config_dir / "personas" / f"{persona_name}.json"
        if not path.is_file():
            raise ConfigError(f"missing persona file: {path}")
        raw = json.loads(path.read_text(encoding="utf-8"))
        persona = self._parse(Persona, raw, str(path))
        self._check_version("personas", persona.version)
        return persona

    def list_personas(self) -> list[str]:
        """Return the names of all persona files present (without ``.json``)."""
        return sorted(p.stem for p in (self.config_dir / "personas").glob("*.json"))

    def _check_version(self, slot: str, actual: str) -> None:
        expected = self.versions().configs.get(slot)
        if expected is None:
            raise ConfigError(f"versions.json has no slot for {slot!r}")
        if actual != expected:
            raise ConfigVersionError(
                f"config '{slot}' has version {actual!r}; expected {expected!r}"
            )

    def validate_all(self) -> None:
        """Load every config + every persona once. Raises on any failure."""
        for name in _CONFIG_FILES:
            self.load(name)
        for persona_name in self.list_personas():
            self.load_persona(persona_name)
