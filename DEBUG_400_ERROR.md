# Troubleshooting 400 Bad Request

## Quick Diagnostics

Your app has a health check endpoint now. Visit:
```
https://playtofunding-production.up.railway.app/health/
```

This should show your current configuration (host, DEBUG setting, ALLOWED_HOSTS).

## Common Causes & Fixes

### 1. **ALLOWED_HOSTS Issue** ✅ FIXED
- The issue was that `*.railway.app` doesn't match `up.railway.app` domains
- Updated pattern to include `*.up.railway.app`

### 2. **Verify Environment Variables in Railway**

In Railway dashboard, check that these are set:

```
DEBUG=False
ALLOWED_HOSTS=playtofunding-production.up.railway.app
VITE_API_URL=https://playtofunding-production.up.railway.app
SECRET_KEY=<must be set>
```

### 3. **VITE_API_URL Setting**

The frontend uses the `VITE_API_URL` environment variable to know where to call the API.

- Set it to: `https://playtofunding-production.up.railway.app` (your actual Railway domain)
- This value gets baked into the frontend build

**If you changed this variable, you need to rebuild:**
1. Push your code again to trigger a rebuild
2. Or restart the Railway deployment

### 4. **Frontend Not Loading?**

If you see "Frontend not found", it means the build step didn't complete properly.

Check Railway build logs for errors in:
- Frontend build (`npm install && npm run build`)
- Backend collectstatic
- Migration errors

### 5. **Manual Fix: Rebuild from Local**

If you need to force a rebuild:

```bash
# Locally build and test
cd frontend && npm install && npm run build
cd ../backend && python manage.py collectstatic --noinput

# Then push to trigger Railway deployment
git add .
git commit -m "Force rebuild"
git push
```

## Debugging Steps

1. **Check health endpoint:**
   ```
   https://playtofunding-production.up.railway.app/health/
   ```
   Should return JSON with status, debug mode, and host info

2. **Check Railway logs:**
   - Go to Railway dashboard
   - View "Logs" tab
   - Look for any error messages

3. **Check environment variables:**
   - Railway dashboard → Variables tab
   - Ensure DEBUG=False and ALLOWED_HOSTS is set

4. **Test API endpoint:**
   ```
   https://playtofunding-production.up.railway.app/api/v1/
   ```
   Should return authentication error (401) or list view

## Common Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| 400 Bad Request | ALLOWED_HOSTS mismatch | Set correct domain in Railway vars |
| Frontend not found | Build didn't complete | Check build logs, rebuild |
| 502 Bad Gateway | App crashed | Check logs, ensure requirements installed |
| 404 on /api/ | Missing routes | Check urls.py is correct |
| CORS errors | Wrong VITE_API_URL | Set correct API URL in Railway |

## What Changed

- ✅ ALLOWED_HOSTS now includes `*.up.railway.app` patterns
- ✅ Added `/health/` endpoint for debugging
- ✅ Improved error messages to show which paths were checked
- ✅ Better static file handling
- ✅ CSRF exemption for health check

## Next Steps

1. Commit and push the changes
2. Monitor Railway deployment
3. Visit `/health/` to verify settings
4. Check if frontend loads at `/`
5. Test API at `/api/v1/`

If still getting 400, share the output from `/health/` endpoint!
