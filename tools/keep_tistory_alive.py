#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
티스토리 세션 킵얼라이브 (tools/keep_tistory_alive.py)

정기적으로(자정 또는 배치 전) 티스토리 글쓰기 에디터 페이지에 접속하여,
카카오 SSO 및 티스토리의 24시간 세션 만료를 방지하고 최신 세션 쿠키를 갱신 저장합니다.
"""

import os
import sys
import time
import argparse
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_DIR = os.path.join(BASE_DIR, ".browser_session", "tistory")
STATE_FILE = os.path.join(SESSION_DIR, "state.json")
DEFAULT_BLOG = "essay30497"

def ping_tistory_session(blog_name=DEFAULT_BLOG):
    if not os.path.exists(STATE_FILE):
        print("❌ 티스토리 세션 파일(state.json)이 없습니다.", flush=True)
        return False

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            storage_state=STATE_FILE
        )
        page = context.new_page()

        print(f"💓 티스토리 세션 킵얼라이브 확인 중... (https://{blog_name}.tistory.com/manage/newpost)", flush=True)
        page.goto(f"https://{blog_name}.tistory.com/manage/newpost")
        
        valid = False
        for _ in range(6):
            time.sleep(1)
            if "manage/newpost" in page.url or "manage/post" in page.url:
                valid = True
                break

        # auth/login 리다이렉트 시 1-Click SSO 시도
        if not valid and ("auth/login" in page.url or "accounts.kakao.com" in page.url):
            try:
                kakao_btn = page.locator("a:has-text('카카오계정으로 로그인'), button:has-text('카카오계정으로 로그인')").first
                if kakao_btn.is_visible(timeout=2000):
                    kakao_btn.click()
                    time.sleep(3)
                    if "manage/newpost" in page.url or "manage/post" in page.url:
                        valid = True
            except Exception:
                pass

        if valid:
            context.storage_state(path=STATE_FILE)
            print("✅ 티스토리 세션이 유효하며 최신 토큰으로 갱신되었습니다!", flush=True)
        else:
            print("⚠️ 티스토리 세션이 만료되었습니다. 재로그인이 필요합니다.", flush=True)

        browser.close()
        return valid

def main():
    parser = argparse.ArgumentParser(description="티스토리 세션 킵얼라이브 도구")
    parser.add_argument("--blog", type=str, default=DEFAULT_BLOG, help=f"티스토리 서브도메인 (기본: {DEFAULT_BLOG})")
    args = parser.parse_args()

    ok = ping_tistory_session(args.blog)
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
