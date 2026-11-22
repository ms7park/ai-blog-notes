#!/usr/bin/env bash
#
# Production(main) & Develop 동시 푸시 스크립트 (scripts/push.sh)
#
# Vercel / GitHub Pages 등 Production 배포(main 브랜치)와
# 작업 브랜치(develop)를 항상 최신 상태로 일치시켜 동시 푸시합니다.
#
set -euo pipefail

PROJECT_DIR="/Users/user/CursorProjects/ai-blog-notes"
cd "$PROJECT_DIR"

COMMIT_MSG="${1:-feat: update blog notes and automation systems}"

echo "=========================================================="
echo " 🚀 Production(main) & Develop 원격 저장소 동시 푸시"
echo "=========================================================="

CURRENT_BRANCH="$(git branch --show-current)"
echo "📌 현재 브랜치: $CURRENT_BRANCH"

# 변경사항이 있다면 커밋
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 변경사항 스테이징 및 커밋 중..."
    git add .
    git commit -m "$COMMIT_MSG"
else
    echo "ℹ️ 새로 커밋할 변경사항이 없습니다."
fi

# local main 브랜치를 현재 커밋과 동기화
if git show-ref --verify --quiet refs/heads/main; then
    git branch -f main "$CURRENT_BRANCH"
    echo "✅ 로컬 main 브랜치 동기화 완료"
fi

# 원격 저장소의 develop과 main 모두 푸시
echo "🚀 origin/develop 푸시 중..."
git push origin "$CURRENT_BRANCH"

echo "🚀 origin/main (Production 배포 브랜치) 동시 푸시 중..."
git push origin "$CURRENT_BRANCH:main"

echo "=========================================================="
echo " 🎉 develop 및 main(Production) 브랜치 푸시 완료!"
echo "=========================================================="
