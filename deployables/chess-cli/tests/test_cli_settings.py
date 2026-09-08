import tempfile
import unittest
from pathlib import Path

from chess_cli.cli_settings import CliSettings, PlayerSettings
from chess_cli.config_error import ConfigError
from chess_cli.display.config import DisplayType
from tests.require import require

SHIPPED_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "chess_cli.yaml"

COMPLETE_CONFIG = """
players:
  white_name: Ada
  black_name: Alan
display:
  display: text
  text_config:
    use_unicode: false
    show_coordinates: true
    transparent_white: false
console:
  console: terminal
  terminal_config:
    prompt_suffix: "> "
"""

MISSING_SECTION_CONFIG = """
players:
  white_name: Ada
  black_name: Alan
"""

MISSING_FIELD_CONFIG = """
players:
  white_name: Ada
display:
  display: text
  text_config:
    use_unicode: false
    show_coordinates: true
    transparent_white: false
console:
  console: terminal
  terminal_config:
    prompt_suffix: "> "
"""

UNKNOWN_DISPLAY_CONFIG = """
players:
  white_name: Ada
  black_name: Alan
display:
  display: holograph
  text_config:
    use_unicode: false
    show_coordinates: true
    transparent_white: false
console:
  console: terminal
  terminal_config:
    prompt_suffix: "> "
"""

NOT_A_MAPPING_CONFIG = "just a string\n"

MALFORMED_CONFIG = "players: [unclosed\n"


def written(text: str) -> Path:
    """
    A throwaway config file holding exactly this text.
    """
    path = Path(tempfile.mkdtemp()) / "config.yaml"
    path.write_text(text, encoding="utf-8")
    return path


class ReadingSettingsTest(unittest.TestCase):
    def test_the_shipped_configuration_parses(self) -> None:
        settings = CliSettings.from_yaml_file(SHIPPED_CONFIG_PATH)
        self.assertEqual(settings.players.white_name, "White")
        self.assertEqual(settings.players.black_name, "Black")
        self.assertIs(settings.display.display, DisplayType.TEXT)
        self.assertTrue(require(settings.display.text_config).use_unicode)

    def test_reads_every_field(self) -> None:
        settings = CliSettings.from_yaml_file(written(COMPLETE_CONFIG))
        self.assertEqual(settings.players, PlayerSettings(white_name="Ada", black_name="Alan"))
        self.assertIs(settings.display.display, DisplayType.TEXT)
        text_config = require(settings.display.text_config)
        self.assertFalse(text_config.use_unicode)
        self.assertTrue(text_config.show_coordinates)

    def test_settings_survive_a_round_trip_through_yaml(self) -> None:
        settings = CliSettings.from_yaml_file(written(COMPLETE_CONFIG))
        path = Path(tempfile.mkdtemp()) / "written.yaml"
        settings.to_yaml_file(path)
        self.assertEqual(CliSettings.from_yaml_file(path), settings)


class RefusingBadSettingsTest(unittest.TestCase):
    def test_a_missing_file_is_reported_with_its_path(self) -> None:
        path = Path(tempfile.mkdtemp()) / "absent.yaml"
        with self.assertRaises(ConfigError) as caught:
            CliSettings.from_yaml_file(path)
        self.assertIn(str(path), str(caught.exception))

    def test_a_missing_section_is_refused(self) -> None:
        with self.assertRaises(ConfigError):
            CliSettings.from_yaml_file(written(MISSING_SECTION_CONFIG))

    def test_a_missing_field_is_refused(self) -> None:
        with self.assertRaises(ConfigError):
            CliSettings.from_yaml_file(written(MISSING_FIELD_CONFIG))

    def test_something_that_is_not_settings_at_all_is_refused(self) -> None:
        with self.assertRaises(ConfigError):
            CliSettings.from_yaml_file(written(NOT_A_MAPPING_CONFIG))

    def test_malformed_yaml_is_refused(self) -> None:
        with self.assertRaises(ConfigError):
            CliSettings.from_yaml_file(written(MALFORMED_CONFIG))

    def test_a_display_type_that_does_not_exist_is_refused(self) -> None:
        with self.assertRaises(ConfigError):
            CliSettings.from_yaml_file(written(UNKNOWN_DISPLAY_CONFIG))
