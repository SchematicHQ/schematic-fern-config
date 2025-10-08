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

# Upgrade all generators
echo "Upgrading generators..."
yq '.groups | keys | .[]' fern/generators.yml | xargs -I {} fern generator upgrade --group {}

# Check if there are changes
if [[ -n $(git status --porcelain) ]]; then
  echo "Changes detected, committing..."
  git add .
  git commit -m "$UPGRADE_COMMIT_MESSAGE"
  git push origin "$BRANCH_NAME" --force-with-lease

  # Check if PR already exists
  existing_pr=$(gh pr list --state open --head "$BRANCH_NAME" --json number,url --jq '.[0].url' 2>/dev/null || echo "")

  if [ -n "$existing_pr" ]; then
    echo "PR already exists: $existing_pr"
    echo "Updating existing PR..."

    # Update PR description
    gh pr edit "$existing_pr" \
      --body "This PR updates Fern generators to their latest versions.

**Updated generators:**
$(yq '.groups | keys | .[]' fern/generators.yml)

Generated automatically by scheduled workflow."
  else
    echo "Creating new PR..."
    pr_url=$(gh pr create \
      --title "chore: upgrade fern generators" \
      --body "This PR updates Fern generators to their latest versions.

**Updated generators:**
$(yq '.groups | keys | .[]' fern/generators.yml)

Generated automatically by scheduled workflow." \
      --base main)

    echo "Created PR: $pr_url"
  fi
else
  echo "No changes detected"

  # Check if there's an existing PR we should close
  existing_pr=$(gh pr list --state open --head "$BRANCH_NAME" --json number --jq '.[0].number' 2>/dev/null || echo "")

  if [ -n "$existing_pr" ]; then
    echo "Closing existing PR #$existing_pr since there are no changes"
    gh pr close "$existing_pr" --comment "Closing PR as there are no longer any changes to merge." --delete-branch
  fi
fi

# Return to initial directory
cd "$INITIAL_DIR"
