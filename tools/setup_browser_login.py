#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 블로그 1회성 브라우저 로그인 세션 생성 도구 (tools/setup_browser_login.py)

사용자가 화면에 열린 Chromium 브라우저에서 직접 네이버에 로그인하면,
로그인 인증 세션(쿠키, 스토리지)을 .browser_session/naver 에 영구 저장합니다.
이후 자동 업로드 시에는 로그인 창 없이 바로 글쓰기가 가능해집니다.
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_DIR = os.path.join(BASE_DIR, ".browser_session", "naver")

import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_DIR = os.path.join(BASE_DIR, ".browser_session", "naver")
STATE_FILE = os.path.join(SESSION_DIR, "state.json")

def setup_naver_session():
    os.makedirs(SESSION_DIR, exist_ok=True)
    print("==========================================================")
    print(" 🌐 네이버 블로그 1회성 로그인 세션 설정")
    print("==========================================================")
    print(" 화면에 브라우저 로그인 창이 열립니다.")
    print(" 1. 브라우저에서 네이버 계정(아이디/비밀번호)으로 로그인해 주세요.")
    print(" 2. 2단계 인증이나 기기 등록이 있다면 완료해 주세요.")
    print(" 3. 로그인이 완료되면 자동으로 감지하여 세션을 저장합니다.")
    print("==========================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            permissions=["clipboard-read", "clipboard-write"]
        )

        page = context.new_page()

        # 네이버 로그인 페이지로 이동
        print("🚀 네이버 로그인 페이지를 여는 중입니다...")
        page.goto("https://nid.naver.com/nidlogin.login")

        # macOS에서 브라우저 창을 화면 맨 앞으로 활성화
        try:
            subprocess.run([
                "osascript", "-e",
                'tell application "Google Chrome for Testing" to activate'
            ], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        print("⏳ 화면에 열린 브라우저 창에서 네이버 로그인을 완료해 주세요...")
        print("💡 로그인 완료 시 자동으로 감지하여 세션을 저장합니다 (최대 10분 대기).")

        logged_in = False
        for i in range(300):
            time.sleep(2)
            try:
                if page.is_closed():
                    print("⚠️ 사용자에 의해 브라우저 창이 닫혔습니다.")
                    break

                cookies = context.cookies()
                cookie_names = [c["name"] for c in cookies]

                # 네이버 로그인 필수 인증 토큰 (NID_AUT, NID_SES)
                if "NID_AUT" in cookie_names and "NID_SES" in cookie_names:
                    print("\n🎉 [1단계 감지] 네이버 로그인 인증 토큰(NID_AUT, NID_SES) 확인!")
                    # 1차 세션 저장
                    context.storage_state(path=STATE_FILE)
                    logged_in = True
                    break
            except Exception:
                pass

        if not logged_in:
            print("⚠️ 로그인이 완료되지 않았거나 창이 닫혔습니다. 다시 시도해 주세요.")
            try:
                browser.close()
            except Exception:
                pass
            return False

        # 2단계: 스마트에디터 글쓰기 페이지 진입 검증
        print("🔍 [2단계 검증] 네이버 블로그 글쓰기 에디터 진입 권한 확인 중...")
        try:
            page.goto("https://blog.naver.com/GoBlogWrite.naver")
            time.sleep(3)
            if "nidlogin" in page.url:
                print("⚠️ 글쓰기 페이지 진입 실패 (세션 만료 또는 2차 인증 필요)")
                logged_in = False
            else:
                print(f"✅ 글쓰기 에디터 진입 성공! (URL: {page.url[:45]}...)")
                # 최종 성공 상태 저장
                context.storage_state(path=STATE_FILE)
                logged_in = True
        except Exception as e:
            print(f"ℹ️ 확인 중 안내: {e}")

        if logged_in:
            print(f"\n✅ 네이버 로그인 세션이 안전하게 저장되었습니다: {STATE_FILE}")
            print("5초 후 로그인 창이 자동으로 닫히며 등록 준비가 완료됩니다...")
            time.sleep(5)

        browser.close()
        return logged_in

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="블로그 1회성 로그인 세션 생성 도구")
    parser.add_argument("--service", choices=["naver", "tistory"], default="naver", help="대상 서비스 (naver 또는 tistory)")
    parser.add_argument("--blog", type=str, default="essay30497", help="티스토리 서브도메인 (tistory 선택 시)")
    args = parser.parse_args()

    if args.service == "tistory":
        try:
            from setup_tistory_login import setup_tistory_session
        except ImportError:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from setup_tistory_login import setup_tistory_session
        setup_tistory_session(args.blog)
    else:
        setup_naver_session()
