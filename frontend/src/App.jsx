import React, { useState, useEffect } from 'react';
import API from "./services/api";

import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 15000,
});

API.interceptors.request.use(config => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default API;

API.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('token'));
  const [currentPage, setCurrentPage] = useState('login');
  const [username, setUsername] = useState(localStorage.getItem('username') || '');
  const [message, setMessage] = useState({ type: '', text: '' });
  const [loading, setLoading] = useState(false);

  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);

  const [activeTab, setActiveTab] = useState('dashboard');
  const [employees, setEmployees] = useState([]);
  const [devices, setDevices] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [threats, setThreats] = useState([]);
  const [liveProcesses, setLiveProcesses] = useState([]);
  const [usbEvents, setUsbEvents] = useState([]);
  const [loginEvents, setLoginEvents] = useState([]);
  const [socTab, setSocTab] = useState("overview");
  const [processSearch, setProcessSearch] = useState("");
  const [processRiskFilter, setProcessRiskFilter] = useState("all");
  const [usbFilter, setUsbFilter] = useState("today");
  const [usbSearch, setUsbSearch] = useState("");
  const [usbStartDate, setUsbStartDate] = useState("");
  const [usbEndDate, setUsbEndDate] = useState("");
  const [loginFilter, setLoginFilter] = useState("today");
  const [loginSearch, setLoginSearch] = useState("");
  const [loginStartDate, setLoginStartDate] = useState("");
  const [loginEndDate, setLoginEndDate] = useState("");

  const [dashboard, setDashboard] = useState({
    total_employees: 0,
    total_devices: 0,
    total_threats: 0,
    online_devices: 0,
    total_incidents: 0
  });

  const [settings, setSettings] = useState({
    smtp_server: '',
    smtp_port: 587,
    smtp_email: '',
    smtp_password: '',
    admin_email: ''
  });

  // Form States
  const [showAddEmployee, setShowAddEmployee] = useState(false);
  const [showEditEmployee, setShowEditEmployee] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [employeeForm, setEmployeeForm] = useState({
    employee_id: '',
    name: '',
    email: '',
    phone: '',
    department: '',
    designation: ''
  });

  const [showAddDevice, setShowAddDevice] = useState(false);
  const [showEditDevice, setShowEditDevice] = useState(false);
  const [editingDevice, setEditingDevice] = useState(null);
  const [deviceForm, setDeviceForm] = useState({
    hostname: '',
    ip_address: '',
    mac_address: '',
    operating_system: '',
    os_version: '',
    device_type: 'Laptop'
  });

  const [showAssignment, setShowAssignment] = useState(false);
  const [showEditAssignment, setShowEditAssignment] = useState(false);
  const [editingAssignment, setEditingAssignment] = useState(null);
  const [assignmentForm, setAssignmentForm] = useState({
    employee_id: '',
    device_id: ''
  });

  const showMsg = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 4000);
  };

  const getEndpointStatus = (device) => {
    if (device.computed_status) return device.computed_status;
    if (typeof device.heartbeat_age_seconds === 'number') {
      return device.heartbeat_age_seconds <= (device.heartbeat_timeout_seconds || 30) ? 'Online' : 'Offline';
    }
    return device.status || 'Offline';
  };

  const formatHeartbeatAge = (device) => {
    if (typeof device.heartbeat_age_seconds !== 'number') return 'No heartbeat yet';
    if (device.heartbeat_age_seconds < 60) return `${device.heartbeat_age_seconds}s ago`;
    return `${Math.floor(device.heartbeat_age_seconds / 60)}m ${device.heartbeat_age_seconds % 60}s ago`;
  };

  const parseUtcTime = (value) => {
    if (!value) return null;
    const normalized = String(value).includes('T') ? String(value) : String(value).replace(' ', 'T');
    const hasTimezone = /([zZ]|[+-]\d{2}:?\d{2})$/.test(normalized);
    return new Date(hasTimezone ? normalized : `${normalized}Z`);
  };

  const formatLocalTime = (value, options = {}) => {
    const date = parseUtcTime(value);
    if (!date || Number.isNaN(date.getTime())) return '-';
    return date.toLocaleString('en-IN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: options.seconds === false ? undefined : '2-digit',
      hour12: true
    });
  };

  const formatTimeOnly = (value) => {
    const date = parseUtcTime(value);
    if (!date || Number.isNaN(date.getTime())) return '-';
    return date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true });
  };

  const formatDateHeader = (value) => {
    const date = parseUtcTime(value);
    if (!date || Number.isNaN(date.getTime())) return 'Unknown Date';
    return date.toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' });
  };

  const formatDuration = (seconds) => {
    if (!seconds && seconds !== 0) return '-';
    const value = Number(seconds);
    const hours = Math.floor(value / 3600);
    const minutes = Math.floor((value % 3600) / 60);
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  const periodParams = (period, startDate, endDate) => ({
    period,
    ...(period === 'custom' && startDate ? { start_date: startDate } : {}),
    ...(period === 'custom' && endDate ? { end_date: endDate } : {})
  });

  const downloadCsv = (filename, headers, rows) => {
    const escapeCell = (value) => `"${String(value ?? '').replace(/"/g, '""')}"`;
    const csv = [headers, ...rows].map((row) => row.map(escapeCell).join(',')).join('\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8;' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  const openReport = (type, format) => {
    window.open(`${API.defaults.baseURL}/reports/${type}/${format}`, '_blank');
  };

  const loginRows = () => loginEvents.flatMap((event) => {
    const rows = [{
      time: event.login_time,
      employee: event.username,
      endpoint: event.hostname,
      event: 'Login',
      session: '-'
    }];
    if (event.logout_time) {
      rows.push({
        time: event.logout_time,
        employee: event.username,
        endpoint: event.hostname,
        event: 'Logout',
        session: formatDuration(event.session_duration)
      });
    }
    return rows;
  }).sort((a, b) => (parseUtcTime(b.time)?.getTime() || 0) - (parseUtcTime(a.time)?.getTime() || 0));

  // ============= LOGIN =============
  const handleLogin = async (e) => {
    e.preventDefault();
    if (!loginForm.username || !loginForm.password) {
      showMsg('error', 'Please enter username and password');
      return;
    }

    setLoading(true);
    try {
      const response = await API.post('/auth/login', loginForm);
      const { access_token, user } = response.data;

      localStorage.setItem('token', access_token);
      localStorage.setItem('username', loginForm.username);

      setUsername(loginForm.username);
      setIsLoggedIn(true);
      setCurrentPage('dashboard');
      setLoginForm({ username: '', password: '' });

      showMsg('success', 'Logged in successfully');
      await fetchAllData();
    } catch (error) {
      showMsg('error', error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    setIsLoggedIn(false);
    setUsername('');
    setCurrentPage('login');
    setActiveTab('dashboard');
  };

  // ============= DATA FETCHING =============
  const fetchAllData = async () => {
    try {
      const usbParams = {
        ...periodParams(usbFilter, usbStartDate, usbEndDate),
        ...(usbSearch ? { search: usbSearch } : {})
      };
      const loginParams = {
        ...periodParams(loginFilter, loginStartDate, loginEndDate),
        ...(loginSearch ? { search: loginSearch } : {})
      };
      const [empRes, devRes, assignRes, threatRes, dashRes, usbRes, procRes, loginRes] = await Promise.all([
        API.get("/employees").catch(() => null),
        API.get("/devices").catch(() => null),
        API.get("/assignments").catch(() => null),
        API.get("/threats").catch(() => null),
        API.get("/dashboard").catch(() => null),
        API.get("/usb-events", { params: usbParams }).catch(() => null),
        API.get("/processes/live").catch(() => null),
        API.get("/login-events", { params: loginParams }).catch(() => null)
      ]);

      if (empRes?.data?.employees) setEmployees(empRes.data.employees);
      if (devRes?.data?.devices) setDevices(devRes.data.devices);
      if (assignRes?.data?.assignments) setAssignments(assignRes.data.assignments);
      if (threatRes?.data?.threats) setThreats(threatRes.data.threats);
      if (dashRes?.data?.summary) setDashboard(dashRes.data.summary);
      if (usbRes?.data?.events) setUsbEvents(usbRes.data.events);
      if (procRes?.data?.processes) setLiveProcesses(procRes.data.processes);
      if (loginRes?.data?.events) setLoginEvents(loginRes.data.events);
    } catch (error) {
      console.error("Fetch error:", error);
    }
  };

  const fetchSettings = async () => {
    try {
      const res = await API.get('/settings');
      setSettings(res.data);
    } catch (error) {
      console.error('Settings fetch error:', error);
    }
  };

  // ============= EMPLOYEE CRUD =============
  const addEmployee = async () => {
    if (!employeeForm.employee_id || !employeeForm.name || !employeeForm.email || !employeeForm.department) {
      showMsg('error', 'Please fill all required fields');
      return;
    }
    setLoading(true);
    try {
      await API.post('/employees', employeeForm);
      showMsg('success', 'Employee added successfully');
      setShowAddEmployee(false);
      setEmployeeForm({ employee_id: '', name: '', email: '', phone: '', department: '', designation: '' });
      await fetchAllData();
    } catch (error) {
      showMsg('error', error.response?.data?.detail || 'Failed to add employee');
    } finally {
      setLoading(false);
    }
  };

  const updateEmployee = async () => {
    setLoading(true);
    try {
      await API.put(`/employees/${editingEmployee.employee_id}`, employeeForm);
      showMsg('success', 'Employee updated successfully');
      setShowEditEmployee(false);
      setEditingEmployee(null);
      setEmployeeForm({ employee_id: '', name: '', email: '', phone: '', department: '', designation: '' });
      await fetchAllData();
    } catch (error) {
      showMsg('error', error.response?.data?.detail || 'Failed to update employee');
    } finally {
      setLoading(false);
    }
  };

  const deleteEmployee = async (empId) => {
    if (!window.confirm('Are you sure you want to delete this employee?')) return;
    try {
      await API.delete(`/employees/${empId}`);
      showMsg('success', 'Employee deleted successfully');
      await fetchAllData();
    } catch (error) {
      showMsg('error', error.response?.data?.detail || 'Failed to delete employee');
    }
  };

  // ============= DEVICE CRUD =============
  const addDevice = async () => {
    if (!deviceForm.hostname || !deviceForm.ip_address || !deviceForm.operating_system) {
      showMsg('error', 'Please fill all required fields');
      return;
    }
    setLoading(true);
    try {
      await API.post('/devices', deviceForm);
      showMsg('success', 'Device registered successfully');
      setShowAddDevice(false);
      setDeviceForm({ hostname: '', ip_address: '', mac_address: '', operating_system: '', os_version: '', device_type: 'Laptop' });
      await fetchAllData();
    } catch (error) {
      showMsg('error', error.response?.data?.detail || 'Failed to add device');
    } finally {
      setLoading(false);
    }
  };

  const updateDevice = async () => {
    setLoading(true);
    try {
      await API.put(`/devices/${editingDevice.device_id}`, deviceForm);
      showMsg('success', 'Device updated successfully');
      setShowEditDevice(false);
      setEditingDevice(null);
      setDeviceForm({ hostname: '', ip_address: '', mac_address: '', operating_system: '', os_version: '', device_type: 'Laptop' });
      await fetchAllData();
    } catch (error) {
      showMsg('error', error.response?.data?.detail || 'Failed to update device');
    } finally {
      setLoading(false);
    }
  };

  const deleteDevice = async (devId) => {
    if (!window.confirm('Are you sure you want to delete this device?')) return;
    try {
      await API.delete(`/devices/${devId}`);
      showMsg('success', 'Device deleted successfully');
      await fetchAllData();
    } catch (error) {
      showMsg('error', error.response?.data?.detail || 'Failed to delete device');
    }
  };

  const clearThreats = async () => {
    if (!window.confirm('Clear all threats from Threat Management? This admin action will be recorded in the audit log.')) return;
    setLoading(true);
    try {
      const response = await API.delete('/threats/clear', { params: { admin: username || 'admin' } });
      showMsg('success', response.data?.message || 'Threats cleared');
      await fetchAllData();
    } catch (error) {
      showMsg('error', error.response?.data?.detail || 'Failed to clear threats');
    } finally {
      setLoading(false);
    }
  };

  const clearUsbEvents = async () => {
    if (!window.confirm('Clear all USB activity records? This admin action will be recorded in the audit log.')) return;
    setLoading(true);
    try {
      const response = await API.delete('/usb-events/clear', { params: { admin: username || 'admin' } });
      showMsg('success', response.data?.message || 'USB activity cleared');
      await fetchAllData();
    } catch (error) {
      showMsg('error', error.response?.data?.detail || 'Failed to clear USB activity');
    } finally {
      setLoading(false);
    }
  };

  const clearProcesses = async () => {
    if (!window.confirm('Clear all live process rows? New process data will appear again after the next agent update. This admin action will be recorded in the audit log.')) return;
    setLoading(true);
    try {
      const response = await API.delete('/processes/clear', { params: { admin: username || 'admin' } });
      showMsg('success', response.data?.message || 'Processes cleared');
      await fetchAllData();
    } catch (error) {
      showMsg('error', error.response?.data?.detail || 'Failed to clear processes');
    } finally {
      setLoading(false);
    }
  };

  // ============= ASSIGNMENTS =============
  const assignDevice = async () => {
    if (!assignmentForm.employee_id || !assignmentForm.device_id) {
      showMsg('error', 'Please select both employee and device');
      return;
    }
    setLoading(true);
    try {
      await API.post('/assignments', assignmentForm);
      showMsg('success', 'Device assigned successfully');
      setShowAssignment(false);
      setAssignmentForm({ employee_id: '', device_id: '' });
      await fetchAllData();
    } catch (error) {
      showMsg('error', error.response?.data?.detail || 'Failed to assign device');
    } finally {
      setLoading(false);
    }
  };

  const updateAssignment = async () => {
    if (!editingAssignment) return;
    setLoading(true);
    try {
      await API.put(`/assignments/${editingAssignment.id}`, assignmentForm);
      showMsg('success', 'Assignment updated successfully');
      setShowEditAssignment(false);
      setEditingAssignment(null);
      setAssignmentForm({ employee_id: '', device_id: '' });
      await fetchAllData();
    } catch (error) {
      showMsg('error', error.response?.data?.detail || 'Failed to update assignment');
    } finally {
      setLoading(false);
    }
  };

  const deleteAssignment = async (assignmentId) => {
    if (!window.confirm('Are you sure you want to delete this assignment?')) return;
    try {
      await API.delete(`/assignments/${assignmentId}`);
      showMsg('success', 'Assignment deleted successfully');
      await fetchAllData();
    } catch (error) {
      showMsg('error', error.response?.data?.detail || 'Failed to delete assignment');
    }
  };

  // ============= SETTINGS =============
  const saveSettings = async () => {
    setLoading(true);
    try {
      await API.post('/settings', settings);
      showMsg('success', 'Settings saved successfully');
    } catch (error) {
      showMsg('error', error.response?.data?.detail || 'Failed to save settings');
    } finally {
      setLoading(false);
    }
  };

  const testEmailConnection = async () => {
    setLoading(true);
    try {
      const response = await API.post('/test-email', {
        to_email: settings.admin_email,
        subject: 'SENTINEL AI - Email Configuration Test',
        message: '<h2>Email Configuration Test</h2><p>If you received this email, your email settings are configured correctly!</p>'
      });
      showMsg('success', response.data.message);
    } catch (error) {
      showMsg('error', error.response?.data?.message || 'Failed to send test email');
    } finally {
      setLoading(false);
    }
  };

  // ============= EFFECTS =============
  useEffect(() => {
    if (isLoggedIn) {
      fetchAllData();
      fetchSettings();

      const interval = setInterval(() => {
        fetchAllData();
      }, 10000);

      return () => clearInterval(interval);
    }
  }, [isLoggedIn, usbFilter, usbSearch, usbStartDate, usbEndDate, loginFilter, loginSearch, loginStartDate, loginEndDate]);

  // ============= RENDER LOGIN PAGE =============
  if (!isLoggedIn) {
    return (
      <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #3b82f6 100%)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
        <div style={{ width: '100%', maxWidth: '420px', background: 'rgba(255,255,255,0.95)', backdropFilter: 'blur(10px)', borderRadius: '15px', padding: '40px', boxShadow: '0 25px 50px rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.2)' }}>
          <div style={{ textAlign: 'center', marginBottom: '30px' }}>
            <div style={{ fontSize: '60px', marginBottom: '15px', animation: 'pulse 2s infinite' }}>🛡️</div>
            <h1 style={{ margin: '0 0 8px 0', color: '#0f172a', fontSize: '28px', fontWeight: 'bold' }}>SENTINEL AI</h1>
            <p style={{ margin: '0', color: '#64748b', fontSize: '14px' }}>Real-Time Cyber Defense System</p>
          </div>

          {message.text && (
            <div style={{ padding: '12px', marginBottom: '20px', borderRadius: '6px', background: message.type === 'error' ? '#fee2e2' : '#dcfce7', color: message.type === 'error' ? '#991b1b' : '#166534', fontSize: '14px' }}>
              {message.text}
            </div>
          )}

          <form onSubmit={handleLogin}>
            <input
              type="text"
              placeholder="Username"
              value={loginForm.username}
              onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
              disabled={loading}
              style={{ width: '100%', padding: '12px', marginBottom: '15px', border: '1px solid #e2e8f0', borderRadius: '6px', fontSize: '14px', boxSizing: 'border-box' }}
            />
            <div style={{ position: 'relative', marginBottom: '20px' }}>
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="Password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                disabled={loading}
                style={{ width: '100%', padding: '12px', border: '1px solid #e2e8f0', borderRadius: '6px', fontSize: '14px', boxSizing: 'border-box' }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{ position: 'absolute', right: '10px', top: '10px', background: 'none', border: 'none', cursor: 'pointer', fontSize: '18px' }}
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{ width: '100%', padding: '12px', background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)', color: 'white', border: 'none', borderRadius: '6px', fontSize: '15px', fontWeight: 'bold', cursor: 'pointer', textTransform: 'uppercase', letterSpacing: '0.5px' }}
            >
              {loading ? 'Logging in...' : 'LOGIN'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // ============= MAIN DASHBOARD =============
  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0f172a 0%, #1a1f35 100%)' }}>
      {/* APP BAR */}
      <div style={{ background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)', color: 'white', padding: '15px 30px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 4px 20px rgba(0,0,0,0.3)' }}>
        <h1 style={{ margin: '0', fontSize: '22px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '10px' }}>🛡️ SENTINEL AI</h1>
        <div style={{ display: 'flex', gap: '30px', alignItems: 'center' }}>
          <span style={{ opacity: 0.9 }}>{username}</span>
          <button onClick={handleLogout} style={{ background: 'rgba(255,255,255,0.2)', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '6px', cursor: 'pointer', fontSize: '14px', transition: 'all 0.3s' }}>
            Logout
          </button>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div style={{ padding: '30px', maxWidth: '1400px', margin: '0 auto' }}>
        {message.text && (
          <div style={{ padding: '15px', marginBottom: '20px', borderRadius: '8px', background: message.type === 'error' ? 'rgba(239,68,68,0.1)' : 'rgba(16,185,129,0.1)', color: message.type === 'error' ? '#fca5a5' : '#86efac', fontSize: '14px', border: `1px solid ${message.type === 'error' ? 'rgba(239,68,68,0.3)' : 'rgba(16,185,129,0.3)'}` }}>
            {message.text}
          </div>
        )}

        {/* NAVIGATION TABS */}
        <div style={{ display: 'flex', gap: '10px', marginBottom: '30px', borderBottom: '2px solid rgba(59,130,246,0.2)', paddingBottom: '0', overflowX: 'auto' }}>
          {['dashboard', 'employees', 'endpoints', 'soc', 'settings'].map((tab) => (
            <button
              key={tab}
              onClick={() => {
                setActiveTab(tab);
                if (tab === 'settings') fetchSettings();
              }}
              style={{
                padding: '12px 20px',
                background: activeTab === tab ? 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)' : 'rgba(255,255,255,0.05)',
                color: activeTab === tab ? 'white' : '#94a3b8',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: activeTab === tab ? 'bold' : 'normal',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                transition: 'all 0.3s',
                whiteSpace: 'nowrap'
              }}
            >
              {tab === 'dashboard' && '📊 Dashboard'}
              {tab === 'employees' && '👥 Employees'}
              {tab === 'endpoints' && '💻 Endpoints'}
              {tab === 'soc' && '🛡 SOC'}
              {tab === 'settings' && '⚙️ Settings'}
            </button>
          ))}
        </div>

        {/* DASHBOARD TAB */}
        {activeTab === 'dashboard' && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px' }}>
            <div style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #1e40af 100%)', color: 'white', padding: '25px', borderRadius: '12px', textAlign: 'center', boxShadow: '0 10px 30px rgba(59,130,246,0.3)', border: '1px solid rgba(255,255,255,0.1)' }}>
              <p style={{ margin: '0', fontSize: '13px', opacity: 0.9, textTransform: 'uppercase' }}>Employees</p>
              <h2 style={{ margin: '10px 0 0 0', fontSize: '48px', fontWeight: 'bold' }}>{dashboard.total_employees}</h2>
            </div>
            <div style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)', color: 'white', padding: '25px', borderRadius: '12px', textAlign: 'center', boxShadow: '0 10px 30px rgba(139,92,246,0.3)', border: '1px solid rgba(255,255,255,0.1)' }}>
              <p style={{ margin: '0', fontSize: '13px', opacity: 0.9, textTransform: 'uppercase' }}>Endpoints</p>
              <h2 style={{ margin: '10px 0 0 0', fontSize: '48px', fontWeight: 'bold' }}>{dashboard.total_devices}</h2>
            </div>
            <div style={{ background: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)', color: 'white', padding: '25px', borderRadius: '12px', textAlign: 'center', boxShadow: '0 10px 30px rgba(236,72,153,0.3)', border: '1px solid rgba(255,255,255,0.1)' }}>
              <p style={{ margin: '0', fontSize: '13px', opacity: 0.9, textTransform: 'uppercase' }}>Threats</p>
              <h2 style={{ margin: '10px 0 0 0', fontSize: '48px', fontWeight: 'bold' }}>{dashboard.total_threats}</h2>
            </div>
            <div style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', color: 'white', padding: '25px', borderRadius: '12px', textAlign: 'center', boxShadow: '0 10px 30px rgba(16,185,129,0.3)', border: '1px solid rgba(255,255,255,0.1)' }}>
              <p style={{ margin: '0', fontSize: '13px', opacity: 0.9, textTransform: 'uppercase' }}>Online</p>
              <h2 style={{ margin: '10px 0 0 0', fontSize: '48px', fontWeight: 'bold' }}>{dashboard.online_devices} 🟢</h2>
            </div>
          </div>
        )}

        {/* EMPLOYEES TAB */}
        {activeTab === 'employees' && (
          <div>
            <button onClick={() => { setShowAddEmployee(true); setEmployeeForm({ employee_id: '', name: '', email: '', phone: '', department: '', designation: '' }); }} style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #1e40af 100%)', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '6px', cursor: 'pointer', marginBottom: '20px', fontWeight: 'bold' }}>
              + Add Employee
            </button>

            <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 10px 30px rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.1)' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: 'rgba(255,255,255,0.08)', borderBottom: '2px solid rgba(59,130,246,0.3)' }}>
                    <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>ID</th>
                    <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>Name</th>
                    <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>Email</th>
                    <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>Department</th>
                    <th style={{ padding: '15px', textAlign: 'center', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {employees.length > 0 ? (
                    employees.map((emp, idx) => (
                      <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', transition: 'all 0.3s' }}>
                        <td style={{ padding: '15px', fontSize: '14px', color: '#cbd5e1' }}>{emp.employee_id}</td>
                        <td style={{ padding: '15px', fontSize: '14px', fontWeight: '500', color: '#e0e7ff' }}>{emp.name}</td>
                        <td style={{ padding: '15px', fontSize: '14px', color: '#cbd5e1' }}>{emp.email}</td>
                        <td style={{ padding: '15px', fontSize: '14px', color: '#cbd5e1' }}>{emp.department}</td>
                        <td style={{ padding: '15px', textAlign: 'center' }}>
                          <button onClick={() => { setEditingEmployee(emp); setEmployeeForm(emp); setShowEditEmployee(true); }} style={{ background: '#3b82f6', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', marginRight: '5px', fontSize: '12px' }}>
                            Edit
                          </button>
                          <button onClick={() => deleteEmployee(emp.employee_id)} style={{ background: '#ef4444', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={5} style={{ padding: '30px', textAlign: 'center', color: '#64748b' }}>
                        No employees. Click "+ Add Employee" to add one.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {showAddEmployee && (
              <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                <div style={{ background: 'linear-gradient(135deg, #1a1f35 0%, #2d3748 100%)', padding: '30px', borderRadius: '12px', width: '100%', maxWidth: '500px', maxHeight: '90vh', overflow: 'auto', border: '1px solid rgba(59,130,246,0.3)' }}>
                  <h2 style={{ margin: '0 0 20px 0', color: '#60a5fa' }}>Add New Employee</h2>
                  <input type="text" placeholder="Employee ID *" value={employeeForm.employee_id} onChange={(e) => setEmployeeForm({ ...employeeForm, employee_id: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <input type="text" placeholder="Name *" value={employeeForm.name} onChange={(e) => setEmployeeForm({ ...employeeForm, name: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <input type="email" placeholder="Email *" value={employeeForm.email} onChange={(e) => setEmployeeForm({ ...employeeForm, email: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <input type="tel" placeholder="Phone" value={employeeForm.phone} onChange={(e) => setEmployeeForm({ ...employeeForm, phone: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <input type="text" placeholder="Department *" value={employeeForm.department} onChange={(e) => setEmployeeForm({ ...employeeForm, department: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <input type="text" placeholder="Designation" value={employeeForm.designation} onChange={(e) => setEmployeeForm({ ...employeeForm, designation: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '20px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button onClick={() => setShowAddEmployee(false)} style={{ flex: 1, padding: '10px', background: 'rgba(255,255,255,0.1)', color: '#e0e7ff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
                      Cancel
                    </button>
                    <button onClick={addEmployee} disabled={loading} style={{ flex: 1, padding: '10px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
                      {loading ? 'Adding...' : 'Add'}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {showEditEmployee && (
              <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                <div style={{ background: 'linear-gradient(135deg, #1a1f35 0%, #2d3748 100%)', padding: '30px', borderRadius: '12px', width: '100%', maxWidth: '500px', maxHeight: '90vh', overflow: 'auto', border: '1px solid rgba(59,130,246,0.3)' }}>
                  <h2 style={{ margin: '0 0 20px 0', color: '#60a5fa' }}>Edit Employee</h2>
                  <input type="text" placeholder="Name *" value={employeeForm.name} onChange={(e) => setEmployeeForm({ ...employeeForm, name: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <input type="email" placeholder="Email *" value={employeeForm.email} onChange={(e) => setEmployeeForm({ ...employeeForm, email: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <input type="tel" placeholder="Phone" value={employeeForm.phone} onChange={(e) => setEmployeeForm({ ...employeeForm, phone: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <input type="text" placeholder="Department *" value={employeeForm.department} onChange={(e) => setEmployeeForm({ ...employeeForm, department: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <input type="text" placeholder="Designation" value={employeeForm.designation} onChange={(e) => setEmployeeForm({ ...employeeForm, designation: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '20px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button onClick={() => setShowEditEmployee(false)} style={{ flex: 1, padding: '10px', background: 'rgba(255,255,255,0.1)', color: '#e0e7ff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
                      Cancel
                    </button>
                    <button onClick={updateEmployee} disabled={loading} style={{ flex: 1, padding: '10px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
                      {loading ? 'Saving...' : 'Save'}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ENDPOINTS TAB */}
        {activeTab === 'endpoints' && (
          <div>
            <button onClick={() => { setShowAddDevice(true); setDeviceForm({ hostname: '', ip_address: '', mac_address: '', operating_system: '', os_version: '', device_type: 'Laptop' }); }} style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #1e40af 100%)', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '6px', cursor: 'pointer', marginBottom: '20px', fontWeight: 'bold' }}>
              + Register Endpoint
            </button>

            <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 10px 30px rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.1)' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: 'rgba(255,255,255,0.08)', borderBottom: '2px solid rgba(59,130,246,0.3)' }}>
                    <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>Hostname</th>
                    <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>IP Address</th>
                    <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>OS</th>
                    <th style={{ padding: '15px', textAlign: 'center', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>CPU</th>
                    <th style={{ padding: '15px', textAlign: 'center', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>RAM</th>
                    <th style={{ padding: '15px', textAlign: 'center', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>Disk</th>
                    <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>Status</th>
                    <th style={{ padding: '15px', textAlign: 'center', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {devices.length > 0 ? (
                    devices.map((dev, idx) => (
                      <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                        <td style={{ padding: '15px', color: '#e0e7ff' }}>{dev.hostname}</td>
                        <td style={{ padding: '15px', color: '#cbd5e1' }}>{dev.ip_address}</td>
                        <td style={{ padding: '15px', color: '#cbd5e1' }}>{dev.operating_system}</td>
                        <td style={{ padding: '15px', textAlign: 'center' }}>{dev.cpu_usage?.toFixed(1) || 0}%</td>
                        <td style={{ padding: '15px', textAlign: 'center' }}>{dev.ram_usage?.toFixed(1) || 0}%</td>
                        <td style={{ padding: '15px', textAlign: 'center' }}>{dev.disk_usage?.toFixed(1) || 0}%</td>
                        <td style={{ padding: '15px' }}>
                          {(() => {
                            const status = getEndpointStatus(dev);
                            return (
                              <div>
                                <span style={{ display: 'inline-block', padding: '5px 12px', borderRadius: '20px', background: status === 'Online' ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)', color: status === 'Online' ? '#22c55e' : '#ef4444', fontWeight: 'bold' }}>
                                  {status}
                                </span>
                                <div style={{ marginTop: '4px', color: '#94a3b8', fontSize: '11px' }}>
                                  Heartbeat: {formatHeartbeatAge(dev)}
                                </div>
                              </div>
                            );
                          })()}
                        </td>
                        <td style={{ padding: '15px', textAlign: 'center' }}>
                          <button onClick={() => { setEditingDevice(dev); setDeviceForm(dev); setShowEditDevice(true); }} style={{ background: '#3b82f6', color: 'white', border: 'none', padding: '7px 14px', borderRadius: '6px', cursor: 'pointer', marginRight: '8px' }}>
                            Edit
                          </button>
                          <button onClick={() => deleteDevice(dev.device_id)} style={{ background: '#ef4444', color: 'white', border: 'none', padding: '7px 14px', borderRadius: '6px', cursor: 'pointer' }}>
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="8" style={{ padding: '30px', textAlign: 'center', color: '#64748b' }}>
                        No endpoints registered.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {showAddDevice && (
              <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                <div style={{ background: 'linear-gradient(135deg, #1a1f35 0%, #2d3748 100%)', padding: '30px', borderRadius: '12px', width: '100%', maxWidth: '500px', maxHeight: '90vh', overflow: 'auto', border: '1px solid rgba(59,130,246,0.3)' }}>
                  <h2 style={{ margin: '0 0 20px 0', color: '#60a5fa' }}>Register New Endpoint</h2>
                  <input type="text" placeholder="Hostname *" value={deviceForm.hostname} onChange={(e) => setDeviceForm({ ...deviceForm, hostname: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <input type="text" placeholder="IP Address *" value={deviceForm.ip_address} onChange={(e) => setDeviceForm({ ...deviceForm, ip_address: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <input type="text" placeholder="MAC Address" value={deviceForm.mac_address} onChange={(e) => setDeviceForm({ ...deviceForm, mac_address: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <input type="text" placeholder="Operating System *" value={deviceForm.operating_system} onChange={(e) => setDeviceForm({ ...deviceForm, operating_system: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <input type="text" placeholder="OS Version" value={deviceForm.os_version} onChange={(e) => setDeviceForm({ ...deviceForm, os_version: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <select value={deviceForm.device_type} onChange={(e) => setDeviceForm({ ...deviceForm, device_type: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '20px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }}>
                    <option value="Laptop">Laptop</option>
                    <option value="Desktop">Desktop</option>
                    <option value="Server">Server</option>
                    <option value="Mobile">Mobile</option>
                  </select>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button onClick={() => setShowAddDevice(false)} style={{ flex: 1, padding: '10px', background: 'rgba(255,255,255,0.1)', color: '#e0e7ff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
                      Cancel
                    </button>
                    <button onClick={addDevice} disabled={loading} style={{ flex: 1, padding: '10px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
                      {loading ? 'Registering...' : 'Register'}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {showEditDevice && (
              <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                <div style={{ background: 'linear-gradient(135deg, #1a1f35 0%, #2d3748 100%)', padding: '30px', borderRadius: '12px', width: '100%', maxWidth: '500px', maxHeight: '90vh', overflow: 'auto', border: '1px solid rgba(59,130,246,0.3)' }}>
                  <h2 style={{ margin: '0 0 20px 0', color: '#60a5fa' }}>Edit Endpoint</h2>
                  <input type="text" placeholder="IP Address *" value={deviceForm.ip_address} onChange={(e) => setDeviceForm({ ...deviceForm, ip_address: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <input type="text" placeholder="MAC Address" value={deviceForm.mac_address} onChange={(e) => setDeviceForm({ ...deviceForm, mac_address: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <input type="text" placeholder="Operating System *" value={deviceForm.operating_system} onChange={(e) => setDeviceForm({ ...deviceForm, operating_system: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <input type="text" placeholder="OS Version" value={deviceForm.os_version} onChange={(e) => setDeviceForm({ ...deviceForm, os_version: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '20px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button onClick={() => setShowEditDevice(false)} style={{ flex: 1, padding: '10px', background: 'rgba(255,255,255,0.1)', color: '#e0e7ff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
                      Cancel
                    </button>
                    <button onClick={updateDevice} disabled={loading} style={{ flex: 1, padding: '10px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
                      {loading ? 'Saving...' : 'Save'}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* SOC TAB */}
        {activeTab === 'soc' && (
          <div>
            <div style={{ display: 'flex', gap: '20px' }}>
              {/* Menu */}
              <div style={{ width: '240px', background: '#111827', borderRadius: '12px', padding: '20px' }}>
                <h2 style={{ color: 'white', marginBottom: '25px' }}>🛡 SOC</h2>
                {['overview', 'endpoints', 'usb', 'processes', 'login', 'threats'].map(item => (
                  <button key={item} onClick={() => setSocTab(item)} style={{ width: '100%', padding: '14px', marginBottom: '10px', border: 'none', borderRadius: '8px', cursor: 'pointer', textAlign: 'left', background: socTab === item ? '#2563eb' : 'transparent', color: 'white', fontWeight: 'bold' }}>
                    {item.toUpperCase()}
                  </button>
                ))}
              </div>

              {/* Content */}
              <div style={{ flex: 1, background: '#111827', borderRadius: '12px', padding: '25px' }}>
                {socTab === 'overview' && (
                  <div>
                    <h2 style={{ color: '#fff', marginBottom: '25px' }}>🛡 Security Operations Center</h2>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                      <div style={{ background: 'rgba(59,130,246,0.2)', padding: '20px', borderRadius: '8px', color: '#60a5fa', textAlign: 'center' }}>
                        <h3 style={{ margin: '0 0 10px 0' }}>🟢 Online</h3>
                        <h1 style={{ margin: '0', fontSize: '36px' }}>{dashboard.online_devices}</h1>
                      </div>
                      <div style={{ background: 'rgba(139,92,246,0.2)', padding: '20px', borderRadius: '8px', color: '#a78bfa', textAlign: 'center' }}>
                        <h3 style={{ margin: '0 0 10px 0' }}>💻 Endpoints</h3>
                        <h1 style={{ margin: '0', fontSize: '36px' }}>{devices.length}</h1>
                      </div>
                      <div style={{ background: 'rgba(236,72,153,0.2)', padding: '20px', borderRadius: '8px', color: '#f472b6', textAlign: 'center' }}>
                        <h3 style={{ margin: '0 0 10px 0' }}>👥 Employees</h3>
                        <h1 style={{ margin: '0', fontSize: '36px' }}>{employees.length}</h1>
                      </div>
                      <div style={{ background: 'rgba(239,68,68,0.2)', padding: '20px', borderRadius: '8px', color: '#fca5a5', textAlign: 'center' }}>
                        <h3 style={{ margin: '0 0 10px 0' }}>⚠ Threats</h3>
                        <h1 style={{ margin: '0', fontSize: '36px' }}>{threats.length}</h1>
                      </div>
                      <div style={{ background: 'rgba(34,197,94,0.2)', padding: '20px', borderRadius: '8px', color: '#86efac', textAlign: 'center' }}>
                        <h3 style={{ margin: '0 0 10px 0' }}>💾 USB Events</h3>
                        <h1 style={{ margin: '0', fontSize: '36px' }}>{usbEvents.length}</h1>
                      </div>
                      <div style={{ background: 'rgba(59,130,246,0.2)', padding: '20px', borderRadius: '8px', color: '#60a5fa', textAlign: 'center' }}>
                        <h3 style={{ margin: '0 0 10px 0' }}>⚙ Processes</h3>
                        <h1 style={{ margin: '0', fontSize: '36px' }}>{liveProcesses.length}</h1>
                      </div>
                    </div>
                  </div>
                )}

                {socTab === 'endpoints' && (
                  <div>
                    <h2 style={{ color: '#e0e7ff', marginBottom: '20px' }}>💻 Endpoint Monitoring</h2>
                    <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '12px', overflow: 'hidden' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                          <tr style={{ background: 'rgba(255,255,255,0.08)' }}>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>Hostname</th>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>IP</th>
                            <th style={{ padding: '15px', textAlign: 'center', color: '#e0e7ff' }}>CPU</th>
                            <th style={{ padding: '15px', textAlign: 'center', color: '#e0e7ff' }}>RAM</th>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {devices.length > 0 ? devices.map((dev, idx) => (
                            <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                              <td style={{ padding: '15px', color: '#e0e7ff' }}>{dev.hostname}</td>
                              <td style={{ padding: '15px', color: '#cbd5e1' }}>{dev.ip_address}</td>
                              <td style={{ padding: '15px', textAlign: 'center', color: '#cbd5e1' }}>{dev.cpu_usage?.toFixed(1)}%</td>
                              <td style={{ padding: '15px', textAlign: 'center', color: '#cbd5e1' }}>{dev.ram_usage?.toFixed(1)}%</td>
                              <td style={{ padding: '15px' }}>
                                {(() => {
                                  const status = getEndpointStatus(dev);
                                  return (
                                    <div>
                                      <span style={{ display: 'inline-block', padding: '5px 10px', borderRadius: '12px', background: status === 'Online' ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)', color: status === 'Online' ? '#22c55e' : '#ef4444', fontSize: '12px' }}>
                                        {status}
                                      </span>
                                      <div style={{ marginTop: '4px', color: '#94a3b8', fontSize: '11px' }}>
                                        {formatHeartbeatAge(dev)}
                                      </div>
                                    </div>
                                  );
                                })()}
                              </td>
                            </tr>
                          )) : (
                            <tr>
                              <td colSpan="5" style={{ padding: '30px', textAlign: 'center', color: '#64748b' }}>
                                No endpoints online
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {socTab === 'usb' && (
                  <div>
                    <h2 style={{ color: '#e0e7ff', marginBottom: '20px' }}>USB Activity Log</h2>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', alignItems: 'center', marginBottom: '15px' }}>
                      <select value={usbFilter} onChange={(e) => setUsbFilter(e.target.value)} style={{ padding: '10px 12px', borderRadius: '6px', border: '1px solid rgba(59,130,246,0.45)', background: '#0f172a', color: '#e0e7ff' }}>
                        <option value="today">Today</option>
                        <option value="yesterday">Yesterday</option>
                        <option value="last7">Last 7 Days</option>
                        <option value="last_month">Last 30 Days</option>
                        <option value="custom">Custom Date Range</option>
                        <option value="all">All Records</option>
                      </select>
                      {usbFilter === 'custom' && (
                        <>
                          <input type="date" value={usbStartDate} onChange={(e) => setUsbStartDate(e.target.value)} style={{ padding: '9px 10px', borderRadius: '6px', border: '1px solid rgba(59,130,246,0.45)', background: '#0f172a', color: '#e0e7ff' }} />
                          <input type="date" value={usbEndDate} onChange={(e) => setUsbEndDate(e.target.value)} style={{ padding: '9px 10px', borderRadius: '6px', border: '1px solid rgba(59,130,246,0.45)', background: '#0f172a', color: '#e0e7ff' }} />
                        </>
                      )}
                      <input type="search" placeholder="Search hostname / user / USB" value={usbSearch} onChange={(e) => setUsbSearch(e.target.value)} style={{ minWidth: '260px', flex: '1 1 260px', padding: '10px 12px', borderRadius: '6px', border: '1px solid rgba(59,130,246,0.45)', background: 'rgba(255,255,255,0.06)', color: '#e0e7ff' }} />
                      <button onClick={fetchAllData} style={{ padding: '10px 14px', background: '#2563eb', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>Refresh</button>
                      <button onClick={() => downloadCsv('usb_activity.csv', ['Action', 'Device', 'Endpoint', 'User', 'Time', 'Status'], usbEvents.map((event) => [event.action, event.device, event.hostname, event.username, formatLocalTime(event.event_time), 'Success']))} style={{ padding: '10px 14px', background: '#10b981', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>Export CSV</button>
                      <button onClick={() => openReport('usb', 'pdf')} style={{ padding: '10px 14px', background: '#7c3aed', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>Export PDF</button>
                      <button onClick={() => { setUsbFilter('today'); setUsbSearch(''); setUsbStartDate(''); setUsbEndDate(''); }} style={{ padding: '10px 14px', background: 'rgba(255,255,255,0.08)', color: '#e0e7ff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>Clear Filter</button>
                      <button onClick={clearUsbEvents} disabled={loading || usbEvents.length === 0} style={{ padding: '10px 14px', background: usbEvents.length === 0 ? 'rgba(148,163,184,0.25)' : '#dc2626', color: 'white', border: 'none', borderRadius: '6px', cursor: usbEvents.length === 0 ? 'not-allowed' : 'pointer', fontWeight: 'bold' }}>
                        {loading ? 'Clearing...' : 'Clear USB'}
                      </button>
                    </div>
                    <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '12px', overflow: 'hidden' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                          <tr style={{ background: 'rgba(255,255,255,0.08)' }}>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>Action</th>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>Device</th>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>Hostname</th>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>User</th>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>Time</th>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {usbEvents.length > 0 ? usbEvents.map((event, idx) => (
                            <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                              <td style={{ padding: '15px' }}>
                                <span style={{ background: event.action === 'Inserted' ? '#10b981' : '#ef4444', color: 'white', padding: '6px 12px', borderRadius: '12px', fontSize: '12px' }}>
                                  {event.action}
                                </span>
                              </td>
                              <td style={{ padding: '15px', color: '#cbd5e1' }}>{event.device}</td>
                              <td style={{ padding: '15px', color: '#cbd5e1' }}>{event.hostname}</td>
                              <td style={{ padding: '15px', color: '#cbd5e1' }}>{event.username}</td>
                              <td style={{ padding: '15px', color: '#cbd5e1' }}>{formatLocalTime(event.event_time)}</td>
                              <td style={{ padding: '15px', color: '#86efac' }}>Success</td>
                            </tr>
                          )) : (
                            <tr>
                              <td colSpan="6" style={{ padding: '30px', textAlign: 'center', color: '#64748b' }}>
                                No USB activity
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {socTab === 'processes' && (
                  <div>
                    <h2 style={{ color: '#e0e7ff', marginBottom: '20px' }}>Live Processes</h2>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', alignItems: 'center', marginBottom: '14px' }}>
                      <select value={processRiskFilter} onChange={(e) => setProcessRiskFilter(e.target.value)} style={{ padding: '10px 12px', borderRadius: '6px', border: '1px solid rgba(59,130,246,0.45)', background: '#0f172a', color: '#e0e7ff' }}>
                        <option value="all">All Risk</option>
                        <option value="Safe">Safe</option>
                        <option value="Suspicious">Suspicious</option>
                        <option value="Critical">Critical</option>
                      </select>
                      <input
                        type="search"
                        placeholder="Search process, user, host, or risk"
                        value={processSearch}
                        onChange={(e) => setProcessSearch(e.target.value)}
                        style={{ minWidth: '260px', flex: '1 1 260px', padding: '10px 12px', border: '1px solid rgba(59,130,246,0.45)', borderRadius: '6px', background: 'rgba(255,255,255,0.06)', color: '#e0e7ff', boxSizing: 'border-box' }}
                      />
                      <button onClick={fetchAllData} style={{ padding: '10px 14px', background: '#2563eb', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>Refresh</button>
                      <button onClick={() => { setProcessRiskFilter('all'); setProcessSearch(''); }} style={{ padding: '10px 14px', background: 'rgba(255,255,255,0.08)', color: '#e0e7ff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>Clear Filter</button>
                      <button onClick={clearProcesses} disabled={loading || liveProcesses.length === 0} style={{ padding: '10px 14px', background: liveProcesses.length === 0 ? 'rgba(148,163,184,0.25)' : '#dc2626', color: 'white', border: 'none', borderRadius: '6px', cursor: liveProcesses.length === 0 ? 'not-allowed' : 'pointer', fontWeight: 'bold' }}>
                        {loading ? 'Clearing...' : 'Clear Processes'}
                      </button>
                    </div>
                    <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '12px', overflow: 'hidden' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                          <tr style={{ background: 'rgba(255,255,255,0.08)' }}>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>Process</th>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>Host</th>
                            <th style={{ padding: '15px', textAlign: 'center', color: '#e0e7ff' }}>CPU %</th>
                            <th style={{ padding: '15px', textAlign: 'center', color: '#e0e7ff' }}>Memory %</th>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>User</th>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>Risk</th>
                          </tr>
                        </thead>
                        <tbody>
                          {liveProcesses.filter((proc) => {
                            const term = processSearch.toLowerCase();
                            const text = [
                              proc.name,
                              proc.process_name,
                              proc.hostname,
                              proc.username,
                              proc.user,
                              proc.classification
                            ].filter(Boolean).join(' ').toLowerCase();
                            const riskMatch = processRiskFilter === 'all' || proc.classification === processRiskFilter;
                            return riskMatch && (!term || text.includes(term));
                          }).length > 0 ? liveProcesses.filter((proc) => {
                            const term = processSearch.toLowerCase();
                            const text = [
                              proc.name,
                              proc.process_name,
                              proc.hostname,
                              proc.username,
                              proc.user,
                              proc.classification
                            ].filter(Boolean).join(' ').toLowerCase();
                            const riskMatch = processRiskFilter === 'all' || proc.classification === processRiskFilter;
                            return riskMatch && (!term || text.includes(term));
                          }).map((proc, idx) => {
                            const processName = proc.name || proc.process_name || `PID ${proc.pid || 'Unknown'}`;
                            const cpu = Number(proc.cpu_percent ?? proc.cpu ?? 0);
                            const memory = Number(proc.memory_percent ?? proc.memory ?? 0);
                            const user = proc.username || proc.user || 'Unknown';
                            const risk = proc.classification || 'Safe';
                            const riskStyle = risk === 'Critical'
                              ? { background: 'rgba(239,68,68,0.2)', color: '#fca5a5' }
                              : risk === 'Suspicious'
                                ? { background: 'rgba(245,158,11,0.2)', color: '#fcd34d' }
                                : { background: 'rgba(16,185,129,0.2)', color: '#86efac' };
                            return (
                              <tr key={`${proc.hostname || 'host'}-${proc.pid || idx}-${processName}`} style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                                <td style={{ padding: '15px', color: '#e0e7ff', fontWeight: 600 }}>{processName}</td>
                                <td style={{ padding: '15px', color: '#cbd5e1' }}>{proc.hostname || '-'}</td>
                                <td style={{ padding: '15px', textAlign: 'center', color: '#cbd5e1' }}>{cpu.toFixed(2)}%</td>
                                <td style={{ padding: '15px', textAlign: 'center', color: '#cbd5e1' }}>{memory.toFixed(3)}%</td>
                                <td style={{ padding: '15px', color: user === 'Unknown' ? '#fcd34d' : '#cbd5e1' }}>{user}</td>
                                <td style={{ padding: '15px' }}>
                                  <span title={proc.reason || risk} style={{ display: 'inline-block', padding: '5px 10px', borderRadius: '12px', fontSize: '12px', fontWeight: 'bold', ...riskStyle }}>
                                    {risk}
                                  </span>
                                </td>
                              </tr>
                            );
                          }) : (
                            <tr>
                              <td colSpan="6" style={{ padding: '30px', textAlign: 'center', color: '#64748b' }}>
                                No processes monitored
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {socTab === 'login' && (
                  <div>
                    <h2 style={{ color: '#e0e7ff', marginBottom: '20px' }}>Login History</h2>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', alignItems: 'center', marginBottom: '15px' }}>
                      <select value={loginFilter} onChange={(e) => setLoginFilter(e.target.value)} style={{ padding: '10px 12px', borderRadius: '6px', border: '1px solid rgba(59,130,246,0.45)', background: '#0f172a', color: '#e0e7ff' }}>
                        <option value="today">Today</option>
                        <option value="yesterday">Yesterday</option>
                        <option value="last7">Last 7 Days</option>
                        <option value="custom">Custom Date</option>
                        <option value="all">All Records</option>
                      </select>
                      {loginFilter === 'custom' && (
                        <>
                          <input type="date" value={loginStartDate} onChange={(e) => setLoginStartDate(e.target.value)} style={{ padding: '9px 10px', borderRadius: '6px', border: '1px solid rgba(59,130,246,0.45)', background: '#0f172a', color: '#e0e7ff' }} />
                          <input type="date" value={loginEndDate} onChange={(e) => setLoginEndDate(e.target.value)} style={{ padding: '9px 10px', borderRadius: '6px', border: '1px solid rgba(59,130,246,0.45)', background: '#0f172a', color: '#e0e7ff' }} />
                        </>
                      )}
                      <input type="search" placeholder="Search employee / endpoint" value={loginSearch} onChange={(e) => setLoginSearch(e.target.value)} style={{ minWidth: '260px', flex: '1 1 260px', padding: '10px 12px', borderRadius: '6px', border: '1px solid rgba(59,130,246,0.45)', background: 'rgba(255,255,255,0.06)', color: '#e0e7ff' }} />
                      <button onClick={fetchAllData} style={{ padding: '10px 14px', background: '#2563eb', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>Refresh</button>
                      <button onClick={() => downloadCsv('login_history.csv', ['Time', 'Employee', 'Endpoint', 'Event', 'Session'], loginRows().map((row) => [formatLocalTime(row.time), row.employee, row.endpoint, row.event, row.session]))} style={{ padding: '10px 14px', background: '#10b981', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>Export CSV</button>
                      <button onClick={() => openReport('login', 'pdf')} style={{ padding: '10px 14px', background: '#7c3aed', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>Export PDF</button>
                      <button onClick={() => { setLoginFilter('today'); setLoginSearch(''); setLoginStartDate(''); setLoginEndDate(''); }} style={{ padding: '10px 14px', background: 'rgba(255,255,255,0.08)', color: '#e0e7ff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>Clear Filter</button>
                    </div>

                    <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '12px', overflow: 'hidden', marginBottom: '22px' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                          <tr style={{ background: 'rgba(255,255,255,0.08)' }}>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>Time</th>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>Employee</th>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>Endpoint</th>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>Event</th>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>Session</th>
                          </tr>
                        </thead>
                        <tbody>
                          {loginRows().length > 0 ? loginRows().map((row, idx) => (
                            <tr key={`${row.endpoint}-${row.employee}-${row.event}-${idx}`} style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                              <td style={{ padding: '15px', color: '#cbd5e1' }}>{formatLocalTime(row.time, { seconds: false })}</td>
                              <td style={{ padding: '15px', color: '#e0e7ff', fontWeight: 600 }}>{row.employee}</td>
                              <td style={{ padding: '15px', color: '#cbd5e1' }}>{row.endpoint}</td>
                              <td style={{ padding: '15px' }}>
                                <span style={{ display: 'inline-block', padding: '5px 10px', borderRadius: '12px', background: row.event === 'Login' ? 'rgba(16,185,129,0.2)' : 'rgba(59,130,246,0.2)', color: row.event === 'Login' ? '#86efac' : '#93c5fd', fontSize: '12px', fontWeight: 'bold' }}>{row.event}</span>
                              </td>
                              <td style={{ padding: '15px', color: '#cbd5e1' }}>{row.session}</td>
                            </tr>
                          )) : (
                            <tr>
                              <td colSpan="5" style={{ padding: '30px', textAlign: 'center', color: '#64748b' }}>No login activity for this filter</td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>

                    <h3 style={{ color: '#e0e7ff', marginBottom: '12px' }}>Timeline</h3>
                    <div style={{ display: 'grid', gap: '14px' }}>
                      {Object.entries(loginRows().reduce((groups, row) => {
                        const key = formatDateHeader(row.time);
                        groups[key] = groups[key] || [];
                        groups[key].push(row);
                        return groups;
                      }, {})).map(([date, rows]) => (
                        <div key={date} style={{ borderLeft: '2px solid rgba(96,165,250,0.6)', paddingLeft: '16px' }}>
                          <div style={{ color: '#60a5fa', fontWeight: 'bold', marginBottom: '8px' }}>{date}</div>
                          {rows.slice().reverse().map((row, idx) => (
                            <div key={`${date}-${idx}`} style={{ color: '#cbd5e1', marginBottom: '9px' }}>
                              <span style={{ color: '#94a3b8', display: 'inline-block', width: '82px' }}>{formatTimeOnly(row.time)}</span>
                              <span>{row.event} - {row.employee} on {row.endpoint}{row.session !== '-' ? ` (${row.session})` : ''}</span>
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {socTab === 'threats' && (
                  <div>
                    <h2 style={{ color: '#e0e7ff', marginBottom: '20px' }}>Threat Management</h2>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', alignItems: 'center', marginBottom: '15px' }}>
                      <span style={{ color: '#cbd5e1', fontWeight: 'bold' }}>{threats.length} active threat{threats.length === 1 ? '' : 's'}</span>
                      <button onClick={fetchAllData} style={{ padding: '10px 14px', background: '#2563eb', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>Refresh</button>
                      <button onClick={() => openReport('threat', 'csv')} style={{ padding: '10px 14px', background: '#10b981', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>Export CSV</button>
                      <button onClick={() => openReport('threat', 'pdf')} style={{ padding: '10px 14px', background: '#7c3aed', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>Export PDF</button>
                      <button onClick={clearThreats} disabled={loading || threats.length === 0} style={{ padding: '10px 14px', background: threats.length === 0 ? 'rgba(148,163,184,0.25)' : '#dc2626', color: 'white', border: 'none', borderRadius: '6px', cursor: threats.length === 0 ? 'not-allowed' : 'pointer', fontWeight: 'bold' }}>
                        {loading ? 'Clearing...' : 'Clear Threats'}
                      </button>
                    </div>
                    <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '12px', overflow: 'hidden' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                          <tr style={{ background: 'rgba(255,255,255,0.08)' }}>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>Threat</th>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>Device</th>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>Type</th>
                            <th style={{ padding: '15px', textAlign: 'left', color: '#e0e7ff' }}>Severity</th>
                          </tr>
                        </thead>
                        <tbody>
                          {threats.length > 0 ? threats.map((threat, idx) => (
                            <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                              <td style={{ padding: '15px', color: '#e0e7ff' }}>{threat.threat_name}</td>
                              <td style={{ padding: '15px', color: '#cbd5e1' }}>{threat.device_id}</td>
                              <td style={{ padding: '15px', color: '#cbd5e1' }}>{threat.threat_type}</td>
                              <td style={{ padding: '15px' }}>
                                <span style={{ display: 'inline-block', padding: '5px 10px', borderRadius: '12px', background: threat.severity === 'Critical' ? 'rgba(239,68,68,0.2)' : 'rgba(245,158,11,0.2)', color: threat.severity === 'Critical' ? '#fca5a5' : '#fcd34d', fontSize: '12px' }}>
                                  {threat.severity}
                                </span>
                              </td>
                            </tr>
                          )) : (
                            <tr>
                              <td colSpan="4" style={{ padding: '30px', textAlign: 'center', color: '#64748b' }}>
                                ✅ No threats detected
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* SETTINGS TAB */}
        {activeTab === 'settings' && (
          <div>
            <h2 style={{ color: '#e0e7ff', marginBottom: '20px' }}>⚙️ Admin Settings</h2>
            <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '12px', padding: '30px', border: '1px solid rgba(59,130,246,0.3)' }}>
              <h3 style={{ color: '#60a5fa', marginBottom: '20px' }}>Gmail SMTP Configuration</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '30px' }}>
                <div>
                  <label style={{ display: 'block', color: '#cbd5e1', marginBottom: '8px', fontSize: '14px', fontWeight: 'bold' }}>SMTP Server</label>
                  <input type="text" placeholder="smtp.gmail.com" value={settings.smtp_server} onChange={(e) => setSettings({ ...settings, smtp_server: e.target.value })} style={{ width: '100%', padding: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                </div>
                <div>
                  <label style={{ display: 'block', color: '#cbd5e1', marginBottom: '8px', fontSize: '14px', fontWeight: 'bold' }}>SMTP Port</label>
                  <input type="number" placeholder="587" value={settings.smtp_port} onChange={(e) => setSettings({ ...settings, smtp_port: parseInt(e.target.value) })} style={{ width: '100%', padding: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                </div>
                <div>
                  <label style={{ display: 'block', color: '#cbd5e1', marginBottom: '8px', fontSize: '14px', fontWeight: 'bold' }}>Email Address</label>
                  <input type="email" placeholder="your-email@gmail.com" value={settings.smtp_email} onChange={(e) => setSettings({ ...settings, smtp_email: e.target.value })} style={{ width: '100%', padding: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                </div>
                <div>
                  <label style={{ display: 'block', color: '#cbd5e1', marginBottom: '8px', fontSize: '14px', fontWeight: 'bold' }}>App Password</label>
                  <input type="password" placeholder="Your Gmail App Password" value={settings.smtp_password} onChange={(e) => setSettings({ ...settings, smtp_password: e.target.value })} style={{ width: '100%', padding: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                </div>
                <div>
                  <label style={{ display: 'block', color: '#cbd5e1', marginBottom: '8px', fontSize: '14px', fontWeight: 'bold' }}>Admin Email</label>
                  <input type="email" placeholder="admin@company.com" value={settings.admin_email} onChange={(e) => setSettings({ ...settings, admin_email: e.target.value })} style={{ width: '100%', padding: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }} />
                </div>
              </div>

              <div style={{ display: 'flex', gap: '10px' }}>
                <button onClick={saveSettings} disabled={loading} style={{ padding: '12px 24px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
                  {loading ? 'Saving...' : '💾 Save Settings'}
                </button>
                <button onClick={testEmailConnection} disabled={loading || !settings.smtp_email} style={{ padding: '12px 24px', background: '#10b981', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
                  {loading ? 'Testing...' : '📧 Test Email'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
