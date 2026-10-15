# Valorant Dashboard

Excel is the source of truth. sync_workbook.py exports public fields into data.js; index.html and app.js contain no account records.

## Automatic local updates

Double-click Start Dashboard.cmd. Keep its window open. It watches Documents/Valorant Info Sheet.xlsx every two seconds and the page refreshes its data every five seconds. Save Excel changes to trigger an update. Python 3 is required; no extra packages are needed.

## Updating GitHub Pages

Run Refresh Data.cmd after saving Excel, then commit and push data.js with the project files. GitHub Pages cannot read a workbook on your computer. The hosted site updates after pushing new data and Pages finishes deploying; caching can delay refresh.

In GitHub Settings > Pages, choose Deploy from a branch, main, and / (root). No build step needed.

## Public data

Only in-game tags, ranks, mode hours, verification flags, check dates, and standardized verification summaries are exported. Passwords, login usernames, raw notes, original hyperlinks, and login-only records are excluded. Totals are recomputed from the mode inputs.

GitHub Pages is normally public. Keep the original workbook outside the repository. AGENTS.md requires data regeneration after agent workbook edits.

Alternate source: python sync_workbook.py --workbook "path/to/workbook.xlsx" --watch --serve

## Automatic GitHub syncing

After the initial authenticated push, run Start GitHub Sync.cmd. Leave its window open on this computer. Saving Excel regenerates data.js, commits only that data file, and pushes it to origin/main. GitHub Pages then redeploys. Failed network/authentication pushes are retried every 60 seconds. Unrelated staged files, unpushed source edits, and diverged history require manual attention; the watcher never force-pushes.

The computer must be awake and the watcher must be running. Closing it stops automatic syncing. GitHub sign-in for the browser and Git on this computer are separate; Finish GitHub Setup.cmd performs the initial push and allows normal Git authentication.
