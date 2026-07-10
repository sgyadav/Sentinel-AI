# ✅ LOGIN CREDENTIALS - SENTINEL AI

## Admin Account Created Successfully ✅

### Login Credentials
```
Username: admin
Password: Admin1234
Email: admin@example.com
Role: Admin
```

---

## How to Login

### Via Web Browser
1. Open: **http://localhost:5173**
2. Enter username: `admin`
3. Enter password: `Admin1234`
4. Click **Login**

### Via API
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin1234"}'
```

**Response:**
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 28800,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "Admin",
    "organization": "Sentinel AI",
    "is_active": true,
    "created_at": "2026-07-09T..."
  }
}
```

---

## System Access URLs

| Service | URL | Status |
|---------|-----|--------|
| Frontend Dashboard | http://localhost:5173 | ✅ Running |
| Backend API | http://localhost:8000 | ✅ Running |
| API Documentation | http://localhost:8000/api/docs | ✅ Available |
| Health Check | http://localhost:8000/health | ✅ OK |
| Auth Status | http://localhost:8000/auth/status | ✅ Operational |

---

## Using JWT Token

After login, use the access token for authenticated requests:

```bash
# Get dashboard data
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/realtime/dashboard/overview

# Get threats
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/realtime/stats/threats

# Get devices
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/realtime/stats/devices
```

---

## Create Additional Users

### Register New Admin
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin2",
    "email": "admin2@example.com",
    "password": "Admin2Pass123",
    "role": "Admin"
  }'
```

### Register Regular User
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user1",
    "email": "user1@example.com",
    "password": "UserPass123",
    "role": "User"
  }'
```

---

## Password Requirements

- **Minimum Length**: 8 characters
- **Maximum Length**: 100 characters
- No special requirements (simplified for testing)

---

## Dashboard After Login

You'll see:
- ✅ Employee count and metrics
- ✅ Device status (online/offline)
- ✅ Incident tracking
- ✅ Threat visualizations
- ✅ Real-time updates (WebSocket)

---

## Troubleshooting

### Can't Login?
1. Check backend is running: `docker-compose ps`
2. Check backend logs: `docker-compose logs backend`
3. Verify credentials are correct
4. Try creating a new account

### Forgot Password?
1. Delete database: `docker-compose down -v`
2. Restart services: `docker-compose up -d`
3. Create new admin account (above)

### WebSocket Connection Issues?
1. Check frontend console (F12)
2. Verify WebSocket URL: `ws://localhost:8000/ws/...`
3. Check browser security/firewall settings

---

## Account Management

### Change Password
```bash
curl -X POST http://localhost:8000/auth/change-password \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "Admin1234",
    "new_password": "NewPass123"
  }'
```

### Verify Token
```bash
curl -X POST http://localhost:8000/auth/verify-token \
  -H "Authorization: Bearer <token>"
```

### Get Current User Info
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer <token>"
```

### Logout
```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer <token>"
```

---

## Next Steps

1. ✅ Login to dashboard
2. ✅ Explore employee management
3. ✅ Register devices
4. ✅ Create security events
5. ✅ Monitor real-time threats
6. ✅ Manage incidents
7. ✅ View analytics

---

**Status**: ✅ **READY TO USE**

**Last Updated**: 2026-07-09

**Support**: Contact via GitHub Issues
