import pytest
from PySide6.QtWidgets import QApplication
from core.coil_math import CoilMathEngine
from ui.dialogs import CoilSummaryDialog

@pytest.fixture(scope="module")
def app():
    app_inst = QApplication.instance()
    if app_inst is None:
        app_inst = QApplication([])
    yield app_inst

def test_asymmetric_spool_geometry():
    spool = CoilMathEngine.calculate_spool_geometry(
        hole_d=10.0,
        inner_d=35.0,
        flange_bottom_d=90.0,
        flange_top_d=110.0,
        width=50.0,
        flange_bottom_on=True,
        flange_top_on=False
    )
    assert spool["flange_bottom_d"] == 90.0
    assert spool["flange_top_d"] == 0.0 # Turned off
    assert spool["r_out"] == 17.5
    assert spool["r_in"] == 5.0

def test_target_ohm_and_length_calculations():
    # Target length
    layers = CoilMathEngine.calculate_layers_for_target_length(
        target_meters=15.0,
        wire_d=0.5,
        inner_d=35.0,
        width=50.0
    )
    assert layers >= 1

    # Target Ohm
    layers_ohm = CoilMathEngine.calculate_layers_for_target_ohm(
        target_ohm=6.0,
        wire_d=0.5,
        ohm_per_m=0.085,
        inner_d=35.0,
        width=50.0
    )
    assert layers_ohm >= 1

def test_inductance_calculation():
    inductance = CoilMathEngine.calculate_inductance_mh(
        turns=200,
        inner_d_mm=35.0,
        width_mm=50.0,
        layers=4,
        wire_d_mm=0.5
    )
    assert inductance > 0.0

def test_coil_summary_dialog(app):
    stats = {
        "total_turns": 180,
        "turns_per_layer": 90.0,
        "layers": 2,
        "length_m": 22.5,
        "resistance_ohm": 1.91,
        "weight_g": 39.5,
        "inductance_mh": 0.450,
        "outer_d_mm": 36.73,
        "width_mm": 50.0,
        "wire_d_mm": 0.5
    }
    dialog = CoilSummaryDialog(stats=stats)
    assert dialog.windowTitle() == "Gedetailleerde Spoel Analyse"
