"""Code version + config-version cross-check.

Per HW2 brief §8.6 ("no hardcoded parameters") and the parent CLAUDE.md
versioning rule, every config file declares a ``version`` field and the app
fails fast at startup if any config's version disagrees with what the code
expects.
"""

from __future__ import annotations

from debate_ai import __version__ as _package_version
from debate_ai.shared.exceptions import ConfigVersionError

CODE_VERSION: str = _package_version


def assert_config_version(
    config_name: str, actual_version: str, expected_version: str
) -> None:
    """Raise ``ConfigVersionError`` if a loaded config carries the wrong version.

    Called once per JSON config by ``shared.config.ConfigLoader`` after
    parsing. The error includes the config name and both versions to make
    misconfigurations obvious at startup.
    """
    if actual_version != expected_version:
        raise ConfigVersionError(
            f"config '{config_name}' has version {actual_version!r}; "
            f"code expects {expected_version!r}"
        )


def code_version_tuple() -> tuple[int, ...]:
    """Parse ``CODE_VERSION`` like ``'1.00'`` into ``(1, 0)``.

    Useful for tests that assert monotonicity across phase tags.
    """
    return tuple(int(part) for part in CODE_VERSION.split("."))
