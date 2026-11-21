#!/usr/bin/env bash
#
# 블로그 수시(온디맨드) 포스팅 원클릭 터미널 실행 스크립트
# 사용법:
#   1) 대화형 메뉴 실행: ./scripts/write-post.sh
#   2) 특정 플랫폼 1편 생성: ./scripts/write-post.sh -p tistory -k "국민연금"
#   3) 전체 플랫폼 실시간 트렌드 1편씩: ./scripts/write-post.sh -p all -a
#   4) 오늘 정규 배치 즉시 실행: ./scripts/write-post.sh --batch
#
set -euo pipefail

PROJECT_DIR="/Users/user/CursorProjects/ai-blog-notes"
cd "$PROJECT_DIR"

PYTHON_BIN="/usr/bin/python3"
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
fi

show_help() {
    echo "=========================================================="
    echo " ✍️ 블로그 수시(온디맨드) 글작성 원클릭 도구"
    echo "=========================================================="
    echo "사용법:"
    echo "  $0                           # 대화형(인터랙티브) 메뉴 실행"
    echo "  $0 -p [naver|tistory|wordpress|all]  # 플랫폼 지정 자동 작성"
    echo "  $0 -p tistory -k \"키워드\"    # 특정 키워드로 작성"
    echo "  $0 -p all -c 2               # 전체 플랫폼에 2편씩 추가"
    echo "  $0 --batch                   # 오늘 정규 배치 실행 (평일 5편 / 주말 30편)"
    echo "=========================================================="
    exit 0
}

PLATFORM=""
KEYWORD=""
COUNT="1"
BATCH_MODE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_help
            ;;
        -p|--platform)
            PLATFORM="$2"
            shift 2
            ;;
        -k|--keyword)
            KEYWORD="$2"
            shift 2
            ;;
        -c|--count)
            COUNT="$2"
            shift 2
            ;;
        -a|--auto)
            KEYWORD=""
            shift
            ;;
        --batch)
            BATCH_MODE=true
            shift
            ;;
        *)
            echo "알 수 없는 옵션: $1"
            show_help
            ;;
    esac
done

# 배치 모드 실행
if [ "$BATCH_MODE" = true ]; then
    echo "🚀 오늘자 정규 통합 배치(평일 5편 / 주말 30편)를 즉시 실행합니다..."
    $PYTHON_BIN tools/daily_naver_batch.py --force
    exit 0
fi

# 인자가 없으면 대화형 메뉴 제공
if [ -z "$PLATFORM" ]; then
    echo "=========================================================="
    echo " ✍️ [원클릭] 블로그 수시(온디맨드) 글작성 메뉴"
    echo "=========================================================="
    echo " 1) 네이버 블로그에 글 1편 추가"
    echo " 2) 티스토리에 글 1편 추가"
    echo " 3) 워드프레스에 글 1편 추가"
    echo " 4) 3대 플랫폼(네이버·티스토리·워드프레스) 전체에 1편씩 추가"
    echo " 5) 오늘자 통합 배치 실행 (주말 30편 / 평일 5편)"
    echo " 6) 종료"
    echo "=========================================================="
    read -r -p "👉 번호를 선택하세요 [1-6] (기본: 4): " choice
    choice=${choice:-4}

    case "$choice" in
        1) PLATFORM="naver" ;;
        2) PLATFORM="tistory" ;;
        3) PLATFORM="wordpress" ;;
        4) PLATFORM="all" ;;
        5)
            echo "🚀 통합 배치를 실행합니다..."
            $PYTHON_BIN tools/daily_naver_batch.py --force
            exit 0
            ;;
        6) echo "종료합니다."; exit 0 ;;
        *) echo "잘못된 선택입니다."; exit 1 ;;
    esac

    echo ""
    read -r -p "🎯 작성할 키워드를 입력하세요 (엔터 시 실시간 트렌드 자동 선정): " input_kw
    KEYWORD="${input_kw:-}"
fi

CMD=("$PYTHON_BIN" "tools/write_ondemand.py" "--platform=$PLATFORM" "--count=$COUNT")
if [ -n "$KEYWORD" ]; then
    CMD+=("--keyword=$KEYWORD")
fi

echo ""
echo "⚙️ 실행 중: ${CMD[*]}"
"${CMD[@]}"
