# Valorant Account Dashboard

[Open the live dashboard](https://farazilahi.github.io/valorant-dashboard/)

An interactive dashboard that turns my private Valorant account spreadsheet into a public view of in-game tags, ranks, playtime, and data verification status. Excel remains the source of truth, and an automated pipeline keeps the website updated after I save changes.

## How I used AI to build this project

I used OpenAI Codex as an AI assistant throughout the project. I described what I wanted in plain language, reviewed the results, and used follow-up requests to develop the workflow. This made the setup easier by reducing the manual work involved in preparing the spreadsheet, building a website, and connecting the pieces.

- **Updating the spreadsheet:** I used AI to help update and organize my account information, including ranks, hours played, verification flags, and an analysis sheet. The workbook distinguishes known accounts from accounts with incomplete or uncertain information, so older values are not automatically treated as verified facts.
- **Creating the dashboard:** I asked AI to turn the spreadsheet into a clean, clickable website. It built the layout, summary cards, playtime charts, searchable account table, filters, sorting, and account detail panels.
- **Connecting Excel to the website:** AI created a Python exporter that reads the workbook and produces a separate public data file. Account records are generated from Excel rather than manually maintained inside the HTML.
- **Setting up GitHub:** AI helped create this repository, prepare the project files, configure GitHub Pages, and implement automatic commits and pushes. I completed the GitHub sign-in and initial authenticated upload on my computer.
- **Testing the complete workflow:** I asked AI to add a dummy account to Excel. The running watcher generated the new data, pushed it to GitHub, and the account appeared on the live website. Removing the dummy record from Excel also removed it from the website through the same automated process.

AI helped implement and test the project, while I directed the requirements and completed account authentication. AI does not need to stay open for the sync to work: the generated programs handle ongoing updates.

## How the project gets its Excel data

The source workbook stays on my computer at `Documents/Valorant Info Sheet.xlsx`. It does **not** need to be in the project folder and is not uploaded to GitHub.

`sync_workbook.py` reads the workbook's `Known accounts` and `Uncertain accounts` sheets. It matches column headers to an explicit list of permitted fields, extracts the account records, normalizes numeric playtime values and verification flags, and recalculates total hours from the three mode inputs. This avoids relying on stale cached Excel formula results.

The exporter writes the result to `data.js`. The website loads that generated file and uses it to populate its cards, charts, table, and account details. `index.html` defines the page structure, and `app.js` provides the interactions; neither contains manually embedded account records.

The exporter also checks for duplicate in-game tags and invalid playtime values. If an export fails, it preserves the last successfully generated data instead of replacing it with a broken file. Saving Excel without changing any exported account information does not create a new data version.

## Automatic update pipeline

```text
Save the Excel workbook
          |
          v
Watcher detects the saved file change
          |
          v
Python exports permitted fields to data.js
          |
          v
Git commits and pushes the changed data.js
          |
          v
GitHub Pages redeploys the website
          |
          v
The open dashboard reloads its data
```

**Start GitHub Sync.cmd** runs the watcher and opens a local preview. The watcher checks the workbook's modification time and size every two seconds. When the file changes, it exports the data and automatically commits and pushes only `data.js` to `origin/main`. GitHub Pages publishes updates from the repository's `main` branch and root folder.

An open dashboard checks for a newer `data.js` every five seconds and redraws its views when new data arrives. Selected filters are retained where valid. The online update also depends on GitHub's deployment time and caching, so it is not instantaneous.

GitHub Pages cannot read an Excel file on my computer. The local watcher is the bridge between the private workbook and the hosted website.

### Requirements and limits

- The computer must be awake, online, and running **Start GitHub Sync.cmd** for automatic GitHub updates.
- Closing the sync window stops the watcher. It does not currently start automatically with Windows.
- Reopening the launcher exports the current workbook and attempts to sync outstanding public data changes.
- Git must be installed and authenticated with permission to push to this repository. Browser sign-in and Git authentication are separate.
- Network or authentication failures are retried every 60 seconds while the watcher runs.
- The watcher refuses to publish unrelated staged files or unpushed source edits. It never force-pushes; conflicting Git history requires manual attention.

## Data analytics features

The dashboard supports descriptive analysis of account activity and the quality of the stored information.

| Feature | What it helps analyze |
| --- | --- |
| Account summary | Counts of named accounts, fully verified accounts, and accounts requiring further checks. |
| Playtime by mode | The distribution of lifetime hours across Competitive, Unrated, and Deathmatch. |
| Verified versus stored hours | Separates confirmed playtime from older or unverified stored values. Verification is applied to each mode individually, so a partially verified account can contribute its confirmed fields. |
| Rank exploration | Compares current and peak ranks, filters by peak rank, and sorts by the highest peak rank. |
| Account comparison | Sorts accounts by stored total hours or in-game tag to identify more active accounts and inspect individual records. |
| Verification status | Shows the distribution of statuses such as verified, partial data, renamed accounts awaiting checks, and inconclusive profile lookups. Clicking a status filters the table. |
| Interactive filtering | Search by in-game tag and combine account-group and peak-rank filters. Summary cards and charts update to match the selection. |
| Data quality checks | Rejects duplicate tags and invalid numeric playtime inputs, recomputes totals, and marks unverified values in amber. |

**Metric definitions:** Stored total hours equal Competitive + Unrated + Deathmatch hours. Verified playtime includes a mode's hours only when its corresponding verification flag is `Yes`. Fully verified account counts use the workbook's `Known accounts` group. Login-only records are excluded because they have no in-game tag or gameplay stats.

The project analyzes the workbook's stored lifetime values. It is not a live Riot API integration, does not automatically discover new gameplay stats, and does not provide match-level trends, win rates, or predictive analysis. A profile lookup also does not verify whether account login access works.

## Privacy and public data

The public export contains only:

- In-game tags (Riot IDs).
- Current and peak ranks.
- Competitive, Unrated, and Deathmatch hours, plus the calculated total.
- Account group, verification flags, check dates, and standardized verification summaries.

**Login usernames, passwords, raw workbook notes, original hyperlinks, and login-only records are excluded.** The exporter creates verification summaries from flags rather than publishing free-text notes that might contain private information.

The original Excel file stays outside the repository. Spreadsheet file types are also listed in `.gitignore` to help prevent accidental inclusion. The GitHub repository and Pages website are public, so the generated `data.js` should always be treated as public information.

## Running the project

Python 3 and Git are required for automatic GitHub syncing. The exporter uses Python's standard library and requires no additional Python packages. The Windows launchers use the bundled Codex Python when available, or fall back to an installed Python.

| File | Purpose |
| --- | --- |
| `index.html` | Dashboard structure and the theme selector. |
| `styles.css` | Layout, responsive styles, and all Straw Hat color palettes. |
| `themes.js` | Applies and remembers the selected theme in the browser. |
| `app.js` | Filtering, sorting, charts, account details, and periodic data reloads. |
| `data.js` | Generated public account data read by the website. |
| `sync_workbook.py` | Reads Excel, exports permitted data, watches saved changes, and optionally commits and pushes updates. |
| `run-dashboard.ps1` | Selects Python and runs the requested launcher mode. |
| `Start GitHub Sync.cmd` | Starts the local dashboard, workbook watcher, and automatic GitHub pushes. |
| `Start Dashboard.cmd` | Starts the local dashboard and watcher without GitHub pushes. |
| `Refresh Data.cmd` | Regenerates `data.js` once without pushing. |
| `Finish GitHub Setup.cmd` | Performs a manual push of committed project changes; used during initial setup and source updates. |
| `AGENTS.md` | Records the privacy rules and workbook-refresh instructions for future AI-assisted changes. |

To use a different workbook location:

```powershell
python sync_workbook.py --workbook "C:\path\to\workbook.xlsx" --watch --serve --push
```

For a one-time export and push:

```powershell
python sync_workbook.py --push
```

Source-code changes and README updates are reviewed and pushed separately. The automatic watcher only publishes the generated account data.

## Straw Hat themes

Use the Straw Hat theme dropdown to choose Luffy, Zoro, Nami, Usopp, Sanji, Chopper, Robin, Franky, Brook, or Jinbe, plus the original Midnight palette. Nami, Chopper, and Franky use softer light surfaces; the others use dark character-inspired palettes. Text contrast is checked across each theme. Charts, status colors, controls, tables, and account details share the selected palette. Your browser remembers the selection when storage is available, and theme changes do not affect filters or account data.
