# Workbook-driven dashboard

The private source workbook is Documents/Valorant Info Sheet.xlsx. Never commit or publish this workbook, login usernames, passwords, raw notes, or workbook hyperlinks.

Whenever updating the workbook, run sync_workbook.py after saving it. It generates data.js through a public-field allowlist. The UI reads data.js; do not embed account data in index.html or app.js.

Verify the generated data after exporter changes. Recompute totals from mode inputs. Preserve field verification flags. Keep the original workbook outside this repository.

Local automatic updates require Start Dashboard.cmd to remain running. Hosted changes require pushing updated data.js to GitHub and a successful Pages deployment. Do not claim that Pages reads the user's local workbook.
