# 🎯 SENTINEL AI - COMPLETE WORKING SYSTEM

## ✅ LOGIN CREDENTIALS

```
Username: admin
Password: Admin1234
```

---

## 🚀 FASTEST WAY TO START (Windows)

**Double-click this file:**
```
RUN_SENTINEL_AI.bat
```

That's it! The system will:
1. Start backend API on port 8000
2. Start frontend on port 5173
3. Open browser automatically
4. You'll see login screen

---

## 📝 MANUAL START (If batch file doesn't work)

### Terminal 1 - Backend
```bash
cd "C:\Users\Administrator\Desktop\Sentinel AI\backend"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Wait for:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Terminal 2 - Frontend
```bash
cd "C:\Users\Administrator\Desktop\Sentinel AI\frontend"
npm run dev
```

Wait for:
```
➜  Local:   http://localhost:5173/
```

### Terminal 3 - Access
Open browser: **http://localhost:5173**

---

## 🔐 LOGIN

**Username:** admin  
**Password:** Admin1234

Click LOGIN

---

## ✨ FEATURES WORKING

### Dashboard Tab
- Overview of total employees, devices, incidents
- System status
- Real-time updates every 5 seconds

### Employees Tab
- ✅ **ADD** - Create new employee (Employee ID, Name, Email, Department, Designation)
- ✅ **EDIT** - Click edit icon to modify employee details
- ✅ **DELETE** - Click delete icon to remove employee
- ✅ Table view of all employees
- ✅ Real-time list updates

### Devices Tab
- ✅ **ADD** - Register new device (Hostname, IP Address, OS)
- ✅ **EDIT** - Click edit icon to modify device info
- ✅ **DELETE** - Click delete icon to remove device
- ✅ Table view of all devices
- ✅ Real-time list updates

### Incidents Tab
- View all security incidents
- Incident details (ID, Hostname, Attack Type, Risk Score, Status)
- Real-time incident updates

### Settings Tab
- ✅ **CHANGE PASSWORD** - Click button to open password change dialog
  - Enter old password (Admin1234)
  - Enter new password (min 8 chars)
  - Confirm new password
  - Click Change

---

## 🌐 ACCESS URLS

| Service | URL |
|---------|-----|
| **Frontend Dashboard** | http://localhost:5173 |
| **Backend API** | http://localhost:8000 |
| **API Swagger Docs** | http://localhost:8000/docs |
| **API Health Check** | http://localhost:8000/health |

---

## 📊 API ENDPOINTS

### Authentication
- `POST /auth/login` - Login with username/password
- `POST /auth/signup` - Create new user account
- `POST /auth/change-password` - Change password
- `GET /auth/me` - Get current user info

### Employees
- `GET /employees` - Get all employees
- `POST /employees` - Create employee
- `PUT /employees/{employee_id}` - Update employee
- `DELETE /employees/{employee_id}` - Delete employee

### Devices
- `GET /devices` - Get all devices
- `POST /devices` - Create device
- `PUT /devices/{hostname}` - Update device
- `DELETE /devices/{hostname}` - Delete device

### Incidents
- `GET /incidents` - Get all incidents
- `POST /event` - Report security event
- `GET /events` - Get all events

### Dashboard
- `GET /dashboard` - Get dashboard data

---

## 🎯 STEP-BY-STEP WORKFLOW

### 1. Login
- Username: `admin`
- Password: `Admin1234`
- Click LOGIN

### 2. Add Employee
1. Click "Employees" tab
2. Click "Add Employee" button
3. Fill in:
   - Employee ID: `EMP001`
   - Name: `John Doe`
   - Email: `john@company.com`
   - Department: `IT Security`
   - Designation: `Security Officer`
4. Click "Add"
5. Employee appears in table

### 3. Add Device
1. Click "Devices" tab
2. Click "Add Device" button
3. Fill in:
   - Hostname: `PC-JOHN`
   - IP Address: `192.168.1.100`
   - Operating System: `Windows 10`
4. Click "Add"
5. Device appears in table

### 4. Edit Employee
1. Click "Employees" tab
2. Find employee in table
3. Click Edit icon (pencil)
4. Modify details
5. Click "Update"
6. Changes saved

### 5. Edit Device
1. Click "Devices" tab
2. Find device in table
3. Click Edit icon (pencil)
4. Modify IP or OS
5. Click "Update"
6. Changes saved

### 6. Delete Employee
1. Click "Employees" tab
2. Find employee in table
3. Click Delete icon (trash)
4. Confirm deletion
5. Employee removed from table

### 7. Delete Device
1. Click "Devices" tab
2. Find device in table
3. Click Delete icon (trash)
4. Confirm deletion
5. Device removed from table

### 8. Change Password
1. Click "Settings" tab
2. Click "Change Password" button
3. Enter:
   - Old Password: `Admin1234`
   - New Password: `YourNewPassword123`
   - Confirm: `YourNewPassword123`
4. Click "Change"
5. Password updated successfully

---

## 🔄 REAL-TIME MONITORING

Dashboard automatically refreshes every 5 seconds showing:
- Employee count
- Device count
- Incident count
- System status

---

## 🛑 STOPPING THE APPLICATION

### If using batch file:
- Close the two command windows that opened

### If using manual terminals:
- In each terminal, press `Ctrl+C`

---

## 🐛 TROUBLESHOOTING

### "Login Failed" Error

**Solution 1: Check Backend is Running**
```bash
# In new terminal, test backend
curl http://localhost:8000/health

# Should return: {"status": "healthy", ...}
```

**Solution 2: Check Port 8000 is Available**
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill it (replace PID with actual number)
taskkill /PID <PID> /F

# Restart backend
python -m uvicorn main:app --port 8000
```

**Solution 3: Reset Database**
```bash
cd backend
del sentinel.db
python init_db.py
```

### "Connection Refused" Error

**Solution:**
1. Make sure Terminal 1 (Backend) is running
2. Wait 5 seconds after starting backend
3. Try refreshing browser (F5)
4. Check http://localhost:8000/health loads

### Frontend Won't Start

**Solution:**
```bash
cd frontend
npm cache clean --force
rm -r node_modules
npm install
npm run dev
```

---

## 📋 CHECKLIST

When system is running, verify:

- [ ] http://localhost:5173 loads in browser
- [ ] Login page appears with fields
- [ ] No "demo" text showing on login
- [ ] Login with admin/Admin1234 works
- [ ] Dashboard shows 4 metric cards
- [ ] Can switch between tabs
- [ ] Can add employees
- [ ] Can edit employees
- [ ] Can delete employees
- [ ] Can add devices
- [ ] Can edit devices
- [ ] Can delete devices
- [ ] Change password button visible
- [ ] Real-time updates working (check timestamp)

---

## 🎓 TESTING EMPLOYEE ADD

1. Click "Employees" tab
2. Click "Add Employee"
3. Enter:
   - ID: `TEST001`
   - Name: `Test User`
   - Email: `test@company.com`
   - Department: `Testing`
   - Designation: `QA`
4. Click "Add"
5. Should see in table immediately

---

## 🎓 TESTING DEVICE ADD

1. Click "Devices" tab
2. Click "Add Device"
3. Enter:
   - Hostname: `PC-TEST`
   - IP: `192.168.1.200`
   - OS: `Windows 11`
4. Click "Add"
5. Should see in table immediately

---

## 🎓 TESTING PASSWORD CHANGE

1. Click "Settings" tab
2. Click "Change Password"
3. Enter:
   - Old: `Admin1234`
   - New: `NewPass123`
   - Confirm: `NewPass123`
4. Click "Change"
5. Should see success message
6. Next login use `NewPass123`

---

## 📊 REAL-TIME FEATURES

- ✅ Dashboard updates every 5 seconds
- ✅ Employee list updates instantly
- ✅ Device list updates instantly
- ✅ Incidents display in real-time
- ✅ Add/Edit/Delete happens immediately
- ✅ No page refresh needed

---

## 🔐 SECURITY

- JWT token-based authentication
- Password encrypted with SHA256
- All API calls require token
- Session expires after 8 hours
- Account lockout after 5 failed attempts

---

## 📞 SUPPORT

**If something doesn't work:**

1. Check backend terminal for errors
2. Check browser console (F12)
3. Try stopping and restarting
4. Delete database and reinitialize
5. Clear browser cache (Ctrl+Shift+Delete)

---

## 📝 FILES STRUCTURE

```
Sentinel AI/
├── backend/
│   ├── main.py              # Complete API
│   ├── init_db.py           # Database setup
│   ├── sentinel.db          # SQLite database
│   ├── requirements.txt      # Python packages
│   ├── auth/                # Authentication
│   ├── db/                  # Database models
│   └── services/            # Business logic
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Complete app (Add/Edit/Delete working)
│   │   ├── App.css          # Styling
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── RUN_SENTINEL_AI.bat      # Start everything
├── docker-compose.yml
└── README.md                # This file
```

---

## ✅ SYSTEM STATUS

- Backend API: ✅ Working
- Frontend UI: ✅ Working
- Database: ✅ Working
- Authentication: ✅ Working
- Add/Edit/Delete: ✅ Working
- Password Change: ✅ Working
- Real-Time Updates: ✅ Working
- No Demo Text: ✅ Clean

---

## 🎉 YOU'RE READY!

**Run:** `RUN_SENTINEL_AI.bat`

**Login:** `admin` / `Admin1234`

**Enjoy your working Cyber Defense System!**

---

**Version:** 1.0.0  
**Status:** Production Ready ✅  
**Last Updated:** 2026-07-09
