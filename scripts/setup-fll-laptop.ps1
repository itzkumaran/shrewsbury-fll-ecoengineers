<#
.SYNOPSIS
    Standardized setup script for Bolton Robotics FLL chapter laptops.

.DESCRIPTION
    Run this script ONCE per donated laptop, while logged in as the
    student team account (which has temporary or permanent admin privileges).

    Pass the team number as the first argument, or run with no arguments
    to see the team menu and be prompted.

    The script:
      1.  Installs core software (Git, Python, VS Code, Chrome, GitHub Desktop) via winget
      2.  Writes a chapter-standard .gitconfig to the user's home directory
      3.  Installs VS Code extensions and configures user settings
      4.  Sets Chrome as default browser, unpins Edge from taskbar
      5.  Quiets Windows notifications, disables suggested content / ads
      6.  Configures power plan, Windows Update active hours
      7.  Creates the team's repo folder, app shortcuts, and team shortcuts on the desktop
      8.  Launches GitHub Desktop and pauses for the user to authenticate and clone the fork
      9.  Configures the cloned repo: upstream remote, Python venv,
          pybricks + pybricksdev packages, VS Code workspace settings

    What it does NOT do (these are interactive, do them manually after):
      - Sign in to Chrome with the team Gmail (Chrome requires a Google account;
        outlook.com teams skip this step)
      - Set Chrome as default browser
      - Install the Pybricks firmware on the SPIKE Prime hub
      - Pin shortcuts to the taskbar (Microsoft removed scripted pinning;
        right-click each desktop shortcut and choose "Pin to taskbar")

    NEW TEAM SUPPORT:
      If the team number is not in the $KnownTeams table, the script will
      prompt for the team's email, display name, and GitHub username. No
      script edit needed to set up a new team. You can optionally add the
      team to $KnownTeams afterward so it appears in the menu next time.

.NOTES
    Author:   Steven Erat with Claude (Bolton Robotics chapter)
    Audience: FLL chapter coaches provisioning team laptops
    Tested on: Windows 11 (should also work on Windows 10 with winget installed)

    Run as Administrator from PowerShell:
        Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
        .\setup-fll-laptop.ps1 27041
#>

# =============================================================================
# TEAM SELECTION
# =============================================================================

param(
    [Parameter(Position = 0)]
    [string]$TeamNumber
)

# Known chapter teams. To add a team to the menu, add an entry here.
# Otherwise, enter the team number at the prompt and the script will
# collect the team's email, name, and GitHub username interactively.
$KnownTeams = @{
    "18300" = @{ Name = "";                Email = "fss.fll.18300@outlook.com" }
    "19991" = @{ Name = "";                Email = "fss.fll.19991@outlook.com" }
    "27041" = @{ Name = "Thought Process"; Email = "fss.fll.27041@gmail.com"   }
    "27042" = @{ Name = "";                Email = "fss.fll.27042@gmail.com"   }
    "62070" = @{ Name = "";                Email = "fss.fll.62070@outlook.com" }
}

# Show menu if no team number was passed on the command line
if (-not $TeamNumber) {
    Write-Host ""
    Write-Host "Bolton Robotics FLL -- known teams:" -ForegroundColor Cyan
    foreach ($t in $KnownTeams.Keys | Sort-Object) {
        $label = if ($KnownTeams[$t].Name) { $KnownTeams[$t].Name } else { "(unnamed)" }
        Write-Host "  $t  $label"
    }
    Write-Host "  (or enter any other 5-digit number for a new team)"
    Write-Host ""
    $TeamNumber = Read-Host "Enter team number for this laptop"
}

# If team is unknown, collect details interactively
if (-not $KnownTeams.ContainsKey($TeamNumber)) {
    Write-Host ""
    Write-Host "Team $TeamNumber is NOT in the known teams list." -ForegroundColor Yellow
    Write-Host "This will set up the laptop as a NEW team." -ForegroundColor Yellow
    Write-Host "(If you meant an existing team, this is a good moment to check for a typo.)" -ForegroundColor Yellow
    $confirm = Read-Host "Continue setup for new team $TeamNumber? (Y/n)"
    if ($confirm -and $confirm -notmatch '^[Yy]') {
        Write-Host "Cancelled. Run the script again with the correct team number." -ForegroundColor Red
        exit 1
    }

    Write-Host ""
    Write-Host "Enter team email." -ForegroundColor Cyan
    Write-Host "Chapter standard format examples (do not press Enter to accept -- type the actual email):" -ForegroundColor Cyan
    Write-Host "  fss.fll.$TeamNumber@gmail.com" -ForegroundColor Gray
    Write-Host "  fss.fll.$TeamNumber@outlook.com" -ForegroundColor Gray
    $newEmail = Read-Host "Team email"
    while (-not $newEmail -or $newEmail -notmatch '@') {
        Write-Warning "Email is required and must contain '@'."
        $newEmail = Read-Host "Team email"
    }

    Write-Host ""
    $newName = Read-Host "Team display name (optional; press Enter to skip)"

    Write-Host ""
    $defaultGitHubUser = "fssfll$TeamNumber"
    $newGitHubUser = Read-Host "GitHub username (press Enter for '$defaultGitHubUser')"
    if (-not $newGitHubUser) { $newGitHubUser = $defaultGitHubUser }

    # Stash into the same structure used for known teams
    $KnownTeams[$TeamNumber] = @{
        Name       = $newName
        Email      = $newEmail
        GitHubUser = $newGitHubUser
    }
}

# Resolve team values
$teamData    = $KnownTeams[$TeamNumber]
$TeamName    = if ($teamData.Name) { $teamData.Name } else { "Bolton Robotics Team $TeamNumber" }
$TeamEmail   = $teamData.Email
$GitHubUser  = if ($teamData.GitHubUser) { $teamData.GitHubUser } else { "fssfll$TeamNumber" }

$GitUserName  = "Bolton Robotics FLL Team $TeamNumber"  # Shows up in commit history
$GitUserEmail = $TeamEmail                              # Per-team email (gmail or outlook)
$ForkUrl      = "https://github.com/$GitHubUser/spike_basecode.git"
$UpstreamUrl  = "https://github.com/stevenerat/spike_basecode.git"

# Local paths
$ReposRoot     = "$env:USERPROFILE\repos"
$RepoPath      = "$ReposRoot\spike_basecode"
$DesktopPath   = [Environment]::GetFolderPath("Desktop")
$GitConfigPath = "$env:USERPROFILE\.gitconfig"

# =============================================================================
# PRELIMINARIES
# =============================================================================

# Stop on errors so failures are visible rather than silent
$ErrorActionPreference = "Stop"

# Verify we're running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal(
    [Security.Principal.WindowsIdentity]::GetCurrent()
)
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "This script must be run as Administrator. Right-click PowerShell -> Run as Administrator."
    exit 1
}

Write-Host ""
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host " FLL Laptop Setup -- Team $TeamNumber ($TeamName)" -ForegroundColor Cyan
Write-Host " Email:  $TeamEmail" -ForegroundColor Cyan
Write-Host " GitHub: $GitHubUser" -ForegroundColor Cyan
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host ""

# =============================================================================
# 1. SOFTWARE INSTALLATION VIA WINGET
# =============================================================================

Write-Host "[1/9] Installing core software via winget..." -ForegroundColor Yellow

$packages = @(
    @{ Id = "Git.Git";                       Name = "Git for Windows" },
    @{ Id = "Python.Python.3.12";            Name = "Python 3.12" },
    @{ Id = "Microsoft.VisualStudioCode";    Name = "VS Code" },
    @{ Id = "Google.Chrome";                 Name = "Google Chrome" },
    @{ Id = "GitHub.GitHubDesktop";          Name = "GitHub Desktop" }
)

foreach ($pkg in $packages) {
    Write-Host "  Installing $($pkg.Name)..." -ForegroundColor Gray
    winget install --id $pkg.Id --exact --silent --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne -1978335189) {
        # -1978335189 = "already installed", which is fine
        Write-Warning "winget reported exit code $LASTEXITCODE for $($pkg.Name). Continuing."
    }
}

# Refresh PATH so newly-installed tools are findable in this session
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "  Software install complete." -ForegroundColor Green
Write-Host ""

# =============================================================================
# 2. GIT CONFIGURATION (.gitconfig)
# =============================================================================

Write-Host "[2/9] Writing chapter-standard .gitconfig..." -ForegroundColor Yellow

# Adapted from Steve's Mac .gitconfig with Windows-specific adjustments:
#   - core.autocrlf set to "false" (the repo's .gitattributes drives EOL
#     behavior; setting autocrlf alongside it causes phantom diffs and
#     conflicting rules). The chapter repo's .gitattributes specifies
#     `* text=auto eol=lf` plus `*.bat eol=crlf`, which is what we want
#     on Windows.
#   - filter "lfs" section removed (Git LFS not installed; chapter repo doesn't use it)
#   - Added init.defaultBranch, pull.rebase, credential.helper
#
# Re-running this script OVERWRITES the .gitconfig file -- any manual edits will be lost.

$gitConfigContent = @"
# ~/.gitconfig -- FLL chapter laptop
# Adapted from Steve's Mac .gitconfig with Windows-specific adjustments.
# Generated by setup-fll-laptop.ps1 -- re-running the script overwrites this file.

[user]
    name = $GitUserName
    email = $GitUserEmail

[init]
    defaultBranch = main

[pull]
    rebase = false                   # Default to merge on pull, not rebase

[credential]
    helper = manager                 # Windows Credential Manager for GitHub auth

[color]
    ui = auto

[color "status"]
    added = green
    changed = yellow
    untracked = red

[color "diff"]
    meta = cyan
    frag = magenta
    old = red
    new = green

[color "branch"]
    current = yellow bold
    local = green
    remote = cyan

[core]
    editor = code --wait             # VS Code as default editor
    pager = less -FRSX               # Better pager (works in Git Bash)
    autocrlf = false                 # .gitattributes drives EOL behavior; don't double up

[help]
    autocorrect = 20                 # Auto-run corrected commands after 2 sec

[merge]
    conflictstyle = diff3            # Show base version during conflicts

[blame]
    coloring = highlightRecent

[diff]
    tool = vimdiff

[difftool]
    prompt = false

[alias]
    st = status -sb
    lg = log --graph --decorate --oneline --all
    lga = log --graph --decorate --pretty=oneline --abbrev-commit --all
    undo = reset --soft HEAD~1
"@

Set-Content -Path $GitConfigPath -Value $gitConfigContent -Encoding UTF8

Write-Host "  .gitconfig written to $GitConfigPath" -ForegroundColor Green
Write-Host "  Configured for $GitUserName <$GitUserEmail>." -ForegroundColor Green
Write-Host ""

# =============================================================================
# 3. VS CODE EXTENSIONS AND USER SETTINGS
# =============================================================================

Write-Host "[3/9] Installing VS Code extensions and configuring user settings..." -ForegroundColor Yellow

# Note: ms-vscode.powershell intentionally NOT included.
# Steve is the only chapter coach who edits PowerShell, and he's on a Mac.
# The extension also stalled during install on a slow network during the
# 5-laptop run -- reliability risk with zero educational value.
$vscodeExtensions = @(
    "ms-python.python",
    "ms-python.vscode-pylance",
    "eamodio.gitlens"
)

foreach ($ext in $vscodeExtensions) {
    Write-Host "  Installing extension: $ext" -ForegroundColor Gray
    code --install-extension $ext --force | Out-Null
}

# Configure VS Code USER settings (apply to all workspaces).
# Workspace settings (per-repo, including the venv interpreter) are written
# in Section 9 after the repo is cloned.
$vscodeSettingsDir  = "$env:APPDATA\Code\User"
$vscodeSettingsPath = "$vscodeSettingsDir\settings.json"

if (-not (Test-Path $vscodeSettingsDir)) {
    New-Item -ItemType Directory -Path $vscodeSettingsDir -Force | Out-Null
}

$vscodeSettings = [ordered]@{
    "terminal.integrated.defaultProfile.windows" = "Git Bash"
    "editor.formatOnSave"                        = $true
    "files.trimTrailingWhitespace"               = $true
    "files.insertFinalNewline"                   = $true
    "telemetry.telemetryLevel"                   = "off"
    "update.showReleaseNotes"                    = $false
    "workbench.startupEditor"                    = "none"
    "explorer.confirmDragAndDrop"                = $false
}

$vscodeSettings | ConvertTo-Json -Depth 5 | Set-Content -Path $vscodeSettingsPath -Encoding UTF8

Write-Host "  VS Code configured." -ForegroundColor Green
Write-Host ""

# =============================================================================
# 4. BROWSER AND TASKBAR CLEANUP
# =============================================================================

Write-Host "[4/9] Configuring browser defaults and cleaning up taskbar..." -ForegroundColor Yellow

# Chrome as default browser cannot be set silently in modern Windows without
# admin SetUserFTA tooling. We'll prompt the user instead.
Write-Host "  NOTE: Setting Chrome as default browser must be done manually." -ForegroundColor Cyan
Write-Host "        After this script finishes, open Settings > Apps > Default apps" -ForegroundColor Cyan
Write-Host "        > Google Chrome > Set default." -ForegroundColor Cyan

# Unpin Edge from taskbar (works on Windows 11)
try {
    $edgeShortcut = "$env:APPDATA\Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar\Microsoft Edge.lnk"
    if (Test-Path $edgeShortcut) {
        Remove-Item $edgeShortcut -Force
        Write-Host "  Removed Edge taskbar pin." -ForegroundColor Gray
    }
} catch {
    Write-Warning "Could not remove Edge taskbar pin automatically. Right-click and unpin manually."
}

Write-Host "  Browser/taskbar cleanup complete." -ForegroundColor Green
Write-Host ""

# =============================================================================
# 5. QUIET WINDOWS -- NOTIFICATIONS, ADS, SUGGESTED CONTENT
# =============================================================================

Write-Host "[5/9] Quieting Windows notifications and ads..." -ForegroundColor Yellow

# Disable "suggested content" in Settings app and Start menu
$contentDeliveryPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"
$suggestedKeys = @(
    "SubscribedContent-338388Enabled",   # Start menu suggestions
    "SubscribedContent-338389Enabled",   # Tips, tricks suggestions
    "SubscribedContent-353694Enabled",   # Settings app suggestions
    "SubscribedContent-353696Enabled",   # Settings app suggestions
    "SilentInstalledAppsEnabled",        # Auto-installed promoted apps
    "SystemPaneSuggestionsEnabled"       # Start menu app suggestions
)
foreach ($key in $suggestedKeys) {
    Set-ItemProperty -Path $contentDeliveryPath -Name $key -Value 0 -Type DWord -Force
}

# Disable web search results in Start menu
$searchPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Search"
if (-not (Test-Path $searchPath)) { New-Item -Path $searchPath -Force | Out-Null }
Set-ItemProperty -Path $searchPath -Name "BingSearchEnabled" -Value 0 -Type DWord -Force
Set-ItemProperty -Path $searchPath -Name "CortanaConsent"    -Value 0 -Type DWord -Force

# Disable lock screen ads / suggestions
Set-ItemProperty -Path $contentDeliveryPath -Name "RotatingLockScreenEnabled" -Value 0 -Type DWord -Force
Set-ItemProperty -Path $contentDeliveryPath -Name "RotatingLockScreenOverlayEnabled" -Value 0 -Type DWord -Force

# Disable OneDrive auto-sync prompts (does not uninstall OneDrive)
$oneDrivePath = "HKCU:\Software\Microsoft\OneDrive"
if (-not (Test-Path $oneDrivePath)) { New-Item -Path $oneDrivePath -Force | Out-Null }
Set-ItemProperty -Path $oneDrivePath -Name "DisablePersonalSync" -Value 1 -Type DWord -Force

Write-Host "  Windows quieted." -ForegroundColor Green
Write-Host ""

# =============================================================================
# 6. POWER PLAN AND WINDOWS UPDATE
# =============================================================================

Write-Host "[6/9] Configuring power plan and Windows Update..." -ForegroundColor Yellow

# Power plan: don't sleep aggressively while plugged in at meetings
powercfg /change standby-timeout-ac 60
powercfg /change monitor-timeout-ac 30
powercfg /change disk-timeout-ac    0      # Never spin down disk on AC

# Windows Update active hours: 8 AM to 8 PM (covers all reasonable meeting times)
$wuPath = "HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings"
if (-not (Test-Path $wuPath)) { New-Item -Path $wuPath -Force | Out-Null }
Set-ItemProperty -Path $wuPath -Name "ActiveHoursStart" -Value 8  -Type DWord -Force
Set-ItemProperty -Path $wuPath -Name "ActiveHoursEnd"   -Value 20 -Type DWord -Force

Write-Host "  Power plan and update hours configured." -ForegroundColor Green
Write-Host ""

# =============================================================================
# 7. REPO FOLDER, DESKTOP SHORTCUTS, README
# =============================================================================

Write-Host "[7/9] Creating repo folder and desktop shortcuts..." -ForegroundColor Yellow

# Create repo parent folder (clone will land here in Section 8)
if (-not (Test-Path $ReposRoot)) {
    New-Item -ItemType Directory -Path $ReposRoot -Force | Out-Null
}

# Helper function to create .lnk shortcuts
function New-Shortcut {
    param(
        [string]$Path,
        [string]$Target,
        [string]$Arguments = "",
        [string]$WorkingDirectory = "",
        [string]$IconLocation = ""
    )
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($Path)
    $shortcut.TargetPath = $Target
    if ($Arguments)        { $shortcut.Arguments = $Arguments }
    if ($WorkingDirectory) { $shortcut.WorkingDirectory = $WorkingDirectory }
    if ($IconLocation)     { $shortcut.IconLocation = $IconLocation }
    $shortcut.Save()
}

# General app shortcuts ------------------------------------------------------

$chromeExe = "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe"
if (-not (Test-Path $chromeExe)) {
    $chromeExe = "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"
}
if (Test-Path $chromeExe) {
    New-Shortcut -Path "$DesktopPath\Google Chrome.lnk" -Target $chromeExe
    Write-Host "  Created shortcut: Google Chrome" -ForegroundColor Gray
} else {
    Write-Warning "  Chrome executable not found; skipping Chrome shortcut."
}

# GitHub Desktop installs per-user under LOCALAPPDATA
$githubDesktopExe = "$env:LOCALAPPDATA\GitHubDesktop\GitHubDesktop.exe"
if (-not (Test-Path $githubDesktopExe)) {
    $candidate = Get-ChildItem "$env:LOCALAPPDATA\GitHubDesktop" -Filter "GitHubDesktop.exe" `
                    -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($candidate) { $githubDesktopExe = $candidate.FullName }
}
if (Test-Path $githubDesktopExe) {
    New-Shortcut -Path "$DesktopPath\GitHub Desktop.lnk" -Target $githubDesktopExe
    Write-Host "  Created shortcut: GitHub Desktop" -ForegroundColor Gray
} else {
    Write-Warning "  GitHub Desktop executable not found; skipping shortcut."
}

# VS Code shortcut (general)
$vscodeExe = "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe"
if (-not (Test-Path $vscodeExe)) {
    $vscodeExe = "${env:ProgramFiles}\Microsoft VS Code\Code.exe"
}
if (Test-Path $vscodeExe) {
    New-Shortcut -Path "$DesktopPath\Visual Studio Code.lnk" -Target $vscodeExe
    Write-Host "  Created shortcut: Visual Studio Code" -ForegroundColor Gray
} else {
    Write-Warning "  VS Code executable not found; skipping general VS Code shortcut."
}

# File Explorer and Command Prompt -- built-in, always present
New-Shortcut -Path "$DesktopPath\File Explorer.lnk" -Target "explorer.exe"
Write-Host "  Created shortcut: File Explorer" -ForegroundColor Gray
New-Shortcut -Path "$DesktopPath\Command Prompt.lnk" -Target "$env:SystemRoot\System32\cmd.exe"
Write-Host "  Created shortcut: Command Prompt" -ForegroundColor Gray

# Team-specific workflow shortcuts ------------------------------------------

if (Test-Path $vscodeExe) {
    New-Shortcut `
        -Path "$DesktopPath\Open Team $TeamNumber Code.lnk" `
        -Target $vscodeExe `
        -Arguments "`"$RepoPath`"" `
        -WorkingDirectory $RepoPath
    Write-Host "  Created shortcut: Open Team $TeamNumber Code" -ForegroundColor Gray
}

New-Shortcut `
    -Path "$DesktopPath\Team $TeamNumber Repo Folder.lnk" `
    -Target "explorer.exe" `
    -Arguments "`"$RepoPath`""
Write-Host "  Created shortcut: Team $TeamNumber Repo Folder" -ForegroundColor Gray

$gitBashExe = "${env:ProgramFiles}\Git\git-bash.exe"
if (Test-Path $gitBashExe) {
    New-Shortcut `
        -Path "$DesktopPath\Git Bash (Team $TeamNumber).lnk" `
        -Target $gitBashExe `
        -Arguments "--cd=`"$RepoPath`""
    Write-Host "  Created shortcut: Git Bash (Team $TeamNumber)" -ForegroundColor Gray
}

# Desktop README -- GitHub Desktop oriented, not git CLI -------------------

$readmeContent = @"
TEAM $TeamNumber - $TeamName
==========================================

YOUR CODE LIVES IN:
  $RepoPath

EVERYDAY WORKFLOW (use GitHub Desktop):

  Get the latest code from your team's repo:
    1. Open GitHub Desktop
    2. Click "Fetch origin" (top bar)
    3. Click "Pull origin" if updates appear

  Save your changes:
    1. Open GitHub Desktop
    2. Review changed files in the "Changes" tab
    3. Type a summary message at the bottom-left
    4. Click "Commit to main"
    5. Click "Push origin" in the top bar

  Pull chapter updates (when Steve announces changes):
    1. Go to https://github.com/$GitHubUser/spike_basecode
    2. If GitHub shows "This branch is N commits behind", click "Sync fork"
    3. In GitHub Desktop, click "Fetch origin" then "Pull origin"

  Run code on the SPIKE hub:
    Open Git Bash (or the VS Code terminal) in the repo folder, then run:
      python -m pybricksdev run ble --name <hub-name> main.py

QUESTIONS?
  Talk to your coach, or contact Steve.

YOUR TEAM'S GITHUB:
  https://github.com/$GitHubUser/spike_basecode

CHAPTER UPSTREAM (where updates come from):
  $UpstreamUrl

NOTE FOR TECHNICAL COACHES:
  Git CLI works too. The repo has scripts/sync-from-upstream.ps1 for
  fetching chapter updates from PowerShell.
"@

Set-Content -Path "$DesktopPath\README - Team $TeamNumber.txt" -Value $readmeContent -Encoding UTF8

Write-Host "  Desktop shortcuts and README created." -ForegroundColor Green
Write-Host ""

# =============================================================================
# 8. GITHUB DESKTOP AUTHENTICATION AND REPO CLONE (INTERACTIVE PAUSE)
# =============================================================================

Write-Host "[8/9] GitHub Desktop authentication and repository clone..." -ForegroundColor Yellow

if (Test-Path "$RepoPath\.git") {
    Write-Host "  Repository already cloned at $RepoPath -- skipping clone step." -ForegroundColor Gray
} else {
    if (Test-Path $githubDesktopExe) {
        Start-Process $githubDesktopExe
        Write-Host "  GitHub Desktop launched." -ForegroundColor Gray
    } else {
        Write-Warning "  GitHub Desktop executable not found -- launch it manually from the Start Menu."
    }

    Write-Host ""
    Write-Host "  MANUAL STEPS in GitHub Desktop:" -ForegroundColor Cyan
    Write-Host "    1. Sign in to GitHub (if not already signed in)." -ForegroundColor Cyan
    Write-Host "       Use the team's GitHub account: $GitHubUser" -ForegroundColor Cyan
    Write-Host "    2. File > Clone Repository > URL tab" -ForegroundColor Cyan
    Write-Host "         URL:        $ForkUrl" -ForegroundColor Cyan
    Write-Host "         Local path: $RepoPath" -ForegroundColor Cyan
    Write-Host "       Click Clone." -ForegroundColor Cyan
    Write-Host "    3. When asked 'How are you planning to use this fork?':" -ForegroundColor Cyan
    Write-Host "         Select 'For my own purposes'." -ForegroundColor Cyan
    Write-Host "         Do NOT select 'To contribute to the parent project'." -ForegroundColor Cyan
    Write-Host "         (Team repos are downstream-only; chapter updates flow one direction.)" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "  Press Enter after the clone is complete"

    if (-not (Test-Path "$RepoPath\.git")) {
        Write-Host ""
        Write-Error "Clone not detected at $RepoPath."
        Write-Host ""
        Write-Host "If you'd rather clone from the command line, open Git Bash and run:" -ForegroundColor Yellow
        Write-Host "  git clone $ForkUrl `"$RepoPath`"" -ForegroundColor Gray
        Write-Host "Then re-run this script -- it is safe to re-run." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "  Clone detected at $RepoPath." -ForegroundColor Green
}
Write-Host ""

# =============================================================================
# 9. POST-CLONE REPO SETUP -- UPSTREAM, VENV, PACKAGES, WORKSPACE SETTINGS
# =============================================================================

Write-Host "[9/9] Configuring repo: upstream remote, Python venv, packages, VS Code workspace..." -ForegroundColor Yellow

Push-Location $RepoPath
try {
    # 9a. Add upstream remote if not configured
    #     (GitHub Desktop's "For my own purposes" choice does NOT configure upstream)
    $existingRemotes = git remote
    if ($existingRemotes -notcontains "upstream") {
        git remote add upstream $UpstreamUrl
        Write-Host "  Added upstream remote: $UpstreamUrl" -ForegroundColor Gray
    } else {
        Write-Host "  Upstream remote already configured -- skipping." -ForegroundColor Gray
    }

    # 9b. Create .venv if not present
    $venvPython = "$RepoPath\.venv\Scripts\python.exe"
    if (-not (Test-Path $venvPython)) {
        Write-Host "  Creating Python virtual environment in .venv..." -ForegroundColor Gray
        python -m venv .venv
        if (-not (Test-Path $venvPython)) {
            Write-Error "Failed to create .venv. Check that Python 3.12 is on PATH (try opening a new PowerShell window and re-running)."
            exit 1
        }
    } else {
        Write-Host "  Python venv already exists -- skipping creation." -ForegroundColor Gray
    }

    # 9c. Upgrade pip inside the venv
    Write-Host "  Upgrading pip in .venv..." -ForegroundColor Gray
    & $venvPython -m pip install --upgrade pip --quiet

    # 9d. Install pybricks and pybricksdev by name (no requirements.txt;
    #     these two packages are the canonical chapter dependencies)
    Write-Host "  Installing pybricks and pybricksdev..." -ForegroundColor Gray
    & $venvPython -m pip install pybricks pybricksdev --quiet
    Write-Host "  Packages installed." -ForegroundColor Gray

    # 9e. Write workspace .vscode/settings.json so VS Code auto-selects the venv
    $workspaceSettingsDir  = "$RepoPath\.vscode"
    $workspaceSettingsPath = "$workspaceSettingsDir\settings.json"
    $venvPythonRelative    = ".venv\Scripts\python.exe"  # workspace-relative; ConvertTo-Json escapes backslashes

    if (-not (Test-Path $workspaceSettingsDir)) {
        New-Item -ItemType Directory -Path $workspaceSettingsDir -Force | Out-Null
    }

    if (Test-Path $workspaceSettingsPath) {
        # Merge: parse existing JSON, set/overwrite our key, write back.
        # Insurance against future repo PRs that add other workspace settings.
        try {
            $existingJson = Get-Content $workspaceSettingsPath -Raw | ConvertFrom-Json
            $existingJson | Add-Member `
                -NotePropertyName "python.defaultInterpreterPath" `
                -NotePropertyValue $venvPythonRelative `
                -Force
            $existingJson | ConvertTo-Json -Depth 10 | Set-Content -Path $workspaceSettingsPath -Encoding UTF8
            Write-Host "  Merged python.defaultInterpreterPath into existing .vscode/settings.json" -ForegroundColor Gray
        } catch {
            Write-Warning "  Could not parse existing .vscode/settings.json; leaving it untouched."
            Write-Warning "  Set the interpreter manually in VS Code:"
            Write-Warning "  Ctrl+Shift+P -> Python: Select Interpreter -> .venv"
        }
    } else {
        $workspaceSettings = [ordered]@{
            "python.defaultInterpreterPath" = $venvPythonRelative
        }
        $workspaceSettings | ConvertTo-Json -Depth 5 | Set-Content -Path $workspaceSettingsPath -Encoding UTF8
        Write-Host "  Wrote .vscode/settings.json with Python interpreter path." -ForegroundColor Gray
    }
} finally {
    Pop-Location
}

Write-Host "  Repo setup complete." -ForegroundColor Green
Write-Host ""

# =============================================================================
# DONE
# =============================================================================

Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host " Setup complete for Team $TeamNumber ($TeamName)" -ForegroundColor Cyan
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "REMAINING MANUAL STEPS:" -ForegroundColor Yellow
Write-Host "  1. Set Chrome as default browser:" -ForegroundColor White
Write-Host "       Settings > Apps > Default apps > Google Chrome > Set default"
Write-Host "  2. (Optional) Sign in to Chrome with $TeamEmail" -ForegroundColor White
Write-Host "       Note: Chrome requires a Google account."
Write-Host "       Outlook.com teams cannot sign in to Chrome -- skip this step."
Write-Host "  3. Pin desktop shortcuts to the taskbar:" -ForegroundColor White
Write-Host "       Right-click each shortcut on the desktop, choose 'Pin to taskbar'."
Write-Host "  4. Launch VS Code via 'Open Team $TeamNumber Code' shortcut." -ForegroundColor White
Write-Host "       Verify the venv shows in the bottom-right status bar"
Write-Host "       (should display '.venv': Python 3.12.x). If it doesn't:"
Write-Host "       Ctrl+Shift+P -> Python: Select Interpreter -> .venv"
Write-Host "  5. Open menu.py in VS Code and confirm pybricks imports do not" -ForegroundColor White
Write-Host "       trigger 'Import could not be resolved' errors. Some type-check"
Write-Host "       warnings may remain depending on the repo's typing stubs;"
Write-Host "       runtime behavior on the hub is what matters."
Write-Host "  6. Connect to a SPIKE Prime hub and run a test program to confirm" -ForegroundColor White
Write-Host "       the full pipeline:"
Write-Host "         python -m pybricksdev run ble --name <hub-name> main.py"
Write-Host ""
Write-Host "If anything went wrong, the script is safe to re-run." -ForegroundColor Gray
Write-Host ""
