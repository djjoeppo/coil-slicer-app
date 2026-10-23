# viewer_3d.py
import numpy as np
import pyqtgraph.opengl as gl
from OpenGL import GL  # Importeer ruwe OpenGL functies voor de glans
from PySide6.QtWidgets import QFrame, QVBoxLayout, QGridLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QVector3D

class CustomGLMeshItem(gl.GLMeshItem):
    """Een geavanceerde mesh die echte OpenGL glans (specular) ondersteunt
       en compatibel is met Python 3.13 / PySide6."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.material_params = None

    def paint(self):
        # --- VOORKOM 6 ARGUMENTS CRASH ---
        # Haal de kleur op uit de pyqtgraph opties
        c = self.opts.get('color', (1, 1, 1, 1))

        # Als de kleur genest is (zoals een tuple in een lijst), breek hem open
        if isinstance(c, (list, tuple)) and len(c) == 1 and isinstance(c[0], (list, tuple, np.ndarray)):
            c = c[0]

        # Zorg dat de kleur ALTIJD exact een platte tuple van 4 getallen is (RGBA)
        c_flat = list(c)
        if len(c_flat) == 3:
            c_flat.append(1.0)
        elif len(c_flat) > 4:
            c_flat = c_flat[:4]
        self.opts['color'] = tuple(c_flat)
        # ---------------------------------

        # Als het materiaal glanzend metaal is, zetten we de spiegeling aan
        if self.material_params and self.material_params.get("is_metallic"):
            GL.glEnable(GL.GL_LIGHTING)
            GL.glEnable(GL.GL_LIGHT0)

            diffuse = self.material_params["diffuse"]
            # Zorg dat diffuse ook exact 4 elementen heeft voor OpenGL
            if len(diffuse) == 3: diffuse = (*diffuse, 1.0)

            specular = (1.0, 0.95, 0.9, 1.0) # De glanzende lichtvlek (hotspot)
            shininess = 110.0                # Hoe scherp de lak reflecteert

            GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_DIFFUSE, diffuse)
            GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_SPECULAR, specular)
            GL.glMaterialf(GL.GL_FRONT_AND_BACK, GL.GL_SHININESS, shininess)
        else:
            # Voor matte kleuren/plastics zetten we de glansvlek uit
            GL.glDisable(GL.GL_LIGHT0)
            if self.material_params:
                diffuse = self.material_params["diffuse"]
                if len(diffuse) == 3: diffuse = (*diffuse, 1.0)
                GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_DIFFUSE, diffuse)
            GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_SPECULAR, (0.0, 0.0, 0.0, 1.0))
            GL.glMaterialf(GL.GL_FRONT_AND_BACK, GL.GL_SHININESS, 0.0)

        try:
            super().paint()
        except Exception:
            # Ultiem vangnet: Als pyqtgraph intern alsnog struikelt over vertex attributen,
            # dwingen we OpenGL hier handmatig naar de juiste kleurmodus.
            GL.glColor4f(*c_flat)


class Coil3DViewer(gl.GLViewWidget):
    def __init__(self):
        super().__init__()
        self.setBackgroundColor("#111111")
        self.opts.update({"distance": 250, "elevation": 30, "azimuth": 150})

        self._current_flange_d = 90.0
        self._current_width = 50.0

        # Create Navigation & ViewCube Overlay (Top Right, Fusion 360 style)
        self.overlay = QFrame(self)
        self.overlay.setStyleSheet("""
            QFrame#viewCubeFrame {
                background-color: rgba(18, 20, 22, 0.90);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
            }
            QLabel#viewBadge {
                color: #00d2ff;
                font-weight: bold;
                font-size: 10px;
                border: none;
                background: transparent;
            }
            QPushButton {
                background-color: rgba(45, 48, 52, 0.95);
                color: #ffffff;
                font-weight: bold;
                font-size: 9px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 3px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #007edc;
                color: #ffffff;
            }
            QPushButton#btnHome {
                background-color: #007edc;
                color: #ffffff;
                font-size: 10px;
            }
            QPushButton#btnHome:hover {
                background-color: #0096ff;
            }
            QPushButton#btnCorner {
                background-color: rgba(60, 65, 72, 0.9);
                color: #ffd700;
                font-size: 8px;
            }
            QPushButton#btnCorner:hover {
                background-color: #ff9800;
                color: #ffffff;
            }
        """)
        self.overlay.setObjectName("viewCubeFrame")

        overlay_layout = QVBoxLayout(self.overlay)
        overlay_layout.setContentsMargins(6, 6, 6, 6)
        overlay_layout.setSpacing(4)

        # Title / Active Orientation Badge
        self.lbl_view_badge = QLabel("ISO VIEW 30°")
        self.lbl_view_badge.setObjectName("viewBadge")
        self.lbl_view_badge.setAlignment(Qt.AlignCenter)
        overlay_layout.addWidget(self.lbl_view_badge)

        # Home Button (House Icon)
        self.btn_home = QPushButton("🏠 Home (ISO)")
        self.btn_home.setObjectName("btnHome")
        self.btn_home.setToolTip("Reset camera to Isometric Home view & Auto-zoom coil")
        self.btn_home.clicked.connect(self.reset_home_view)
        overlay_layout.addWidget(self.btn_home)

        # ViewCube Grid with Faces & Corners (Fusion 360 Style)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(2)

        # Row 0: Top Corners & Top Face
        btn_top_fl = QPushButton("T-F-L")
        btn_top_fl.setObjectName("btnCorner")
        btn_top_fl.setToolTip("Top-Front-Left Corner")
        btn_top_fl.clicked.connect(lambda: self.set_view_preset(30, 135))
        grid_layout.addWidget(btn_top_fl, 0, 0)

        btn_top = QPushButton("TOP")
        btn_top.clicked.connect(lambda: self.set_view_preset(90, 0))
        grid_layout.addWidget(btn_top, 0, 1)

        btn_top_fr = QPushButton("T-F-R")
        btn_top_fr.setObjectName("btnCorner")
        btn_top_fr.setToolTip("Top-Front-Right Corner")
        btn_top_fr.clicked.connect(lambda: self.set_view_preset(30, 45))
        grid_layout.addWidget(btn_top_fr, 0, 2)

        # Row 1: Side Faces
        btn_left = QPushButton("LEFT")
        btn_left.clicked.connect(lambda: self.set_view_preset(0, 180))
        grid_layout.addWidget(btn_left, 1, 0)

        btn_front = QPushButton("FRONT")
        btn_front.clicked.connect(lambda: self.set_view_preset(0, 90))
        grid_layout.addWidget(btn_front, 1, 1)

        btn_right = QPushButton("RIGHT")
        btn_right.clicked.connect(lambda: self.set_view_preset(0, 0))
        grid_layout.addWidget(btn_right, 1, 2)

        # Row 2: Bottom Corners & Back Face
        btn_top_bl = QPushButton("T-B-L")
        btn_top_bl.setObjectName("btnCorner")
        btn_top_bl.setToolTip("Top-Back-Left Corner")
        btn_top_bl.clicked.connect(lambda: self.set_view_preset(30, 225))
        grid_layout.addWidget(btn_top_bl, 2, 0)

        btn_back = QPushButton("BACK")
        btn_back.clicked.connect(lambda: self.set_view_preset(0, 270))
        grid_layout.addWidget(btn_back, 2, 1)

        btn_top_br = QPushButton("T-B-R")
        btn_top_br.setObjectName("btnCorner")
        btn_top_br.setToolTip("Top-Back-Right Corner")
        btn_top_br.clicked.connect(lambda: self.set_view_preset(30, 315))
        grid_layout.addWidget(btn_top_br, 2, 2)

        # Row 3: Bottom Face
        btn_bot = QPushButton("BOTTOM")
        btn_bot.clicked.connect(lambda: self.set_view_preset(-90, 0))
        grid_layout.addWidget(btn_bot, 3, 0, 1, 3)

        overlay_layout.addLayout(grid_layout)
        self.overlay.adjustSize()

        start_verts = np.array([[0,0,0], [1,0,0], [0,1,0]], dtype=np.float32)
        start_faces = np.array([[0,1,2]], dtype=np.uint32)
        light_mesh = gl.MeshData(vertexes=start_verts, faces=start_faces)

        self.hub = CustomGLMeshItem(meshdata=light_mesh, smooth=True, shader="shaded")
        self.flange_l = CustomGLMeshItem(meshdata=light_mesh, smooth=True, shader="shaded")
        self.flange_r = CustomGLMeshItem(meshdata=light_mesh, smooth=True, shader="shaded")
        self.addItem(self.hub)
        self.addItem(self.flange_l)
        self.addItem(self.flange_r)

        # Machine Components
        # Nozzle tracker: Custom mesh-based cube to avoid gl.GLBoxItem numpy attribute bugs
        verts = np.array([
            [0,0,0], [1,0,0], [1,1,0], [0,1,0],
            [0,0,1], [1,0,1], [1,1,1], [0,1,1]
        ], dtype=np.float32)
        faces = np.array([
            [0,1,2], [0,2,3], [0,1,5], [0,5,4], [1,2,6], [1,6,5],
            [2,3,7], [2,7,6], [3,0,4], [3,4,7], [4,5,6], [4,6,7]
        ], dtype=np.uint32)
        nozzle_md = gl.MeshData(vertexes=verts, faces=faces)
        self.nozzle = CustomGLMeshItem(meshdata=nozzle_md, smooth=False, shader="shaded")
        self.nozzle.scale(2, 2, 5)
        self.nozzle.setColor((1, 0, 0, 1))
        self.addItem(self.nozzle)

        self.wire_items = []

    def update_machine_elements(self, a_rot_deg, x_pos, y_pos, z_pos):
        # Spool rotates
        for item in [self.hub, self.flange_l, self.flange_r]:
            item.resetTransform()
            item.rotate(a_rot_deg, 0, 0, 1)

        # Nozzle moves
        self.nozzle.resetTransform()
        self.nozzle.translate(x_pos, y_pos, z_pos)

    def mouseMoveEvent(self, ev):
        super().mouseMoveEvent(ev)
        self.update_view_badge()

    def mouseReleaseEvent(self, ev):
        super().mouseReleaseEvent(ev)
        self.update_view_badge()

    def update_view_badge(self):
        """Updates the ViewCube active orientation badge in real time as camera rotates."""
        if not hasattr(self, 'lbl_view_badge'):
            return
        elev = int(self.opts.get('elevation', 30))
        azim = int(self.opts.get('azimuth', 150)) % 360

        if elev >= 75:
            view_str = "TOP VIEW"
        elif elev <= -75:
            view_str = "BOTTOM VIEW"
        else:
            if 45 <= azim < 135:
                view_str = "FRONT VIEW"
            elif 135 <= azim < 225:
                view_str = "LEFT VIEW"
            elif 225 <= azim < 315:
                view_str = "BACK VIEW"
            else:
                view_str = "RIGHT VIEW"

        self.lbl_view_badge.setText(f"{view_str} ({elev}°)")

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        if hasattr(self, 'overlay'):
            self.overlay.move(self.width() - self.overlay.width() - 15, 15)

    def auto_fit_view(self):
        """Auto-calculates optimal camera distance and center point to fit coil nicely in viewport."""
        flange_d = getattr(self, '_current_flange_d', 90.0)
        width = getattr(self, '_current_width', 50.0)

        max_dim = max(flange_d, width, 20.0)
        calc_dist = max_dim * 1.85
        calc_dist = max(40.0, min(1500.0, calc_dist))

        center_z = width / 2.0

        self.opts['center'] = QVector3D(0.0, 0.0, center_z)
        self.opts['distance'] = calc_dist
        self.update()

    def reset_home_view(self):
        """Resets camera to isometric perspective and auto-zooms to coil."""
        self.opts['elevation'] = 30
        self.opts['azimuth'] = 150
        self.auto_fit_view()

    def set_view_preset(self, elevation, azimuth):
        """Snaps camera to a flat view face (Top, Front, Right, Left, Back, Bottom)."""
        self.opts['elevation'] = elevation
        self.opts['azimuth'] = azimuth
        self.auto_fit_view()

    def build_spool_meshes(self, spool_data):
        self._current_flange_d = spool_data.get("flange_d", 90.0)
        self._current_width = spool_data.get("width", 50.0)

        r_out = spool_data["r_out"]
        r_in = spool_data["r_in"]
        cols = spool_data["cols"]
        width = spool_data["width"]
        flange_d = spool_data["flange_d"]

        if r_in > 0:
            ang = np.linspace(0, 2*np.pi, cols, endpoint=False)
            cos_a, sin_a = np.cos(ang), np.sin(ang)
            v_out_b = np.column_stack([r_out * cos_a, r_out * sin_a, np.zeros(cols)])
            v_out_t = np.column_stack([r_out * cos_a, r_out * sin_a, np.full(cols, width)])
            v_in_b = np.column_stack([r_in * cos_a, r_in * sin_a, np.zeros(cols)])
            v_in_t = np.column_stack([r_in * cos_a, r_in * sin_a, np.full(cols, width)])
            v_hub = np.vstack([v_out_b, v_out_t, v_in_b, v_in_t])
            f_hub = []
            for i in range(cols):
                n = (i + 1) % cols
                f_hub.append([i, n, i + cols]); f_hub.append([n, n + cols, i + cols])
                f_hub.append([i + 2*cols, i + 3*cols, n + 2*cols]); f_hub.append([n + 2*cols, i + 3*cols, n + 3*cols])
                f_hub.append([i, i + 2*cols, n]); f_hub.append([n, i + 2*cols, n + 2*cols])
                f_hub.append([i + cols, n + cols, i + 3*cols]); f_hub.append([n + cols, n + 3*cols, i + 3*cols])
            hub_mesh = gl.MeshData(vertexes=v_hub.astype(np.float32), faces=np.array(f_hub, dtype=np.uint32))
        else:
            md = gl.MeshData.cylinder(rows=1, cols=cols, radius=[r_out, r_out], length=width)
            v = md.vertexes(); f = list(md.faces())
            b, t = len(v), len(v)+1
            v = np.vstack([v, [0,0,0], [0,0,width]])
            for i in range(cols):
                n = (i+1)%cols
                f.append([b, i, n]); f.append([t, i+cols, n+cols])
            hub_mesh = gl.MeshData(vertexes=v.astype(np.float32), faces=np.array(f, dtype=np.uint32))

        def _make_flange(z_offset, thickness):
            rf_out = flange_d / 2
            rf_in = r_in
            ang = np.linspace(0, 2*np.pi, cols, endpoint=False)
            cos_a, sin_a = np.cos(ang), np.sin(ang)
            v_o_b = np.column_stack([rf_out * cos_a, rf_out * sin_a, np.full(cols, z_offset)])
            v_o_t = np.column_stack([rf_out * cos_a, rf_out * sin_a, np.full(cols, z_offset + thickness)])
            v_i_b = np.column_stack([rf_in * cos_a, rf_in * sin_a, np.full(cols, z_offset)])
            v_i_t = np.column_stack([rf_in * cos_a, rf_in * sin_a, np.full(cols, z_offset + thickness)])
            v_fl = np.vstack([v_o_b, v_o_t, v_i_b, v_i_t])
            f_fl = []
            for i in range(cols):
                n = (i + 1) % cols
                f_fl.append([i, n, i + cols]); f_fl.append([n, n + cols, i + cols])
                f_fl.append([i + 2*cols, i + 3*cols, n + 2*cols]); f_fl.append([n + 2*cols, i + 3*cols, n + 3*cols])
                f_fl.append([i, i + 2*cols, n]); f_fl.append([n, i + 2*cols, n + 2*cols])
                f_fl.append([i + cols, n + cols, i + 3*cols]); f_fl.append([n + cols, n + 3*cols, i + 3*cols])
            return gl.MeshData(vertexes=v_fl.astype(np.float32), faces=np.array(f_fl, dtype=np.uint32))

        self.hub.setMeshData(meshdata=hub_mesh)
        self.flange_l.setMeshData(meshdata=_make_flange(-3, 3))
        self.flange_r.setMeshData(meshdata=_make_flange(width, 3))

    def render_wire_meshes(self, meshes_data):
        """Render wire meshes efficiently by reusing items when possible (Bolt optimization)."""
        # If number of meshes changed, we reset
        if len(meshes_data) != len(self.wire_items):
            for item in self.wire_items:
                self.removeItem(item)
            self.wire_items.clear()

            for mesh_data in meshes_data:
                item = CustomGLMeshItem(meshdata=mesh_data, smooth=True, shader='shaded')
                item.setGLOptions('opaque')
                self.addItem(item)
                self.wire_items.append(item)
        else:
            # Update existing items' mesh data
            for idx, mesh_data in enumerate(meshes_data):
                self.wire_items[idx].setMeshData(meshdata=mesh_data)

    def update_materials(self, wire_materials, spool_material):
        for part in [self.hub, self.flange_l, self.flange_r]:
            part.material_params = spool_material
            part.setColor((*spool_material["diffuse"], 1.0))
            part.update()

        for idx, item in enumerate(self.wire_items):
            if idx < len(wire_materials):
                mat = wire_materials[idx]
                item.material_params = mat
                item.setColor((*mat["diffuse"], 1.0))
                item.update()

    def set_spool_visibility(self, visible: bool):
        self.hub.setVisible(visible)
        self.flange_l.setVisible(visible)
        self.flange_r.setVisible(visible)

    def set_machine_visibility(self, visible: bool):
        self.nozzle.setVisible(visible)
