#!/usr/bin/env bash
# 重新导出机会卡快照并发布到两处：
#   1) 源站（自建后端，地址走环境变量）—— 源站自己有后端，快照只是备份
#   2) Cloudflare Pages                —— 没有后端，靠这份快照查全量历史卡
#
# 每天 08:30 出卡之后跑一次，CF 那个入口才不会落后于最新卡。
#
# 需要的环境变量（都不写进仓库）：
#   LING_API_BASE        源站后端地址，必须能返回 JSON，例如 https://你的域名
#   LING_SSH_HOST        源站主机地址（scp/ssh 目标）
#   SERVER_SSH_PASSWORD  未设置时跳过源站同步
#
# 用法：LING_API_BASE=... LING_SSH_HOST=... bash scripts/refresh_snapshot_and_deploy.sh
set -euo pipefail

: "${LING_API_BASE:?请先设置 LING_API_BASE（源站后端地址，必须能返回 JSON）}"

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

echo "=== 1/4 重新导出快照 ==="
python3 scripts/build_cards_snapshot.py "$LING_API_BASE"

echo
echo "=== 2/4 提交并推送 ==="
git add frontend/data
if git diff --cached --quiet; then
  echo "（快照无变化，跳过提交）"
else
  git -c user.name=LLing486 commit -q -m "chore(snapshot): 机会卡快照刷新 $(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M')"
  gh auth switch -u LLing486 >/dev/null 2>&1 || true
  git push origin master
fi

echo
echo "=== 3/4 同步到源站 ==="
if [ -z "${SERVER_SSH_PASSWORD:-}" ] || [ -z "${LING_SSH_HOST:-}" ]; then
  echo "⚠ 未设置 SERVER_SSH_PASSWORD 或 LING_SSH_HOST，跳过源站同步（源站有自己的后端，影响不大）"
else
  export SSHPASS="$SERVER_SSH_PASSWORD"
  tar czf /tmp/lingling-data.tgz frontend/data
  sshpass -e scp -o StrictHostKeyChecking=no frontend/cards.html frontend/cards-all.html \
    "root@${LING_SSH_HOST}:/opt/product-lingling/frontend/"
  sshpass -e scp -o StrictHostKeyChecking=no /tmp/lingling-data.tgz "root@${LING_SSH_HOST}:/tmp/"
  sshpass -e ssh -o StrictHostKeyChecking=no "root@${LING_SSH_HOST}" \
    'cd /opt/product-lingling && tar xzf /tmp/lingling-data.tgz && rm -f /tmp/lingling-data.tgz'
  rm -f /tmp/lingling-data.tgz
fi

echo
echo "=== 4/4 发布到 Cloudflare Pages ==="
set -a; . "$HOME/.cloudflare_token.sh"; set +a
npx --no-install wrangler pages deploy frontend \
  --project-name=product-lingling --branch=main --commit-dirty=true

echo
echo "完成。公开入口：https://product-lingling.pages.dev"
