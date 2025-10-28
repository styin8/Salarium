# 401 Unauthorized Auto Logout & Redirect Implementation

## Overview
This document describes the implementation of automatic logout and redirect to login page when the backend returns a 401 Unauthorized response.

## Implementation Details

### 1. Global Axios Instance with Interceptors (`src/utils/axios.js`)
- Created a global axios instance configured with `/api` as base URL
- **Request Interceptor**: Automatically attaches the JWT token from the user store to all requests
- **Response Interceptor**: 
  - Catches 401 responses from protected endpoints
  - Excludes auth endpoints (`/auth/login`, `/auth/register`, `/auth/refresh`) to prevent redirect loops
  - Excludes login page to prevent redirect loops
  - Calls `userStore.logout()` to clear all session data
  - Shows a warning message "登录已过期，请重新登录"
  - Redirects to login page with the original path as `redirect` query parameter

### 2. Router Guard Enhancement (`src/router/index.js`)
- Updated the `beforeEach` guard to:
  - Store the target path as `redirect` query parameter when redirecting unauthenticated users to login
  - This allows users to return to their intended destination after login

### 3. Login Component Enhancement (`src/views/Login.vue`)
- Uses the global axios instance
- After successful login:
  - Checks for `redirect` query parameter
  - Redirects to the original target page if redirect exists and is not `/login`
  - Defaults to `/stats` if no redirect is specified

### 4. Session Cleanup (`src/store/user.js`)
- The `logout()` method already:
  - Clears the token from state and localStorage
  - Calls `statsStore.resetAll()` to clear all cached data
  - Resets user information

### 5. Updated Components
All components now use the global axios instance from `src/utils/axios.js`:
- `src/views/Login.vue`
- `src/views/Persons.vue`
- `src/views/Salaries.vue`
- `src/views/Stats.vue`
- `src/api/stats.js`

## User Flow

### Scenario 1: Token Expiration
1. User is browsing `/persons` page
2. Token expires or becomes invalid
3. User makes a request (e.g., GET `/api/persons/`)
4. Backend returns 401
5. Frontend:
   - Shows message: "登录已过期，请重新登录"
   - Clears all session data (token, cached stats, etc.)
   - Redirects to `/login?redirect=/persons`
6. User logs in
7. User is automatically redirected back to `/persons`

### Scenario 2: Direct Access Without Token
1. User navigates directly to `/salaries/123`
2. Router guard detects no token
3. Redirects to `/login?redirect=/salaries/123`
4. User logs in
5. User is automatically redirected to `/salaries/123`

### Scenario 3: Login Failure (Not 401)
1. User enters wrong credentials on `/login`
2. Backend returns 401 for login endpoint
3. Interceptor skips auto-redirect (auth endpoint whitelist)
4. Login component shows error message
5. User remains on login page

## Testing

### Manual Test Cases
1. **Token Expiration Test**:
   - Login to the app
   - Manually delete the token from localStorage in browser DevTools
   - Navigate to any protected page or refresh
   - Should redirect to login with redirect parameter
   - After login, should return to the original page

2. **Invalid Token Test**:
   - Login to the app
   - Manually change the token value in localStorage to an invalid string
   - Perform any action that requires API call
   - Should redirect to login with warning message

3. **Multiple Account Switch Test**:
   - Login with user A
   - Note the data shown
   - Logout or get 401
   - Login with user B
   - Verify that all data is for user B (no cached data from user A)

4. **No Redirect Loop Test**:
   - Make sure auth endpoints don't trigger redirect
   - Failed login attempts should not redirect away from login page

## Backend Configuration
The backend already properly returns 401 status with `WWW-Authenticate: Bearer` header:
- File: `backend/app/utils/auth.py`
- Function: `get_current_user()`
- Returns proper 401 with headers when token is invalid/expired

## Benefits
- **Better UX**: Clear message about session expiration
- **Seamless Recovery**: Users return to their intended page after re-login
- **Secure**: All session data is cleared on 401
- **No Infinite Loops**: Proper whitelisting prevents redirect loops
- **Centralized**: All axios instances use the same interceptor logic
