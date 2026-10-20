# core/gcode_engine.py
import math
import numpy as np

class GCodeEngine:
    def __init__(self):
        self.start_gcode = "G28 ; Home all axes"
        self.end_gcode = "M30 ; Program end"
        self.units = "mm" 

    def generate(self, pts_list, angles_list, wire_d=0.5, nozzle_y_offset=0.0, wire_offset=0.0, spool_offset=0.0, z_force=0.5, feedrate=500, wrap_feedrate=150, dwell_time=1.0, pause_on_turn=True, compress_gcode=True, units="mm", max_x=200.0):
        """Generates G-code based on simulation paths, machine offsets, custom turnaround sequence, and optional move compression."""
        if not pts_list or not angles_list:
            return ""
            
        gcode = []
        
        # Units
        if units.lower() == "inch":
            gcode.append("G20 ; Inches")
        else:
            gcode.append("G21 ; Millimeters")
            
        gcode.append("G90 ; Absolute positioning")
        
        if self.start_gcode:
            gcode.append(self.start_gcode)

        # For simplicity, we use the first wire's path
        pts = pts_list[0]
        angles = angles_list[0]
        
        a_axis = np.degrees(angles)
        x_axis = pts[:, 2] + spool_offset + wire_offset
        y_axis = np.sqrt(pts[:, 0]**2 + pts[:, 1]**2) + nozzle_y_offset
        
        scale = 1.0 / 25.4 if units.lower() == "inch" else 1.0

        # Start position check
        if x_axis[0] > max_x or x_axis[0] < 0:
            gcode.append(f"; ERROR: Machine limit reached! X ({x_axis[0] * scale:.3f}) exceeds limit (0-{max_x * scale}).")
            return "\n".join(gcode)

        # Calculate initial Z position: 10.0mm reference - wire_d - 0.5mm clearance
        z_start = max(0.0, 10.0 - wire_d - 0.5)

        # Initial move to start position
        gcode.append(f"G0 A{a_axis[0]:.3f} X{x_axis[0] * scale:.3f} Y{y_axis[0] * scale:.3f} Z{z_start:.3f}")
        
        # M403 Z[weight] sets Force Mode with specified tension weight in kg (e.g. M403 Z2)
        gcode.append(f"M403 Z{z_force:g} ; Force Mode ON (Z-force in kg)")

        if pause_on_turn:
            gcode.append("M0 ; Pause before start (Check setup)")

        if dwell_time > 0:
            gcode.append(f"G4 P{dwell_time:.1f} ; Initial wraparound dwell")

        # Collect trajectory moves
        moves = []
        current_dir = None
        points_in_turnaround = 0
        wrap_points_count = 5 # Number of slow points at wraparound

        # First point entry
        moves.append({
            'a': a_axis[0],
            'x': x_axis[0] * scale,
            'y': y_axis[0] * scale,
            'f': feedrate,
            'meta': []
        })

        for i in range(1, len(pts)):
            if x_axis[i] > max_x or x_axis[i] < 0:
                gcode.append(f"; ERROR: Machine limit reached! X ({x_axis[i] * scale:.3f}) exceeds limit (0-{max_x * scale}).")
                return "\n".join(gcode)

            dx = x_axis[i] - x_axis[i-1]
            new_dir = 1 if dx > 1e-4 else (-1 if dx < -1e-4 else current_dir)

            meta = []
            # Turnaround detected!
            if current_dir is not None and new_dir is not None and new_dir != current_dir:
                if dwell_time > 0:
                    meta.append(f"G4 P{dwell_time:.1f} ; Dwell in flange for clean turnaround")
                if pause_on_turn:
                    meta.append("M0 ; Pause for layer inspection")
                points_in_turnaround = wrap_points_count

            current_dir = new_dir if new_dir is not None else current_dir

            current_f = wrap_feedrate if points_in_turnaround > 0 else feedrate
            if points_in_turnaround > 0:
                points_in_turnaround -= 1

            moves.append({
                'a': a_axis[i],
                'x': x_axis[i] * scale,
                'y': y_axis[i] * scale,
                'f': current_f,
                'meta': meta
            })

        # Compress moves if enabled
        if compress_gcode:
            moves = self._compress_moves(moves)

        # Output G-code lines from moves (starting from index 1 since index 0 was G0 start)
        for m in moves[1:]:
            for comment in m['meta']:
                gcode.append(comment)
            gcode.append(f"G1 A{m['a']:.3f} X{m['x']:.3f} Y{m['y']:.3f} F{m['f']:.0f}")

        # Force Mode OFF
        gcode.append("M400 ; Force Mode OFF")

        if self.end_gcode:
            gcode.append(self.end_gcode)
            
        return "\n".join(gcode)

    @staticmethod
    def _compress_moves(moves):
        """Simplifies consecutive collinear G1 moves along constant Y and feedrate."""
        if len(moves) <= 2:
            return moves

        compressed = [moves[0]]
        for i in range(1, len(moves) - 1):
            prev = compressed[-1]
            curr = moves[i]
            nxt = moves[i + 1]

            # Keep points that have turnaround metadata (dwell/pause)
            if curr.get('meta'):
                compressed.append(curr)
                continue

            # Keep points where feedrate changes
            if curr['f'] != nxt['f'] or prev['f'] != curr['f']:
                compressed.append(curr)
                continue

            # Keep points where Y changes
            if abs(prev['y'] - curr['y']) > 1e-4 or abs(curr['y'] - nxt['y']) > 1e-4:
                compressed.append(curr)
                continue

            # Check collinearity: constant slope (delta X / delta A)
            da1 = curr['a'] - prev['a']
            da2 = nxt['a'] - curr['a']
            if abs(da1) < 1e-6 or abs(da2) < 1e-6:
                compressed.append(curr)
                continue

            slope1 = (curr['x'] - prev['x']) / da1
            slope2 = (nxt['x'] - curr['x']) / da2

            if abs(slope1 - slope2) > 1e-4:
                compressed.append(curr)
            else:
                # Omit redundant intermediate collinear point
                pass

        compressed.append(moves[-1])
        return compressed
