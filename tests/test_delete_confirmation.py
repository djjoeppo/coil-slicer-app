import sys
import pytest
from PySide6.QtWidgets import QApplication, QMessageBox
from ui.dialogs import MaterialsPopUp

@pytest.fixture(scope="module")
def app():
    app_inst = QApplication.instance()
    if app_inst is None:
        app_inst = QApplication([])
    yield app_inst

def test_delete_material_cancelled(app, monkeypatch, tmp_path):
    # Setup temporary materials file
    json_path = tmp_path / "materials.json"
    popup = MaterialsPopUp(lang="NL")
    popup.json_path = str(json_path)
    popup.materials_data = [
        {"name": "Test Wire 1", "diameter": 0.5, "insulation": 0.05, "ohm": 0.08, "max_current": 2.0, "max_voltage": 300, "min_spool_d": 20.0},
        {"name": "Test Wire 2", "diameter": 0.8, "insulation": 0.06, "ohm": 0.05, "max_current": 4.0, "max_voltage": 600, "min_spool_d": 35.0}
    ]
    popup.update_list_widget(0)

    # Mock QMessageBox to simulate clicking 'No' (Cancel)
    clicked_btn = None
    def mock_exec(self):
        nonlocal clicked_btn
        # Find the 'No' button
        for btn in self.buttons():
            if self.buttonRole(btn) == QMessageBox.NoRole or btn.text() in ["Nee", "No"]:
                clicked_btn = btn
                break
        return 0

    def mock_clicked_button(self):
        return clicked_btn

    monkeypatch.setattr(QMessageBox, "exec", mock_exec)
    monkeypatch.setattr(QMessageBox, "clickedButton", mock_clicked_button)

    popup.delete_current_material()

    # Verify material was NOT deleted
    assert len(popup.materials_data) == 2
    assert popup.materials_data[0]["name"] == "Test Wire 1"

def test_delete_material_confirmed(app, monkeypatch, tmp_path):
    json_path = tmp_path / "materials.json"
    popup = MaterialsPopUp(lang="EN")
    popup.json_path = str(json_path)
    popup.materials_data = [
        {"name": "Test Wire 1", "diameter": 0.5, "insulation": 0.05, "ohm": 0.08, "max_current": 2.0, "max_voltage": 300, "min_spool_d": 20.0},
        {"name": "Test Wire 2", "diameter": 0.8, "insulation": 0.06, "ohm": 0.05, "max_current": 4.0, "max_voltage": 600, "min_spool_d": 35.0}
    ]
    popup.update_list_widget(0)

    # Mock QMessageBox to simulate clicking 'Yes' (Confirm)
    clicked_btn = None
    def mock_exec(self):
        nonlocal clicked_btn
        for btn in self.buttons():
            if self.buttonRole(btn) == QMessageBox.YesRole or btn.text() in ["Ja", "Yes"]:
                clicked_btn = btn
                break
        return 0

    def mock_clicked_button(self):
        return clicked_btn

    monkeypatch.setattr(QMessageBox, "exec", mock_exec)
    monkeypatch.setattr(QMessageBox, "clickedButton", mock_clicked_button)

    popup.delete_current_material()

    # Verify material WAS deleted
    assert len(popup.materials_data) == 1
    assert popup.materials_data[0]["name"] == "Test Wire 2"
