# Provisioning a New FLL Team Laptop

A guide for any coach setting up a donated laptop for a Bolton Robotics FLL
team. Start with **Quick Start** below. If anything's unclear, the
**Detailed Steps** section that follows expands every line with specifics.

## Quick Start

The major steps, in order. The script does the heavy lifting — most of
these are short:

1. **Team email** — `fss.fll.<TeamNumber>@gmail.com` or `@outlook.com`. Create one if the team doesn't have it.
2. **Team GitHub** — a `fssfll<TeamNumber>` user with a fork of `stevenerat/spike_basecode`. Create and fork if needed.
3. **Download** `setup-fll-laptop.ps1` from the chapter upstream to the new laptop (e.g., to `Downloads`).
4. **Open PowerShell as Administrator** and run:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\setup-fll-laptop.ps1 <TeamNumber>
   ```

5. **Follow the prompts** when the script asks — confirm new-team data if it's a new team, then complete the GitHub Desktop sign-in and clone during the script's pause partway through.
6. **Verify** — repo cloned to `~\repos\spike_basecode\`, VS Code opens it with the `.venv` interpreter, and a test program runs on a SPIKE Prime hub.
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

### 2. Set up a team GitHub account (if one does not already exist)

Chapter standard username: `fssfll<TeamNumber>` (e.g. `fssfll27041`).

The account needs to have a fork of `stevenerat/spike_basecode`. If the
team is new, sign in as the team's GitHub user and click **Fork** at
`https://github.com/stevenerat/spike_basecode`.

2FA is optional — the chapter has only enabled it for teams with a security-
conscious lead coach. Decide based on who will be using the account.

### 3. Download the setup script to the laptop

You'll download `setup-fll-laptop.ps1` as a standalone file (right-click →
Save link as, or use the Raw view → save). This is the bootstrap: the
script can't be cloned because nothing on the laptop knows how to clone
yet. Save it somewhere easy to find, like `Downloads`.

The two cases below differ only in whether you sync the team's fork first.

#### 3a. New team — download from upstream

Go to `https://github.com/stevenerat/spike_basecode/tree/main/scripts/`,
open `setup-fll-laptop.ps1`, and save the Raw view. This is the chapter's
source of truth for the script.

#### 3b. Existing team — sync the fork first, then download

If the team already has a fork (e.g., this laptop is replacing an old one),
the fork may be behind upstream. Before downloading the script:

1. Go to `https://github.com/fssfll<TeamNumber>/spike_basecode`
2. If GitHub shows "This branch is N commits behind", click **Sync fork**
3. Then download `setup-fll-laptop.ps1` from the team's fork (or from
   upstream — either is fine once the fork is synced)

Syncing the fork first ensures the cloned repo the script lands on the
laptop will have the latest chapter code, not just the latest script.

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
  name, and GitHub username. Examples are shown in the prompts.
- **GitHub Desktop authentication and clone**: midway through, the script
  launches GitHub Desktop and pauses. Follow the on-screen instructions:
  sign in to GitHub as the team user, clone the fork to the path the script
  shows, and — when asked "How are you planning to use this fork?" — select
  **For my own purposes**, not "To contribute to the parent project". Press
  Enter in the PowerShell window when the clone is done.

If anything goes sideways, the script is safe to re-run from the start.

### 6. Verify the setup

When the script finishes, confirm:

- The repo folder exists at `C:\Users\<user>\repos\spike_basecode\` and
  contains the chapter code (not just a `.git` folder).
- GitHub Desktop is signed in as the team user and shows the cloned repo.
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
`https://github.com/stevenerat/spike_basecode/blob/main/scripts/setup-fll-laptop.ps1`.
For chapter-specific questions, contact Steve. For technical questions
about a specific failure mode, capture the PowerShell output and send it
along.
