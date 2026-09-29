"""Synchronous Musca dome shutter controller.

Wraps the Musca Bluetooth serial protocol (9600/8/N/1) for dome shutter
control. Sends heartbeat pings to satisfy the Musca firmware watchdog and
handles Bluetooth dropout detection with automatic reconnection.

A single background thread handles all serial I/O: reading status lines
from the Musca continuously, sending periodic heartbeats, and dispatching
commands. This avoids the serial desync that occurs when multiple gRPC
threads each try to send Status_update and read responses.

This module has no SensorKit or asyncio dependency — it uses pyserial
and threading, matching the synchronous style of the existing gRPC server.
"""

import logging
import threading
import time
from dataclasses import dataclass

import serial

logger = logging.getLogger(__name__)

# ── Protocol constants (from Musca firmware) ─────────────────────────

OPEN_CMD = "Shutter_open"
CLOSE_CMD = "Shutter_close"
KEEP_OPEN_CMD = "Keep_dome_open"
STATUS_CMD = "Status_update"


@dataclass
class MuscaConfig:
    """Configuration for the Musca shutter controller."""

    serial_port: str = "/dev/rfcomm0"
    baud_rate: int = 9600
    heartbeat_interval: float = 60.0
    shutter_timeout: float = 100.0
    min_battery_voltage: float = 12.0
    reconnect_delay: float = 5.0
    max_reconnect_delay: float = 60.0
    read_timeout: float = 3.0
    status_interval: float = 5.0  # how often to poll status in background


@dataclass
class MuscaStatus:
    """Last known status from the Musca controller."""

    shutter: str = "unknown"
    door: str = "unknown"
    battery_voltage: float | None = None
    solar_current: float | None = None
    switch_mode: str | None = None


class MuscaController:
    """Synchronous controller for the Musca dome shutter over Bluetooth serial.

    All serial I/O is handled by a single background thread (_io_loop).
    Commands are dispatched to that thread via a queue-like mechanism
    (the _pending_cmd field). The gRPC thread pool never touches the
    serial port directly.
    """

    def __init__(self, config: MuscaConfig | None = None):
        self.config = config or MuscaConfig()
        self._serial: serial.Serial | None = None
        self._connected = False
        self._keep_open = False
        self._last_heartbeat_time: float = 0.0
        self._reconnect_delay = self.config.reconnect_delay
        self._status = MuscaStatus()
        self._lock = threading.Lock()  # protects _status and _connected reads
        self._io_thread: threading.Thread | None = None
        self._io_stop = threading.Event()
        self._pending_cmd: str | None = None
        self._cmd_lock = threading.Lock()

    # ── Properties ────────────────────────────────────────────────────

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def status(self) -> MuscaStatus:
        with self._lock:
            return self._status

    @property
    def shutter_assumed_closed(self) -> bool:
        """True if BT has been down long enough for the Musca watchdog to
        have auto-closed the shutter."""
        if self._connected:
            return False
        if not self._keep_open:
            return False
        elapsed = time.monotonic() - self._last_heartbeat_time
        return elapsed > self.config.heartbeat_interval

    # ── Connection lifecycle ──────────────────────────────────────────

    def connect(self):
        """Open the Bluetooth serial connection, read initial status,
        and start the background I/O thread."""
        self._open_serial()
        self._send(STATUS_CMD)
        self._read_full_status()
        self._start_io_thread()

    def _open_serial(self):
        """Open the serial port."""
        try:
            self._serial = serial.Serial(
                port=self.config.serial_port,
                baudrate=self.config.baud_rate,
                timeout=self.config.read_timeout,
            )
            self._connected = True
            self._reconnect_delay = self.config.reconnect_delay
            logger.info("Musca serial connected on %s", self.config.serial_port)
        except serial.SerialException as e:
            self._connected = False
            raise ConnectionError(
                f"Failed to connect to Musca on {self.config.serial_port}: {e}"
            ) from e

    def disconnect(self):
        """Stop the I/O thread and close the serial connection."""
        self._stop_io_thread()
        self._connected = False
        if self._serial:
            try:
                self._serial.close()
            except Exception:
                pass
            self._serial = None

    def reconnect(self) -> bool:
        """Disconnect and reconnect with exponential backoff.

        Blocks until reconnection succeeds. Returns True on success.
        """
        self._connected = False
        if self._serial:
            try:
                self._serial.close()
            except Exception:
                pass
            self._serial = None

        while True:
            logger.info("Musca reconnecting in %.0fs...", self._reconnect_delay)
            time.sleep(self._reconnect_delay)
            try:
                self._open_serial()
                self._send(STATUS_CMD)
                self._read_full_status()
                logger.info("Musca reconnected")
                return True
            except (ConnectionError, serial.SerialException):
                self._reconnect_delay = min(
                    self._reconnect_delay * 2, self.config.max_reconnect_delay
                )

    # ── Serial I/O (called only from the I/O thread or during init) ──

    def _send(self, cmd: str) -> bool:
        """Send a command line. Returns True on success."""
        if not self._connected or self._serial is None:
            return False
        try:
            self._serial.write(f"{cmd}\n".encode())
            self._serial.flush()
            return True
        except (serial.SerialException, OSError) as e:
            logger.warning("Musca send failed: %s", e)
            self._connected = False
            return False

    # Known status field keys from the Musca firmware
    _STATUS_KEYS = {"Shutter", "Door", "Battery", "Solar_A", "Switch"}

    # Sentinel: readline() returned data but it wasn't a status field
    _SKIPPED = ("_SKIP", "")

    def _read_raw_line(self) -> bytes | None:
        """Read one raw line from serial. Returns None on timeout or error."""
        if not self._connected or self._serial is None:
            return None
        try:
            line = self._serial.readline()
            if not line:
                return None  # timeout
            return line
        except (serial.SerialException, OSError) as e:
            logger.warning("Musca read failed: %s", e)
            self._connected = False
            return None

    def _parse_line(self, raw: bytes) -> tuple[str, str] | None:
        """Parse a raw line into (key, value) if it's a status field.
        Returns _SKIPPED for non-status lines, None should not be returned here.
        """
        decoded = raw.decode(errors="replace").strip()
        if not decoded:
            return self._SKIPPED
        parts = decoded.split(":", 1)
        if len(parts) == 2 and parts[0].strip() in self._STATUS_KEYS:
            return parts[0].strip(), parts[1].strip()
        return self._SKIPPED

    def _read_full_status(self):
        """Read lines until all 5 status fields have been received or timeout.

        The Musca sends a 'Status:\\r\\n' header followed by 5 key:value lines.
        We keep reading as long as data arrives, skipping non-status lines.
        We stop when we've received all 5 fields or when readline() times out
        (meaning no more data is available).
        """
        received = set()
        timeouts = 0
        while timeouts < 2:
            raw = self._read_raw_line()
            if raw is None:
                # Timeout — no more data right now
                timeouts += 1
                continue
            timeouts = 0  # reset on any data
            parsed = self._parse_line(raw)
            if parsed is not self._SKIPPED and parsed is not None:
                self._apply_status(parsed)
                received.add(parsed[0])
                logger.debug("Musca status field: %s = %s", parsed[0], parsed[1])
                if received >= self._STATUS_KEYS:
                    break

    def _drain_and_update(self):
        """Read any available lines from serial and update status.
        Stops when readline() times out (no more data)."""
        while True:
            raw = self._read_raw_line()
            if raw is None:
                break
            parsed = self._parse_line(raw)
            if parsed is not self._SKIPPED and parsed is not None:
                self._apply_status(parsed)
                logger.debug("Musca status field: %s = %s", parsed[0], parsed[1])

    def _apply_status(self, msg: tuple[str, str]):
        """Update internal status from a parsed key:value pair."""
        key, value = msg
        with self._lock:
            if key == "Shutter":
                self._status.shutter = value
            elif key == "Door":
                self._status.door = value
            elif key == "Battery":
                try:
                    self._status.battery_voltage = float(value)
                except ValueError:
                    pass
            elif key == "Solar_A":
                try:
                    self._status.solar_current = float(value)
                except ValueError:
                    pass
            elif key == "Switch":
                self._status.switch_mode = value

    # ── Background I/O thread ─────────────────────────────────────────

    def _start_io_thread(self):
        """Start the background I/O thread."""
        if self._io_thread and self._io_thread.is_alive():
            return
        self._io_stop.clear()
        self._io_thread = threading.Thread(target=self._io_loop, daemon=True)
        self._io_thread.start()

    def _stop_io_thread(self):
        """Stop the background I/O thread."""
        self._io_stop.set()
        if self._io_thread and self._io_thread.is_alive():
            self._io_thread.join(timeout=10.0)
        self._io_thread = None

    def _io_loop(self):
        """Single thread that handles all serial communication.

        Periodically:
        - Sends Status_update and reads responses
        - Sends Keep_dome_open heartbeat when shutter is open
        - Dispatches any pending command (open/close)
        - Handles reconnection if the link drops
        """
        last_status_time = 0.0
        last_heartbeat_time = time.monotonic()
        self._last_heartbeat_time = last_heartbeat_time

        while not self._io_stop.is_set():
            # Handle reconnection
            if not self._connected:
                try:
                    self._open_serial()
                    self._send(STATUS_CMD)
                    self._read_full_status()
                    last_status_time = time.monotonic()
                    logger.info("Musca reconnected in I/O loop")
                except (ConnectionError, serial.SerialException, OSError):
                    self._reconnect_delay = min(
                        self._reconnect_delay * 2, self.config.max_reconnect_delay
                    )
                    self._io_stop.wait(self._reconnect_delay)
                    continue

            now = time.monotonic()

            # Dispatch any pending command
            with self._cmd_lock:
                cmd = self._pending_cmd
                self._pending_cmd = None
            if cmd:
                logger.debug("I/O thread sending command: %s", cmd)
                self._send(cmd)
                # After a command, drain any immediate response
                self._drain_and_update()

            # Periodic status poll
            if now - last_status_time >= self.config.status_interval:
                self._send(STATUS_CMD)
                self._read_full_status()
                last_status_time = time.monotonic()

            # Heartbeat
            if self._keep_open and (now - last_heartbeat_time >= self.config.heartbeat_interval):
                ok = self._send(KEEP_OPEN_CMD)
                if ok:
                    last_heartbeat_time = time.monotonic()
                    self._last_heartbeat_time = last_heartbeat_time
                    logger.debug("Musca heartbeat sent")
                else:
                    logger.warning("Musca heartbeat failed — link may be down")

            # Sleep briefly to avoid busy-waiting, but stay responsive
            self._io_stop.wait(0.5)

    def _enqueue_cmd(self, cmd: str):
        """Queue a command for the I/O thread to send."""
        with self._cmd_lock:
            self._pending_cmd = cmd

    # ── Public commands ───────────────────────────────────────────────

    def request_status(self) -> MuscaStatus:
        """Return the most recent cached status (updated by the I/O thread)."""
        with self._lock:
            return self._status

    def open_shutter(self):
        """Open the dome shutter.

        Checks battery voltage first. Starts the heartbeat via the I/O thread.
        Raises RuntimeError if battery is too low or serial is disconnected.
        """
        if not self._connected:
            raise RuntimeError("Bluetooth serial not connected")

        with self._lock:
            voltage = self._status.battery_voltage or 0
            if voltage < self.config.min_battery_voltage:
                raise RuntimeError(
                    f"Battery too low ({voltage:.1f}V "
                    f"< {self.config.min_battery_voltage:.1f}V)"
                )

            if self._status.shutter == "Open":
                logger.info("Shutter already open")
                self._keep_open = True
                return

        logger.info("Opening Musca shutter")
        self._enqueue_cmd(OPEN_CMD)
        self._keep_open = True

    def close_shutter(self):
        """Close the dome shutter. Stops the heartbeat."""
        self._keep_open = False

        with self._lock:
            if self._status.shutter == "Closed":
                logger.info("Shutter already closed")
                return

        if not self._connected:
            logger.warning(
                "Cannot send close command — BT disconnected "
                "(Musca watchdog should auto-close)"
            )
            return

        logger.info("Closing Musca shutter")
        self._enqueue_cmd(CLOSE_CMD)

    # ── Legacy compat (used by tests) ─────────────────────────────────

    def start_heartbeat(self):
        """No-op — heartbeat is handled by the I/O thread."""
        pass

    def stop_heartbeat(self):
        """No-op — heartbeat is handled by the I/O thread."""
        pass
