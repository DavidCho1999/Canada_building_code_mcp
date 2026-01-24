# Start Development Server

Safely start the Next.js development server.

## Execution Steps

1. **Check if port 3001 is in use**
   ```bash
   netstat -ano | findstr :3001
   ```

2. **If in use, kill the process** (after checking PID)
   ```bash
   taskkill /PID <PID> /F
   ```

3. **Delete .next/dev/lock file** (if exists)
   ```bash
   rm -f codevault/.next/dev/lock
   ```

4. **Start server in background**
   ```bash
   cd codevault && npm run dev
   ```
   - Use `run_in_background: true` option
   - Wait 3 seconds after server starts

5. **Verify server status**
   - Check if http://localhost:3001 is accessible

## Important Notes

- Server command must run in **background** (prevents crashes)
- Lock file conflicts can cause Claude Code to terminate
- Port conflict check is essential
