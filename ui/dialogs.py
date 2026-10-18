# ui/dialogs.py
import os
import json
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QVBoxLayout, QWidget, QFrame,
                             QListWidget, QListWidgetItem, QLabel, QLineEdit, QPushButton, QGridLayout, QMessageBox,
                             QScrollArea, QInputDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator, QPixmap, QPainter, QPen, QBrush, QColor
from core.config import TRANSLATIONS, get_resource_path

class MachineLimitsDialog(QDialog):
    """Dialog for configuring machine travel and force limits."""
    def __init__(self, parent=None, current_limits=None):
        super().__init__(parent)
        self.setWindowTitle("Machine Limieten")
        self.setFixedWidth(350)
        self.limits = current_limits or {
            "max_x": 200.0,
            "max_y": 100.0,
            "max_z": 15.0,
            "max_z_force": 10.0
        }
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        grid = QGridLayout()
        layout.addLayout(grid)

        self.inputs = {}

        fields = [
            ("max_x", "Maximale travel X (mm):"),
            ("max_y", "Maximale travel Y (mm):"),
            ("max_z", "Maximale travel Z (mm):"),
            ("max_z_force", "Maximale Z-kracht (kg):")
        ]

        for i, (key, label) in enumerate(fields):
            lbl = QLabel(label)
            edit = QLineEdit(str(self.limits[key]))
            grid.addWidget(lbl, i, 0)
            grid.addWidget(edit, i, 1)
            self.inputs[key] = edit

        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Opslaan")
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel = QPushButton("Annuleren")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

    def get_values(self):
        try:
            return {
                "max_x": float(self.inputs["max_x"].text().replace(',', '.')),
                "max_y": float(self.inputs["max_y"].text().replace(',', '.')),
                "max_z": float(self.inputs["max_z"].text().replace(',', '.')),
                "max_z_force": float(self.inputs["max_z_force"].text().replace(',', '.'))
            }
        except ValueError:
            return self.limits

class MaterialsPopUp(QDialog):
    """Het pop-up scherm voor uitgebreid Materialenbeheer met JSON-koppeling"""
    def __init__(self, parent=None, is_light_theme=False, lang="NL"):
        super().__init__(parent)
        self.lang = lang
        self.is_light_theme = is_light_theme
        self.setWindowTitle("Materialenbeheer" if lang == "NL" else "Material Management")
        self.resize(750, 500)  
        self.setWindowModality(Qt.WindowModal)
        
        # JSON Database pad bepalen
        self.json_path = get_resource_path("materials.json")
        
        self.materials_data = []
        self.current_index = -1
        self.inputs = {}
        
        self.init_ui()
        self.apply_theme()
        self.load_materials_from_json()

    def get_current_unit(self):
        """Dynamic unit discovery from application tabs/parent."""
        try:
            if self.parent():
                p = self.parent()
                # PrepareTab or SettingsTab is our parent
                if hasattr(p, 'main_window'):
                    return p.main_window.tab_settings.combo_units.currentText()
                if hasattr(p, 'tab_settings'):
                    return p.tab_settings.combo_units.currentText()
        except Exception:
            pass
        return "mm"

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 1. LINKERZIJDE: De Materialenlijst
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_list_title = QLabel("Materialenbeheer" if self.lang == "NL" else "Material Management")
        lbl_list_title.setObjectName("sectionTitle")
        left_layout.addWidget(lbl_list_title)
        
        self.material_list = QListWidget()
        self.material_list.setObjectName("materialList")
        self.material_list.currentRowChanged.connect(self.on_material_selected)
        left_layout.addWidget(self.material_list)
        
        main_layout.addWidget(left_container, 2)

        # 2. RECHTERZIJDE: Het Invoerformulier (Card-styling)
        right_card = QFrame()
        right_card.setObjectName("sectionCard")
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(10)

        double_validator = QDoubleValidator(0.0, 10000.0, 4, self)
        double_validator.setNotation(QDoubleValidator.StandardNotation)

        unit = self.get_current_unit()
        unit_suffix = "inch" if unit == "inch" else "MM"

        fields = [
            ("name", "Naam" if self.lang == "NL" else "Name", None),
            ("diameter", f"Diameter {unit_suffix}", double_validator),
            ("insulation", f"Isolatie {unit_suffix}" if self.lang == "NL" else f"Insulation {unit_suffix}", double_validator),
            ("ohm", "Ohm per meter" if self.lang == "NL" else "Ohm per meter", double_validator),
            ("max_current", "Max stroom A" if self.lang == "NL" else "Max current A", double_validator),
            ("max_voltage", "Max spanning V" if self.lang == "NL" else "Max voltage V", double_validator),
            ("min_spool_d", f"Minimale spoel diameter {unit_suffix}" if self.lang == "NL" else f"Minimum spool diameter {unit_suffix}", double_validator)
        ]

        for key, label_text, validator in fields:
            row_widget = QWidget()
            row_layout = QVBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(4)
            
            lbl = QLabel(label_text)
            lbl.setObjectName("formLabel")
            
            le = QLineEdit()
            if validator:
                le.setValidator(validator)
                le.setAlignment(Qt.AlignRight)
                
            row_layout.addWidget(lbl)
            row_layout.addWidget(le)
            right_layout.addWidget(row_widget)
            
            self.inputs[key] = le

        right_layout.addStretch()

        # 3. ACTIEKNOPPEN
        self.btn_new = QPushButton("Nieuw" if self.lang == "NL" else "New")
        self.btn_new.setObjectName("actionBtnNew")
        self.btn_new.clicked.connect(self.add_new_material)
        right_layout.addWidget(self.btn_new)

        self.btn_save = QPushButton("Opslaan" if self.lang == "NL" else "Save")
        self.btn_save.setObjectName("actionBtnSave")
        self.btn_save.clicked.connect(self.save_current_material)
        right_layout.addWidget(self.btn_save)

        self.btn_delete = QPushButton("Verwijder" if self.lang == "NL" else "Delete")
        self.btn_delete.setObjectName("actionBtnDelete")
        self.btn_delete.clicked.connect(self.delete_current_material)
        right_layout.addWidget(self.btn_delete)

        main_layout.addWidget(right_card, 3)

    def load_materials_from_json(self):
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    self.materials_data = json.load(f)
            except Exception as e:
                print(f"Fout bij laden materialen: {e}")
                self.materials_data = []
        else:
            self.materials_data = [
                {"name": "Koperdraad", "diameter": 0.500, "insulation": 0.050, "ohm": 0.085, "max_current": 2.5, "max_voltage": 500, "min_spool_d": 20.0},
                {"name": "Aluminiumdraad", "diameter": 0.800, "insulation": 0.060, "ohm": 0.054, "max_current": 4.0, "max_voltage": 600, "min_spool_d": 35.0}
            ]
            self.save_to_json_file()

        self.update_list_widget()

    def save_to_json_file(self):
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(self.materials_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Fout bij wegschrijven JSON: {e}")

    def update_list_widget(self, select_index=0):
        self.material_list.blockSignals(True)
        self.material_list.clear()
        
        unit = self.get_current_unit()

        for mat in self.materials_data:
            d = float(mat.get("diameter", 0.0))
            i = float(mat.get("insulation", 0.0))
            total_d = d + i

            if unit == "inch":
                from core.config import mm_to_awg
                awg_val = mm_to_awg(total_d)
                display_text = f"{mat['name']} {awg_val} gage"
            else:
                display_text = f"{mat['name']} {total_d:.2f} MM"
            
            item = QListWidgetItem(display_text)
            self.material_list.addItem(item)
            
        self.material_list.blockSignals(False)
        
        if self.materials_data and select_index < len(self.materials_data):
            self.material_list.setCurrentRow(select_index)
        else:
            self.clear_form_fields()

    def on_material_selected(self, index):
        if index < 0 or index >= len(self.materials_data):
            self.current_index = -1
            self.clear_form_fields()
            return
            
        self.current_index = index
        mat = self.materials_data[index]
        
        unit = self.get_current_unit()
        scale = 1.0 / 25.4 if unit == "inch" else 1.0

        d_val = float(mat.get("diameter", 0.0)) * scale
        i_val = float(mat.get("insulation", 0.0)) * scale
        min_spool_val = float(mat.get("min_spool_d", 0.0)) * scale

        self.inputs["name"].setText(str(mat["name"]))
        self.inputs["diameter"].setText(f"{d_val:.4f}".replace('.', ',') if unit == "inch" else f"{d_val:.3f}".replace('.', ','))
        self.inputs["insulation"].setText(f"{i_val:.4f}".replace('.', ',') if unit == "inch" else f"{i_val:.3f}".replace('.', ','))
        self.inputs["min_spool_d"].setText(f"{min_spool_val:.3f}".replace('.', ',') if unit == "inch" else f"{min_spool_val:.2f}".replace('.', ','))

        self.inputs["ohm"].setText(str(mat.get("ohm", 0.0)).replace('.', ','))
        self.inputs["max_current"].setText(str(mat.get("max_current", 0.0)).replace('.', ','))
        self.inputs["max_voltage"].setText(str(mat.get("max_voltage", 0.0)).replace('.', ','))

    def clear_form_fields(self):
        for le in self.inputs.values():
            le.clear()

    def parse_float(self, text):
        try:
            return float(text.replace(',', '.'))
        except ValueError:
            return 0.0

    def add_new_material(self):
        new_mat = {
            "name": "Nieuw" if self.lang == "NL" else "New",
            "diameter": 0.500,
            "insulation": 0.050,
            "ohm": 0.000,
            "max_current": 0.0,
            "max_voltage": 0.0,
            "min_spool_d": 0.0
        }
        self.materials_data.append(new_mat)
        self.save_to_json_file()
        self.update_list_widget(select_index=len(self.materials_data) - 1)

    def save_current_material(self):
        if self.current_index < 0 or self.current_index >= len(self.materials_data):
            return
            
        name_text = self.inputs["name"].text().strip()
        if not name_text:
            name_text = "Naamloos" if self.lang == "NL" else "Unnamed"

        unit = self.get_current_unit()
        scale_back = 25.4 if unit == "inch" else 1.0

        d_parsed = self.parse_float(self.inputs["diameter"].text()) * scale_back
        i_parsed = self.parse_float(self.inputs["insulation"].text()) * scale_back
        min_spool_parsed = self.parse_float(self.inputs["min_spool_d"].text()) * scale_back

        self.materials_data[self.current_index] = {
            "name": name_text,
            "diameter": d_parsed,
            "insulation": i_parsed,
            "ohm": self.parse_float(self.inputs["ohm"].text()),
            "max_current": self.parse_float(self.inputs["max_current"].text()),
            "max_voltage": self.parse_float(self.inputs["max_voltage"].text()),
            "min_spool_d": min_spool_parsed
        }
        self.save_to_json_file()
        self.update_list_widget(select_index=self.current_index)

    def delete_current_material(self):
        if self.current_index < 0 or self.current_index >= len(self.materials_data):
            return

        mat_name = self.materials_data[self.current_index].get("name", "")

        if self.lang == "NL":
            title = "Materiaal Verwijderen"
            text = f"Weet u zeker dat u '{mat_name}' wilt verwijderen?"
            btn_yes = "Ja"
            btn_no = "Nee"
        else:
            title = "Delete Material"
            text = f"Are you sure you want to delete '{mat_name}'?"
            btn_yes = "Yes"
            btn_no = "No"

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        yes_btn = msg_box.addButton(btn_yes, QMessageBox.YesRole)
        no_btn = msg_box.addButton(btn_no, QMessageBox.NoRole)
        msg_box.setDefaultButton(no_btn)

        msg_box.exec()
        if msg_box.clickedButton() != yes_btn:
            return

        del self.materials_data[self.current_index]
        self.save_to_json_file()

        new_idx = max(0, self.current_index - 1)
        if not self.materials_data:
            new_idx = -1

        self.update_list_widget(select_index=new_idx)

    def apply_theme(self):
        if self.is_light_theme:
            self.setStyleSheet("""
                QDialog { background-color: #f8f9fa; }
                QLabel#sectionTitle { color: #000000; font-weight: bold; font-size: 14px; border-bottom: 1px solid #dee2e6; padding-bottom: 4px; margin-bottom: 5px; }
                QLabel#formLabel { color: #495057; font-weight: 500; }
                QListWidget#materialList { background-color: #ffffff; border: 1px solid #ced4da; border-radius: 4px; color: #212529; padding: 5px; }
                QListWidget#materialList::item { padding: 6px; border-bottom: 1px solid #f1f3f5; }
                QListWidget#materialList::item:hover { background-color: #dee2e6; border-radius: 3px; }
                QListWidget#materialList::item:selected { background-color: #007edc; color: white; border-radius: 3px; }
                QFrame#sectionCard { background-color: #ffffff; border: 1px solid #ced4da; border-radius: 6px; }
                QLineEdit { background-color: #ffffff; color: #212529; border: 1px solid #ced4da; border-radius: 3px; padding: 4px; }
                QLineEdit:focus { border: 1px solid #007edc; }
                QPushButton { background-color: #f1f3f5; color: #212529; border: 1px solid #ced4da; border-radius: 4px; padding: 6px; font-weight: bold; }
                QPushButton:hover { background-color: #dee2e6; }
                QPushButton#actionBtnSave { background-color: #007edc; color: white; border: none; }
                QPushButton#actionBtnSave:hover { background-color: #0096ff; }
                QPushButton#actionBtnDelete { background-color: #dc3545; color: white; border: none; }
                QPushButton#actionBtnDelete:hover { background-color: #ff4d5e; }
            """)
        else:
            self.setStyleSheet("""
                QDialog { background-color: #1e2022; }
                QLabel#sectionTitle { color: #ffffff; font-weight: bold; font-size: 14px; border-bottom: 1px solid #383b3d; padding-bottom: 4px; margin-bottom: 5px; }
                QLabel#formLabel { color: #9da3a8; font-weight: 500; }
                QListWidget#materialList { background-color: #111213; border: 1px solid #383b3d; border-radius: 4px; color: #e3e4e5; padding: 5px; }
                QListWidget#materialList::item { padding: 6px; border-bottom: 1px solid #1a1c1d; }
                QListWidget#materialList::item:hover { background-color: #242628; border-radius: 3px; }
                QListWidget#materialList::item:selected { background-color: #007edc; color: white; border-radius: 3px; }
                QFrame#sectionCard { background-color: #222527; border: 1px solid #2d2f31; border-radius: 6px; }
                QLineEdit { background-color: #111213; color: #ffffff; border: 1px solid #383b3d; border-radius: 3px; padding: 4px; }
                QLineEdit:focus { border: 1px solid #007edc; }
                QPushButton { background-color: #2c2f31; color: #e3e4e5; border: 1px solid #383b3d; border-radius: 4px; padding: 6px; font-weight: bold; }
                QPushButton:hover { background-color: #383b3d; }
                QPushButton#actionBtnSave { background-color: #007edc; color: white; border: none; }
                QPushButton#actionBtnSave:hover { background-color: #0096ff; }
                QPushButton#actionBtnDelete { background-color: #b22222; color: white; border: none; }
                QPushButton#actionBtnDelete:hover { background-color: #dc3545; }
            """)

class SpoolPresetsDialog(QDialog):
    """Pop-up Venster met visuele kaarten en 2D thumbnail previews van spoel presets."""
    def __init__(self, parent=None, is_light_theme=False, lang="NL"):
        super().__init__(parent)
        self.lang = lang
        self.is_light_theme = is_light_theme
        self.setWindowTitle("Spoel Presets" if lang == "NL" else "Spool Presets")
        self.resize(750, 500)
        self.setWindowModality(Qt.WindowModal)

        self.json_path = get_resource_path("spool_presets.json")
        self.presets_data = []
        self.selected_preset = None

        self.init_ui()
        self.apply_theme()
        self.load_presets()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header / Top Action
        top_row = QHBoxLayout()
        lbl_title = QLabel("Spoel Presets" if self.lang == "NL" else "Spool Presets")
        lbl_title.setObjectName("sectionTitle")
        top_row.addWidget(lbl_title)
        top_row.addStretch()

        self.btn_add_preset = QPushButton("+ Opslaan als nieuwe preset" if self.lang == "NL" else "+ Save as new preset")
        self.btn_add_preset.setObjectName("actionBtnSave")
        self.btn_add_preset.clicked.connect(self.save_new_preset)
        top_row.addWidget(self.btn_add_preset)

        layout.addLayout(top_row)

        # Scroll Area for Cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.cards_layout = QGridLayout(self.scroll_content)
        self.cards_layout.setSpacing(12)
        self.scroll_area.setWidget(self.scroll_content)

        layout.addWidget(self.scroll_area)

    def load_presets(self):
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    self.presets_data = json.load(f)
            except Exception as e:
                print(f"Fout bij laden spool presets: {e}")
                self.presets_data = []
        else:
            self.presets_data = [
                {"name": "Standaard Luidsprekerspoel 35mm", "i": 35.0, "hole": 0.0, "f": 90.0, "b": 50.0},
                {"name": "Miniatuur Spoel 15mm", "i": 15.0, "hole": 5.0, "f": 45.0, "b": 25.0},
                {"name": "Grote Subwoofer Spoel 75mm", "i": 75.0, "hole": 10.0, "f": 160.0, "b": 80.0}
            ]
            self.save_presets_to_file()

        self.render_cards()

    def save_presets_to_file(self):
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(self.presets_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Fout bij opslaan spool presets: {e}")

    def render_cards(self):
        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        col_count = 2
        for idx, preset in enumerate(self.presets_data):
            row = idx // col_count
            col = idx % col_count

            card = QFrame()
            card.setObjectName("sectionCard")
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(10, 10, 10, 10)
            card_layout.setSpacing(10)

            # Thumbnail
            thumb_label = QLabel()
            thumb_pixmap = self.generate_spool_thumbnail(
                float(preset.get("i", 35)),
                float(preset.get("hole", 0)),
                float(preset.get("f", 90)),
                float(preset.get("b", 50))
            )
            thumb_label.setPixmap(thumb_pixmap)
            card_layout.addWidget(thumb_label)

            # Info column
            info_widget = QWidget()
            info_layout = QVBoxLayout(info_widget)
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(4)

            lbl_name = QLabel(preset.get("name", "Naamloze Spoel"))
            lbl_name.setStyleSheet("font-weight: bold; font-size: 13px;")

            unit = "mm"
            if self.parent() and hasattr(self.parent(), 'main_window'):
                unit = self.parent().main_window.tab_settings.combo_units.currentText()
            scale = 1.0 / 25.4 if unit == "inch" else 1.0

            i_val = float(preset.get("i", 0)) * scale
            hole_val = float(preset.get("hole", 0)) * scale
            f_val = float(preset.get("f", 0)) * scale
            b_val = float(preset.get("b", 0)) * scale

            details = f"Kern-Ø: {i_val:.1f} {unit} | Gat-Ø: {hole_val:.1f} {unit}\nFlens-Ø: {f_val:.1f} {unit} | Breedte: {b_val:.1f} {unit}"
            lbl_details = QLabel(details)
            lbl_details.setStyleSheet("color: #9da3a8; font-size: 11px;")

            info_layout.addWidget(lbl_name)
            info_layout.addWidget(lbl_details)
            info_layout.addStretch()

            # Buttons
            btn_row = QHBoxLayout()
            btn_select = QPushButton("Selecteren" if self.lang == "NL" else "Select")
            btn_select.setObjectName("actionBtnSave")
            btn_select.clicked.connect(lambda checked, p=preset: self.select_preset(p))

            btn_delete = QPushButton("Verwijderen" if self.lang == "NL" else "Delete")
            btn_delete.setObjectName("actionBtnDelete")
            btn_delete.clicked.connect(lambda checked, idx=idx: self.delete_preset(idx))

            btn_row.addWidget(btn_select)
            btn_row.addWidget(btn_delete)
            info_layout.addLayout(btn_row)

            card_layout.addWidget(info_widget, 1)

            self.cards_layout.addWidget(card, row, col)

    def generate_spool_thumbnail(self, i, hole, f, b, width=120, height=100):
        pixmap = QPixmap(width, height)
        bg_color = QColor(17, 18, 19) if not self.is_light_theme else QColor(240, 240, 240)
        pixmap.fill(bg_color)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        max_dim = max(f, b, 1.0)
        scale = min((width - 24) / max_dim, (height - 24) / max_dim)

        cx, cy = width / 2.0, height / 2.0
        w_px = max(8.0, b * scale)
        f_px = max(12.0, f * scale)
        i_px = max(4.0, i * scale)
        hole_px = hole * scale if hole > 0 else 0

        flange_color = QColor("#007edc")
        painter.setBrush(QBrush(flange_color))
        painter.setPen(QPen(flange_color.darker(120), 1))

        t_px = max(3.0, w_px * 0.12)

        # Left flange
        painter.drawRect(int(cx - w_px/2), int(cy - f_px/2), int(t_px), int(f_px))
        # Right flange
        painter.drawRect(int(cx + w_px/2 - t_px), int(cy - f_px/2), int(t_px), int(f_px))

        # Core cylinder
        core_color = QColor("#d97706")
        painter.setBrush(QBrush(core_color))
        painter.setPen(QPen(core_color.darker(120), 1))
        painter.drawRect(int(cx - w_px/2 + t_px), int(cy - i_px/2), int(w_px - 2*t_px), int(i_px))

        # Center hole if present
        if hole_px > 0:
            hole_color = QColor(25, 25, 25) if not self.is_light_theme else QColor(255, 255, 255)
            painter.setBrush(QBrush(hole_color))
            painter.setPen(Qt.NoPen)
            painter.drawRect(int(cx - w_px/2), int(cy - hole_px/2), int(w_px), int(hole_px))

        painter.end()
        return pixmap

    def select_preset(self, preset):
        self.selected_preset = preset
        self.accept()

    def save_new_preset(self):
        title = "Nieuwe Preset Opslaan" if self.lang == "NL" else "Save New Preset"
        label = "Voer preset naam in:" if self.lang == "NL" else "Enter preset name:"
        name, ok = QInputDialog.getText(self, title, label)

        if ok and name.strip():
            i_val, hole_val, f_val, b_val = 35.0, 0.0, 90.0, 50.0
            if self.parent() and hasattr(self.parent(), 'inputs'):
                from core.config import parse_fraction_or_float
                p = self.parent()
                i_val = parse_fraction_or_float(p.inputs["i"].text())
                hole_val = parse_fraction_or_float(p.inputs["hole"].text())
                f_val = parse_fraction_or_float(p.inputs["f"].text())
                b_val = parse_fraction_or_float(p.inputs["b"].text())

            new_preset = {
                "name": name.strip(),
                "i": i_val,
                "hole": hole_val,
                "f": f_val,
                "b": b_val
            }
            self.presets_data.append(new_preset)
            self.save_presets_to_file()
            self.render_cards()

    def delete_preset(self, idx):
        if idx < 0 or idx >= len(self.presets_data): return
        p_name = self.presets_data[idx].get("name", "")

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Preset Verwijderen" if self.lang == "NL" else "Delete Preset")
        msg_box.setText(f"Weet u zeker dat u '{p_name}' wilt verwijderen?")
        yes_btn = msg_box.addButton("Ja" if self.lang == "NL" else "Yes", QMessageBox.YesRole)
        no_btn = msg_box.addButton("Nee" if self.lang == "NL" else "No", QMessageBox.NoRole)
        msg_box.exec()

        if msg_box.clickedButton() == yes_btn:
            del self.presets_data[idx]
            self.save_presets_to_file()
            self.render_cards()

    def apply_theme(self):
        if self.is_light_theme:
            self.setStyleSheet("""
                QDialog { background-color: #f8f9fa; }
                QLabel#sectionTitle { color: #000000; font-weight: bold; font-size: 14px; border-bottom: 1px solid #dee2e6; padding-bottom: 4px; }
                QFrame#sectionCard { background-color: #ffffff; border: 1px solid #ced4da; border-radius: 6px; }
                QPushButton#actionBtnSave { background-color: #007edc; color: white; border: none; font-weight: bold; padding: 5px 10px; border-radius: 4px; }
                QPushButton#actionBtnSave:hover { background-color: #0096ff; }
                QPushButton#actionBtnDelete { background-color: #dc3545; color: white; border: none; font-weight: bold; padding: 5px 10px; border-radius: 4px; }
                QPushButton#actionBtnDelete:hover { background-color: #ff4d5e; }
            """)
        else:
            self.setStyleSheet("""
                QDialog { background-color: #1e2022; }
                QLabel#sectionTitle { color: #ffffff; font-weight: bold; font-size: 14px; border-bottom: 1px solid #383b3d; padding-bottom: 4px; }
                QFrame#sectionCard { background-color: #222527; border: 1px solid #2d2f31; border-radius: 6px; }
                QPushButton#actionBtnSave { background-color: #007edc; color: white; border: none; font-weight: bold; padding: 5px 10px; border-radius: 4px; }
                QPushButton#actionBtnSave:hover { background-color: #0096ff; }
                QPushButton#actionBtnDelete { background-color: #b22222; color: white; border: none; font-weight: bold; padding: 5px 10px; border-radius: 4px; }
                QPushButton#actionBtnDelete:hover { background-color: #dc3545; }
            """)

class CoilSummaryDialog(QDialog):
    """Gedetailleerde Spoel-Analyse Pop-up met alle fysische en elektrische maatspecificaties."""
    def __init__(self, parent=None, stats=None):
        super().__init__(parent)
        self.stats = stats or {}
        self.setWindowTitle("Gedetailleerde Spoel Analyse")
        self.resize(520, 420)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("📊 Uitgebreide Spoel-Analyse & Specificaties")
        title.setObjectName("sectionTitle")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #007edc;")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(10)

        s = self.stats
        items = [
            ("🔄 Totaal Windingen:", f"{s.get('total_turns', 0)}"),
            ("🥞 Aantal Lagen:", f"{s.get('layers', 1)}"),
            ("🌀 Windingen per Laag:", f"{s.get('turns_per_layer', 0):.1f}"),
            ("📏 Totale Draadlengte:", f"{s.get('length_m', 0.0):.2f} m ({s.get('length_m', 0.0)*3.28084:.1f} ft)"),
            ("⚡ DC-Weerstand (Rdc):", f"{s.get('resistance_ohm', 0.0):.2f} Ω"),
            ("⚖️ Koper/Spoel Gewicht:", f"{s.get('weight_g', 0.0):.1f} gram"),
            ("🧲 Lucht-Inductie (L):", f"{s.get('inductance_mh', 0.0):.3f} mH"),
            ("⭕ Buitenste Wikkeldiameter:", f"{s.get('outer_d_mm', 0.0):.2f} mm"),
            ("📐 Wikkelhoogte / Breedte:", f"{s.get('width_mm', 0.0):.2f} mm"),
            ("🧵 Draad Diameter (incl. lak):", f"{s.get('wire_d_mm', 0.0):.3f} mm")
        ]

        for idx, (label, val) in enumerate(items):
            card = QFrame()
            card.setStyleSheet("background-color: #222527; border: 1px solid #2d2f31; border-radius: 4px; padding: 6px;")
            card_lay = QVBoxLayout(card)
            card_lay.setContentsMargins(6, 6, 6, 6)
            card_lay.setSpacing(2)

            lbl = QLabel(label)
            lbl.setStyleSheet("color: #9da3a8; font-size: 11px;")
            v_lbl = QLabel(val)
            v_lbl.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 13px;")

            card_lay.addWidget(lbl)
            card_lay.addWidget(v_lbl)
            grid.addWidget(card, idx // 2, idx % 2)

        layout.addLayout(grid)
        layout.addStretch()

        btn_close = QPushButton("Sluiten")
        btn_close.setObjectName("actionBtnSave")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
