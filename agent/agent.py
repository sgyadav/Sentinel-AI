"""
SENTINEL AI - ENDPOINT AGENT
Monitors Windows system and reports to backend server
Supports: Heartbeat, CPU/RAM/Disk, Processes, USB events, Login/Logout

Install: python agent.py install
Start: python agent.py start
Stop: python agent.py stop
"""

import os
import sys
import json
import time
import uuid
import socket
import psutil
import requests
import threading
import subprocess
import logging
import getpass
from pathlib import Path
from datetime import datetime
from collections import deque
import socket as socket_module

try:
    import pythoncom
    import pywintypes
    import win32serviceutil
    import win32service
    import win32event
    import win32evtlog
    import win32timezone
    import servicemanager
    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False
    win32evtlog = None

# ============= CONFIGURATION =============
CONFIG_DIR = Path("C:/ProgramData/SentinelAI")
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_FILE = CONFIG_DIR / "agent.log"
STATE_FILE = CONFIG_DIR / "state.json"

DEFAULT_CONFIG = {
    "server_url": "https://sentinel-ai-fz5u.onrender.com",
    "organization": "Default",
    "heartbeat_interval": 10,  # seconds
    "usb_check_interval": 5,
    "process_check_interval": 30,
    "max_retries": 3,
    "retry_delay": 5,
    "agent_id": "GENERATE_NEW",
    "agent_version": "1.0.0"
}

# ============= LOGGING =============
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============= SYSTEM INFO COLLECTION =============
class SystemMonitor:
    def __init__(self, config):
        self.config = config
        self.last_usb_devices = set()
        self.last_processes = set()
        self.last_event_record = 0
        self.usb_baseline_ready = False
        self.load_state()

    def agent_id(self):
        return self.config.get("agent_id") or "GENERATE_NEW"

    def interactive_username(self):
        """Return the active Windows console/RDP user, or None when nobody is logged in."""
        try:
            result = subprocess.run(
                "query user",
                capture_output=True,
                text=True,
                timeout=3,
                shell=True
            )
            for line in result.stdout.splitlines()[1:]:
                clean = line.strip().lstrip(">")
                if " Active " in f" {clean} ":
                    username = clean.split()[0]
                    if username:
                        return username
        except Exception:
            pass
        return None

    def current_username(self):
        active_user = self.interactive_username()
        if active_user:
            return active_user
        for key in ("USERNAME", "USER", "USERDOMAIN"):
            value = os.getenv(key)
            if value:
                if key == "USERDOMAIN" and os.getenv("USERNAME"):
                    return f"{value}\\{os.getenv('USERNAME')}"
                return value
        try:
            return getpass.getuser()
        except Exception:
            return "Unknown"

    def load_state(self):
        """Load last known state"""
        try:
            if STATE_FILE.exists():
                with open(STATE_FILE, 'r') as f:
                    state = json.load(f)
                    self.last_usb_devices = set(state.get('usb_devices', []))
                    self.last_processes = set(state.get('processes', []))
                    self.last_event_record = int(state.get('last_event_record', 0) or 0)
                    self.usb_baseline_ready = bool(state.get('usb_baseline_ready', False))
        except Exception as e:
            logger.error(f"Error loading state: {e}")

    def save_state(self):
        """Save current state"""
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump({
                    'usb_devices': list(self.last_usb_devices),
                    'processes': list(self.last_processes),
                    'last_event_record': self.last_event_record,
                    'usb_baseline_ready': self.usb_baseline_ready
                }, f)
        except Exception as e:
            logger.error(f"Error saving state: {e}")

    def get_system_info(self):
        """Collect system information"""
        try:
            # CPU info
            cpu_count = psutil.cpu_count(logical=True)
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory info
            memory = psutil.virtual_memory()
            ram_total = memory.total / (1024**3)  # GB
            ram_available = memory.available / (1024**3)  # GB
            ram_percent = memory.percent

            # Disk info
            disk = psutil.disk_usage('C:')
            disk_percent = disk.percent

            # System info
            hostname = socket_module.gethostname()
            mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                                    for elements in range(0, 2*6, 2)][::-1])
            
            # Get IP address
            try:
                s = socket_module.socket(socket_module.AF_INET, socket_module.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip_address = s.getsockname()[0]
                s.close()
            except:
                ip_address = "127.0.0.1"

            # OS info
            import platform
            os_name = platform.system()
            os_version = platform.release()
            boot_time = datetime.fromtimestamp(psutil.boot_time()).isoformat()

            return {
                "device_uuid": self.agent_id(),
                "agent_id": self.agent_id(),
                "hostname": hostname,
                "username": self.current_username(),
                "ip_address": ip_address,
                "mac_address": mac_address,
                "operating_system": os_name,
                "os_version": os_version,
                "cpu_cores": cpu_count,
                "cpu_usage": cpu_percent,
                "total_ram": ram_total,
                "available_ram": ram_available,
                "ram_usage": ram_percent,
                "disk_usage": disk_percent,
                "boot_time": boot_time,
                "last_seen": datetime.utcnow().isoformat(),
                "status": "Online",
                "agent_version": self.config.get("agent_version", "1.0.0")
            }
        except Exception as e:
            logger.error(f"Error collecting system info: {e}")
            return None

    def get_processes(self):
        """Get running processes"""
        try:
            hostname = socket_module.gethostname()
            agent_id = self.agent_id()
            fallback_user = self.current_username()
            processes = []

            # Prime per-process CPU counters. Without this first pass, psutil returns 0.0
            # for most processes because it has no previous sample to compare against.
            primed = []
            for proc in psutil.process_iter(['pid']):
                try:
                    proc.cpu_percent(None)
                    primed.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            time.sleep(0.25)

            for proc in primed:
                try:
                    pinfo = proc.as_dict(attrs=['pid', 'name', 'memory_percent', 'username'])
                    name = pinfo.get('name') or f"pid-{pinfo.get('pid')}"
                    username = pinfo.get('username') or fallback_user
                    cpu_percent = proc.cpu_percent(None)
                    memory_percent = pinfo.get('memory_percent') or 0
                    processes.append({
                        "agent_id": agent_id,
                        "hostname": hostname,
                        "pid": pinfo.get('pid') or 0,
                        "name": name,
                        "process_name": name,
                        "cpu_percent": round(float(cpu_percent or 0), 2),
                        "memory_percent": round(float(memory_percent or 0), 3),
                        "username": username,
                        "user": username
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            processes.sort(key=lambda item: (item["cpu_percent"], item["memory_percent"]), reverse=True)
            return {
                "agent_id": agent_id,
                "hostname": hostname,
                "processes": processes[:300]
            }
        except Exception as e:
            logger.error(f"Error collecting processes: {e}")
            return None

    def get_usb_events(self):
        """Detect USB device changes"""
        try:
            # Get current USB devices
            current_devices = set()
            try:
                result = subprocess.run(
                    ["wmic", "logicaldisk", "get", "name"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                for line in result.stdout.split('\n'):
                    if ':' in line:
                        current_devices.add(line.strip())
            except:
                pass

            events = []

            if not self.usb_baseline_ready:
                self.last_usb_devices = current_devices
                self.usb_baseline_ready = True
                self.save_state()
                logger.info(f"USB baseline initialized with {len(current_devices)} device(s)")
                return []
            
            # Check for inserted devices
            inserted = current_devices - self.last_usb_devices
            for device in inserted:
                events.append({
                    "agent_id": self.agent_id(),
                    "action": "Inserted",
                    "device": device,
                    "hostname": socket_module.gethostname(),
                    "username": self.current_username()
                })
                logger.info(f"USB device inserted: {device}")

            # Check for removed devices
            removed = self.last_usb_devices - current_devices
            for device in removed:
                events.append({
                    "agent_id": self.agent_id(),
                    "action": "Removed",
                    "device": device,
                    "hostname": socket_module.gethostname(),
                    "username": self.current_username()
                })
                logger.info(f"USB device removed: {device}")

            self.last_usb_devices = current_devices
            return events

        except Exception as e:
            logger.error(f"Error detecting USB events: {e}")
            return []

# ============= API CLIENT =============
class SentinelAPIClient:
    def __init__(self, config):
        self.config = config
        self.server_url = str(config['server_url']).rstrip("/")
        self.config['server_url'] = self.server_url
        self.session = requests.Session()
        self.retry_count = 0

    def send_heartbeat(self, system_info):
        """Send heartbeat to server"""
        try:
            response = self.session.post(
                f"{self.server_url}/heartbeat",
                json=system_info,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                server_agent_id = data.get("agent_id") or data.get("device_id")
                if server_agent_id and server_agent_id != self.config.get("agent_id"):
                    self.config["agent_id"] = server_agent_id
                    save_config(self.config)
                logger.info(f"Heartbeat sent successfully")
                self.retry_count = 0
                return True
            else:
                logger.warning(f"Heartbeat failed: {response.status_code} {response.text[:300]}")
                self.retry_count += 1
                return False
        except requests.exceptions.RequestException as e:
            logger.warning(f"Heartbeat error: {e}")
            self.retry_count += 1
            return False

    def send_processes(self, processes):
        """Send process list to server"""
        try:
            response = self.session.post(
                f"{self.server_url}/processes",
                json=processes,
                timeout=10
            )
            if response.status_code == 200:
                logger.info(f"Sent {len(processes['processes'])} processes")
                return True
            return False
        except Exception as e:
            logger.warning(f"Process send error: {e}")
            return False

    def send_usb_event(self, event):
        """Send USB event to server"""
        try:
            response = self.session.post(
                f"{self.server_url}/usb-events",
                json=event,
                timeout=10
            )
            if response.status_code == 200:
                logger.info(f"USB event reported: {event['action']}")
                return True
            return False
        except Exception as e:
            logger.warning(f"USB event send error: {e}")
            return False

    def send_session_event(self, event):
        """Send Windows login/logout event to server"""
        try:
            response = self.session.post(
                f"{self.server_url}/endpoint-sessions",
                json=event,
                timeout=10
            )
            if response.status_code == 200:
                logger.info(f"Session event reported: {event['action']} {event['username']}")
                return True
            logger.warning(f"Session event failed: {response.status_code}")
            return False
        except Exception as e:
            logger.warning(f"Session event send error: {e}")
            return False

    def is_server_available(self):
        """Check if server is available"""
        try:
            response = self.session.get(
                f"{self.server_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

# ============= CONFIGURATION MANAGEMENT =============
def load_config():
    """Load or create configuration"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                changed = False
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                        changed = True
                if not config.get("agent_id"):
                    config["agent_id"] = "GENERATE_NEW"
                    changed = True
                if changed:
                    save_config(config)
                return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
    
    # Create default config
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG

def save_config(config):
    """Save configuration"""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Config saved to {CONFIG_FILE}")
    except Exception as e:
        logger.error(f"Error saving config: {e}")

# ============= AGENT MAIN LOOP =============
class AgentService:
    def __init__(self):
        self.config = load_config()
        self.monitor = SystemMonitor(self.config)
        self.client = SentinelAPIClient(self.config)
        self.running = True
        self.active_username = None

    def run(self):
        """Main agent loop"""
        logger.info("=" * 60)
        logger.info("SENTINEL AI ENDPOINT AGENT STARTED")
        logger.info(f"Server: {self.config['server_url']}")
        logger.info(f"Agent ID: {self.config['agent_id']}")
        logger.info("=" * 60)

        # Start monitoring threads
        heartbeat_thread = threading.Thread(target=self.heartbeat_loop, daemon=True)
        process_thread = threading.Thread(target=self.process_loop, daemon=True)
        usb_thread = threading.Thread(target=self.usb_loop, daemon=True)
        session_thread = threading.Thread(
            target=self.event_log_loop if PYWIN32_AVAILABLE else self.session_loop,
            daemon=True
        )

        heartbeat_thread.start()
        process_thread.start()
        usb_thread.start()
        session_thread.start()

        # Keep agent running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Agent stopped by user")
            self.send_logout_event()
            self.running = False

    def heartbeat_loop(self):
        """Send heartbeat at intervals"""
        while self.running:
            try:
                if self.client.is_server_available():
                    system_info = self.monitor.get_system_info()
                    if system_info:
                        self.client.send_heartbeat(system_info)
                else:
                    logger.warning("Server unavailable, retrying...")
                
                time.sleep(self.config['heartbeat_interval'])
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
                time.sleep(self.config['retry_delay'])

    def process_loop(self):
        """Send processes at intervals"""
        while self.running:
            try:
                if self.client.is_server_available():
                    processes = self.monitor.get_processes()
                    if processes:
                        self.client.send_processes(processes)
                
                time.sleep(self.config['process_check_interval'])
            except Exception as e:
                logger.error(f"Process loop error: {e}")
                time.sleep(self.config['retry_delay'])

    def usb_loop(self):
        """Monitor USB events"""
        while self.running:
            try:
                events = self.monitor.get_usb_events()
                for event in events:
                    if self.client.is_server_available():
                        self.client.send_usb_event(event)
                
                self.monitor.save_state()
                time.sleep(self.config['usb_check_interval'])
            except Exception as e:
                logger.error(f"USB loop error: {e}")
                time.sleep(self.config['retry_delay'])

    def _session_payload(self, action, username=None):
        system_info = self.monitor.get_system_info() or {}
        selected_user = username or self.monitor.interactive_username() or self.monitor.current_username()
        return {
            "agent_id": self.config.get("agent_id", "GENERATE_NEW"),
            "hostname": system_info.get("hostname") or socket_module.gethostname(),
            "username": selected_user,
            "ip_address": system_info.get("ip_address", "127.0.0.1"),
            "action": action,
            "event_time": datetime.utcnow().isoformat()
        }

    def send_logout_event(self):
        if self.active_username and self.client.is_server_available():
            self.client.send_session_event(self._session_payload("logout", self.active_username))

    def _event_time_iso(self, event):
        try:
            value = event.TimeGenerated
            if hasattr(value, "timestamp"):
                return datetime.utcfromtimestamp(value.timestamp()).isoformat()
            return datetime.utcnow().isoformat()
        except Exception:
            return datetime.utcnow().isoformat()

    def _valid_windows_user(self, username):
        if not username:
            return False
        blocked = {"-", "SYSTEM", "LOCAL SERVICE", "NETWORK SERVICE", "ANONYMOUS LOGON"}
        return username.upper() not in blocked and not username.endswith("$")

    def _session_event_from_windows_event(self, event):
        event_id = event.EventID & 0xFFFF
        strings = list(event.StringInserts or [])

        if event_id == 4624:
            logon_type = strings[8] if len(strings) > 8 else ""
            if str(logon_type) not in {"2", "7", "10", "11"}:
                return None
            username = strings[5] if len(strings) > 5 else ""
            domain = strings[6] if len(strings) > 6 else ""
            action = "login"
        elif event_id in {4634, 4647}:
            logon_type = strings[4] if len(strings) > 4 else ""
            if str(logon_type) and str(logon_type) not in {"2", "7", "10", "11"}:
                return None
            username = strings[1] if len(strings) > 1 else ""
            domain = strings[2] if len(strings) > 2 else ""
            action = "logout"
        else:
            return None

        if not self._valid_windows_user(username):
            return None

        display_user = f"{domain}\\{username}" if domain and domain not in {"-", "."} else username
        system_info = self.monitor.get_system_info() or {}
        return {
            "agent_id": self.config.get("agent_id", "GENERATE_NEW"),
            "hostname": system_info.get("hostname") or socket_module.gethostname(),
            "username": display_user,
            "ip_address": system_info.get("ip_address", "127.0.0.1"),
            "action": action,
            "event_time": self._event_time_iso(event)
        }

    def event_log_loop(self):
        """Poll Windows Security log for login/logout events."""
        server = "localhost"
        log_type = "Security"
        flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEEK_READ

        while self.running:
            try:
                handle = win32evtlog.OpenEventLog(server, log_type)
                try:
                    oldest = win32evtlog.GetOldestEventLogRecord(handle)
                    total = win32evtlog.GetNumberOfEventLogRecords(handle)
                    newest = oldest + total - 1

                    if not self.monitor.last_event_record:
                        self.monitor.last_event_record = newest
                        self.monitor.save_state()
                        current_user = self.monitor.interactive_username()
                        if current_user and self.client.is_server_available():
                            self.active_username = current_user
                            self.client.send_session_event(self._session_payload("login", current_user))
                        time.sleep(15)
                        continue

                    start_record = max(self.monitor.last_event_record + 1, oldest)
                    events = []
                    while start_record <= newest:
                        batch = win32evtlog.ReadEventLog(handle, flags, start_record)
                        if not batch:
                            break
                        events.extend(batch)
                        start_record = batch[-1].RecordNumber + 1

                    for event in events:
                        self.monitor.last_event_record = max(self.monitor.last_event_record, event.RecordNumber)
                        payload = self._session_event_from_windows_event(event)
                        if payload and self.client.is_server_available():
                            self.client.send_session_event(payload)
                            if payload["action"] == "login":
                                self.active_username = payload["username"]
                            elif payload["action"] == "logout" and payload["username"] == self.active_username:
                                self.active_username = None

                    self.monitor.save_state()
                finally:
                    win32evtlog.CloseEventLog(handle)
                time.sleep(15)
            except Exception as e:
                logger.error(f"Windows event log session loop error: {e}")
                # Fall back to current-user polling if Security log access is unavailable.
                try:
                    self.session_loop()
                except Exception:
                    time.sleep(self.config['retry_delay'])
                return

    def session_loop(self):
        """Track Windows user sessions for SOC login/logout history."""
        while self.running:
            try:
                current_username = self.monitor.interactive_username()
                if current_username != self.active_username:
                    if self.active_username and self.client.is_server_available():
                        self.client.send_session_event(self._session_payload("logout", self.active_username))
                    self.active_username = current_username
                    if self.active_username and self.client.is_server_available():
                        self.client.send_session_event(self._session_payload("login", self.active_username))
                time.sleep(15)
            except Exception as e:
                logger.error(f"Session loop error: {e}")
                time.sleep(self.config['retry_delay'])


def register_once():
    """Send one heartbeat now and persist the backend-assigned AGT ID."""
    config = load_config()
    client = SentinelAPIClient(config)
    monitor = SystemMonitor(config)

    print("SENTINEL AI AGENT REGISTRATION")
    print(f"Config: {CONFIG_FILE}")
    print(f"Server: {client.server_url}")
    print(f"Agent ID before: {config.get('agent_id')}")

    if not client.is_server_available():
        print(f"[ERROR] Backend is not reachable: {client.server_url}/health")
        print("Fix server_url in C:\\ProgramData\\SentinelAI\\config.json and confirm firewall/network access.")
        return 2

    system_info = monitor.get_system_info()
    if not system_info:
        print("[ERROR] Could not collect system information.")
        return 3

    if not client.send_heartbeat(system_info):
        print("[ERROR] Heartbeat registration failed. Check C:\\ProgramData\\SentinelAI\\agent.log")
        return 4

    print(f"[OK] Registered/updated endpoint: {config.get('agent_id')}")
    return 0


def run_diagnostics():
    """Print the agent's practical registration state."""
    config = load_config()
    client = SentinelAPIClient(config)

    print("SENTINEL AI AGENT DIAGNOSTICS")
    print(f"Config file: {CONFIG_FILE}")
    print(f"Log file: {LOG_FILE}")
    print(f"Server URL: {client.server_url}")
    print(f"Agent ID: {config.get('agent_id')}")
    print(f"Backend health: {'OK' if client.is_server_available() else 'FAILED'}")
    print()
    return register_once()


# ============= WINDOWS SERVICE WRAPPER =============
if PYWIN32_AVAILABLE:
    class SentinelWindowsService(win32serviceutil.ServiceFramework):
        _svc_name_ = "SentinelAIAgent"
        _svc_display_name_ = "Sentinel AI Endpoint Agent"
        _svc_description_ = (
            "Collects endpoint heartbeat, process, USB, and login/logout telemetry."
        )

        def __init__(self, args):
            super().__init__(args)
            self.stop_event = win32event.CreateEvent(None, 0, 0, None)
            self.agent = AgentService()

        def SvcStop(self):
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

            try:
                self.agent.running = False
                self.agent.send_logout_event()
            except Exception:
                logger.exception("Error while stopping service")

            win32event.SetEvent(self.stop_event)

        def SvcDoRun(self):
            try:
                logger.info("Sentinel Windows Service started")

                servicemanager.LogInfoMsg(
                    "Sentinel AI Endpoint Agent service starting"
                )

                self.ReportServiceStatus(win32service.SERVICE_RUNNING)

                worker = threading.Thread(
                    target=self.agent.run,
                    daemon=True
                )
                worker.start()

                while self.agent.running:
                    rc = win32event.WaitForSingleObject(self.stop_event, 1000)
                    if rc == win32event.WAIT_OBJECT_0:
                        break

                worker.join(timeout=5)

            except Exception:
                logger.exception("SERVICE CRASHED")
                raise


# ============= ENTRY POINT =============
if __name__ == "__main__":
    service_commands = {"install", "update", "remove", "start", "stop", "restart", "debug"}
    agent_command = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    if agent_command == "register":
        sys.exit(register_once())
    if agent_command == "diagnose":
        sys.exit(run_diagnostics())
    if agent_command in service_commands:
        if not PYWIN32_AVAILABLE:
            print("pywin32 is required for Windows service commands. Install with: pip install pywin32")
            sys.exit(1)
        win32serviceutil.HandleCommandLine(SentinelWindowsService)
    elif PYWIN32_AVAILABLE and getattr(sys, "frozen", False):
        try:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(SentinelWindowsService)
            servicemanager.StartServiceCtrlDispatcher()
        except Exception as exc:
            logger.warning(f"Service dispatcher unavailable, running console agent: {exc}")
            agent = AgentService()
            agent.run()
    else:
        agent = AgentService()
        agent.run()
