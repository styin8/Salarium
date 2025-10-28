# Implementation Summary: 401 Unauthorized Auto Logout & Redirect

## Objective
Implement automatic session cleanup and redirect to login page when the backend returns 401 Unauthorized, with support for returning to the original page after re-authentication.

## Changes Made

### 1. New Files Created

#### `frontend/src/utils/axios.js` (NEW)
- Created global axios instance with baseURL `/api`
- Implemented request interceptor to automatically attach JWT token from user store
- Implemented response interceptor to handle 401 errors:
  - Detects 401 status code
  - Whitelists auth endpoints to prevent redirect loops
  - Calls `userStore.logout()` to clear session
  - Shows warning message: "登录已过期，请重新登录"
  - Redirects to login with `redirect` query parameter
- Exported `setupAxiosInterceptors()` function to initialize interceptors with router and store instances

#### `frontend/AUTH_401_HANDLING.md` (NEW)
- Comprehensive documentation of the implementation
- Describes all components and their interactions
- Documents user flows for different scenarios
- Explains benefits and backend configuration

#### `frontend/TESTING_401_HANDLER.md` (NEW)
- Step-by-step manual testing guide
- Six test cases covering different scenarios
- Instructions for automated testing via console
- Common issues and troubleshooting

### 2. Modified Files

#### `frontend/src/main.js`
**Changes**:
- Import `setupAxiosInterceptors` and `useUserStore`
- Create Pinia instance before other plugins
- Call `setupAxiosInterceptors(router, userStore)` after Pinia setup to initialize interceptors

**Purpose**: Initialize the global axios interceptors with access to router and user store

#### `frontend/src/router/index.js`
**Changes**:
- Updated `beforeEach` guard to return an object with `path` and `query` instead of just a string
- Added `redirect` query parameter containing the target route's `fullPath`

**Purpose**: Save the original destination when redirecting to login so user can return after authentication

#### `frontend/src/views/Login.vue`
**Changes**:
- Import `api` from `'../utils/axios'` instead of direct axios import
- Import `useRoute` in addition to `useRouter`
- Updated `handleLogin()`:
  - Changed endpoint from `/api/auth/login` to `/auth/login` (baseURL handled by axios instance)
  - Check for `route.query.redirect` parameter
  - Redirect to original page if redirect exists and is not `/login`
  - Use `router.replace()` instead of `router.push()` for cleaner history
- Updated `handleRegister()`:
  - Changed endpoint from `/api/auth/register` to `/auth/register`

**Purpose**: Use global axios instance and handle redirect after successful login

#### `frontend/src/views/Persons.vue`
**Changes**:
- Import `api` from `'../utils/axios'` instead of creating local axios instance
- Removed `const api = axios.create(...)` line

**Purpose**: Use global axios instance with interceptors

#### `frontend/src/views/Salaries.vue`
**Changes**:
- Import `api` from `'../utils/axios'` instead of creating local axios instance
- Removed `const api = axios.create(...)` line

**Purpose**: Use global axios instance with interceptors

#### `frontend/src/views/Stats.vue`
**Changes**:
- Import `api` from `'../utils/axios'` instead of creating local axios instance
- Removed `const api = axios.create(...)` line

**Purpose**: Use global axios instance with interceptors

#### `frontend/src/api/stats.js`
**Changes**:
- Import `api` from `'../utils/axios'` instead of axios
- Simplified `client()` function to just return the global `api` instance
- Removed user store import (no longer needed)

**Purpose**: Use global axios instance with interceptors

### 3. Existing Functionality (No Changes Required)

#### `frontend/src/store/user.js`
- Already has proper `logout()` method that:
  - Clears token from state and localStorage
  - Calls `statsStore.resetAll()` to clear cached data
  - Resets username
- No changes needed

#### `frontend/src/store/stats.js`
- Already has `resetAll()` method that clears all cached statistics data
- No changes needed

#### `backend/app/utils/auth.py`
- Already returns proper 401 status with `WWW-Authenticate: Bearer` header
- No changes needed

## Technical Implementation Details

### Request Flow (Normal Case)
1. Component makes API call using `api.get('/persons/')`
2. Request interceptor adds `Authorization: Bearer {token}` header
3. Backend validates token and returns data
4. Response is returned to component

### Request Flow (401 Case)
1. Component makes API call using `api.get('/persons/')` from `/persons` page
2. Request interceptor adds expired/invalid token
3. Backend returns 401 Unauthorized
4. Response interceptor catches 401:
   - Checks it's not an auth endpoint
   - Checks it's not already on login page
   - Calls `userStore.logout()` to clear session
   - Shows warning message
   - Redirects to `/login?redirect=/persons`
5. User logs in with valid credentials
6. Login handler checks redirect parameter
7. User is redirected back to `/persons`

### Preventing Redirect Loops
- Auth endpoints (`/auth/login`, `/auth/register`, `/auth/refresh`) are whitelisted
- Login page path is checked before redirecting
- Only 401 from protected endpoints trigger redirect

## Verification

### Build Status
✅ Build successful with no errors
- Frontend builds cleanly: `npm run build`
- All imports are correct
- No syntax errors

### Code Quality Checks
✅ All components use global axios instance
✅ No duplicate axios.create() calls except in utils/axios.js
✅ No direct axios imports except in utils/axios.js
✅ Proper error handling in interceptors
✅ Session cleanup is comprehensive

### Test Coverage
✅ Documentation includes 6 manual test cases
✅ Test cases cover:
- Invalid token handling
- Missing token handling
- Session cleanup across user switches
- No redirect loops on login failures
- Redirect after login works correctly
- Default route when no redirect parameter

## Benefits

1. **Improved Security**: Automatic session cleanup on authorization failure
2. **Better UX**: Users are returned to their intended destination after re-authentication
3. **Consistent Behavior**: Centralized 401 handling across the entire app
4. **Clean Code**: Single axios instance with interceptors, no duplication
5. **No Bugs**: Prevents infinite redirect loops with proper whitelisting
6. **Data Isolation**: Each user sees only their data (cache is cleared on logout)

## Files Changed Summary
- **Created**: 3 files (1 source file, 2 documentation files)
- **Modified**: 7 files (all source files)
- **Total lines changed**: ~100 lines of code changes
- **Build status**: ✅ Passing
- **Breaking changes**: None (backward compatible)

## Next Steps for Deployment
1. Review the changes
2. Test manually using the testing guide
3. Merge to main branch
4. Deploy frontend and backend together
5. Monitor for any 401-related issues in production logs
