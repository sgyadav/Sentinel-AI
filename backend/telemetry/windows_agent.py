"""Windows Endpoint Agent for real-time telemetry collection"""

import os
import json
import socket
import logging
import requests
import psutil
from datetime import datetime
from typing import Dict, List, Any
import time
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class WindowsEndpointAgent:
    """Collects telemetry from Windows endpoints"""
    
    def __init__(self, server_url: str = "http://localhost:8000", hostname: str = None):
        """
        Initialize Windows Endpoint Agent
        
        Args:
            server_url: SENTINEL AI server URL
            hostname: Device hostname (auto-detected if None)
        """
        self.server_url = server_url.rstrip("/")
        self.hostname = hostname or socket.gethostname()
        self.ip_address = self._get_ip_address()
        self.mac_address = self._get_mac_address()
        
    def _get_ip_address(self) -> str:
        """Get primary IP address"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            sock.close()
            return ip
        except:
            return "127.0.0.1"
    
    def _get_mac_address(self) -> str:
        """Get MAC address"""
        try:
            return ":".join(["{:02x}".format((uuid.getnode() >> ele) & 0xff)
                           for ele in range(0, 8*6, 8)][::-1])
        except:
            return "00:00:00:00:00:00"
    
    def collect_system_info(self) -> Dict[str, Any]:
        """Collect system information"""
        try:
            return {
                "hostname": self.hostname,
                "ip_address": self.ip_address,
                "mac_address": self.mac_address,
                "os": os.name,
                "platform": self._get_os_version(),
                "cpu_cores": psutil.cpu_count(),
                "total_ram": psutil.virtual_memory().total // (1024**2),  # MB
                "total_disk": psutil.disk_usage("/").total // (1024**3),  # GB
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to collect system info: {e}")
            return {}
    
    def _get_os_version(self) -> str:
        """Get Windows version"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-WmiObject Win32_OperatingSystem | Select-Object -ExpandProperty Caption"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except:
            return "Windows"
    
    def collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect real-time performance metrics"""
        try:
            vm = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu_usage": psutil.cpu_percent(interval=1),
                "ram_usage": vm.percent,
                "ram_available_mb": vm.available // (1024**2),
                "disk_usage": disk.percent,
                "disk_free_gb": disk.free // (1024**3),
                "disk_read_count": psutil.disk_io_counters().read_count if psutil.disk_io_counters() else 0,
                "disk_write_count": psutil.disk_io_counters().write_count if psutil.disk_io_counters() else 0,
                "network_bytes_sent": psutil.net_io_counters().bytes_sent,
                "network_bytes_received": psutil.net_io_counters().bytes_recv,
                "process_count": len(psutil.pids()),
                "uptime_seconds": int(time.time() - psutil.boot_time())
            }
        except Exception as e:
            logger.error(f"Failed to collect performance metrics: {e}")
            return {}
    
    def collect_processes(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Collect running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        "pid": proc.pid,
                        "name": proc.name(),
                        "username": proc.info.get('username', 'N/A'),
                        "cpu_percent": proc.info.get('cpu_percent', 0),
                        "memory_mb": proc.info.get('memory_percent', 0)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage and return top processes
            return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
        except Exception as e:
            logger.error(f"Failed to collect processes: {e}")
            return []
    
    def collect_network_connections(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Collect active network connections"""
        try:
            connections = []
            for conn in psutil.net_connections():
                try:
                    connections.append({
                        "local_ip": conn.laddr.ip,
                        "local_port": conn.laddr.port,
                        "remote_ip": conn.raddr.ip if conn.raddr else None,
                        "remote_port": conn.raddr.port if conn.raddr else None,
                        "status": conn.status,
                        "type": conn.type
                    })
                except Exception:
                    continue
            
            return connections[:limit]
        except Exception as e:
            logger.error(f"Failed to collect network connections: {e}")
            return []
    
    def check_security_status(self) -> Dict[str, Any]:
        """Check security status (Windows Defender, Firewall, etc.)"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", """
                    $defender = Get-MpPreference
                    @{
                        'antivirus_enabled' = $defender.DisableRealtimeMonitoring -eq $false
                        'firewall_enabled' = $(Get-NetFirewallProfile -Profile Domain,Public,Private | Select-Object -ExpandProperty Enabled -First 1)
                    } | ConvertTo-Json
                """],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            return {"antivirus_enabled": True, "firewall_enabled": True}
        except Exception as e:
            logger.error(f"Failed to check security status: {e}")
            return {"antivirus_enabled": True, "firewall_enabled": True}
    
    def collect_telemetry(self) -> Dict[str, Any]:
        """Collect all telemetry data"""
        try:
            telemetry = {
                "agent_version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "system_info": self.collect_system_info(),
                "performance": self.collect_performance_metrics(),
                "processes": self.collect_processes(),
                "network_connections": self.collect_network_connections(),
                "security_status": self.check_security_status()
            }
            
            return telemetry
        except Exception as e:
            logger.error(f"Failed to collect telemetry: {e}")
            return {}
    
    def send_telemetry(self, telemetry: Dict[str, Any] = None) -> bool:
        """Send telemetry to SENTINEL server"""
        try:
            if not telemetry:
                telemetry = self.collect_telemetry()
            
            response = requests.post(
                f"{self.server_url}/api/agent/telemetry",
                json=telemetry,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Telemetry sent successfully for {self.hostname}")
                return True
            else:
                logger.error(f"Failed to send telemetry: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Telemetry transmission error: {e}")
            return False
    
    def heartbeat(self) -> bool:
        """Send heartbeat to server"""
        try:
            response = requests.post(
                f"{self.server_url}/api/agent/heartbeat",
                json={
                    "hostname": self.hostname,
                    "ip_address": self.ip_address,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "Online"
                },
                timeout=5
            )
            
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
            return False
    
    def start_continuous_monitoring(self, interval_seconds: int = 60):
        """Start continuous telemetry collection"""
        logger.info(f"Starting Windows Endpoint Agent on {self.hostname}")
        
        while True:
            try:
                # Send telemetry
                self.send_telemetry()
                
                # Send heartbeat
                self.heartbeat()
                
                # Wait before next collection
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("Windows Endpoint Agent stopped")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(interval_seconds)


# ===========================
# Main Entry Point
# ===========================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Initialize agent
    server_url = os.getenv("SENTINEL_SERVER_URL", "http://localhost:8000")
    agent = WindowsEndpointAgent(server_url=server_url)
    
    # Start monitoring
    agent.start_continuous_monitoring(interval_seconds=60)
