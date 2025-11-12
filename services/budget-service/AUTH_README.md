# Authentication & Authorization System

This document describes the authentication and authorization system implemented in the FinCloud Budget Service.

## Features

✅ JWT-based authentication
✅ Password hashing with bcrypt
✅ User registration and login
✅ Token refresh functionality
✅ Role-Based Access Control (RBAC)
✅ User profile management
✅ Password reset functionality
✅ Protected route middleware

## Architecture

### Components

1. **Security Utilities** (`app/core/security.py`)
   - Password hashing and verification (bcrypt)
   - JWT token generation (access & refresh tokens)
   - Token decoding and validation

2. **Authentication Middleware** (`app/core/auth.py`)
   - `get_current_user`: Extract and validate user from JWT token
   - `get_current_active_user`: Ensure user is active
   - `get_current_verified_user`: Ensure user email is verified
   - `RoleChecker`: RBAC dependency for role-based access control

3. **Authentication Service** (`app/services/auth_service.py`)
   - User registration logic
   - User authentication (login)
   - Token creation and refresh
   - Password management

4. **Pydantic Schemas** (`app/schemas/auth.py`)
   - Request/response models with validation
   - Password strength validation
   - Email format validation

5. **API Endpoints**
   - `app/api/v1/endpoints/auth.py`: Authentication endpoints
   - `app/api/v1/endpoints/users.py`: User profile management
   - `app/api/v1/endpoints/password_reset.py`: Password reset

## API Endpoints

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Register new user | No |
| POST | `/login` | Login and get tokens | No |
| POST | `/refresh` | Refresh access token | No |
| GET | `/me` | Get current user info | Yes |
| POST | `/logout` | Logout user | Yes |

### User Management (`/api/v1/users`)

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| GET | `/profile` | Get user profile | Yes | Any |
| PATCH | `/profile` | Update user profile | Yes | Any |
| POST | `/change-password` | Change password | Yes | Any |
| DELETE | `/account` | Delete account (soft) | Yes | Any |
| GET | `/{user_id}` | Get user by ID | Yes | Admin |
| PATCH | `/{user_id}/role` | Update user role | Yes | Admin |
| PATCH | `/{user_id}/activate` | Activate user | Yes | Admin |

### Password Reset (`/api/v1/password-reset`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/request` | Request password reset | No |
| POST | `/reset` | Reset password with token | No |

## User Roles

The system supports three roles with different access levels:

- **user** (default): Standard user access
- **premium**: Premium features access
- **admin**: Full system access including user management

## Authentication Flow

### 1. Registration

```bash
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "preferred_currency": "USD",
  "timezone": "UTC"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

### 2. Login

```bash
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Making Authenticated Requests

Include the access token in the Authorization header:

```bash
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

### 4. Token Refresh

When the access token expires (default: 30 minutes):

```bash
POST /api/v1/auth/refresh
{
  "refresh_token": "<refresh_token>"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Role-Based Access Control (RBAC)

### Protecting Endpoints by Role

Use the `RoleChecker` dependency to restrict access:

```python
from app.core.auth import RoleChecker

@router.get("/admin-only", dependencies=[Depends(RoleChecker(["admin"]))])
async def admin_endpoint():
    return {"message": "Admin access"}
```

### Convenience Dependencies

```python
from app.core.auth import require_admin, require_premium

# Admin only
@router.get("/admin", dependencies=[require_admin])
async def admin_endpoint():
    pass

# Premium or Admin
@router.get("/premium", dependencies=[require_premium])
async def premium_endpoint():
    pass
```

## Configuration

Update `.env` file with secure values:

```env
# Security
JWT_SECRET=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**⚠️ IMPORTANT:** Change `JWT_SECRET` to a strong, random value in production!

Generate a secure secret:
```bash
openssl rand -hex 32
```

## Database Migration

To add the role field to existing databases:

```bash
cd services/budget-service
alembic upgrade head
```

Migration file: `alembic/versions/8b3e94f12a11_add_role_field_to_users.py`

## Security Best Practices

1. **JWT Secret**: Use a strong, random secret key in production
2. **HTTPS**: Always use HTTPS in production to protect tokens
3. **Token Storage**: Store tokens securely on the client (httpOnly cookies or secure storage)
4. **Token Expiration**: Keep access token expiration short (15-30 minutes)
5. **Password Policy**: Enforce strong passwords
6. **Rate Limiting**: Implement rate limiting on auth endpoints (TODO)
7. **Email Verification**: Enable email verification in production (TODO)

## Testing with Swagger UI

1. Start the service: `uvicorn app.main:app --reload`
2. Open: http://localhost:8001/docs
3. Register a user via `/api/v1/auth/register`
4. Login via `/api/v1/auth/login` to get tokens
5. Click "Authorize" button in Swagger UI
6. Enter: `Bearer <access_token>`
7. Test protected endpoints

## Example: Complete User Journey

```bash
# 1. Register
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123",
    "first_name": "Test",
    "last_name": "User"
  }'

# 2. Login
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'

# Response: Save the access_token and refresh_token

# 3. Get profile
curl -X GET http://localhost:8001/api/v1/users/profile \
  -H "Authorization: Bearer <access_token>"

# 4. Update profile
curl -X PATCH http://localhost:8001/api/v1/users/profile \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Updated",
    "preferred_currency": "EUR"
  }'

# 5. Change password
curl -X POST http://localhost:8001/api/v1/users/change-password \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "SecurePass123",
    "new_password": "NewSecurePass456"
  }'
```

## Future Enhancements

- [ ] Email verification with email service integration
- [ ] Rate limiting on authentication endpoints
- [ ] Token blacklist/revocation (Redis-based)
- [ ] OAuth2 integration (Google, GitHub, etc.)
- [ ] Two-factor authentication (2FA)
- [ ] Account lockout after failed login attempts
- [ ] Audit logging for security events
- [ ] Session management

## Troubleshooting

### "Could not validate credentials"
- Token might be expired or invalid
- Check if token is properly formatted: `Bearer <token>`
- Verify JWT_SECRET matches between token generation and validation

### "Inactive user account"
- User account has been deactivated
- Admin needs to reactivate: `PATCH /api/v1/users/{user_id}/activate`

### "Email already registered"
- Email is already in use
- Use password reset if you forgot your password

### "Access denied. Required roles: ..."
- Your user role doesn't have permission
- Contact admin to update your role if needed
