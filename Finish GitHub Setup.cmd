@echo off
cd /d "%~dp0"
echo Uploading the committed dashboard project to FarazIlahi/valorant-dashboard.
echo If GitHub asks you to sign in, complete that sign-in in your browser.
git push -u origin main
if errorlevel 1 (
  echo Upload failed. Copy the error message and share it in the chat.
) else (
  echo Upload complete. Return to the chat so Pages can be enabled.
)
pause
