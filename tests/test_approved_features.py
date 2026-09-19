import os
import json
import pytest
from PySide6.QtWidgets import QApplication
from core.gcode_engine import GCodeEngine
from core.config import load_user_config, save_user_config

@pytest.fixture(scope="module")
def app():
    app_inst = QApplication.instance()
    if app_inst is None:
        app_inst = QApplication([])
    yield app_inst

def test_gcode_parser():
    gcode = """
    G21 ; Millimeters
    G90 ; Absolute positioning
    G0 A0.000 X10.000 Y25.000 Z0.500
    G1 A360.000 X15.000 Y25.000 Z0.500 F500
    """
    moves = GCodeEngine.parse_gcode(gcode)
    assert len(moves) == 2
    assert moves[0]["a_deg"] == 0.0
    assert moves[0]["x"] == 10.0
    assert moves[0]["y"] == 25.0
    assert moves[1]["a_deg"] == 360.0
    assert moves[1]["x"] == 15.0

def test_user_config_load_save(tmp_path, monkeypatch):
    cfg_file = tmp_path / "user_config.json"
    import core.config as cfg_module
    monkeypatch.setattr(cfg_module, "get_resource_path", lambda fn: str(cfg_file))

    test_data = {
        "lang": "EN",
        "units": "inch",
        "theme": "light",
        "machine_limits": {"max_x": 250.0, "max_y": 120.0, "max_z": 20.0, "max_z_force": 12.0},
        "t_res": "32",
        "p_res": "64"
    }

    save_user_config(test_data)
    loaded = load_user_config()

    assert loaded["lang"] == "EN"
    assert loaded["units"] == "inch"
    assert loaded["theme"] == "light"
    assert loaded["machine_limits"]["max_x"] == 250.0

def test_prepare_input_validation(app):
    from ui.tabs.prepare_tab import PrepareTab
    from ui.main_window import CoilAppLayout

    window = CoilAppLayout()
    tab = window.tab_prepare

    # Valid inputs
    tab.inputs["i"].setText("35")
    tab.inputs["hole"].setText("10")
    tab.inputs["f"].setText("90")
    tab.inputs["b"].setText("50")
    tab.inputs["l"].setText("2")
    assert tab.validate_inputs() is True

    # Invalid hole >= i
    tab.inputs["hole"].setText("40")
    assert tab.validate_inputs() is False

    # Invalid core i >= f
    tab.inputs["hole"].setText("10")
    tab.inputs["i"].setText("100")
    assert tab.validate_inputs() is False

def test_spool_presets_dialog(app, tmp_path, monkeypatch):
    from ui.dialogs import SpoolPresetsDialog
    presets_file = tmp_path / "spool_presets.json"
    import core.config as cfg_module
    monkeypatch.setattr(cfg_module, "get_resource_path", lambda fn: str(presets_file))

    dialog = SpoolPresetsDialog(lang="NL")
    assert len(dialog.presets_data) == 3
    assert dialog.presets_data[0]["i"] == 35.0

    # Test thumbnail generation
    pix = dialog.generate_spool_thumbnail(35.0, 0.0, 90.0, 50.0)
    assert not pix.isNull()
    assert pix.width() == 120
