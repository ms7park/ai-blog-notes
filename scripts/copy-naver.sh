#!/usr/bin/env bash
#
# 네이버 블로그 1-Click 서식 복사 도우미 스크립트 (방안 A)
#
# 계정 보호조치를 100% 원천 차단하기 위해 사람이 직접 평소 브라우저에서
# 30초 만에 네이버 블로그에 포스팅을 등록할 수 있도록 돕습니다.
#
set -euo pipefail

PROJECT_DIR="/Users/user/CursorProjects/ai-blog-notes"
cd "$PROJECT_DIR"

POST_NUM="${1:-1}"

python3 tools/copy_naver_helper.py --post "$POST_NUM"
