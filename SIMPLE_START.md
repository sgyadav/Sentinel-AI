# 🚀 SENTINEL AI - SIMPLE START GUIDE

## ⚡ FASTEST WAY - 2 FILES TO DOUBLE-CLICK

### Option 1: Start Everything Automatically
**Double-click this file:**
```
START_ALL.bat
```

This will:
1. Start Backend (port 8000)
2. Start Frontend (port 5173)
3. Open browser automatically
4. Show login page

Then login with:
```
Username: admin
Password: Admin1234
```

---

### Option 2: Start Separately

**First - Double-click:**
```
START_BACKEND.bat
```

**Then - In a NEW window, double-click:**
```
START_FRONTEND.bat
```

**Then - Open browser:**
```
http://localhost:5173
```

---

## 🔐 LOGIN

```
Username: admin
Password: Admin1234
```

---

## 📊 ALL FEATURES WORKING

✅ Add Employee - Click "Add Employee", fill form, click "Add"  
✅ Edit Employee - Click Edit icon, modify, click "Update"  
✅ Delete Employee - Click Delete icon, confirm  
✅ Add Device - Click "Register Device", fill form  
✅ Edit Device - Click Edit icon, modify, click "Update"  
✅ Delete Device - Click Delete icon, confirm  
✅ Assign Devices - Select employee and device, click "Assign"  
✅ View Threats - Real threats in real-time  
✅ Dashboard - Live metric updates  

---

## 🎨 UI/UX

- Beautiful purple gradient design
- Professional login page
- Color-coded status indicators
- Smooth animations
- Real-time auto-refresh (5 seconds)
- Responsive design
- Easy-to-use dialogs

---

## 📱 TABS AVAILABLE

1. **Dashboard** - Overview metrics
2. **Employees** - Add/Edit/Delete employees
3. **Devices** - Register/Edit/Delete devices
4. **Assignments** - Assign devices to employees
5. **Threats** - View detected threats

---

## 🌐 URLs

```
Frontend:  http://localhost:5173
Backend:   http://localhost:8000
API Docs:  http://localhost:8000/docs
Health:    http://localhost:8000/health
```

---

## ❌ STOP THE APPLICATION

1. Close the "SENTINEL AI - Backend" window
2. Close the "SENTINEL AI - Frontend" window

Done!

---

## 🆘 IF SOMETHING DOESN'T WORK

### Frontend won't start
- Make sure Backend is running first
- Wait 5 seconds after backend starts
- Check if port 5173 is free
- Try: `netstat -ano | findstr :5173`

### Backend won't start
- Check if port 8000 is free
- Try: `netstat -ano | findstr :8000`
- Make sure Python is installed

### Login fails
- Verify backend is running: `http://localhost:8000/health`
- Use correct credentials: `admin` / `Admin1234`
- Clear browser cache (Ctrl+Shift+Delete)

### Can't add employee
- Make sure all fields are filled
- Check browser console (F12) for errors
- Verify backend is running

---

## ✨ QUICK TEST

1. Double-click `START_ALL.bat`
2. Wait for browser to open
3. Login with admin/Admin1234
4. Go to "Employees" tab
5. Click "Add Employee"
6. Fill:
   - ID: TEST001
   - Name: Test User
   - Email: test@company.com
   - Department: Testing
   - Designation: QA
7. Click "Add"
8. ✅ Employee appears in table

---

**THAT'S IT! YOUR SYSTEM IS READY! 🎉**

Enjoy SENTINEL AI!
