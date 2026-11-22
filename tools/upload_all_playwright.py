#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3대 블로그(네이버·티스토리·워드프레스) 통합 Playwright 자동 등록기 (tools/upload_all_playwright.py)

단 1번의 명령어로 3대 플랫폼의 로그인 세션을 자동 점검하고,
오늘 작성된 모든 글을 에디터 서식복사 방식으로 즉시 정식 발행(PUBLISH)합니다.

사용법:
  python3 tools/upload_all_playwright.py              # 3대 플랫폼 전체 즉시 정식 발행 (기본값)
  python3 tools/upload_all_playwright.py --publish    # 3대 플랫폼 전체 즉시 정식 발행
  python3 tools/upload_all_playwright.py --test       # 3대 플랫폼 1번 글 시험 발행
  python3 tools/upload_all_playwright.py --login      # 3대 플랫폼 로그인 세션 통합 확인/생성
  python3 tools/upload_all_playwright.py --draft      # 3대 플랫폼 임시저장 모드
"""

import os
import sys
import time
import argparse
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_DIR = os.path.join(BASE_DIR, ".browser_session")

PLATFORMS = [
    {
        "id": "naver",
        "name": "🟢 네이버 블로그",
        "session_file": os.path.join(SESSION_DIR, "naver", "state.json"),
        "login_script": os.path.join(BASE_DIR, "tools", "setup_browser_login.py"),
        "upload_script": os.path.join(BASE_DIR, "tools", "upload_naver_playwright.py"),
    },
    {
        "id": "tistory",
        "name": "🟠 티스토리 블로그",
        "session_file": os.path.join(SESSION_DIR, "tistory", "state.json"),
        "login_script": os.path.join(BASE_DIR, "tools", "setup_tistory_login.py"),
        "upload_script": os.path.join(BASE_DIR, "tools", "upload_tistory_playwright.py"),
    },
    {
        "id": "wordpress",
        "name": "🔵 워드프레스 블로그",
        "session_file": os.path.join(SESSION_DIR, "wordpress", "state.json"),
        "login_script": os.path.join(BASE_DIR, "tools", "setup_wordpress_login.py"),
        "upload_script": os.path.join(BASE_DIR, "tools", "upload_wordpress_playwright.py"),
    },
]

def check_and_ensure_sessions(selected_platforms, force_login=False):
    """선택된 플랫폼들의 로그인 세션을 점검하고 필요 시 로그인 창 실행"""
    print("==========================================================", flush=True)
    print(" 🔐 3대 블로그 로그인 세션 통합 점검", flush=True)
    print("==========================================================", flush=True)

    all_ready = True
    for p in selected_platforms:
        exists = os.path.exists(p["session_file"])
        if force_login or not exists:
            print(f"\n👉 [{p['name']}] 세션 {'재설정' if force_login else '생성'}이 필요합니다. 로그인 창을 엽니다...", flush=True)
            res = subprocess.run([sys.executable, "-u", p["login_script"]], cwd=BASE_DIR)
            if res.returncode != 0 or not os.path.exists(p["session_file"]):
                print(f"❌ [{p['name']}] 로그인 세션 생성 실패", flush=True)
                all_ready = False
            else:
                print(f"✅ [{p['name']}] 로그인 세션 저장 완료!", flush=True)
        else:
            print(f"✅ [{p['name']}] 기존 로그인 세션 유효함 ({os.path.basename(p['session_file'])})", flush=True)

    return all_ready

def run_uploads(selected_platforms, mode="publish", is_test=False, date_str=None, single_num=None, naver_reserve=False):
    """선택된 플랫폼들에 순차적으로 자동 포스팅 실행"""
    print("\n==========================================================", flush=True)
    mode_str = "1편 시험 발행(TEST)" if is_test else f"전체 즉시 정식 발행({mode.upper()})"
    print(f" 🚀 3대 블로그 통합 Playwright 자동 등록 시작 (모드: {mode_str})", flush=True)
    print("==========================================================", flush=True)

    results = {}
    for i, p in enumerate(selected_platforms, 1):
        print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", flush=True)
        print(f" [{i}/{len(selected_platforms)}] {p['name']} 자동 등록 진행", flush=True)
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", flush=True)

        cmd = [sys.executable, "-u", p["upload_script"], f"--mode={mode}"]
        
        # 플랫폼별 안전 가드레일 분기
        if p["id"] == "naver":
            # 네이버 블로그: 보호조치(아이디 잠금) 방지를 위해 기본 1편 안전 등록
            if is_test or single_num:
                num = single_num if single_num else 1
                cmd.append(f"--single={num}")
            else:
                cmd.append("--limit=1")
            if naver_reserve:
                cmd.append("--reserve")
        else:
            # 티스토리 / 워드프레스: 전체 발행 허용
            if is_test or single_num:
                num = single_num if single_num else 1
                cmd.append(f"--single={num}")
            else:
                cmd.append("--all")

        if date_str:
            cmd.append(f"--date={date_str}")

        start_t = time.time()
        res = subprocess.run(cmd, cwd=BASE_DIR)
        elapsed = round(time.time() - start_t, 1)

        success = (res.returncode == 0)
        results[p["id"]] = {"name": p["name"], "success": success, "elapsed": elapsed}

        if i < len(selected_platforms):
            print(f"\n⏳ 다음 플랫폼 준비 대기 (3초)...", flush=True)
            time.sleep(3)

    print("\n==========================================================", flush=True)
    print(" 🎉 3대 블로그 통합 자동 등록 결과 종합 리포트", flush=True)
    print("==========================================================", flush=True)
    total_success = 0
    for pid, r in results.items():
        status_icon = "✅ 성공" if r["success"] else "❌ 실패"
        if r["success"]:
            total_success += 1
        print(f"  • {r['name']}: {status_icon} (소요시간: {r['elapsed']}초)", flush=True)
    print("----------------------------------------------------------", flush=True)
    print(f" 🏆 총 {len(selected_platforms)}개 플랫폼 중 {total_success}개 성공!", flush=True)
    print("==========================================================", flush=True)

    return total_success == len(selected_platforms)

def main():
    parser = argparse.ArgumentParser(description="3대 블로그 통합 Playwright 원클릭 자동 등록기")
    parser.add_argument("--login", "-l", action="store_true", help="3대 플랫폼 로그인 세션 통합 점검 (누락 시 로그인 창 실행)")
    parser.add_argument("--force", "-f", action="store_true", help="기존 세션이 있어도 강제로 로그인 창 다시 열기")
    parser.add_argument("--test", "-t", action="store_true", help="3대 플랫폼 1번 글 단건 시험 발행")
    parser.add_argument("--publish", "-p", action="store_true", default=False, help="3대 플랫폼 전체 즉시 정식 발행 (기본값)")
    parser.add_argument("--draft", "-d", action="store_true", help="임시저장(Draft) 모드로 등록")
    parser.add_argument("--single", type=int, default=None, help="특정 포스트 번호만 등록")
    parser.add_argument("--date", type=str, default=None, help="대상 날짜 (기본: 오늘)")
    parser.add_argument("--platforms", type=str, default="all", help="대상 플랫폼 (예: all, naver, tistory, wordpress)")
    parser.add_argument("--skip-naver", action="store_true", help="네이버 블로그 등록 건너뛰기 (티스토리·워드프레스만 등록)")
    parser.add_argument("--naver-reserve", action="store_true", help="네이버 블로그 등록 시 예약 발행 모드 적용")

    args = parser.parse_args()

    # 대상 플랫폼 필터링
    if args.platforms == "all":
        selected = [p for p in PLATFORMS if not (args.skip_naver and p["id"] == "naver")] if args.skip_naver else PLATFORMS
    else:
        target_ids = [p.strip().lower() for p in args.platforms.split(",")]
        selected = [p for p in PLATFORMS if p["id"] in target_ids]
        if args.skip_naver:
            selected = [p for p in selected if p["id"] != "naver"]
        if not selected:
            print(f"❌ 유효하지 않은 플랫폼 지정 또는 대상 플랫폼이 비어있습니다: {args.platforms}", flush=True)
            sys.exit(1)

    # 1. 로그인 점검 모드
    if args.login:
        check_and_ensure_sessions(selected, force_login=args.force)
        sys.exit(0)

    # 2. 세션 자동 확인 (누락된 세션이 있으면 자동으로 로그인 창 띄움)
    sessions_ok = check_and_ensure_sessions(selected, force_login=False)
    if not sessions_ok:
        print("⚠️ 일부 플랫폼의 로그인이 완료되지 않아 등록을 중단합니다.", flush=True)
        sys.exit(1)

    # 3. 등록 모드 결정 (기본: publish)
    mode = "draft" if args.draft else "publish"
    is_test = args.test

    # 4. 전체 자동 업로드 실행
    ok = run_uploads(selected, mode=mode, is_test=is_test, date_str=args.date, single_num=args.single, naver_reserve=args.naver_reserve)
    if not ok:
        sys.exit(1)

if __name__ == "__main__":
    main()
