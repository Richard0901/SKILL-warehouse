#!/bin/bash

# 配置路径
SKILLS_DIR="/Users/richard/Documents/life/SKILLS"
LOG_FILE="$SKILLS_DIR/sync.log"

cd "$SKILLS_DIR" || exit

echo "--- Sync Started: $(date) ---" >> "$LOG_FILE"

# 1. 保存本地更改
git add .
if ! git diff-index --quiet HEAD --; then
    git commit -m "Auto-sync: local changes $(date)" >> "$LOG_FILE" 2>&1
fi

# 2. 拉取云端更改 (采用 rebase 保持提交历史整洁)
echo "Pulling remote changes..." >> "$LOG_FILE"
git pull origin main --rebase >> "$LOG_FILE" 2>&1

# 3. 推送至云端
echo "Pushing to remote..." >> "$LOG_FILE"
git push origin main >> "$LOG_FILE" 2>&1

echo "--- Sync Finished: $(date) ---" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"