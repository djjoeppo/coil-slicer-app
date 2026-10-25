# viewer_3d.py
import math
import numpy as np
import pyqtgraph.opengl as gl
from OpenGL import GL  # Importeer ruwe OpenGL functies voor de glans
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QGridLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QPoint, QPointF, QRectF
from PySide6.QtGui import QVector3D, QPainter, QPolygonF, QColor, QPen, QBrush, QFont, QPainterPath, QTransform


class FusionViewCubeWidget(QWidget):
    """An interactive 3D ViewCube widget matching Fusion 360 with live 3D rotation, face labels, red X/blue Z axes, and home house icon."""
    def __init__(self, viewer):
        super().__init__(viewer)
        self.viewer = viewer
        self.setFixedSize(125, 125)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setMouseTracking(True)
        self.hovered_face = None
        self.home_rect = QRectF(4, 4, 26, 26)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. Draw Home House Icon at Top-Left
        self._draw_home_icon(painter)

        # 2. Get camera orientation
        elev = self.viewer.opts.get('elevation', 30)
        azim = self.viewer.opts.get('azimuth', 45)

        e_rad = math.radians(elev)
        a_rad = math.radians(azim)

        cx, cy = 62, 65
        scale = 26.0

        # Camera view vectors
        cam_x = math.cos(e_rad) * math.cos(a_rad)
        cam_y = math.cos(e_rad) * math.sin(a_rad)
        cam_z = math.sin(e_rad)

        v_right_x = math.sin(a_rad)
        v_right_y = -math.cos(a_rad)
        v_right_z = 0.0

        v_up_x = -math.sin(e_rad) * math.cos(a_rad)
        v_up_y = -math.sin(e_rad) * math.sin(a_rad)
        v_up_z = math.cos(e_rad)

        def project(vx, vy, vz):
            sx = vx * v_right_x + vy * v_right_y + vz * v_right_z
            sy = vx * v_up_x + vy * v_up_y + vz * v_up_z
            depth = vx * cam_x + vy * cam_y + vz * cam_z

            px = cx + sx * scale
            py = cy - sy * scale
            return px, py, depth

        # Define 8 Cube Vertices (-1..1)
        cube_verts_3d = {
            'FTL': (-1, 1, 1),   'FTR': (1, 1, 1),
            'FBL': (-1, 1, -1),  'FBR': (1, 1, -1),
            'BTL': (-1, -1, 1),  'BTR': (1, -1, 1),
            'BBL': (-1, -1, -1), 'BBR': (1, -1, -1)
        }

        proj_verts = {}
        for k, (vx, vy, vz) in cube_verts_3d.items():
            proj_verts[k] = project(vx, vy, vz)

        # Define 6 Faces with outward normal vectors
        faces = [
            ('TOP', ['FTL', 'FTR', 'BTR', 'BTL'], (0, 0, 1)),
            ('BOTTOM', ['FBL', 'FBR', 'BBR', 'BBL'], (0, 0, -1)),
            ('FRONT', ['FTL', 'FTR', 'FBR', 'FBL'], (0, 1, 0)),
            ('BACK', ['BTL', 'BTR', 'BBR', 'BBL'], (0, -1, 0)),
            ('RIGHT', ['FTR', 'BTR', 'BBR', 'FBR'], (1, 0, 0)),
            ('LEFT', ['FTL', 'BTL', 'BBL', 'FBL'], (-1, 0, 0))
        ]

        # Calculate face depth and normal dot product with camera vector
        visible_faces = []
        for name, v_keys, (nx, ny, nz) in faces:
            depth = nx * cam_x + ny * cam_y + nz * cam_z
            if depth > 0.01:
                avg_depth = sum(proj_verts[vk][2] for vk in v_keys) / 4.0
                visible_faces.append((avg_depth, name, v_keys))

        visible_faces.sort(key=lambda item: item[0])

        # 3. Draw Solid Opaque Cube Faces
        self.face_polygons = {}
        for depth, name, v_keys in visible_faces:
            poly = QPolygonF([QPoint(int(proj_verts[vk][0]), int(proj_verts[vk][1])) for vk in v_keys])
            self.face_polygons[name] = poly

            is_hover = (self.hovered_face == name)
            bg_color = QColor(0, 126, 220, 255) if is_hover else QColor(235, 238, 242, 255)
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(QColor(40, 45, 50), 1.5))
            painter.drawPolygon(poly)

            # Draw Face Label Fixed On Cube Face Center
            center_px = sum(proj_verts[vk][0] for vk in v_keys) / 4.0
            center_py = sum(proj_verts[vk][1] for vk in v_keys) / 4.0

            painter.setPen(QPen(QColor(255, 255, 255) if is_hover else QColor(20, 25, 30)))
            painter.setFont(QFont("Segoe UI", 7, QFont.Bold))
            rect = QRectF(center_px - 20, center_py - 10, 40, 20)
            painter.drawText(rect, Qt.AlignCenter, name)

        # 4. Draw Red X, Green Y, Blue Z Axes in foreground
        ox, oy, _ = project(-1, -1, -1)
        xx, xy, _ = project(1.3, -1, -1)
        yx, yy, _ = project(-1, 1.3, -1)
        zx, zy, _ = project(-1, -1, 1.3)

        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))

        # Red X Axis
        painter.setPen(QPen(QColor(255, 60, 60), 2))
        painter.drawLine(int(ox), int(oy), int(xx), int(xy))
        painter.drawText(int(xx) + 2, int(xy) + 4, "X")

        # Green Y Axis
        painter.setPen(QPen(QColor(40, 200, 80), 2))
        painter.drawLine(int(ox), int(oy), int(yx), int(yy))
        painter.drawText(int(yx) + 2, int(yy) - 2, "Y")

        # Blue Z Axis
        painter.setPen(QPen(QColor(60, 130, 255), 2))
        painter.drawLine(int(ox), int(oy), int(zx), int(zy))
        painter.drawText(int(zx) - 8, int(zy) - 2, "Z")

    def _draw_home_icon(self, painter):
        is_home_hover = (self.hovered_face == 'HOME')
        pen = QPen(QColor(0, 126, 220) if is_home_hover else QColor(170, 175, 180), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        path = QPainterPath()
        path.moveTo(17, 7)
        path.lineTo(7, 15)
        path.lineTo(27, 15)
        path.closeSubpath()
        painter.drawPath(path)

        painter.drawRect(9, 15, 16, 12)
        painter.drawRect(14, 19, 6, 8)

    def mouseMoveEvent(self, event):
        pos = event.position()
        old_hover = self.hovered_face
        self.hovered_face = None

        if self.home_rect.contains(pos):
            self.hovered_face = 'HOME'
        elif hasattr(self, 'face_polygons'):
            for name, poly in self.face_polygons.items():
                if poly.containsPoint(pos, Qt.OddEvenFill):
                    self.hovered_face = name
                    break

        if old_hover != self.hovered_face:
            self.update()

    def mousePressEvent(self, event):
        pos = event.position()
        if self.home_rect.contains(pos):
            self.viewer.reset_home_view()
            return

        if hasattr(self, 'face_polygons'):
            for name, poly in self.face_polygons.items():
                if poly.containsPoint(pos, Qt.OddEvenFill):
                    presets = {
                        'TOP': (90, 0),
                        'BOTTOM': (-90, 0),
                        'FRONT': (0, 90),
                        'BACK': (0, 270),
                        'RIGHT': (0, 0),
                        'LEFT': (0, 180)
                    }
                    if name in presets:
                        elev, azim = presets[name]
                        self.viewer.set_view_preset(elev, azim)
                    break

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
        self.opts.update({"distance": 250, "elevation": 30, "azimuth": 45})

        self._current_flange_d = 90.0
        self._current_width = 50.0

        # Create Interactive 3D ViewCube Widget (Fusion 360 Style)
        self.view_cube = FusionViewCubeWidget(self)

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
        if hasattr(self, 'view_cube'):
            self.view_cube.update()

    def mouseReleaseEvent(self, ev):
        super().mouseReleaseEvent(ev)
        if hasattr(self, 'view_cube'):
            self.view_cube.update()

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        if hasattr(self, 'view_cube'):
            self.view_cube.move(self.width() - self.view_cube.width() - 15, 15)

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
        self.opts['azimuth'] = 45
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
