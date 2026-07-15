"""
SENTINEL AI - PRODUCTION TESTING SUITE
Complete workflow testing for v1.0 release
"""

import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def add_pass(self, test_name, message=""):
        self.passed += 1
        self.tests.append((True, test_name, message))
        print(f"{GREEN}[PASS]{RESET}: {test_name}")
        if message:
            print(f"  {message}")

    def add_fail(self, test_name, message=""):
        self.failed += 1
        self.tests.append((False, test_name, message))
        print(f"{RED}[FAIL]{RESET}: {test_name}")
        if message:
            print(f"  {message}")

    def summary(self):
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        print(f"\n{'='*60}")
        print(f"TOTAL: {total} | {GREEN}PASSED: {self.passed}{RESET} | {RED}FAILED: {self.failed}{RESET}")
        print(f"SUCCESS RATE: {percentage:.1f}%")
        print(f"{'='*60}\n")
        return self.failed == 0

# ============= TEST SUITE =============
class ProductionTests:
    def __init__(self):
        self.results = TestResults()
        self.token = None
        self.user = None

    def test_authentication(self):
        print(f"\n{BLUE}=== PHASE: AUTHENTICATION ==={RESET}\n")

        # Login
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": "admin", "password": "Admin1234"}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data['access_token']
                self.user = data['user']
                self.results.add_pass("Login works", f"User: {self.user['username']}")
            else:
                self.results.add_fail("Login works", f"Status: {response.status_code}")
                return
        except Exception as e:
            self.results.add_fail("Login works", str(e))
            return

        # Wrong password
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": "admin", "password": "wrongpassword"}
            )
            if response.status_code == 401:
                self.results.add_pass("Wrong password rejected")
            else:
                self.results.add_fail("Wrong password rejected", f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.results.add_fail("Wrong password rejected", str(e))

    def test_employees(self):
        print(f"\n{BLUE}=== PHASE: EMPLOYEES ==={RESET}\n")

        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}

        # Add employee
        emp_data = {
            "employee_id": "EMP-001",
            "name": "John Doe",
            "email": "john@company.com",
            "phone": "555-1234",
            "department": "IT Security",
            "designation": "Security Analyst"
        }
        try:
            response = requests.post(f"{BASE_URL}/employees", json=emp_data, headers=headers)
            if response.status_code == 200:
                self.results.add_pass("Add employee works", "EMP-001 created")
            else:
                self.results.add_fail("Add employee works", f"Status: {response.status_code}")
        except Exception as e:
            self.results.add_fail("Add employee works", str(e))

        # Get employees
        try:
            response = requests.get(f"{BASE_URL}/employees", headers=headers)
            if response.status_code == 200:
                employees = response.json()['employees']
                if any(e['employee_id'] == 'EMP-001' for e in employees):
                    self.results.add_pass("Get employees works", f"Found {len(employees)} employees")
                else:
                    self.results.add_fail("Get employees works", "EMP-001 not found")
            else:
                self.results.add_fail("Get employees works", f"Status: {response.status_code}")
        except Exception as e:
            self.results.add_fail("Get employees works", str(e))

        # Edit employee
        edit_data = emp_data.copy()
        edit_data['name'] = 'John Smith'
        try:
            response = requests.put(f"{BASE_URL}/employees/EMP-001", json=edit_data, headers=headers)
            if response.status_code == 200:
                self.results.add_pass("Edit employee works")
            else:
                self.results.add_fail("Edit employee works", f"Status: {response.status_code}")
        except Exception as e:
            self.results.add_fail("Edit employee works", str(e))

        # Delete employee
        try:
            response = requests.delete(f"{BASE_URL}/employees/EMP-001", headers=headers)
            if response.status_code == 200:
                self.results.add_pass("Delete employee works")
            else:
                self.results.add_fail("Delete employee works", f"Status: {response.status_code}")
        except Exception as e:
            self.results.add_fail("Delete employee works", str(e))

    def test_endpoints(self):
        print(f"\n{BLUE}=== PHASE: ENDPOINTS ==={RESET}\n")

        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}

        # Register endpoint manually
        device_data = {
            "hostname": "PC-001",
            "ip_address": "192.168.1.100",
            "mac_address": "00:11:22:33:44:55",
            "operating_system": "Windows 10",
            "os_version": "22H2",
            "device_type": "Laptop"
        }
        try:
            response = requests.post(f"{BASE_URL}/devices", json=device_data, headers=headers)
            if response.status_code == 200:
                self.device_id = response.json()['device_id']
                self.results.add_pass("Register endpoint works", f"Device: PC-001")
            else:
                self.results.add_fail("Register endpoint works", f"Status: {response.status_code}")
                return
        except Exception as e:
            self.results.add_fail("Register endpoint works", str(e))
            return

        # Test heartbeat (auto-register)
        heartbeat_data = {
            "device_uuid": "test-uuid-1",
            "hostname": "PC-AUTO",
            "username": "testuser",
            "ip_address": "192.168.1.101",
            "operating_system": "Windows 11",
            "cpu_usage": 25.5,
            "ram_usage": 50.2,
            "disk_usage": 75.8,
            "cpu_cores": 8,
            "total_ram": 16.0,
            "available_ram": 8.0,
            "boot_time": "2024-01-15 10:00:00",
            "last_seen": "2024-01-15 14:30:00",
            "status": "Online"
        }
        try:
            response = requests.post(f"{BASE_URL}/heartbeat", json=heartbeat_data, headers=headers)
            if response.status_code == 200:
                self.results.add_pass("Heartbeat (auto-register) works", "PC-AUTO registered")
            else:
                self.results.add_fail("Heartbeat (auto-register) works", f"Status: {response.status_code}")
        except Exception as e:
            self.results.add_fail("Heartbeat (auto-register) works", str(e))

        # Get endpoints
        try:
            response = requests.get(f"{BASE_URL}/devices", headers=headers)
            if response.status_code == 200:
                devices = response.json()['devices']
                self.results.add_pass("Get endpoints works", f"Found {len(devices)} endpoints")
            else:
                self.results.add_fail("Get endpoints works", f"Status: {response.status_code}")
        except Exception as e:
            self.results.add_fail("Get endpoints works", str(e))

    def test_assignments(self):
        print(f"\n{BLUE}=== PHASE: ASSIGNMENTS ==={RESET}\n")

        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}

        # Create employee first
        emp_data = {
            "employee_id": "EMP-TEST",
            "name": "Test Employee",
            "email": "test@company.com",
            "department": "IT",
            "designation": "Analyst"
        }
        try:
            requests.post(f"{BASE_URL}/employees", json=emp_data, headers=headers)
        except:
            pass

        # Assign device
        assignment_data = {
            "employee_id": "EMP-TEST",
            "device_id": self.device_id if hasattr(self, 'device_id') else "PC-001_1234567"
        }
        try:
            response = requests.post(f"{BASE_URL}/assignments", json=assignment_data, headers=headers)
            if response.status_code == 200:
                self.results.add_pass("Assign device works")
            else:
                self.results.add_fail("Assign device works", f"Status: {response.status_code}")
        except Exception as e:
            self.results.add_fail("Assign device works", str(e))

    def test_monitoring(self):
        print(f"\n{BLUE}=== PHASE: MONITORING ==={RESET}\n")

        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}

        # USB events
        try:
            response = requests.get(f"{BASE_URL}/usb-events", headers=headers)
            if response.status_code == 200:
                usb_events = response.json().get('events', [])
                self.results.add_pass("USB monitoring works", f"Found {len(usb_events)} events")
            else:
                self.results.add_fail("USB monitoring works", f"Status: {response.status_code}")
        except Exception as e:
            self.results.add_fail("USB monitoring works", str(e))

        # Processes
        try:
            response = requests.get(f"{BASE_URL}/processes/live", headers=headers)
            if response.status_code == 200:
                processes = response.json().get('processes', [])
                self.results.add_pass("Process monitoring works", f"Monitoring {len(processes)} processes")
            else:
                self.results.add_fail("Process monitoring works", f"Status: {response.status_code}")
        except Exception as e:
            self.results.add_fail("Process monitoring works", str(e))

    def test_dashboard(self):
        print(f"\n{BLUE}=== PHASE: DASHBOARD & REPORTS ==={RESET}\n")

        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}

        # Dashboard
        try:
            response = requests.get(f"{BASE_URL}/dashboard", headers=headers)
            if response.status_code == 200:
                dashboard = response.json()['summary']
                self.results.add_pass("Dashboard works",
                    f"Employees: {dashboard['total_employees']}, Endpoints: {dashboard['total_devices']}, Threats: {dashboard['total_threats']}")
            else:
                self.results.add_fail("Dashboard works", f"Status: {response.status_code}")
        except Exception as e:
            self.results.add_fail("Dashboard works", str(e))

        # Threats
        try:
            response = requests.get(f"{BASE_URL}/threats", headers=headers)
            if response.status_code == 200:
                threats = response.json().get('threats', [])
                self.results.add_pass("Threats endpoint works", f"Found {len(threats)} threats")
            else:
                self.results.add_fail("Threats endpoint works", f"Status: {response.status_code}")
        except Exception as e:
            self.results.add_fail("Threats endpoint works", str(e))

        # Settings
        try:
            response = requests.get(f"{BASE_URL}/settings", headers=headers)
            if response.status_code == 200:
                self.results.add_pass("Settings endpoint works")
            else:
                self.results.add_fail("Settings endpoint works", f"Status: {response.status_code}")
        except Exception as e:
            self.results.add_fail("Settings endpoint works", str(e))

    def test_email(self):
        print(f"\n{BLUE}=== PHASE: EMAIL ==={RESET}\n")

        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}

        # Test email (may fail if SMTP not configured, but endpoint should exist)
        try:
            response = requests.post(
                f"{BASE_URL}/test-email",
                json={
                    "to_email": "test@example.com",
                    "subject": "Test",
                    "message": "Test email"
                },
                headers=headers
            )
            if response.status_code in [200, 400]:  # 400 if SMTP not configured is OK
                self.results.add_pass("Email endpoint works")
            else:
                self.results.add_fail("Email endpoint works", f"Status: {response.status_code}")
        except Exception as e:
            self.results.add_fail("Email endpoint works", str(e))

    def run_all(self):
        print(f"\n{BLUE}{'='*60}")
        print(f"SENTINEL AI v1.0 - PRODUCTION TEST SUITE")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}{RESET}\n")

        # Health check
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code != 200:
                print(f"{RED}Backend not responding at {BASE_URL}{RESET}")
                return False
        except:
            print(f"{RED}Cannot connect to backend at {BASE_URL}{RESET}")
            return False

        # Run test phases
        self.test_authentication()
        if not self.token:
            print(f"{RED}Authentication failed, stopping tests{RESET}")
            return False

        self.test_employees()
        self.test_endpoints()
        self.test_assignments()
        self.test_monitoring()
        self.test_dashboard()
        self.test_email()

        # Summary
        return self.results.summary()

if __name__ == "__main__":
    tester = ProductionTests()
    success = tester.run_all()
    sys.exit(0 if success else 1)
