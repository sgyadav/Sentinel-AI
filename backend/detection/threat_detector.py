"""Real-time threat detection engine"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)


class ThreatDetector:
    """Real-time threat detection engine"""
    
    # Attack signatures and patterns
    ATTACK_SIGNATURES = {
        "brute_force": {
            "pattern": "multiple_failed_logins",
            "threshold": 5,
            "window_seconds": 300,
            "severity": "High",
            "mitre_tactic": "Credential Access",
            "mitre_technique": "T1110.001"
        },
        "malware": {
            "pattern": "suspicious_process_execution",
            "threshold": 1,
            "window_seconds": 60,
            "severity": "Critical",
            "mitre_tactic": "Execution",
            "mitre_technique": "T1204.002"
        },
        "ransomware": {
            "pattern": "high_disk_activity",
            "threshold": 1000,  # operations/minute
            "window_seconds": 60,
            "severity": "Critical",
            "mitre_tactic": "Impact",
            "mitre_technique": "T1486"
        },
        "privilege_escalation": {
            "pattern": "process_creation_as_system",
            "threshold": 1,
            "window_seconds": 60,
            "severity": "High",
            "mitre_tactic": "Privilege Escalation",
            "mitre_technique": "T1548.004"
        },
        "data_exfiltration": {
            "pattern": "large_data_transfer",
            "threshold": 1024 * 1024 * 100,  # 100 MB
            "window_seconds": 300,
            "severity": "High",
            "mitre_tactic": "Exfiltration",
            "mitre_technique": "T1041"
        },
        "port_scan": {
            "pattern": "multiple_connection_attempts",
            "threshold": 50,
            "window_seconds": 60,
            "severity": "Medium",
            "mitre_tactic": "Discovery",
            "mitre_technique": "T1046"
        },
        "usb_attack": {
            "pattern": "usb_device_insertion",
            "threshold": 1,
            "window_seconds": 1,
            "severity": "High",
            "mitre_tactic": "Initial Access",
            "mitre_technique": "T1091"
        },
        "dns_tunneling": {
            "pattern": "high_dns_query_volume",
            "threshold": 100,
            "window_seconds": 60,
            "severity": "Medium",
            "mitre_tactic": "Command and Control",
            "mitre_technique": "T1071.004"
        }
    }
    
    # Suspicious process names
    SUSPICIOUS_PROCESSES = {
        "psexec": "Process Execution Tool",
        "mimikatz": "Credential Dumper",
        "powercat": "Reverse Shell",
        "ncat": "Netcat Clone",
        "backdoor": "Backdoor Process",
        "cmd.exe": "Command Shell (suspicious if from user profile)",
        "powershell.exe": "PowerShell (monitor for scripts)"
    }
    
    # Suspicious file paths
    SUSPICIOUS_PATHS = {
        "%AppData%": "User AppData folder",
        "%Temp%": "Temporary folder",
        "C:\\Temp": "Root temp folder",
        "C:\\ProgramData": "Program Data folder"
    }
    
    def __init__(self):
        """Initialize threat detector"""
        self.event_history = defaultdict(list)
        self.threat_cache = {}
        self.logger = logging.getLogger(__name__)
    
    def analyze_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze a security event
        
        Args:
            event: Security event data
            
        Returns:
            Threat analysis result or None if not a threat
        """
        try:
            event_type = event.get("event_type", "").lower()
            hostname = event.get("hostname", "")
            
            # Rule-based detection
            if "failed login" in event_type:
                return self._detect_brute_force(event)
            
            elif "process" in event_type:
                return self._detect_malware(event)
            
            elif "disk" in event_type:
                return self._detect_ransomware(event)
            
            elif "privilege" in event_type:
                return self._detect_privilege_escalation(event)
            
            elif "network" in event_type:
                return self._detect_data_exfiltration(event)
            
            elif "connection" in event_type:
                return self._detect_port_scan(event)
            
            elif "usb" in event_type:
                return self._detect_usb_attack(event)
            
            elif "dns" in event_type:
                return self._detect_dns_tunneling(event)
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing event: {e}")
            return None
    
    def _detect_brute_force(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Detect brute force attacks"""
        hostname = event.get("hostname", "")
        source_ip = event.get("source_ip", "")
        
        sig = self.ATTACK_SIGNATURES["brute_force"]
        
        return {
            "attack_type": "Brute Force Attack",
            "risk_score": 75,
            "confidence": 0.85,
            "description": f"Multiple failed login attempts detected from {source_ip}",
            "mitre_tactic": sig["mitre_tactic"],
            "mitre_technique": sig["mitre_technique"],
            "severity": "High",
            "recommended_action": "Review login attempts, enable MFA, implement account lockout policy"
        }
    
    def _detect_malware(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Detect malware execution"""
        process_name = event.get("process_name", "").lower()
        
        sig = self.ATTACK_SIGNATURES["malware"]
        
        risk_score = 90
        for suspicious_proc, desc in self.SUSPICIOUS_PROCESSES.items():
            if suspicious_proc in process_name:
                risk_score = 95
                break
        
        return {
            "attack_type": "Malware Detected",
            "risk_score": risk_score,
            "confidence": 0.90,
            "description": f"Suspicious process execution detected: {process_name}",
            "mitre_tactic": sig["mitre_tactic"],
            "mitre_technique": sig["mitre_technique"],
            "severity": "Critical",
            "recommended_action": "Kill process, isolate device, run full antivirus scan, analyze with sandboxing"
        }
    
    def _detect_ransomware(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Detect ransomware activity"""
        disk_activity = event.get("disk_activity", 0)
        
        sig = self.ATTACK_SIGNATURES["ransomware"]
        
        return {
            "attack_type": "Ransomware Activity",
            "risk_score": 98,
            "confidence": 0.95,
            "description": f"Abnormal disk write activity detected: {disk_activity} operations/min",
            "mitre_tactic": sig["mitre_tactic"],
            "mitre_technique": sig["mitre_technique"],
            "severity": "Critical",
            "recommended_action": "Immediately isolate device, preserve logs, restore from clean backup, notify incident response"
        }
    
    def _detect_privilege_escalation(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Detect privilege escalation attempts"""
        sig = self.ATTACK_SIGNATURES["privilege_escalation"]
        
        return {
            "attack_type": "Privilege Escalation Attempt",
            "risk_score": 80,
            "confidence": 0.88,
            "description": "Unauthorized privilege escalation attempt detected",
            "mitre_tactic": sig["mitre_tactic"],
            "mitre_technique": sig["mitre_technique"],
            "severity": "High",
            "recommended_action": "Verify user authorization, review UAC settings, monitor system activities"
        }
    
    def _detect_data_exfiltration(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Detect data exfiltration patterns"""
        data_volume = event.get("data_volume", 0)
        
        sig = self.ATTACK_SIGNATURES["data_exfiltration"]
        
        return {
            "attack_type": "Data Exfiltration",
            "risk_score": 85,
            "confidence": 0.82,
            "description": f"Unusual data transfer detected: {data_volume / (1024*1024):.2f} MB",
            "mitre_tactic": sig["mitre_tactic"],
            "mitre_technique": sig["mitre_technique"],
            "severity": "High",
            "recommended_action": "Block destination, review network traffic, check file access logs, notify DLP team"
        }
    
    def _detect_port_scan(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Detect port scanning activity"""
        connection_count = event.get("connection_count", 0)
        
        sig = self.ATTACK_SIGNATURES["port_scan"]
        
        return {
            "attack_type": "Port Scanning Activity",
            "risk_score": 65,
            "confidence": 0.75,
            "description": f"Multiple connection attempts detected: {connection_count} connections",
            "mitre_tactic": sig["mitre_tactic"],
            "mitre_technique": sig["mitre_technique"],
            "severity": "Medium",
            "recommended_action": "Monitor for follow-up attacks, review outbound firewall rules, investigate source"
        }
    
    def _detect_usb_attack(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Detect USB-based attacks"""
        sig = self.ATTACK_SIGNATURES["usb_attack"]
        
        return {
            "attack_type": "USB Attack Vector",
            "risk_score": 80,
            "confidence": 0.90,
            "description": "Unauthorized USB device connected",
            "mitre_tactic": sig["mitre_tactic"],
            "mitre_technique": sig["mitre_technique"],
            "severity": "High",
            "recommended_action": "Review USB device connection, scan for malware, enforce USB policies"
        }
    
    def _detect_dns_tunneling(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Detect DNS tunneling attempts"""
        dns_queries = event.get("dns_query_count", 0)
        
        sig = self.ATTACK_SIGNATURES["dns_tunneling"]
        
        return {
            "attack_type": "DNS Tunneling Detected",
            "risk_score": 70,
            "confidence": 0.78,
            "description": f"Abnormal DNS activity: {dns_queries} queries in short period",
            "mitre_tactic": sig["mitre_tactic"],
            "mitre_technique": sig["mitre_technique"],
            "severity": "Medium",
            "recommended_action": "Block DNS tunnel domains, review DNS logs, check for C&C communications"
        }
    
    def get_threat_intelligence(self, attack_type: str) -> Dict[str, Any]:
        """Get threat intelligence for attack type"""
        intelligence = {
            "Brute Force Attack": {
                "cis_controls": ["5.2", "6.1"],
                "nist_controls": ["AC-2", "AC-7"],
                "recommended_tools": ["Fail2Ban", "DenyHosts"]
            },
            "Malware Detected": {
                "cis_controls": ["2.1", "7.1"],
                "nist_controls": ["SI-3", "SI-4"],
                "recommended_tools": ["Defender", "Sophos", "CrowdStrike"]
            },
            "Ransomware Activity": {
                "cis_controls": ["3.10", "5.2"],
                "nist_controls": ["CP-10", "SI-4"],
                "recommended_tools": ["CrowdStrike", "SentinelOne", "Carbon Black"]
            }
        }
        
        return intelligence.get(attack_type, {})


class RealtimeAnalyzer:
    """Real-time stream analyzer"""
    
    def __init__(self):
        """Initialize realtime analyzer"""
        self.detector = ThreatDetector()
        self.event_queue = asyncio.Queue()
        self.active_threats = {}
    
    async def process_event_stream(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process event from stream"""
        try:
            threat = self.detector.analyze_event(event)
            
            if threat:
                threat["timestamp"] = datetime.utcnow().isoformat()
                threat["hostname"] = event.get("hostname")
                threat["source_user"] = event.get("source_user")
                
                return threat
            
            return None
            
        except Exception as e:
            logger.error(f"Stream processing error: {e}")
            return None
