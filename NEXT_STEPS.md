# Next Steps - Getting Started with Development

> Quick reference guide for immediate next actions

## 🚀 Immediate Actions (Week 1)

### 1. Set Up Your Development Environment

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/silviu-suhoverschi/FinCloud.git
cd FinCloud

# Set up environment variables
cp .env.example .env

# Edit .env and add your configuration
# Required:
# - JWT_SECRET (generate with: openssl rand -hex 32)
# - Database credentials
# Optional but recommended:
# - ALPHA_VANTAGE_API_KEY (get free at https://www.alphavantage.co/support/#api-key)

# Start development environment
docker-compose up -d

# Check that all services are running
docker-compose ps

# View logs
docker-compose logs -f
```

### 2. Verify Setup

After services start, verify each component:

```bash
# Backend services health checks
curl http://localhost:8000/health  # API Gateway
curl http://localhost:8001/health  # Budget Service
curl http://localhost:8002/health  # Portfolio Service
curl http://localhost:8003/health  # Notification Service

# Frontend
open http://localhost:3000

# API Documentation
open http://localhost:8001/docs  # Budget Service API
open http://localhost:8002/docs  # Portfolio Service API

# Database
psql postgresql://fincloud:fincloud_dev_password@localhost:5432/fincloud

# Redis
redis-cli ping

# MinIO Console
open http://localhost:9001
```

## 📋 Week 1 Development Tasks

### Task 1: Database Schema Design (Day 1-2)

**Goal**: Design the complete database schema for budget and portfolio services.

**Steps**:
1. Create ERD (Entity Relationship Diagram) using draw.io or similar
2. Define all tables, columns, and relationships
3. Identify indexes needed for performance
4. Document constraints and validation rules

**Files to create**:
- `docs/architecture/database-schema.md`
- `docs/architecture/erd.png`

**Resources**:
- [SQLAlchemy Relationships](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html)
- [Database Design Best Practices](https://www.postgresql.org/docs/current/ddl.html)

### Task 2: User Authentication System (Day 3-4)

**Goal**: Implement complete user registration and authentication.

**Budget Service** (`services/budget-service/`):

1. Create User model:
```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

2. Create authentication utilities:
```python
# app/core/security.py
from passlib.context import CryptContext
from jose import JWTError, jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    # Implement JWT token creation
    pass
```

3. Create auth endpoints:
```python
# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

@router.post("/register")
async def register(user_data: UserCreate):
    # Implement user registration
    pass

@router.post("/login")
async def login(credentials: OAuth2PasswordRequestForm):
    # Implement login
    pass

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    # Implement token refresh
    pass
```

4. Write tests:
```python
# tests/test_auth.py
def test_register_user():
    # Test user registration
    pass

def test_login_valid_credentials():
    # Test successful login
    pass

def test_login_invalid_credentials():
    # Test failed login
    pass
```

### Task 3: Account Management (Day 5-6)

**Goal**: Implement CRUD operations for user accounts.

**Steps**:
1. Create Account model in `app/models/account.py`
2. Create account schemas in `app/schemas/account.py`
3. Implement CRUD operations in `app/crud/account.py`
4. Update API endpoints in `app/api/v1/accounts.py`
5. Write tests

**Example Account Model**:
```python
# app/models/account.py
class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(Enum(AccountType), nullable=False)  # checking, savings, credit, cash
    currency = Column(String(3), default="USD")
    balance = Column(Numeric(15, 2), default=0)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
```

### Task 4: Frontend Authentication Flow (Day 7)

**Goal**: Build login and registration pages in the frontend.

**Steps**:

1. Create API client:
```typescript
// frontend/src/lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

export const auth = {
  register: (data: RegisterData) => api.post('/auth/register', data),
  login: (credentials: LoginData) => api.post('/auth/login', credentials),
  logout: () => api.post('/auth/logout'),
};
```

2. Create auth store:
```typescript
// frontend/src/stores/auth.ts
import { create } from 'zustand';

interface AuthState {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  login: async (email, password) => {
    // Implement login
  },
  logout: () => {
    // Implement logout
  },
}));
```

3. Create login page:
```tsx
// frontend/src/app/login/page.tsx
'use client';
import { useAuthStore } from '@/stores/auth';

export default function LoginPage() {
  // Implement login form
}
```

## 🔧 Development Workflow

### Daily Routine

1. **Start development environment**:
   ```bash
   make dev  # or docker-compose up -d
   ```

2. **Check service logs**:
   ```bash
   docker-compose logs -f [service-name]
   ```

3. **Run tests before committing**:
   ```bash
   # Backend
   cd services/budget-service
   pytest

   # Frontend
   cd frontend
   npm test
   ```

4. **Commit with conventional commits**:
   ```bash
   git add .
   git commit -m "feat(auth): implement user registration endpoint"
   git push
   ```

### Helpful Commands

```bash
# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d postgres

# Run database migrations
docker-compose exec budget-service alembic upgrade head

# Access database shell
docker-compose exec postgres psql -U fincloud

# Run specific service tests
docker-compose exec budget-service pytest tests/test_auth.py

# Rebuild specific service
docker-compose up -d --build budget-service

# View real-time logs for specific service
docker-compose logs -f budget-service
```

## 📚 Learning Resources

### Backend (FastAPI + SQLAlchemy)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Pydantic Models](https://docs.pydantic.dev/latest/)

### Frontend (Next.js + React)
- [Next.js Documentation](https://nextjs.org/docs)
- [React Hooks](https://react.dev/reference/react)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [React Query](https://tanstack.com/query/latest/docs/framework/react/overview)
- [Zustand State Management](https://docs.pmnd.rs/zustand/getting-started/introduction)

### Testing
- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Jest](https://jestjs.io/docs/getting-started)

## 🐛 Troubleshooting

### Services won't start
```bash
# Check Docker is running
docker --version

# Check ports are available
lsof -i :3000  # Frontend
lsof -i :8000  # API Gateway
lsof -i :5432  # PostgreSQL

# View detailed logs
docker-compose logs
```

### Database connection errors
```bash
# Ensure PostgreSQL is healthy
docker-compose ps postgres

# Check connection from host
psql postgresql://fincloud:fincloud_dev_password@localhost:5432/fincloud

# Restart database
docker-compose restart postgres
```

### Frontend not loading
```bash
# Check Node.js version
node --version  # Should be 20+

# Clear Next.js cache
cd frontend
rm -rf .next
npm install
```

### Python import errors
```bash
# Ensure you're in the right directory
cd services/budget-service

# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
echo $PYTHONPATH
```

## 📊 Progress Tracking

Create a GitHub Project board with columns:
- 📋 Backlog
- 🏗️ In Progress
- 👀 Review
- ✅ Done

Track your progress against the TODO.md file.

## 🤝 Getting Help

- **Documentation**: Check `/docs` directory
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: Create PRs for feedback

## 🎯 Week 1 Success Criteria

By end of Week 1, you should have:
- ✅ Development environment running smoothly
- ✅ Database schema designed and documented
- ✅ User model and authentication implemented
- ✅ Account model and CRUD operations
- ✅ Login/registration pages in frontend
- ✅ Basic tests written and passing
- ✅ Understanding of the codebase structure

## 📅 Week 2 Preview

Week 2 will focus on:
- Transaction management (CRUD)
- Category system
- Basic budget tracking
- Transaction list UI
- Dashboard with key metrics

---

**Remember**:
- Write tests as you code
- Commit often with clear messages
- Ask for help when stuck
- Document as you build
- Focus on one task at a time

Good luck! 🚀
