#!/usr/bin/env bash
set -e
TMP=tmp_repo_demo
rm -rf $TMP
mkdir -p $TMP
cd $TMP
git init
echo "Othello MCP demo repo" > README.md
git add README.md
git commit -m "Demo commit from git_demo.sh"
echo "Created demo repo at $(pwd)"
