"""
The app's settings, parsed from YAML.

Every value the app needs to run is a field here. This module is the only place
that reads or writes the configuration file, and nothing in the app reads the
environment.

mashumaro reads these annotations at runtime to build the parser, so
`from __future__ import annotations` would leave it nothing to read.
"""

from dataclasses import dataclass
from pathlib import Path

from mashumaro.exceptions import MissingField, UnserializableField
from mashumaro.mixins.yaml import DataClassYAMLMixin
from yaml import YAMLError

from chess_cli.config_error import ConfigError
from chess_cli.console.config import ConsoleConfig
from chess_cli.display.config import DisplayConfig

CONFIG_ENCODING = "utf-8"


@dataclass(frozen=True, slots=True)
class PlayerSettings(DataClassYAMLMixin):
    """
    Who is sitting down to play.
    """

    white_name: str
    black_name: str


@dataclass(frozen=True, slots=True)
class CliSettings(DataClassYAMLMixin):
    """
    Everything the app needs to start.
    """

    players: PlayerSettings
    display: DisplayConfig
    console: ConsoleConfig

    @staticmethod
    def from_yaml_file(path: Path) -> "CliSettings":
        """
        Read settings from a YAML file, refusing anything that is not settings.
        """
        try:
            text = path.read_text(encoding=CONFIG_ENCODING)
        except OSError as error:
            raise ConfigError(f"could not read the configuration at {path}: {error}") from error
        try:
            return CliSettings.from_yaml(text)
        except (
            YAMLError,
            MissingField,
            UnserializableField,
            ValueError,
            TypeError,
            AttributeError,
        ) as error:
            raise ConfigError(f"{path} does not describe valid settings: {error}") from error

    def to_yaml_file(self, path: Path) -> None:
        """
        The one place settings become a file again.
        """
        # The library may hand back either text or bytes depending on its loader.
        encoded = self.to_yaml()
        text = encoded.decode(CONFIG_ENCODING) if isinstance(encoded, bytes) else encoded
        path.write_text(text, encoding=CONFIG_ENCODING)
