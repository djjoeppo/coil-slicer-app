# ui/tabs/prepare_tab.py
import os
import json
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QLineEdit, QComboBox, QScrollArea, QPushButton, QSplitter
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon, QColor
from core.config import TRANSLATIONS, get_resource_path
from ui.components import Dummy3DViewer
from ui.dialogs import MaterialsPopUp

class PrepareTab(QWidget):
    def __init__(self, main_window, wire_colors=None, spool_colors=None):
        super().__init__(main_window)
        self.main_window = main_window  
        self.inputs = {}
        self.wire_color_combos = []
        
        # JSON Database pad bepalen
        self.json_path = get_resource_path("materials.json")
        
        # De materiaallijst cache die we inladen vanuit JSON
        self.materials_database = []
        
        # Kleuren voor overige zaken
        self.wire_colors = wire_colors if wire_colors else {
            "Koper": (0.85, 0.38, 0.15), "Goud": (0.95, 0.75, 0.1), "Zilver": (0.75, 0.75, 0.75),
            "Rood": (0.85, 0.15, 0.15), "Blauw": (0.15, 0.45, 0.75), "Groen": (0.15, 0.7, 0.3),
            "Paars": (0.5, 0.1, 0.6), "Zwart": (0.1, 0.1, 0.1), "Wit": (0.95, 0.95, 0.95)
        }
        self.spool_colors = spool_colors if spool_colors else {
            "Standaard (Donker)": (0.2, 0.2, 0.2), "Aluminium": (0.7, 0.73, 0.75),
            "Messing": (0.78, 0.66, 0.25), "Plastic Zwart": (0.08, 0.09, 0.1), "Plastic Wit": (0.9, 0.9, 0.9)
        }
        
        self.init_ui()
        self.load_materials_into_combobox()

    def init_ui(self):
        lay_prepare = QHBoxLayout(self)
        lay_prepare.setContentsMargins(0, 0, 0, 0)
        lay_prepare.setSpacing(0)

        # Create Splitter
        self.splitter = QSplitter(Qt.Horizontal)
        lay_prepare.addWidget(self.splitter)

        sidebar_container = QWidget()
        sidebar_container.setMinimumWidth(250)
        sidebar_container.setMaximumWidth(600)
        sidebar_container.setObjectName("sidebarContainer")
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(12)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("paramScroll")
        scroll_content = QWidget()
        lay_scroll = QVBoxLayout(scroll_content)
        lay_scroll.setContentsMargins(0, 0, 0, 0)
        lay_scroll.setSpacing(15)

        # --- SECTIE: SPOEL ---
        card_spool = QFrame(); card_spool.setObjectName("sectionCard")
        lay_card_spool = QVBoxLayout(card_spool)

        spool_title_row = QWidget(); lay_st = QHBoxLayout(spool_title_row); lay_st.setContentsMargins(0,0,0,0)
        self.sec_spool_title = QLabel(); self.sec_spool_title.setObjectName("sectionTitle")
        self.btn_spool_presets = QPushButton("🔍 Presets")
        self.btn_spool_presets.setObjectName("secondaryActionButton")
        self.btn_spool_presets.clicked.connect(self.open_spool_presets_popup)
        lay_st.addWidget(self.sec_spool_title)
        lay_st.addStretch()
        lay_st.addWidget(self.btn_spool_presets)
        lay_card_spool.addWidget(spool_title_row)
        
        from PySide6.QtWidgets import QCheckBox

        self.lbl_inner_d = QLabel(); self.inputs["i"] = QLineEdit("35")
        self.lbl_hole_d = QLabel(); self.inputs["hole"] = QLineEdit("0")
        self.lbl_flange_d = QLabel("Flens Onder (mm):"); self.inputs["f"] = QLineEdit("90")
        self.chk_flange_b = QCheckBox("Flens Onder Aan")
        self.chk_flange_b.setChecked(True)

        self.lbl_flange_top_d = QLabel("Flens Boven (mm):"); self.inputs["f_top"] = QLineEdit("90")
        self.chk_flange_t = QCheckBox("Flens Boven Aan")
        self.chk_flange_t.setChecked(True)

        self.chk_asymmetric = QCheckBox("Oneven Flenzen (Asymmetrisch)")
        self.chk_asymmetric.toggled.connect(self.toggle_asymmetric_flanges)

        self.lbl_width = QLabel(); self.inputs["b"] = QLineEdit("50")
        self.lbl_spool_color = QLabel(); self.combo_spool_color = QComboBox()
        
        lay_card_spool.addWidget(self.create_form_row(self.inputs["i"], self.lbl_inner_d))
        lay_card_spool.addWidget(self.create_form_row(self.inputs["hole"], self.lbl_hole_d))
        lay_card_spool.addWidget(self.chk_asymmetric)

        row_fb = QWidget(); lay_fb = QHBoxLayout(row_fb); lay_fb.setContentsMargins(0,2,0,2)
        self.lbl_flange_d.setObjectName("formLabel")
        lay_fb.addWidget(self.chk_flange_b); lay_fb.addWidget(self.lbl_flange_d); lay_fb.addStretch(); lay_fb.addWidget(self.inputs["f"])
        self.inputs["f"].setFixedWidth(80)
        lay_card_spool.addWidget(row_fb)

        row_ft = QWidget(); lay_ft = QHBoxLayout(row_ft); lay_ft.setContentsMargins(0,2,0,2)
        self.lbl_flange_top_d.setObjectName("formLabel")
        lay_ft.addWidget(self.chk_flange_t); lay_ft.addWidget(self.lbl_flange_top_d); lay_ft.addStretch(); lay_ft.addWidget(self.inputs["f_top"])
        self.inputs["f_top"].setFixedWidth(80)
        lay_card_spool.addWidget(row_ft)
        self.lbl_flange_top_d.hide(); self.inputs["f_top"].hide()

        lay_card_spool.addWidget(self.create_form_row(self.inputs["b"], self.lbl_width))
            
        lay_card_spool.addWidget(self.lbl_spool_color)
        for c_name, rgb in self.spool_colors.items():
            pix = QPixmap(14, 14); pix.fill(QColor.fromRgbF(*rgb))
            self.combo_spool_color.addItem(QIcon(pix), c_name)
        lay_card_spool.addWidget(self.combo_spool_color)
        lay_scroll.addWidget(card_spool)

        # --- SECTIE: WIKKELING ---
        card_coil = QFrame(); card_coil.setObjectName("sectionCard")
        lay_card_coil = QVBoxLayout(card_coil)
        self.sec_coil_title = QLabel(); self.sec_coil_title.setObjectName("sectionTitle")
        lay_card_coil.addWidget(self.sec_coil_title)
        
        self.lbl_material = QLabel()
        self.combo_material = QComboBox()
        self.combo_material.setFixedWidth(160) 
        
        self.btn_edit_materials = QPushButton("📝")
        self.btn_edit_materials.setObjectName("editMaterialsBtn")
        self.btn_edit_materials.setFixedSize(24, 24)
        self.btn_edit_materials.clicked.connect(self.open_materials_popup)
        
        self.lbl_wire_d = QLabel()
        self.input_wire_d_display = QLineEdit()
        self.input_wire_d_display.setFixedWidth(80)
        self.input_wire_d_display.setReadOnly(True)
        self.input_wire_d_display.setAlignment(Qt.AlignRight)
        
        self.lbl_winding_mode = QLabel("Wikkellimiet Gebaseerd Op:")
        self.combo_winding_mode = QComboBox()
        self.combo_winding_mode.addItems(["Aantal Lagen", "Doel Ohm-waarde (Ω)", "Herspoelen / Meter-modus (m)"])
        self.combo_winding_mode.currentIndexChanged.connect(self.toggle_winding_mode_fields)

        self.lbl_layers = QLabel("Aantal Lagen:"); self.inputs["l"] = QLineEdit("2")
        self.lbl_target_val = QLabel("Doel Waarde:"); self.inputs["target_val"] = QLineEdit("6.0")

        self.lbl_wire_type = QLabel(); self.combo_wire_type = QComboBox()
        self.combo_wire_type.addItems(["Single Wire", "Multi-Wire"])
        self.combo_wire_type.currentIndexChanged.connect(self.toggle_multi_wire_fields)
        
        self.lbl_num_wires = QLabel(); self.inputs["num_wires"] = QLineEdit("5")
        self.inputs["num_wires"].textChanged.connect(self.generate_dynamic_wire_color_menus)
        self.scroll_colors = QScrollArea(); self.scroll_colors.setWidgetResizable(True)
        self.scroll_colors.setMaximumHeight(150)
        self.scroll_colors_container = QWidget(); self.scroll_colors_layout = QVBoxLayout(self.scroll_colors_container)
        self.scroll_colors.setWidget(self.scroll_colors_container)
        
        self.lbl_single_color = QLabel(); self.combo_wire_color = QComboBox()
        
        for c_name, rgb in self.wire_colors.items():
            pix = QPixmap(14, 14); pix.fill(QColor.fromRgbF(*rgb))
            self.combo_wire_color.addItem(QIcon(pix), c_name)
            
        self.combo_material.currentTextChanged.connect(self.on_material_dropdown_changed)

        row_mat = QWidget(); lay_m = QHBoxLayout(row_mat); lay_m.setContentsMargins(0,2,0,2)
        self.lbl_material.setObjectName("formLabel")
        lay_m.addWidget(self.lbl_material)
        lay_m.addStretch()
        lay_m.addWidget(self.combo_material)
        lay_m.addWidget(self.btn_edit_materials)
        lay_card_coil.addWidget(row_mat)
        
        lay_card_coil.addWidget(self.create_form_row(self.input_wire_d_display, self.lbl_wire_d))

        lay_card_coil.addWidget(self.lbl_winding_mode)
        lay_card_coil.addWidget(self.combo_winding_mode)

        lay_card_coil.addWidget(self.create_form_row(self.inputs["l"], self.lbl_layers))
        row_target = self.create_form_row(self.inputs["target_val"], self.lbl_target_val)
        lay_card_coil.addWidget(row_target)
        self.lbl_target_val.hide(); self.inputs["target_val"].hide()

        lay_card_coil.addWidget(self.lbl_wire_type); lay_card_coil.addWidget(self.combo_wire_type)
        lay_card_coil.addWidget(self.create_form_row(self.inputs["num_wires"], self.lbl_num_wires))
        lay_card_coil.addWidget(self.scroll_colors)
        lay_card_coil.addWidget(self.lbl_single_color); lay_card_coil.addWidget(self.combo_wire_color)
        
        lay_scroll.addWidget(card_coil)
        self.lbl_num_wires.hide(); self.inputs["num_wires"].hide(); self.scroll_colors.hide()
        
        lay_scroll.addStretch()
        scroll_area.setWidget(scroll_content)
        sidebar_layout.addWidget(scroll_area)

        self.btn_update = QPushButton()
        self.btn_update.setObjectName("sliceActionButton")
        sidebar_layout.addWidget(self.btn_update)

        # Connect change signals for visual status indicator
        self._setup_dirty_listeners()
        
        self.btn_toggle_spool = QPushButton()
        self.btn_toggle_spool.setObjectName("secondaryActionButton")
        sidebar_layout.addWidget(self.btn_toggle_spool)

        self.viewer = Dummy3DViewer()
        
        # Add to splitter
        self.splitter.addWidget(sidebar_container)
        self.splitter.addWidget(self.viewer)
        self.splitter.setStretchFactor(1, 1) # Viewer should grow

    def _setup_dirty_listeners(self):
        for key, inp in self.inputs.items():
            inp.textChanged.connect(self._on_input_changed)
        self.chk_flange_b.toggled.connect(lambda: self.set_calculate_dirty(True))
        self.chk_flange_t.toggled.connect(lambda: self.set_calculate_dirty(True))
        self.chk_asymmetric.toggled.connect(lambda: self.set_calculate_dirty(True))
        self.combo_winding_mode.currentIndexChanged.connect(lambda: self.set_calculate_dirty(True))
        self.combo_spool_color.currentIndexChanged.connect(lambda: self.set_calculate_dirty(True))
        self.combo_wire_color.currentIndexChanged.connect(lambda: self.set_calculate_dirty(True))
        self.combo_wire_type.currentIndexChanged.connect(lambda: self.set_calculate_dirty(True))
        self.combo_material.currentIndexChanged.connect(lambda: self.set_calculate_dirty(True))

    def _on_input_changed(self):
        self.validate_inputs()
        self.set_calculate_dirty(True)

    def validate_inputs(self):
        from core.config import parse_fraction_or_float
        is_valid = True
        invalid_style = "border: 1.5px solid #ef4444; background-color: rgba(239, 68, 68, 0.1);"

        # Validate Core Diameter i vs Flange f and Hole
        try:
            val_i = parse_fraction_or_float(self.inputs["i"].text())
            val_f = parse_fraction_or_float(self.inputs["f"].text())
            if val_i <= 0 or val_i >= val_f:
                self.inputs["i"].setStyleSheet(invalid_style)
                is_valid = False
            else:
                self.inputs["i"].setStyleSheet("")
        except Exception:
            self.inputs["i"].setStyleSheet(invalid_style)
            is_valid = False

        # Validate Hole Diameter hole (hole < i and hole >= 0)
        try:
            val_hole = parse_fraction_or_float(self.inputs["hole"].text())
            val_i = parse_fraction_or_float(self.inputs["i"].text())
            if val_hole < 0 or val_hole >= val_i or val_i <= 0:
                self.inputs["hole"].setStyleSheet(invalid_style)
                is_valid = False
            else:
                self.inputs["hole"].setStyleSheet("")
        except Exception:
            self.inputs["hole"].setStyleSheet(invalid_style)
            is_valid = False

        # Validate Flange Diameter f (f > i)
        try:
            val_f = parse_fraction_or_float(self.inputs["f"].text())
            val_i = parse_fraction_or_float(self.inputs["i"].text())
            if val_f <= val_i:
                self.inputs["f"].setStyleSheet(invalid_style)
                is_valid = False
            else:
                self.inputs["f"].setStyleSheet("")
        except Exception:
            self.inputs["f"].setStyleSheet(invalid_style)
            is_valid = False

        # Validate Width b (b > 0)
        try:
            val_b = parse_fraction_or_float(self.inputs["b"].text())
            if val_b <= 0:
                self.inputs["b"].setStyleSheet(invalid_style)
                is_valid = False
            else:
                self.inputs["b"].setStyleSheet("")
        except Exception:
            self.inputs["b"].setStyleSheet(invalid_style)
            is_valid = False

        # Validate Layers l (l >= 1)
        try:
            val_l = int(self.inputs["l"].text())
            if val_l < 1:
                self.inputs["l"].setStyleSheet(invalid_style)
                is_valid = False
            else:
                self.inputs["l"].setStyleSheet("")
        except Exception:
            self.inputs["l"].setStyleSheet(invalid_style)
            is_valid = False

        return is_valid

    def set_calculate_dirty(self, dirty: bool):
        self._calculate_dirty = dirty
        if dirty:
            self.btn_update.setStyleSheet("""
                QPushButton#sliceActionButton {
                    background-color: #d97706;
                    color: white;
                    font-weight: bold;
                    font-size: 13px;
                    padding: 10px;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton#sliceActionButton:hover {
                    background-color: #f59e0b;
                }
            """)
            self.btn_update.setText("⚠️ Berekenen vereist")
        else:
            self.btn_update.setStyleSheet("")
            tx = TRANSLATIONS.get(self.main_window.current_lang, {}) if hasattr(self, 'main_window') else {}
            self.btn_update.setText(tx.get("btn_update", "BEREKEN & SLICE"))

    def create_form_row(self, widget_right, text_label):
        row = QWidget(); lay = QHBoxLayout(row)
        lay.setContentsMargins(0, 2, 0, 2)
        text_label.setObjectName("formLabel")
        widget_right.setFixedWidth(80)
        lay.addWidget(text_label)
        lay.addStretch()
        lay.addWidget(widget_right)
        return row

    def load_materials_into_combobox(self):
        self.combo_material.blockSignals(True)
        self.combo_material.clear()
        
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    self.materials_database = json.load(f)
            except Exception as e:
                print(f"Fout bij inladen dropdown JSON: {e}")
                self.materials_database = []
        else:
            self.materials_database = []

        for mat in self.materials_database:
            self.combo_material.addItem(mat["name"])
            
        self.combo_material.blockSignals(False)
        
        if self.combo_material.count() > 0:
            self.on_material_dropdown_changed(self.combo_material.currentText())
        else:
            self.input_wire_d_display.setText("0.0 mm")

    def on_material_dropdown_changed(self, selected_name):
        from core.config import mm_to_awg
        for mat in self.materials_database:
            if mat["name"] == selected_name:
                d = float(mat.get("diameter", 0.0))
                i = float(mat.get("insulation", 0.0))
                total_d = d + i

                # Check current unit
                unit = self.main_window.tab_settings.combo_units.currentText() if hasattr(self.main_window, 'tab_settings') else "mm"
                if unit == "inch":
                    awg_val = mm_to_awg(total_d)
                    inch_val = total_d / 25.4
                    self.input_wire_d_display.setText(f"{awg_val} AWG ({inch_val:.4f}\")")
                else:
                    self.input_wire_d_display.setText(f"{total_d:.2f} mm")
                return

    def on_unit_changed(self, unit_text):
        """Converts currently typed values in the inputs from old unit to new unit, and updates the display."""
        from core.config import parse_fraction_or_float, mm_to_inch, inch_to_mm

        # Convert the inputs: i, hole, f, b
        keys_to_convert = ['i', 'hole', 'f', 'b']

        for k in keys_to_convert:
            if k in self.inputs:
                raw_text = self.inputs[k].text()
                val = parse_fraction_or_float(raw_text)
                if unit_text == "inch":
                    # Convert from mm to inch
                    converted = mm_to_inch(val)
                    self.inputs[k].setText(f"{converted:.4f}")
                else:
                    # Convert from inch to mm
                    converted = inch_to_mm(val)
                    self.inputs[k].setText(f"{converted:.2f}")

        # Update labels in languages
        tx = TRANSLATIONS.get(self.main_window.current_lang, {})
        self.retranslate_ui(tx)

    def toggle_winding_mode_fields(self, index):
        if index == 0:
            self.lbl_layers.show(); self.inputs["l"].show()
            self.lbl_target_val.hide(); self.inputs["target_val"].hide()
        elif index == 1:
            self.lbl_layers.hide(); self.inputs["l"].hide()
            self.lbl_target_val.setText("Doel Ohm (Ω):")
            self.inputs["target_val"].setText("6.0")
            self.lbl_target_val.show(); self.inputs["target_val"].show()
        elif index == 2:
            self.lbl_layers.hide(); self.inputs["l"].hide()
            self.lbl_target_val.setText("Doel Lengte (m):")
            self.inputs["target_val"].setText("15.0")
            self.lbl_target_val.show(); self.inputs["target_val"].show()

    def toggle_asymmetric_flanges(self, enabled):
        if enabled:
            self.lbl_flange_top_d.show()
            self.inputs["f_top"].show()
        else:
            self.lbl_flange_top_d.hide()
            self.inputs["f_top"].hide()
            self.inputs["f_top"].setText(self.inputs["f"].text())

    def open_spool_presets_popup(self):
        from ui.dialogs import SpoolPresetsDialog
        is_light = (self.main_window.current_theme == "light")
        popup = SpoolPresetsDialog(self, is_light_theme=is_light, lang=self.main_window.current_lang)
        if popup.exec() and popup.selected_preset:
            p = popup.selected_preset
            unit = self.main_window.tab_settings.combo_units.currentText() if hasattr(self.main_window, 'tab_settings') else "mm"
            scale = 1.0 / 25.4 if unit == "inch" else 1.0

            i_val = float(p.get("i", 35)) * scale
            hole_val = float(p.get("hole", 0)) * scale
            f_val = float(p.get("f", 90)) * scale
            b_val = float(p.get("b", 50)) * scale

            fmt = "{:.4f}" if unit == "inch" else "{:.2f}"
            self.inputs["i"].setText(fmt.format(i_val))
            self.inputs["hole"].setText(fmt.format(hole_val))
            self.inputs["f"].setText(fmt.format(f_val))
            self.inputs["b"].setText(fmt.format(b_val))
            self.validate_inputs()
            self.set_calculate_dirty(True)

    def open_materials_popup(self):
        is_light = (self.main_window.current_theme == "light")
        popup = MaterialsPopUp(self, is_light_theme=is_light, lang=self.main_window.current_lang)
        popup.exec()
        self.load_materials_into_combobox()

    def toggle_multi_wire_fields(self, index):
        if index == 1:
            self.lbl_num_wires.show(); self.inputs["num_wires"].show(); self.scroll_colors.show()
            self.lbl_single_color.hide(); self.combo_wire_color.hide()
            self.generate_dynamic_wire_color_menus()
        else:
            self.lbl_num_wires.hide(); self.inputs["num_wires"].hide(); self.scroll_colors.hide()
            self.lbl_single_color.show(); self.combo_wire_color.show()

    def generate_dynamic_wire_color_menus(self):
        if not hasattr(self, 'scroll_colors_layout') or self.scroll_colors_layout is None: return
        for i in reversed(range(self.scroll_colors_layout.count())): 
            widget = self.scroll_colors_layout.itemAt(i).widget()
            if widget is not None: widget.setParent(None)
        self.wire_color_combos.clear()
        
        if self.combo_wire_type.currentIndex() != 1: return
        try:
            num_wires = int(self.inputs["num_wires"].text())
            if num_wires < 1: num_wires = 1
            if num_wires > 24: num_wires = 24
        except ValueError: return

        tx = TRANSLATIONS[self.main_window.current_lang]
        for idx in range(num_wires):
            row_widget = QWidget(); row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 2, 0, 2)
            lbl = QLabel(f"{tx['wire_idx']} {idx+1}:")
            lbl.setStyleSheet("color: #9da3a8; font-size: 11px;")
            combo = QComboBox()
            for c_name, rgb in self.wire_colors.items():
                pix = QPixmap(14, 14); pix.fill(QColor.fromRgbF(*rgb))
                combo.addItem(QIcon(pix), c_name)
            combo.setCurrentIndex(idx % len(self.wire_colors))
            row_layout.addWidget(lbl); row_layout.addStretch(); row_layout.addWidget(combo)
            self.scroll_colors_layout.addWidget(row_widget)
            self.wire_color_combos.append(combo)

    def retranslate_ui(self, tx):
        self.sec_spool_title.setText(tx["sec_spool"])
        self.sec_coil_title.setText(tx["sec_coil"])

        # Adjust mm / inch suffix based on current settings unit
        unit = self.main_window.tab_settings.combo_units.currentText() if hasattr(self.main_window, 'tab_settings') else "mm"
        suffix = " (inch):" if unit == "inch" else " (mm):"

        inner_d_txt = tx.get("lbl_inner_d", "Kern Diameter (mm):").replace(" (mm):", suffix).replace(" (inch):", suffix)
        hole_d_txt = tx.get("lbl_hole_d", "Gat Diameter (mm):").replace(" (mm):", suffix).replace(" (inch):", suffix)
        flange_d_txt = tx.get("lbl_flange_d", "Flens Diameter (mm):").replace(" (mm):", suffix).replace(" (inch):", suffix)
        width_txt = tx.get("lbl_width", "Spoel Breedte (mm):").replace(" (mm):", suffix).replace(" (inch):", suffix)

        self.lbl_inner_d.setText(inner_d_txt)
        self.lbl_hole_d.setText(hole_d_txt)
        self.lbl_flange_d.setText(flange_d_txt)
        self.lbl_width.setText(width_txt)

        self.lbl_spool_color.setText(tx["lbl_spool_color"])
        self.lbl_material.setText(tx["lbl_material"])

        wire_d_lbl = tx["lbl_wire_d"]
        if unit == "inch":
            wire_d_lbl = wire_d_lbl.replace("Ø", "AWG / Ø")
        self.lbl_wire_d.setText(wire_d_lbl)
        self.lbl_layers.setText(tx["lbl_layers"])
        self.lbl_wire_type.setText(tx["lbl_wire_type"])
        self.lbl_num_wires.setText(tx["lbl_num_wires"])
        self.lbl_single_color.setText(tx["lbl_single_color"])
        self.btn_update.setText(tx["btn_update"])
        self.btn_toggle_spool.setText(tx["btn_toggle_spool"])
        
        current_text = self.combo_material.currentText()
        self.load_materials_into_combobox()
        self.combo_material.setCurrentText(current_text)
