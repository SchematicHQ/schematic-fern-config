#!/bin/bash
set -e

# This script upgrades Fern generators to their latest versions
# It creates or updates a pull request if changes are detected

BRANCH_NAME="update-generators"
INITIAL_DIR="$(pwd)"

# Function to ensure git identity is set
ensure_git_identity() {
  if [ -z "$(git config user.email)" ]; then
    git config user.email "bot@schematichq.com"
    git config user.name "Schematic Bot"
    echo "Set default git identity for repository"
  fi
}

# Function to set GitHub Actions output
set_output() {
  if [[ ! -z "$GITHUB_OUTPUT" ]]; then
    echo "$1=$2" >> "$GITHUB_OUTPUT"
  fi
}

# Set git identity
ensure_git_identity

# Create commit message
UPGRADE_COMMIT_MESSAGE="chore: upgrade fern generators to latest versions"
if [[ ! -z "$GITHUB_ACTIONS" ]]; then
  UPGRADE_COMMIT_MESSAGE="${UPGRADE_COMMIT_MESSAGE}

GitHub ref: $GITHUB_REF
GitHub repo: $GITHUB_REPOSITORY
Git SHA: $GITHUB_SHA
"
fi

# Fetch latest changes
git fetch origin

# Check if branch exists on remote
if git ls-remote --heads origin "$BRANCH_NAME" | grep -q "$BRANCH_NAME"; then
  echo "Branch $BRANCH_NAME exists, checking out and updating..."
  git checkout "$BRANCH_NAME"
  git pull origin "$BRANCH_NAME"
  # Rebase with main to keep it up to date
  git pull origin main --rebase
else
  echo "Creating new branch $BRANCH_NAME..."
  git checkout main
  git pull origin main
  git checkout -b "$BRANCH_NAME"
fi

# Baseline the comparison against main, not against the branch we just checked
# out. The branch is long-lived: on every run after the one that created it, it
# already carries the pending upgrades, so diffing against it reports no change
# even while the PR still has everything to merge.
VERSIONS_BEFORE=$(mktemp)
MAIN_GENERATORS=$(mktemp)
git show origin/main:fern/generators.yml > "$MAIN_GENERATORS"
for group in $(yq '.groups | keys | .[]' "$MAIN_GENERATORS"); do
  version=$(yq ".groups.\"$group\".generators[0].version" "$MAIN_GENERATORS")
  echo "$group=$version" >> "$VERSIONS_BEFORE"
done

# Upgrade all generators
echo "Upgrading generators..."
yq '.groups | keys | .[]' fern/generators.yml | xargs -I {} fern generator upgrade --group {}

# Detect which groups had version changes
CHANGED_GROUPS="["
first=true
for group in $(yq '.groups | keys | .[]' fern/generators.yml); do
  new_version=$(yq ".groups.\"$group\".generators[0].version" fern/generators.yml)
  old_version=$(grep "^$group=" "$VERSIONS_BEFORE" | cut -d= -f2)
  if [ -z "$old_version" ]; then
    old_version="(absent on main)"
  fi
  if [ "$old_version" != "$new_version" ]; then
    echo "Generator $group changed: $old_version -> $new_version"
    if [ "$first" = true ]; then
      first=false
    else
      CHANGED_GROUPS+=","
    fi
    CHANGED_GROUPS+="\"$group\""
  fi
done
CHANGED_GROUPS+="]"
rm -f "$VERSIONS_BEFORE" "$MAIN_GENERATORS"

echo "Changed groups: $CHANGED_GROUPS"
set_output "changed_groups" "$CHANGED_GROUPS"

# Does the branch propose anything main does not already have? This is the
# question the PR answers, so it is the one that decides whether to keep the PR
# open -- an upgrade applied on an earlier run still counts.
if ! git diff --quiet origin/main -- fern/generators.yml; then
  echo "Changes detected against main"
  set_output "has_changes" "true"

  if [[ -n $(git status --porcelain) ]]; then
    echo "Committing the upgrades applied by this run..."
    git add .
    git commit -m "$UPGRADE_COMMIT_MESSAGE"
  else
    echo "Branch already carries these upgrades; nothing new to commit."
  fi

  git push origin "$BRANCH_NAME" --force-with-lease

  # Check if PR already exists
  existing_pr=$(gh pr list --state open --head "$BRANCH_NAME" --json number --jq '.[0].number' 2>/dev/null || echo "")

  if [ -n "$existing_pr" ]; then
    echo "PR already exists: #$existing_pr"
    set_output "pr_number" "$existing_pr"
  else
    echo "Creating new PR..."
    pr_url=$(gh pr create \
      --title "chore: upgrade fern generators" \
      --body "This PR updates Fern generators to their latest versions. Validation in progress..." \
      --base main)

    pr_number=$(gh pr list --state open --head "$BRANCH_NAME" --json number --jq '.[0].number' 2>/dev/null || echo "")
    echo "Created PR: $pr_url"
    set_output "pr_number" "$pr_number"
  fi
else
  echo "No changes detected: main is already on these generator versions"
  set_output "has_changes" "false"

  # Check if there's an existing PR we should close
  existing_pr=$(gh pr list --state open --head "$BRANCH_NAME" --json number --jq '.[0].number' 2>/dev/null || echo "")

  if [ -n "$existing_pr" ]; then
    echo "Closing existing PR #$existing_pr since there are no changes"
    gh pr close "$existing_pr" --comment "Closing PR as there are no longer any changes to merge." --delete-branch
  fi
fi

# Return to initial directory
cd "$INITIAL_DIR"
