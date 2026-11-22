#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 블로그 1-Click 서식 복사 도우미 (tools/copy_naver_helper.py) - 방안 A 구현

네이버 계정 보호(보호조치 원천 차단)를 위해 사람이 직접 일반 브라우저에서
클릭 1~2번으로 30초 만에 네이버 블로그에 포스팅을 등록할 수 있도록 지원합니다.

동작:
1. 오늘 작성된 네이버 포스트 HTML 뷰어를 기본 브라우저(사파리/크롬 등)로 자동 실행
2. 네이버 공식 스마트에디터 ONE 글쓰기 페이지(blog.naver.com/GoBlogWrite.naver) 자동 실행
3. 터미널에 제목 및 서식 복사 가이드 출력
"""

import os
import sys
import glob
import re
import argparse
import subprocess
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(BASE_DIR, "blog", "naver", "posts")

def sort_key(path):
    m = re.search(r'(\d{4}-\d{2}-\d{2})(?:-(\d+))?\.', path)
    if m:
        date_part = m.group(1)
        num = int(m.group(2)) if m.group(2) else 1
        return (date_part, num)
    return (path, 0)

def main():
    parser = argparse.ArgumentParser(description="네이버 블로그 1-Click 서식 복사 & 글쓰기 도우미 (방안 A)")
    parser.add_argument("--post", "-p", type=int, default=1, help="열람할 포스트 번호 (기본값: 1)")
    parser.add_argument("--date", "-d", type=str, default=None, help="대상 날짜 (기본: 오늘)")
    parser.add_argument("--no-open", action="store_true", help="브라우저 자동 열람 비활성화")
    args = parser.parse_args()

    today_str = args.date or datetime.now().strftime("%Y-%m-%d")
    ym = today_str[:7].replace("-", "")
    target_dir = os.path.join(POSTS_DIR, ym)

    if not os.path.exists(target_dir):
        print(f"❌ 해당 월의 포스트 폴더가 없습니다: {target_dir}")
        sys.exit(1)

    pattern = os.path.join(target_dir, f"{today_str}*.html")
    all_posts = sorted(glob.glob(pattern), key=sort_key)
    if not all_posts:
        print(f"❌ 오늘({today_str}) 작성된 네이버 포스트를 찾을 수 없습니다.")
        sys.exit(1)

    # 요청된 번호에 해당하는 포스트 찾기
    selected_file = None
    target_suffix = "" if args.post == 1 else f"-{args.post}"
    expected_filename = f"{today_str}{target_suffix}.html"

    for p in all_posts:
        if os.path.basename(p) == expected_filename:
            selected_file = p
            break

    if not selected_file:
        selected_file = all_posts[0]

    # HTML 파일에서 제목 추출
    title = ""
    try:
        with open(selected_file, "r", encoding="utf-8") as f:
            content = f.read()
            m = re.search(r'<h1 class="post-title">\s*([\s\S]*?)\s*</h1>', content)
            if m:
                title = m.group(1).strip()
            else:
                m_title = re.search(r'<title>.*?\|\s*([\s\S]*?)</title>', content)
                if m_title:
                    title = m_title.group(1).strip()
    except Exception as e:
        title = "네이버 블로그 포스팅"

    abs_path = os.path.abspath(selected_file)

    print("==========================================================")
    print(" 🛡️ [방안 A] 네이버 블로그 1-Click 서식 복사 & 수동 발행 도우미")
    print("==========================================================")
    print(f" 📄 파일명: {os.path.basename(selected_file)}")
    print(f" 📌 제목  : {title}")
    print("----------------------------------------------------------")
    print(" 💡 봇 탐지 0% 원천 차단! 네이버 계정을 100% 안전하게 지킵니다.")
    print("==========================================================")
    print("\n👉 [간편 30초 등록 가이드]")
    print(f" 1. 열린 포스트 화면 상단에서 [🟢 네이버 스마트에디터 서식 복사] 버튼을 누릅니다.")
    print(f" 2. 네이버 글쓰기 화면에 아래 제목을 붙여넣습니다:\n")
    print(f"    👉 {title}\n")
    print(f" 3. 본문 입력란을 클릭하고 Cmd+V (붙여넣기)를 누릅니다.")
    print(f"    (초록 요약박스·소제목 바·표·볼드 서식이 완벽하게 복원됩니다)")
    print(f" 4. 우측 상단 [발행] 버튼을 클릭하면 완료!")
    print("==========================================================")

    if not args.no_open:
        # 1. 포스트 로컬 뷰어 열기
        subprocess.run(["open", abs_path], check=False)
        # 2. 네이버 스마트에디터 ONE 글쓰기 새창 열기
        subprocess.run(["open", "https://blog.naver.com/GoBlogWrite.naver"], check=False)
        print("🚀 기본 웹 브라우저에서 포스트 뷰어와 네이버 글쓰기 창이 실행되었습니다.\n")

if __name__ == "__main__":
    main()
