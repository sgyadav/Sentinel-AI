# SENTINEL AI - LOGIN CREDENTIALS & STARTUP GUIDE

## 🔐 LOGIN CREDENTIALS

```
Username: admin
Password: Admin1234
```

**These are your login credentials. Keep them safe!**

---

## 🚀 QUICK START - 3 STEPS

### Step 1: Start Backend (FastAPI)

Open a **Command Prompt** or **PowerShell** and run:

```bash
cd "C:\Users\Administrator\Desktop\Sentinel AI\backend"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started server process
INFO:     Application startup complete
```

**Keep this terminal open while using the application.**

---

### Step 2: Start Frontend (React) - NEW TERMINAL

Open a **NEW Command Prompt** or **PowerShell** and run:

```bash
cd "C:\Users\Administrator\Desktop\Sentinel AI\frontend"
npm run dev
```

**Expected Output:**
```
  VITE v... build ...
  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

**Keep this terminal open while using the application.**

---

### Step 3: Login

1. **Open Browser**: http://localhost:5173
2. **Enter Credentials**:
   - Username: `admin`
   - Password: `Admin1234`
3. **Click LOGIN**
4. **You're In!** 🎉

---

## ✅ IF LOGIN SAYS "FAILED"

### Issue 1: Backend Not Running

**Check if port 8000 is responding:**
```bash
curl http://localhost:8000/health
```

**If no response:**
1. Make sure Step 1 is completed
2. Check that backend terminal shows `Uvicorn running on...`
3. If port is in use:
   ```bash
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

### Issue 2: Frontend Can't Connect to Backend

**Solution:**
1. Make sure browser can access: http://localhost:8000/health
2. Check browser Console (F12) for errors
3. Try hard refresh: `Ctrl+Shift+R`
4. Clear localStorage:
   ```javascript
   // In browser console (F12)
   localStorage.clear()
   location.reload()
   ```

### Issue 3: "Invalid Credentials"

**Check database has admin user:**
```bash
cd "C:\Users\Administrator\Desktop\Sentinel AI\backend"
python init_db.py
```

If prompted to reset, type `y`

Then try logging in again.

---

## 📱 SYSTEM REQUIREMENTS

- Windows 10/11 or Linux/Mac
- Python 3.8+ 
- Node.js 16+
- 2GB RAM minimum
- Ports available: 5173 (frontend), 8000 (backend)

---

## 🌐 ACCESS URLS

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | http://localhost:5173 | Browser access |
| **Backend API** | http://localhost:8000 | API server |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **API Redoc** | http://localhost:8000/redoc | ReDoc UI |

---

## 🎯 WHAT YOU CAN DO AFTER LOGIN

### Dashboard
- View summary metrics (employees, devices, incidents, status)
- See real-time updates

### Employees Tab
- Add new employees
- View all employees
- Edit employee information
- Delete employees
- Track employee data

### Devices Tab
- Register new devices
- View all registered devices
- Edit device information
- Delete devices
- See device status

### Device Assignment Tab
- Assign devices to employees
- View assignments
- Track which employee has which device

### Incidents Tab
- View all security incidents
- See incident details
- Track incident status

### Events Tab
- Report security events
- Specify event type
- Set severity level
- Add description

### Settings Tab
- Change password
- Configure security policies
- Manage system settings

---

## 🔑 PASSWORD CHANGE (RECOMMENDED)

After first login:

1. Click **Settings** (bottom left in sidebar)
2. Click **Change Password**
3. Enter:
   - Current: `Admin1234`
   - New: Your secure password
   - Confirm: Your secure password
4. Click **Update**
5. You're now secure!

---

## 🛑 STOP THE APPLICATION

When you're done:

1. In backend terminal: Press `Ctrl+C`
2. In frontend terminal: Press `Ctrl+C`
3. Both services will stop

---

## 🔧 TROUBLESHOOTING

### Backend won't start

```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# If in use, kill the process
taskkill /PID <PID> /F

# Try again
python -m uvicorn main:app --port 8000
```

### Frontend won't start

```bash
# Try clearing npm cache
npm cache clean --force

# Reinstall dependencies
cd frontend
rm -r node_modules
npm install

# Try again
npm run dev
```

### Reset everything

```bash
# Backend
cd backend
del sentinel.db
python init_db.py

# Frontend
cd ..\frontend
npm run dev
```

---

## 📊 TEST THE API

### Check Health
```bash
curl http://localhost:8000/health
```

### Test Login
```bash
curl -X POST http://localhost:8000/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"password\":\"Admin1234\"}"
```

### Get Employees
```bash
curl http://localhost:8000/employees
```

---

## 💡 TIPS

1. **Keep terminals open** - Don't close them while using the app
2. **Bookmark URLs** - Save http://localhost:5173 in bookmarks
3. **Check console** - Press F12 in browser for error messages
4. **Check backend logs** - Watch the backend terminal for any errors
5. **Use API docs** - Visit http://localhost:8000/docs for API reference

---

## 📞 SUPPORT

If you encounter issues:

1. **Check logs** - Look at terminal output for error messages
2. **Try fresh start** - Stop and restart both services
3. **Reset database** - Delete `sentinel.db` and reinitialize
4. **Check ports** - Ensure 5173 and 8000 are available

---

##  SUCCESS CHECKLIST

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Browser opens http://localhost:5173
- [ ] Login page shows
- [ ] Enter admin / Admin1234
- [ ] Successfully logged in
- [ ] See dashboard with employees/devices
- [ ] Can navigate tabs
- [ ] System working!

---

**Version**: 1.0.0  
**Last Updated**: 2026-07-09  
**Status**: Ready to Use ✅

**NEXT: Follow the 3 steps above to get started!**
