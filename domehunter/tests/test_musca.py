"""Tests for the Musca dome shutter controller.

Uses a PTY-based simulator to emulate the Musca microcontroller over a
virtual serial port, so no real hardware or Bluetooth is needed.
"""

import os
import pty
import threading
import time

import pytest

from domehunter.musca import (
    CLOSE_CMD,
    KEEP_OPEN_CMD,
    OPEN_CMD,
    STATUS_CMD,
    MuscaConfig,
    MuscaController,
)


class MuscaSimulator:
    """Simulates the Musca microcontroller over a PTY pair.

    Runs a background thread that reads commands from the master side
    and writes back status responses, mimicking the real firmware.
    """

    def __init__(self):
        self.master_fd, self.slave_fd = pty.openpty()
        self.slave_path = os.ttyname(self.slave_fd)

        # Simulated state
        self.shutter = "Closed"
        self.door = "Closed"
        self.battery = 13.2
        self.solar = 0.45
        self.switch = "Relays"
        self.keep_open_count = 0
        self.shutter_delay = 0.1  # fast transitions for tests

        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def close(self):
        self._running = False
        try:
            os.close(self.master_fd)
        except OSError:
            pass
        try:
            os.close(self.slave_fd)
        except OSError:
            pass
        self._thread.join(timeout=2.0)

    def _run(self):
        """Read commands from master fd and respond."""
        buf = b""
        while self._running:
            try:
                data = os.read(self.master_fd, 1024)
                if not data:
                    break
                buf += data
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    cmd = line.decode(errors="replace").strip()
                    self._handle_command(cmd)
            except OSError:
                break

    def _handle_command(self, cmd: str):
        if cmd == STATUS_CMD:
            self._send_full_status()
        elif cmd == OPEN_CMD:
            self.shutter = "Opening"
            self._send_full_status()
            time.sleep(self.shutter_delay)
            self.shutter = "Open"
            self._send_full_status()
        elif cmd == CLOSE_CMD:
            self.shutter = "Closing"
            self._send_full_status()
            time.sleep(self.shutter_delay)
            self.shutter = "Closed"
            self._send_full_status()
        elif cmd == KEEP_OPEN_CMD:
            self.keep_open_count += 1

    def _send_full_status(self):
        # Match real Musca firmware: Status: header, \r\n line endings
        lines = (
            f"Status:\r\n"
            f"Shutter:{self.shutter}\r\n"
            f"Door:{self.door}\r\n"
            f"Battery:\t {self.battery}\r\n"
            f"Solar_A:\t{self.solar}\r\n"
            f"Switch:{self.switch}\r\n"
        )
        try:
            os.write(self.master_fd, lines.encode())
        except OSError:
            pass


@pytest.fixture
def simulator():
    sim = MuscaSimulator()
    yield sim
    sim.close()


@pytest.fixture
def musca(simulator):
    config = MuscaConfig(
        serial_port=simulator.slave_path,
        baud_rate=9600,
        heartbeat_interval=0.3,  # fast for testing
        shutter_timeout=5.0,
        min_battery_voltage=12.0,
        reconnect_delay=0.1,
        max_reconnect_delay=1.0,
        read_timeout=2.0,
        status_interval=0.5,  # fast status polling for tests
    )
    ctrl = MuscaController(config)
    ctrl.connect()
    yield ctrl
    ctrl.disconnect()


def wait_for_shutter(musca, target, timeout=5.0):
    """Poll cached status until shutter reaches target state."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        status = musca.request_status()
        if status.shutter == target:
            return status
        time.sleep(0.2)
    raise TimeoutError(
        f"Shutter did not reach '{target}' within {timeout}s "
        f"(last: '{musca.status.shutter}')"
    )


class TestConnect:
    def test_connect_succeeds(self, musca):
        assert musca.connected is True

    def test_initial_status_read(self, musca):
        s = musca.status
        assert s.shutter == "Closed"
        assert s.door == "Closed"
        assert s.battery_voltage == pytest.approx(13.2)
        assert s.solar_current == pytest.approx(0.45)
        assert s.switch_mode == "Relays"


class TestStatus:
    def test_request_status(self, musca):
        status = musca.request_status()
        assert status.shutter == "Closed"
        assert status.battery_voltage == pytest.approx(13.2)

    def test_status_updates_after_change(self, musca, simulator):
        simulator.battery = 11.5
        # Wait for the I/O thread to pick up the new value
        time.sleep(1.5)
        status = musca.request_status()
        assert status.battery_voltage == pytest.approx(11.5)


class TestOpenClose:
    def test_open_shutter(self, musca, simulator):
        musca.open_shutter()
        status = wait_for_shutter(musca, "Open")
        assert status.shutter == "Open"

    def test_close_shutter(self, musca, simulator):
        musca.open_shutter()
        wait_for_shutter(musca, "Open")
        musca.close_shutter()
        status = wait_for_shutter(musca, "Closed")
        assert status.shutter == "Closed"

    def test_open_already_open(self, musca, simulator):
        """Opening when already open should be a no-op."""
        musca.open_shutter()
        wait_for_shutter(musca, "Open")
        # Should not raise
        musca.open_shutter()

    def test_close_already_closed(self, musca):
        """Closing when already closed should be a no-op."""
        musca.close_shutter()  # should not raise


class TestBatteryCheck:
    def test_low_battery_blocks_open(self, musca, simulator):
        simulator.battery = 11.0
        # Wait for the I/O thread to pick up the low battery
        time.sleep(1.5)
        with pytest.raises(RuntimeError, match="Battery too low"):
            musca.open_shutter()

    def test_sufficient_battery_allows_open(self, musca, simulator):
        simulator.battery = 13.5
        musca.open_shutter()  # should not raise
        status = wait_for_shutter(musca, "Open")
        assert status.shutter == "Open"


class TestHeartbeat:
    def test_heartbeat_sends_keep_open(self, musca, simulator):
        musca.open_shutter()
        # Heartbeat interval is 0.3s, wait for a few beats
        time.sleep(1.5)
        assert simulator.keep_open_count > 0

    def test_heartbeat_stops_on_close(self, musca, simulator):
        musca.open_shutter()
        wait_for_shutter(musca, "Open")
        count_before = simulator.keep_open_count
        musca.close_shutter()
        wait_for_shutter(musca, "Closed")
        time.sleep(1.0)
        # No more heartbeats should have been sent after close
        assert simulator.keep_open_count <= count_before + 1


class TestBtDropout:
    def test_shutter_assumed_closed_after_dropout(self, musca, simulator):
        musca.open_shutter()
        wait_for_shutter(musca, "Open")

        # Simulate BT dropout
        simulator.close()
        musca._connected = False

        # Wait past heartbeat interval
        time.sleep(0.5)
        assert musca.shutter_assumed_closed is True

    def test_not_assumed_closed_when_connected(self, musca):
        musca.open_shutter()
        time.sleep(0.5)
        assert musca.shutter_assumed_closed is False
