# Frontend Authentication Integration Guide

## 🎯 Overview

This guide explains how to integrate the authentication system into your MAHER AI frontend.

## 📦 What's Been Created

### 1. **API Client Updates** (`api.ts`)
- ✅ Authentication methods added
- ✅ Session management (getSessionId, getUserRole, isAdmin)
- ✅ Admin login/logout
- ✅ Analytics endpoint
- ✅ Session ID automatically included in agent CRUD requests

### 2. **React Components**

#### `AuthProvider.tsx`
- Automatically creates guest session on app load
- Verifies existing sessions
- Provides `useAuth()` hook for role checking

#### `AdminLogin.tsx` + `AdminLogin.css`
- Beautiful login form with password input
- Error handling and loading states
- Modern gradient design

#### `AdminDashboard.tsx` + `AdminDashboard.css`
- Real-time analytics KPI cards
- Top agents chart
- Recent activity feed
- Auto-refresh every 30 seconds
- Logout button

#### `ProtectedRoute.tsx`
- `<ProtectedRoute>` - Conditional rendering wrapper
- `<AdminOnly>` - Show only to admins
- `<GuestOnly>` - Show only to guests

## 🔧 Integration Steps

### Step 1: Wrap App with AuthProvider

Update `App.tsx`:

```typescript
import { AuthProvider } from './components/AuthProvider';

function App() {
  return (
    <AuthProvider>
      {/* Your existing app content */}
    </AuthProvider>
  );
}
```

### Step 2: Add Admin Routes

Add routes for admin login and dashboard:

```typescript
import { AdminLogin } from './components/AdminLogin';
import { AdminDashboard } from './components/AdminDashboard';
import { useAuth } from './components/AuthProvider';

function App() {
  const { isAdmin } = useAuth();
  const [showAdminLogin, setShowAdminLogin] = useState(false);

  // Show admin dashboard if logged in as admin
  if (isAdmin) {
    return (
      <AuthProvider>
        <AdminDashboard />
      </AuthProvider>
    );
  }

  // Show admin login if requested
  if (showAdminLogin) {
    return (
      <AuthProvider>
        <AdminLogin onLoginSuccess={() => window.location.reload()} />
      </AuthProvider>
    );
  }

  // Regular app
  return (
    <AuthProvider>
      {/* Your existing app */}
    </AuthProvider>
  );
}
```

### Step 3: Add Admin Login Button

In your header or sidebar:

```typescript
import { useAuth } from './components/AuthProvider';

function Header() {
  const { isAdmin } = useAuth();

  return (
    <header>
      {/* Existing header content */}
      
      {!isAdmin && (
        <button onClick={() => window.location.href = '/admin/login'}>
          Admin Login
        </button>
      )}
      
      {isAdmin && (
        <div className="admin-badge">
          <svg>...</svg>
          Admin
        </div>
      )}
    </header>
  );
}
```

### Step 4: Protect Agent Management UI

Hide create/edit/delete buttons for guests:

```typescript
import { AdminOnly } from './components/ProtectedRoute';

function AgentList() {
  return (
    <div>
      {/* Agent list visible to everyone */}
      
      <AdminOnly>
        <button onClick={createAgent}>Create New Agent</button>
      </AdminOnly>
      
      {agents.map(agent => (
        <div key={agent.id}>
          <h3>{agent.name}</h3>
          
          <AdminOnly>
            <button onClick={() => editAgent(agent.id)}>Edit</button>
            <button onClick={() => deleteAgent(agent.id)}>Delete</button>
          </AdminOnly>
        </div>
      ))}
    </div>
  );
}
```

## 🎨 Styling

All components come with CSS files:
- `AdminLogin.css` - Modern gradient login form
- `AdminDashboard.css` - Responsive dashboard layout

The styles use:
- CSS Grid for responsive layouts
- Smooth animations and transitions
- Modern color gradients
- Mobile-friendly design

## 🔐 Security Notes

1. **Session Storage**: Sessions stored in localStorage
2. **Auto-Session**: Guest sessions created automatically
3. **Backend Validation**: All admin actions validated on backend
4. **Session Headers**: X-Session-ID automatically sent with requests

## 📊 Admin Dashboard Features

### KPI Cards
- Total Visits (with today's count)
- Total Chats (with today's count)
- Active Users (last 24h)
- Total Agents

### Top Agents
- Top 5 most-used agents
- Usage count with visual bars
- Ranked display

### Recent Activity
- Last 10 chat sessions
- Agent name and message count
- Timestamp

### Auto-Refresh
- Dashboard refreshes every 30 seconds
- Manual refresh on error

## 🧪 Testing

1. **Guest Flow**:
   - Open app → Auto guest session created
   - Try to create agent → Blocked (403)
   - View agents → Works ✓

2. **Admin Flow**:
   - Click "Admin Login"
   - Enter password: `maher_admin_2026`
   - Redirected to dashboard
   - Create/edit/delete agents → Works ✓

3. **Session Persistence**:
   - Refresh page → Session persists
   - Close/reopen browser → Session persists
   - Logout → Returns to guest

## 🚀 Quick Start Example

Minimal integration in `App.tsx`:

```typescript
import React, { useState } from 'react';
import { AuthProvider, useAuth } from './components/AuthProvider';
import { AdminLogin } from './components/AdminLogin';
import { AdminDashboard } from './components/AdminDashboard';

function AppContent() {
  const { isAdmin } = useAuth();
  const [route, setRoute] = useState('home');

  if (route === 'admin-login') {
    return <AdminLogin onLoginSuccess={() => setRoute('admin-dashboard')} />;
  }

  if (route === 'admin-dashboard' && isAdmin) {
    return <AdminDashboard />;
  }

  return (
    <div>
      <button onClick={() => setRoute('admin-login')}>Admin</button>
      {/* Your existing app */}
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
```

## ✅ Checklist

- [ ] Wrap app with `<AuthProvider>`
- [ ] Add admin login route/button
- [ ] Add admin dashboard route
- [ ] Protect agent create/edit/delete with `<AdminOnly>`
- [ ] Test guest session creation
- [ ] Test admin login
- [ ] Test agent management permissions
- [ ] Test dashboard analytics

## 🎉 You're Done!

The authentication system is now fully integrated! Users will automatically get guest sessions, and admins can login to access the dashboard and manage agents.
