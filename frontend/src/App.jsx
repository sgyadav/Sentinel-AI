import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = axios.create({ 
  baseURL: 'https://sentinel-ai-fz5u.onrender.com',
  timeout: 15000 
});

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
  const [employeeMonitoring, setEmployeeMonitoring] = useState([]);
  const [dashboard, setDashboard] = useState({
    total_employees: 0,
    total_devices: 0,
    total_threats: 0,
    total_incidents: 0
  });

  // Admin Settings States
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
  const [assignmentForm, setAssignmentForm] = useState({
    employee_id: '',
    device_id: ''
  });

  const showMsg = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 4000);
  };

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
      const [empRes, devRes, assignRes, threatRes, dashRes, monitorRes] = await Promise.all([
        API.get('/employees').catch(() => null),
        API.get('/devices').catch(() => null),
        API.get('/assignments').catch(() => null),
        API.get('/threats').catch(() => null),
        API.get('/dashboard').catch(() => null),
        API.get('/employee-monitoring').catch(() => null)
      ]);

      if (empRes?.data?.employees) setEmployees(empRes.data.employees);
      if (devRes?.data?.devices) setDevices(devRes.data.devices);
      if (assignRes?.data?.assignments) setAssignments(assignRes.data.assignments);
      if (threatRes?.data?.threats) setThreats(threatRes.data.threats);
      if (dashRes?.data?.summary) setDashboard(dashRes.data.summary);
      if (monitorRes?.data?.employees) setEmployeeMonitoring(monitorRes.data.employees);
    } catch (error) {
      console.error('Fetch error:', error);
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

  // ============= DEVICE ASSIGNMENT =============
 const deleteAssignment = async (assignmentId) => {
  const confirmDelete = window.confirm(
    "Are you sure you want to delete this assignment?"
  );

  if (!confirmDelete) return;

  try {
    await API.delete(`/assignments/${assignmentId}`);
    showMsg("success", "Assignment deleted successfully");
    await fetchAllData();
  } catch (error) {
    showMsg(
      "error",
      error.response?.data?.detail || "Failed to delete assignment"
    );
  }
};

const assignDevice = async () => {
  if (!assignmentForm.employee_id || !assignmentForm.device_id) {
    showMsg("error", "Please select both employee and device");
    return;
  }

  setLoading(true);

  try {
    await API.post("/assignments", assignmentForm);

    showMsg("success", "Device assigned successfully");

    setShowAssignment(false);

    setAssignmentForm({
      employee_id: "",
      device_id: ""
    });

    await fetchAllData();

  } catch (error) {
    showMsg(
      "error",
      error.response?.data?.detail || "Failed to assign device"
    );
  } finally {
    setLoading(false);
  }
};

  // ============= ADMIN SETTINGS =============
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
      const interval = setInterval(fetchAllData, 10000);
      return () => clearInterval(interval);
    }
  }, [isLoggedIn]);

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
          {['dashboard', 'employees', 'devices', 'assignments', 'monitoring', 'threats', 'settings'].map((tab) => (
            <button
              key={tab}
              onClick={() => { setActiveTab(tab); if (tab === 'settings') fetchSettings(); }}
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
              {tab === 'devices' && '💻 Devices'}
              {tab === 'assignments' && '🔗 Assignments'}
              {tab === 'monitoring' && '📡 Live Monitoring'}
              {tab === 'threats' && '⚠️ Threats'}
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
              <p style={{ margin: '0', fontSize: '13px', opacity: 0.9, textTransform: 'uppercase' }}>Devices</p>
              <h2 style={{ margin: '10px 0 0 0', fontSize: '48px', fontWeight: 'bold' }}>{dashboard.total_devices}</h2>
            </div>
            <div style={{ background: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)', color: 'white', padding: '25px', borderRadius: '12px', textAlign: 'center', boxShadow: '0 10px 30px rgba(236,72,153,0.3)', border: '1px solid rgba(255,255,255,0.1)' }}>
              <p style={{ margin: '0', fontSize: '13px', opacity: 0.9, textTransform: 'uppercase' }}>Threats</p>
              <h2 style={{ margin: '10px 0 0 0', fontSize: '48px', fontWeight: 'bold' }}>{dashboard.total_threats}</h2>
            </div>
            <div style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', color: 'white', padding: '25px', borderRadius: '12px', textAlign: 'center', boxShadow: '0 10px 30px rgba(16,185,129,0.3)', border: '1px solid rgba(255,255,255,0.1)' }}>
              <p style={{ margin: '0', fontSize: '13px', opacity: 0.9, textTransform: 'uppercase' }}>Status</p>
              <h2 style={{ margin: '10px 0 0 0', fontSize: '48px', fontWeight: 'bold' }}>🟢</h2>
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

        {/* DEVICES TAB */}
        {activeTab === 'devices' && (
          <div>
            <button onClick={() => { setShowAddDevice(true); setDeviceForm({ hostname: '', ip_address: '', mac_address: '', operating_system: '', os_version: '', device_type: 'Laptop' }); }} style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #1e40af 100%)', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '6px', cursor: 'pointer', marginBottom: '20px', fontWeight: 'bold' }}>
              + Register Device
            </button>

            <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 10px 30px rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.1)' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: 'rgba(255,255,255,0.08)', borderBottom: '2px solid rgba(59,130,246,0.3)' }}>
                    <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>Hostname</th>
                    <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>IP Address</th>
                    <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>OS</th>
                    <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>Status</th>
                    <th style={{ padding: '15px', textAlign: 'center', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {devices.length > 0 ? (
                    devices.map((dev, idx) => (
                      <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                        <td style={{ padding: '15px', fontSize: '14px', fontWeight: '500', color: '#e0e7ff' }}>{dev.hostname}</td>
                        <td style={{ padding: '15px', fontSize: '14px', color: '#cbd5e1' }}>{dev.ip_address}</td>
                        <td style={{ padding: '15px', fontSize: '14px', color: '#cbd5e1' }}>{dev.operating_system}</td>
                        <td style={{ padding: '15px', fontSize: '14px' }}>
                          <span style={{ display: 'inline-block', background: dev.status === 'Online' ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)', color: dev.status === 'Online' ? '#86efac' : '#fca5a5', padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 'bold' }}>
                            🟢 {dev.status}
                          </span>
                        </td>
                        <td style={{ padding: '15px', textAlign: 'center' }}>
                          <button onClick={() => { setEditingDevice(dev); setDeviceForm(dev); setShowEditDevice(true); }} style={{ background: '#3b82f6', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', marginRight: '5px', fontSize: '12px' }}>
                            Edit
                          </button>
                          <button onClick={() => deleteDevice(dev.device_id)} style={{ background: '#ef4444', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={5} style={{ padding: '30px', textAlign: 'center', color: '#64748b' }}>
                        No devices. Click "+ Register Device" to add one.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {showAddDevice && (
              <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                <div style={{ background: 'linear-gradient(135deg, #1a1f35 0%, #2d3748 100%)', padding: '30px', borderRadius: '12px', width: '100%', maxWidth: '500px', maxHeight: '90vh', overflow: 'auto', border: '1px solid rgba(59,130,246,0.3)' }}>
                  <h2 style={{ margin: '0 0 20px 0', color: '#60a5fa' }}>Register New Device</h2>
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
                  <h2 style={{ margin: '0 0 20px 0', color: '#60a5fa' }}>Edit Device</h2>
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

        {/* ASSIGNMENTS TAB */}
        {activeTab === 'assignments' && (
          <div>
            <button onClick={() => setShowAssignment(true)} style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #1e40af 100%)', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '6px', cursor: 'pointer', marginBottom: '20px', fontWeight: 'bold' }}>
              + Assign Device
            </button>

            <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 10px 30px rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.1)' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
               <thead>
                <tr style={{ background: 'rgba(255,255,255,0.08)', borderBottom: '2px solid rgba(59,130,246,0.3)' }}>
    <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>Employee ID</th>
    <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>Device ID</th>
    <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>Assigned Date</th>

    <th style={{ padding: '15px', textAlign: 'center', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>
      Actions
    </th>
  </tr>
</thead>
                <tbody>
                  {assignments.length > 0 ? (
                    assignments.map((assign, idx) => (
                     <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
  <td style={{ padding: '15px', fontSize: '14px', fontWeight: '500', color: '#e0e7ff' }}>
    {assign.employee_id}
  </td>

  <td style={{ padding: '15px', fontSize: '14px', color: '#cbd5e1' }}>
    {assign.device_id}
  </td>

  <td style={{ padding: '15px', fontSize: '14px', color: '#cbd5e1' }}>
    {new Date(assign.assigned_date).toLocaleDateString()}
  </td>

  <td style={{ padding: '15px', textAlign: 'center' }}>
    <button
      style={{
        background: '#3b82f6',
        color: 'white',
        border: 'none',
        borderRadius: '5px',
        padding: '6px 12px',
        cursor: 'pointer',
        marginRight: '8px'
      }}
    >
      ✏ Edit
    </button>

    <button
  onClick={() => deleteAssignment(assign.id)}
  style={{
    background: '#ef4444',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    padding: '6px 12px',
    cursor: 'pointer'
  }}
>
  🗑 Delete
</button>
  </td>
</tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={4} style={{ padding: '30px', textAlign: 'center', color: '#64748b' }}>
                        No assignments. Click "+ Assign Device" to create one.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {showAssignment && (
              <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                <div style={{ background: 'linear-gradient(135deg, #1a1f35 0%, #2d3748 100%)', padding: '30px', borderRadius: '12px', width: '100%', maxWidth: '400px', border: '1px solid rgba(59,130,246,0.3)' }}>
                  <h2 style={{ margin: '0 0 20px 0', color: '#60a5fa' }}>Assign Device to Employee</h2>
                  <select value={assignmentForm.employee_id} onChange={(e) => setAssignmentForm({ ...assignmentForm, employee_id: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '15px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }}>
                    <option value="">Select Employee</option>
                    {employees.map((emp) => (
                      <option key={emp.employee_id} value={emp.employee_id}>
                        {emp.name} ({emp.employee_id})
                      </option>
                    ))}
                  </select>
                  <select value={assignmentForm.device_id} onChange={(e) => setAssignmentForm({ ...assignmentForm, device_id: e.target.value })} style={{ width: '100%', padding: '12px', marginBottom: '20px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }}>
                    <option value="">Select Device</option>
                    {devices.map((dev) => (
                      <option key={dev.device_id} value={dev.device_id}>
                        {dev.hostname} ({dev.ip_address})
                      </option>
                    ))}
                  </select>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button onClick={() => setShowAssignment(false)} style={{ flex: 1, padding: '10px', background: 'rgba(255,255,255,0.1)', color: '#e0e7ff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
                      Cancel
                    </button>
                    <button onClick={assignDevice} disabled={loading || !assignmentForm.employee_id || !assignmentForm.device_id} style={{ flex: 1, padding: '10px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
                      {loading ? 'Assigning...' : 'Assign'}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* LIVE MONITORING TAB */}
        {activeTab === 'monitoring' && (
          <div>
            <h2 style={{ color: '#e0e7ff', marginBottom: '20px' }}>📡 Live Employee Monitoring</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
              {employeeMonitoring.length > 0 ? (
                employeeMonitoring.map((emp) => (
                  <div key={emp.employee_id} style={{ background: `linear-gradient(135deg, ${emp.color}20 0%, ${emp.color}05 100%)`, border: `1px solid ${emp.color}40`, borderRadius: '12px', padding: '20px', transition: 'all 0.3s' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '15px' }}>
                      <div>
                        <h3 style={{ margin: '0 0 5px 0', color: '#e0e7ff', fontSize: '16px', fontWeight: 'bold' }}>{emp.name}</h3>
                        <p style={{ margin: '0', color: '#cbd5e1', fontSize: '12px' }}>{emp.employee_id}</p>
                      </div>
                      <span style={{ display: 'inline-block', background: emp.color, color: 'white', padding: '6px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 'bold' }}>
                        {emp.status}
                      </span>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '15px' }}>
                      <div style={{ background: 'rgba(255,255,255,0.05)', padding: '10px', borderRadius: '6px' }}>
                        <p style={{ margin: '0', color: '#94a3b8', fontSize: '12px' }}>Devices</p>
                        <p style={{ margin: '5px 0 0 0', color: '#e0e7ff', fontSize: '18px', fontWeight: 'bold' }}>{emp.device_count}</p>
                      </div>
                      <div style={{ background: 'rgba(255,255,255,0.05)', padding: '10px', borderRadius: '6px' }}>
                        <p style={{ margin: '0', color: '#94a3b8', fontSize: '12px' }}>Threats</p>
                        <p style={{ margin: '5px 0 0 0', color: '#e0e7ff', fontSize: '18px', fontWeight: 'bold' }}>{emp.threat_count}</p>
                      </div>
                    </div>
                    <div style={{ background: 'rgba(255,255,255,0.05)', padding: '10px', borderRadius: '6px' }}>
                      <p style={{ margin: '0', color: '#94a3b8', fontSize: '12px' }}>Risk Score</p>
                      <div style={{ margin: '8px 0 0 0', background: 'rgba(255,255,255,0.1)', borderRadius: '4px', height: '8px', overflow: 'hidden' }}>
                        <div style={{ background: emp.color, height: '100%', width: `${emp.risk_score}%`, transition: 'all 0.3s' }} />
                      </div>
                      <p style={{ margin: '5px 0 0 0', color: '#cbd5e1', fontSize: '12px' }}>{emp.risk_score.toFixed(1)}%</p>
                    </div>
                  </div>
                ))
              ) : (
                <div style={{ gridColumn: '1 / -1', padding: '40px', textAlign: 'center', color: '#64748b' }}>
                  No employees to monitor. Add employees first.
                </div>
              )}
            </div>
          </div>
        )}

        {/* THREATS TAB */}
        {activeTab === 'threats' && (
          <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 10px 30px rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.1)' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: 'rgba(255,255,255,0.08)', borderBottom: '2px solid rgba(59,130,246,0.3)' }}>
                  <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>Threat ID</th>
                  <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>Device</th>
                  <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>Type</th>
                  <th style={{ padding: '15px', textAlign: 'left', fontWeight: 'bold', fontSize: '14px', color: '#e0e7ff' }}>Severity</th>
                </tr>
              </thead>
              <tbody>
                {threats.length > 0 ? (
                  threats.map((threat, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                      <td style={{ padding: '15px', fontSize: '14px', fontWeight: '500', color: '#e0e7ff' }}>{threat.threat_id}</td>
                      <td style={{ padding: '15px', fontSize: '14px', color: '#cbd5e1' }}>{threat.device_id}</td>
                      <td style={{ padding: '15px', fontSize: '14px', color: '#cbd5e1' }}>{threat.threat_type}</td>
                      <td style={{ padding: '15px', fontSize: '14px' }}>
                        <span style={{ display: 'inline-block', background: threat.severity === 'Critical' ? 'rgba(239,68,68,0.2)' : threat.severity === 'High' ? 'rgba(245,158,11,0.2)' : 'rgba(34,197,94,0.2)', color: threat.severity === 'Critical' ? '#fca5a5' : threat.severity === 'High' ? '#fcd34d' : '#86efac', padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 'bold' }}>
                          {threat.severity === 'Critical' ? '🔴' : threat.severity === 'High' ? '🟠' : '🟢'} {threat.severity}
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} style={{ padding: '30px', textAlign: 'center', color: '#64748b' }}>
                      ✅ No threats detected. System is secure.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
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
                  <input
                    type="text"
                    placeholder="smtp.gmail.com"
                    value={settings.smtp_server}
                    onChange={(e) => setSettings({ ...settings, smtp_server: e.target.value })}
                    style={{ width: '100%', padding: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', color: '#cbd5e1', marginBottom: '8px', fontSize: '14px', fontWeight: 'bold' }}>SMTP Port</label>
                  <input
                    type="number"
                    placeholder="587"
                    value={settings.smtp_port}
                    onChange={(e) => setSettings({ ...settings, smtp_port: parseInt(e.target.value) })}
                    style={{ width: '100%', padding: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', color: '#cbd5e1', marginBottom: '8px', fontSize: '14px', fontWeight: 'bold' }}>Email Address</label>
                  <input
                    type="email"
                    placeholder="your-email@gmail.com"
                    value={settings.smtp_email}
                    onChange={(e) => setSettings({ ...settings, smtp_email: e.target.value })}
                    style={{ width: '100%', padding: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', color: '#cbd5e1', marginBottom: '8px', fontSize: '14px', fontWeight: 'bold' }}>App Password</label>
                  <input
                    type="password"
                    placeholder="Your Gmail App Password"
                    value={settings.smtp_password}
                    onChange={(e) => setSettings({ ...settings, smtp_password: e.target.value })}
                    style={{ width: '100%', padding: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }}
                  />
                  <p style={{ margin: '8px 0 0 0', color: '#94a3b8', fontSize: '12px' }}>💡 Generate App Password from Google Account Security Settings</p>
                </div>
                <div>
                  <label style={{ display: 'block', color: '#cbd5e1', marginBottom: '8px', fontSize: '14px', fontWeight: 'bold' }}>Admin Email</label>
                  <input
                    type="email"
                    placeholder="admin@company.com"
                    value={settings.admin_email}
                    onChange={(e) => setSettings({ ...settings, admin_email: e.target.value })}
                    style={{ width: '100%', padding: '12px', border: '1px solid rgba(59,130,246,0.5)', borderRadius: '6px', boxSizing: 'border-box', fontSize: '14px', background: 'rgba(255,255,255,0.05)', color: '#e0e7ff' }}
                  />
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

              <div style={{ marginTop: '30px', padding: '20px', background: 'rgba(59,130,246,0.1)', borderRadius: '8px', border: '1px solid rgba(59,130,246,0.3)' }}>
                <h4 style={{ color: '#60a5fa', margin: '0 0 10px 0' }}>📖 Gmail Setup Guide</h4>
                <ol style={{ margin: '0', paddingLeft: '20px', color: '#cbd5e1', fontSize: '13px', lineHeight: '1.8' }}>
                  <li>Go to Google Account Security Settings</li>
                  <li>Enable 2-Factor Authentication</li>
                  <li>Generate an App Password for "Mail"</li>
                  <li>Use the app password in the field above</li>
                  <li>SMTP Server: smtp.gmail.com</li>
                  <li>SMTP Port: 587</li>
                </ol>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
