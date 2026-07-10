# ⚡ QUICK START - 30 SECONDS

## 1️⃣ Run This File
```
Double-click: RUN_SENTINEL_AI.bat
```

## 2️⃣ Wait for Browser
Should open automatically at:
```
http://localhost:5173
```

## 3️⃣ Login
```
Username: admin
Password: Admin1234
```

## ✅ Done!

---

## What's Working

✅ Login/Logout  
✅ Add Employees (with form)  
✅ Edit Employees  
✅ Delete Employees  
✅ Add Devices (with form)  
✅ Edit Devices  
✅ Delete Devices  
✅ View Incidents  
✅ Change Password  
✅ Real-time updates (5 sec)  
✅ Professional UI  

---

## Tabs Available

1. **Dashboard** - Overview metrics
2. **Employees** - Manage employees
3. **Devices** - Manage devices
4. **Incidents** - View security incidents
5. **Settings** - Change password

---

## Need Help?

**Backend not starting:**
```bash
cd backend
python -m uvicorn main:app --port 8000
```

**Frontend not starting:**
```bash
cd frontend
npm run dev
```

**Reset everything:**
```bash
del backend\sentinel.db
python backend\init_db.py
```

---

**That's it! System is ready to use.**
