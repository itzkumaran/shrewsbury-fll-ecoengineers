<#
.SYNOPSIS
    Sync the team's local repo and GitHub fork with the chapter upstream.

.DESCRIPTION
    Pulls the latest changes from stevenerat/spike_basecode (upstream) into
    the local main branch, then pushes them up to the team's fork (origin)
    so github.com is also current.

    Equivalent to clicking "Sync fork" on the GitHub web UI followed by
    "Pull" in GitHub Desktop - but does both in one shot, from the repo.

    Pre-flight checks (script refuses to run if any fail):
      1. Must be inside a git working tree
      2. Must have an 'upstream' remote configured
      3. Must be on the 'main' branch
      4. Working tree must be clean (no uncommitted changes)

    Sync steps:
      1. git fetch upstream
      2. git merge --ff-only upstream/main
      3. git push origin main

    Uses --ff-only on purpose: if the team's local main has commits that
    aren't on upstream/main, the script stops with a clear message rather
    than starting a merge that could introduce conflicts. In that case,
    coordinate with Steve or Dan to decide how to integrate.

.NOTES
    Author:   Steven Erat with Claude (Bolton Robotics chapter)
    Audience: Steve, Dan, or any coach with a configured team laptop

    Run from anywhere inside the repo (the script cd's to the repo root
    automatically and restores your previous location on exit):
        cd ~\repos\spike_basecode
        .\scripts\sync-from-upstream.ps1
#>

$ErrorActionPreference = "Stop"

# -----------------------------------------------------------------------------
# Helper output functions
# -----------------------------------------------------------------------------

function Write-Step($message) {
    Write-Host ""
    Write-Host ">>> $message" -ForegroundColor Cyan
}

function Write-Ok($message) {
    Write-Host "    $message" -ForegroundColor Green
}

function Write-Fail($message) {
    Write-Host ""
    Write-Host "ERROR: $message" -ForegroundColor Red
    Write-Host ""
    Pop-Location -ErrorAction SilentlyContinue
    exit 1
}

# -----------------------------------------------------------------------------
# Pre-flight checks
# -----------------------------------------------------------------------------

Write-Step "Pre-flight checks"

# Check 1: are we inside a git working tree?
$insideRepo = git rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0 -or $insideRepo -ne "true") {
    Write-Fail "Not inside a git repository. cd to the repo folder first."
}

# Move to the repo root so all subsequent commands behave predictably.
# Push-Location lets us restore the caller's location on exit.
$repoRoot = git rev-parse --show-toplevel
Push-Location $repoRoot
Write-Ok "Repo: $repoRoot"

# Check 2: does the 'upstream' remote exist?
$upstreamUrl = git remote get-url upstream 2>$null
if (-not $upstreamUrl) {
    Write-Fail @"
No 'upstream' remote configured for this repo.

Run finalize-team-<num>.ps1 from the desktop first, or add it manually:
    git remote add upstream https://github.com/stevenerat/spike_basecode.git
"@
}
Write-Ok "Upstream: $upstreamUrl"

# Check 3: are we on main?
$currentBranch = git rev-parse --abbrev-ref HEAD
if ($currentBranch -ne "main") {
    Write-Fail @"
Currently on branch '$currentBranch', not 'main'.

This script syncs main with upstream. Switch to main first:
    git checkout main

If you're intentionally working on a different branch, talk to
Steve or Dan before syncing.
"@
}
Write-Ok "Branch: main"

# Check 4: is the working tree clean?
$dirtyFiles = git status --porcelain
if ($dirtyFiles) {
    Write-Host ""
    Write-Host "Uncommitted changes detected:" -ForegroundColor Yellow
    Write-Host $dirtyFiles
    Write-Fail @"
Working tree is not clean. Commit or stash your changes before syncing:
    git add .
    git commit -m "describe your changes"
  OR
    git stash
"@
}
Write-Ok "Working tree clean"

# -----------------------------------------------------------------------------
# Sync
# -----------------------------------------------------------------------------

Write-Step "Fetching from upstream"
git fetch upstream
if ($LASTEXITCODE -ne 0) {
    Write-Fail "git fetch upstream failed. Check your network or the upstream URL."
}
Write-Ok "Fetched"

Write-Step "Merging upstream/main into local main (fast-forward only)"

# Capture HEAD before and after so we can report what actually changed.
$headBefore = git rev-parse HEAD

git merge --ff-only upstream/main
if ($LASTEXITCODE -ne 0) {
    Write-Fail @"
Fast-forward merge failed.

This usually means your local main has commits that aren't on
upstream/main, so a clean fast-forward isn't possible.

Talk to Steve or Dan to decide how to integrate the changes.
"@
}

$headAfter = git rev-parse HEAD
if ($headBefore -ne $headAfter) {
    Write-Ok "Merged. New commits pulled in:"
    git log --oneline "$headBefore..$headAfter" | ForEach-Object {
        Write-Host "      $_" -ForegroundColor Gray
    }
} else {
    Write-Ok "Already up to date with upstream - nothing to merge"
}

Write-Step "Pushing to origin (team fork on github.com)"
git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Fail "git push origin main failed. Check your GitHub authentication."
}
Write-Ok "Pushed"

# -----------------------------------------------------------------------------
# Done
# -----------------------------------------------------------------------------

Pop-Location

Write-Host ""
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host " Sync complete - local, team fork, and upstream are all in sync" -ForegroundColor Cyan
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host ""
