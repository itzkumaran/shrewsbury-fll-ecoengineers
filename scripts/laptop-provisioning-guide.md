# Provisioning a New FLL Team Laptop

A guide for any coach setting up a donated laptop for a ECO Engineers FLL
team. Start with **Quick Start** below. If anything's unclear, the
**Detailed Steps** section that follows expands every line with specifics.

## Quick Start

The major steps, in order. The script does the heavy lifting — most of
these are short:

1. **Team email** — `fss.fll.<TeamNumber>@gmail.com` or `@outlook.com`. Create one if the team doesn't have it.
2. **Your GitHub account** — each team member uses their own unique GitHub username. Create one if you don't already have one. You'll clone the shared team repo at `itzkumaran/shrewsbury-fll-ecoengineers`; there is no per-user fork.
3. **Download** `setup-fll-laptop.ps1` from the chapter upstream to the new laptop (e.g., to `Downloads`).
4. **Open PowerShell as Administrator** and run:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\setup-fll-laptop.ps1 <TeamNumber>
   ```

5. **Follow the prompts** when the script asks — confirm new-team data if it's a new team, then complete the GitHub Desktop sign-in and clone during the script's pause partway through.
6. **Verify** — repo cloned to `~\repos\shrewsbury-fll-ecoengineers\`, VS Code opens it with the `.venv` interpreter, and a test program runs on a SPIKE Prime hub.
7. **Pin shortcuts** to the taskbar from the desktop icons the script created.

That's the whole flow — typically 30 to 60 minutes, mostly waiting on
downloads. If the list above makes sense, you're ready to go.

For prerequisites, specific URLs, the new-team interactive prompts, and
gotchas, continue to **Detailed Steps** below.

## Detailed Steps

This section expands each Quick Start step with the URLs, edge cases, and
decisions you'll encounter.

One framing note up front: the setup script must be downloaded as a
standalone `.ps1` file before anything else, because a freshly-wiped laptop
doesn't have Git, GitHub Desktop, or any other chapter tooling yet. The
script itself is what installs them. You can't clone the repo first.

### Prerequisites

Before you start the laptop itself:

- A donated laptop, freshly wiped, running Windows 10 or 11
- The laptop's local user account has admin privileges (confirm with the donor)
- A reliable internet connection
- The team's email and GitHub credentials (or willingness to create them — see Step 1 and Step 2)
- About an hour of uninterrupted time

### 1. Set up a team email account (if one does not already exist)

Chapter standard format: `fss.fll.<TeamNumber>@gmail.com` or
`fss.fll.<TeamNumber>@outlook.com`. Either provider is acceptable. Gmail is
preferred when feasible because it integrates with Chrome sign-in;
Outlook is the fallback when Gmail signup is blocked.

This email becomes the team's identity for GitHub, commits, and any chapter
communications. Don't reuse a coach's personal email.

### 2. Set up a GitHub account for each team member

Each team member — coach, mentor, or student — uses their own unique
GitHub username. There is no team-wide standard username; a personal
GitHub account is fine.

Every user clones the same shared team repository at
`itzkumaran/shrewsbury-fll-ecoengineers`. There is no per-user fork; the
team maintains one shared repo that everyone commits into (with write
access granted by the repo owner).

If a team member doesn't have a GitHub account yet, they can create one
at `https://github.com/signup` using any email address.

2FA is recommended but not required. Decide based on who will be using
the account.

### 3. Download the setup script to the laptop

You'll download `setup-fll-laptop.ps1` as a standalone file (right-click →
Save link as, or use the Raw view → save). This is the bootstrap: the
script can't be cloned because nothing on the laptop knows how to clone
yet. Save it somewhere easy to find, like `Downloads`.

Go to
`https://github.com/itzkumaran/shrewsbury-fll-ecoengineers/tree/main/scripts/`,
open `setup-fll-laptop.ps1`, and save the Raw view. Save it somewhere
easy to find, like `Downloads`.

Since the team maintains one shared repo (no per-user forks), every user
downloads the same script from the same URL — there is no separate
new-team vs. existing-team flow.

### 4. Open PowerShell as Administrator and run the script

1. Press the Windows key, type `PowerShell`, right-click **Windows PowerShell**, and choose **Run as administrator**.
2. Allow the UAC prompt.
3. Set the execution policy for this session only (does not persist):

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

4. Change to the folder containing the script (e.g., `cd $env:USERPROFILE\Downloads`).
5. Run the script with the team number:

   ```powershell
   .\setup-fll-laptop.ps1 27041
   ```

   Replace `27041` with the actual team number. If you omit the number, the
   script will show a menu of known teams and prompt for one.

### 5. Complete prompts as the script runs

The script is mostly hands-off, but it will pause for input in a few places:

- **New team setup**: if the team number is not in the script's known-teams
  list, it will ask you to confirm and prompt for the team email, display
  name, and — for each user — their own unique GitHub username.
- **GitHub Desktop authentication and clone**: midway through, the script
  launches GitHub Desktop and pauses. Follow the on-screen instructions:
  sign in to GitHub with your own account, clone the shared team repo
  (`itzkumaran/shrewsbury-fll-ecoengineers`) to the path the script shows,
  and press Enter in the PowerShell window when the clone is done.

If anything goes sideways, the script is safe to re-run from the start.

### 6. Verify the setup

When the script finishes, confirm:

- The repo folder exists at `C:\Users\<user>\repos\shrewsbury-fll-ecoengineers\` and
  contains the chapter code (not just a `.git` folder).
- GitHub Desktop is signed in with your own account and shows the cloned repo.
- VS Code can be launched from the desktop shortcut **Open Team N Code**,
  and the bottom-right status bar shows a `.venv` Python interpreter. If
  not, use `Ctrl+Shift+P → Python: Select Interpreter → .venv`.
- Opening `menu.py` in VS Code does not show "Import could not be resolved"
  on `from pybricks...` lines.
- Connect to a SPIKE Prime hub and run a test program to confirm the full
  pipeline works:

  ```
  python -m pybricksdev run ble --name <hub-name> main.py
  ```

### 7. Add desktop shortcuts to the taskbar (optional)

The script creates several desktop shortcuts but cannot pin them to the
taskbar (Microsoft removed scripted pinning). For each shortcut the team
will use often — typically **Open Team N Code**, **GitHub Desktop**, and
**Google Chrome** — right-click and choose **Pin to taskbar**.

Also worth doing at this point:

- Set Chrome as the default browser: Settings → Apps → Default apps →
  Google Chrome → Set default.
- Sign in to Chrome with the team email (Gmail teams only — Chrome
  does not accept Outlook accounts).

## Notes and gotchas

**Account creation friction.** Gmail enforces a phone-number rate limit
that may block creating multiple accounts in succession; GitHub may block
account creation from `@outlook.com` addresses. If you hit either, the
chapter's workaround is to create a GitHub account using a personal email 
address TEMPORARILY, and then switch then later 
GitHub account's primary email to the team's permanent (Outlook or Gmail) address 
and then set that address as the primary email for GitHub. Then remove the personal address.  

**The script is idempotent.** If anything fails partway through, re-running
the script from the start is the recommended fix. Already-installed
software, existing configs, and an existing clone will all be detected and
skipped.

**Where to find help.** The script is at
`https://github.com/itzkumaran/shrewsbury-fll-ecoengineers/blob/main/scripts/setup-fll-laptop.ps1`.
For team-specific questions, contact the team lead. For technical questions
about a specific failure mode, capture the PowerShell output and send it
along.
