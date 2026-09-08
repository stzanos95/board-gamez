"""
Building the display the configuration asked for.

A registry rather than a chain of conditionals: a new display is an entry here and
its own module.
"""

from collections.abc import Callable

from chess_cli.config_error import ConfigError
from chess_cli.display.base_display import BaseDisplay
from chess_cli.display.config import DisplayConfig, DisplayType
from chess_cli.display.text_display import TextDisplay


class DisplayProvider:
    """
    The one place a display is constructed.
    """

    @staticmethod
    def get_display(config: DisplayConfig) -> BaseDisplay:
        """
        The display the configuration selects, holding its own settings.

        Raises ConfigError when the selected display has no builder, or when its
        settings section is missing.
        """
        builder = DISPLAY_BUILDERS_BY_TYPE.get(config.display)
        if builder is None:
            raise ConfigError(
                f"no display is registered for {config.display.value!r}; "
                f"known displays are "
                f"{', '.join(sorted(display.value for display in DISPLAY_BUILDERS_BY_TYPE))}"
            )
        return builder(config)

    @staticmethod
    def _build_text_display(config: DisplayConfig) -> BaseDisplay:
        if config.text_config is None:
            raise ConfigError(
                f"display is {DisplayType.TEXT.value!r} but text_config is missing; "
                f"add a text_config section to the configuration file"
            )
        return TextDisplay(config=config.text_config)


# Keys are data — a display type names its builder. This is a lookup, not a
# record. Defined after the class so it can name the static methods above.
DISPLAY_BUILDERS_BY_TYPE: dict[DisplayType, Callable[[DisplayConfig], BaseDisplay]] = {
    DisplayType.TEXT: DisplayProvider._build_text_display,
}
