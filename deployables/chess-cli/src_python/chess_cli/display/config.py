"""
How the game is shown, and the settings each option needs.

An enum selects, one config dataclass describes each option, and the container
carries one optional field per option. The enum and the configs share a module
because they form one contract.

Adding a display means adding a member, a config, a field on DisplayConfig, a
class and a registry entry in `provider`. Nothing existing changes.
"""

from dataclasses import dataclass
from enum import Enum

from mashumaro.mixins.yaml import DataClassYAMLMixin


class DisplayType(Enum):
    """
    Which display to build.
    """

    TEXT = "text"


@dataclass(frozen=True, slots=True)
class TextDisplayConfig(DataClassYAMLMixin):
    """
    Settings for the plain-text board.
    """

    use_unicode: bool
    show_coordinates: bool
    transparent_white: bool


@dataclass(frozen=True, slots=True)
class DisplayConfig(DataClassYAMLMixin):
    """
    The chosen display, and the settings for each display that has any.

    One optional field per display type. The selected one must be present; the
    rest are ignored, so a file may carry settings for a display it is not using.
    """

    display: DisplayType
    text_config: TextDisplayConfig | None = None
