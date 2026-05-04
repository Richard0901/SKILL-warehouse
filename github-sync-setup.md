# SKILLs -> GitHub Daily Sync

## Files
- `D:\Life\SKILLs\sync-to-github.ps1`: mirror local SKILLs into a local git clone, then commit + push.
- `D:\Life\SKILLs\register-sync-task.ps1`: create a Windows daily scheduled task.

## One-time setup
1. Make sure Git can push to your private repo in non-interactive mode.
2. Run one manual sync test:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File "D:\Life\SKILLs\sync-to-github.ps1"
   ```
3. Register a daily task (example: 02:00 every day):
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File "D:\Life\SKILLs\register-sync-task.ps1" -RunTime "02:00"
   ```

## Useful commands
- Run task now:
  ```powershell
  Start-ScheduledTask -TaskName "SKILLs-Daily-GitHub-Sync"
  ```
- Check task:
  ```powershell
  Get-ScheduledTask -TaskName "SKILLs-Daily-GitHub-Sync" | Get-ScheduledTaskInfo
  ```
- Logs:
  - `D:\Life\private\skill-github-sync.log`

## Notes
- Script uses `robocopy /MIR`, so remote content will match local `D:\Life\SKILLs` exactly.
- Local clone path defaults to `D:\Life\private\SKILL-warehouse`.
- If no file changes are detected, script exits without creating a commit.
- Script auto-uses absolute executables:
  - Git: `C:\Program Files\Git\bin\git.exe` (fallback auto-detect)
  - Robocopy: `C:\Windows\System32\robocopy.exe`
