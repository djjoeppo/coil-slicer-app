import unittest
from unittest.mock import MagicMock, patch
import os
import sys

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import QCoreApplication

app = QCoreApplication.instance() or QCoreApplication(sys.argv)

from core.machine_worker import MachineWorker

class TestMachineWorker(unittest.TestCase):
    @patch('serial.Serial')
    def test_connect_port_non_blocking(self, mock_serial_cls):
        mock_ser = MagicMock()
        mock_ser.is_open = True
        mock_serial_cls.return_value = mock_ser

        worker = MachineWorker()

        connected_signal_received = []
        worker.connected.connect(lambda msg: connected_signal_received.append(msg))

        worker.connect_port("COM3", 115200)

        self.assertTrue(worker.is_connected())
        self.assertEqual(len(connected_signal_received), 1)
        self.assertIn("connected (COM3)", connected_signal_received[0])
        self.assertTrue(worker._poll_timer.isActive())

        worker.disconnect_port()
        self.assertFalse(worker.is_connected())

if __name__ == "__main__":
    unittest.main()
