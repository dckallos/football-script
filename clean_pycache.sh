#!/usr/bin/env bash
# =============================================================================
# FILE: clean_pycache.sh
# =============================================================================
#
# 🧹✨ Python Cache Cleaner ✨🧹
#
# Description:
#   This script recursively finds and removes Python cache directories
#   (`__pycache__`) and compiled Python files (`*.pyc`) starting from the
#   current directory. Useful for cleaning up your project workspace! 🗑️
#
# Usage:
#   ./clean_pycache.sh
#   (Run this script from the root directory of your project)
#
# Safety:
#   Uses `set -euo pipefail` for robust error handling.
#   `rm -rf` is used for directories, so ensure you run this in the
#   correct project directory! Be cautious. ☢️
#
# Emojis:
#   Used liberally for fun and clarity! 🎉🥳🚀
#
# =============================================================================

# --- Safety First! ---
# Exit immediately if a command exits with a non-zero status.
# Treat unset variables as an error when substituting.
# Exit if any command in a pipeline fails, not just the last one.
set -euo pipefail

# --- Script Start ---
printf "🚀 Starting Python cache cleanup in directory: $(pwd)\n"

# --- Step 1: Remove __pycache__ directories ---
printf "🧹 Finding and removing '__pycache__' directories...\n"
# -type d: Find directories
# -name "__pycache__": Match the specific directory name
# -exec rm -rf {}: Execute 'rm -rf' on each found directory. '{}' is replaced by the found path.
# +: Execute rm with multiple found paths at once for efficiency.
find . -type d -name "__pycache__" -exec rm -rf {} +
printf "✅ Done removing directories.\n"

# --- Step 2: Remove *.pyc files ---
printf "🗑️ Finding and removing '*.pyc' files...\n"
# -name "*.pyc": Find files ending with .pyc
# -exec rm -f {}: Execute 'rm -f' (force remove) on each found file.
# +: Execute rm with multiple found paths at once.
find . -name "*.pyc" -exec rm -f {} +
printf "✅ Done removing .pyc files.\n"

# --- Script End ---
printf "✨ Python cache cleanup complete! Your workspace is sparkling clean! ✨\n"

# Exit cleanly
exit 0
