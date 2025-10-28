# Manual Testing Guide for 401 Auto Logout

## Prerequisites
1. Backend server running on `http://localhost:8000`
2. Frontend dev server running on `http://localhost:5173` or build served

## Test Cases

### Test 1: Invalid Token Handling
**Purpose**: Verify that an invalid token triggers automatic logout and redirect

**Steps**:
1. Open the app and login with valid credentials
2. Open Browser DevTools (F12) → Application/Storage → Local Storage
3. Find the `token` key and change its value to something invalid (e.g., "invalid_token")
4. Navigate to any protected page (e.g., `/persons` or `/salaries`)
5. Or perform any action that makes an API call

**Expected Result**:
- Toast message appears: "登录已过期,请重新登录"
- User is redirected to `/login?redirect=/persons` (or the page you were on)
- Token is cleared from localStorage
- After re-login, user returns to the original page

---

### Test 2: Deleted Token Handling
**Purpose**: Verify that missing token triggers redirect via router guard

**Steps**:
1. Login to the app
2. Open Browser DevTools → Application/Storage → Local Storage
3. Delete the `token` key entirely
4. Try to navigate to any protected route (e.g., click on "人员管理" menu)

**Expected Result**:
- User is immediately redirected to `/login?redirect=/persons`
- After login, user is redirected back to the requested page

---

### Test 3: Session Cleanup on Logout
**Purpose**: Verify that all user data is cleared when logged out

**Steps**:
1. Login as User A
2. Navigate through the app and load some data (persons, salaries, stats)
3. Manually trigger a 401 by invalidating the token (as in Test 1)
4. After being redirected to login, login as User B (different account)
5. Navigate to the same pages

**Expected Result**:
- All data shown belongs to User B
- No cached data from User A is visible
- Stats store is reset (can verify in Vue DevTools)

---

### Test 4: No Redirect Loop on Login
**Purpose**: Verify that auth endpoints don't trigger redirects

**Steps**:
1. Ensure you're logged out
2. Try to login with wrong credentials
3. Backend will return 401 for invalid login

**Expected Result**:
- Error message: "登录失败，请检查用户名和密码"
- User stays on login page (NO redirect)
- No infinite redirect loops

---

### Test 5: Redirect After Login Works
**Purpose**: Verify the redirect query parameter works correctly

**Steps**:
1. While logged out, manually navigate to: `http://localhost:5173/salaries/5`
2. Router guard will redirect to `/login?redirect=/salaries/5`
3. Login with valid credentials

**Expected Result**:
- After successful login, user is redirected to `/salaries/5` (not to `/stats`)
- The page loads correctly with the person's salary data

---

### Test 6: Default Route When No Redirect
**Purpose**: Verify default behavior when no redirect parameter exists

**Steps**:
1. Manually go to `/login` (while already logged out)
2. Login with valid credentials

**Expected Result**:
- User is redirected to `/stats` (the default route)
- No errors in console

---

## Automated Testing with Browser Console

You can also test the 401 handler by simulating an invalid token response:

```javascript
// In browser console after logging in:
// This will make the next API call fail with 401
localStorage.setItem('token', 'invalid_token_value');

// Then trigger an API call, for example by navigating to persons page
// or by running:
fetch('/api/persons/', {
  headers: { 'Authorization': 'Bearer invalid_token_value' }
})
```

## Checking in Vue DevTools

1. Install Vue DevTools browser extension
2. Open DevTools → Vue tab
3. Check the Pinia stores:
   - `user` store should show `token: ''` after logout
   - `stats` store should be reset (empty persons array, cleared cache)

## Verifying Network Calls

1. Open DevTools → Network tab
2. Filter by `XHR` or `Fetch`
3. Make an API call that returns 401
4. Check the response:
   - Status: 401 Unauthorized
   - Headers should include `WWW-Authenticate: Bearer`
5. Verify that the interceptor runs:
   - Check console for the warning message
   - Check that redirect happened
   - Verify localStorage is cleared

## Common Issues

**Issue**: Redirect loop
- **Cause**: Login endpoint is not whitelisted in interceptor
- **Solution**: Check that `/auth/login` is in the whitelist

**Issue**: Token not cleared
- **Cause**: `userStore.logout()` not being called
- **Solution**: Verify interceptor calls logout before redirect

**Issue**: Cached data from previous user
- **Cause**: Stats store not being reset
- **Solution**: Verify `statsStore.resetAll()` is called in `userStore.logout()`

**Issue**: No warning message
- **Cause**: ElMessage not imported or not set up
- **Solution**: Check that Element Plus is properly configured
