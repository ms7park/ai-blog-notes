#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
티스토리 블로그 1회성 브라우저 로그인 세션 생성 도구 (tools/setup_tistory_login.py)

사용자가 화면에 열린 Chromium 브라우저에서 카카오/티스토리에 직접 로그인하면,
로그인 인증 세션을 .browser_session/tistory/state.json 및 프로필에 영구 저장합니다.
"""

import os
import sys
import time
import argparse
import subprocess
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_DIR = os.path.join(BASE_DIR, ".browser_session", "tistory")
STATE_FILE = os.path.join(SESSION_DIR, "state.json")
DEFAULT_BLOG = "essay30497"

def setup_tistory_session(blog_name=DEFAULT_BLOG):
    os.makedirs(SESSION_DIR, exist_ok=True)
    print("==========================================================", flush=True)
    print(" 🌐 티스토리(카카오) 블로그 1회성 로그인 세션 설정", flush=True)
    print("==========================================================", flush=True)
    print(f" 🎯 대상 블로그: https://{blog_name}.tistory.com/", flush=True)
    print(" 화면에 브라우저 로그인 창이 열립니다.", flush=True)
    print(" 1. 열린 브라우저에서 [카카오계정으로 로그인]을 클릭합니다.", flush=True)
    print(" 2. 카카오 계정 아이디/비밀번호 입력 및 2단계 인증을 완료합니다.", flush=True)
    print(" 3. 로그인이 완료되면 자동으로 감지하여 세션을 저장합니다.", flush=True)
    print("==========================================================", flush=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            viewport={"width": 1280, "height": 900},
            permissions=["clipboard-read", "clipboard-write"],
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )

        page = context.pages[0] if context.pages else context.new_page()

        # 티스토리 로그인 페이지로 이동
        print("🚀 티스토리 로그인 페이지를 여는 중입니다...", flush=True)
        login_url = f"https://www.tistory.com/auth/login?redirectUrl=https%3A%2F%2F{blog_name}.tistory.com%2Fmanage%2Fnewpost"
        page.goto(login_url)

        # macOS에서 브라우저 창을 화면 맨 앞으로 활성화
        try:
            subprocess.run([
                "osascript", "-e",
                'tell application "Google Chrome for Testing" to activate'
            ], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        print("\n⏳ 화면에 열린 브라우저 창에서 카카오 로그인을 진행해 주세요...", flush=True)
        print("💡 로그인 완료 시 자동으로 감지하여 세션을 저장합니다 (최대 10분 대기).", flush=True)

        logged_in = False
        auto_checked_save = False

        for i in range(300):
            time.sleep(2)
            try:
                # 활성 창 목록 확인
                all_pages = [p for p in context.pages if not p.is_closed()]
                if not all_pages:
                    print("⚠️ 브라우저 창이 닫혔습니다.", flush=True)
                    break

                active_urls = [p.url for p in all_pages]
                active_page = all_pages[-1]

                # 1. '카카오계정으로 로그인' 버튼이 보이면 1-Click 자동 클릭
                try:
                    for p_item in all_pages:
                        if "tistory.com/auth/login" in p_item.url:
                            kakao_btn = p_item.locator("a:has-text('카카오계정으로 로그인'), button:has-text('카카오계정으로 로그인')").first
                            if kakao_btn.is_visible(timeout=500):
                                kakao_btn.click()
                                break
                except Exception:
                    pass

                # 2. 카카오 로그인 페이지의 '로그인 상태 유지' 체크박스 자동 활성화 (최대 30일 유지)
                if not auto_checked_save:
                    try:
                        for p_item in all_pages:
                            if "accounts.kakao.com" in p_item.url:
                                save_chk = p_item.locator("input[name='saveSignedIn'], #saveSignedIn, label[for='saveSignedIn']").first
                                if save_chk.is_visible(timeout=500):
                                    if not p_item.locator("input[name='saveSignedIn']").first.is_checked():
                                        save_chk.click()
                                        print("  🔒 [안내] 카카오 '로그인 상태 유지'를 자동 활성화했습니다 (세션 장기 보존).", flush=True)
                                    auto_checked_save = True
                                    break
                    except Exception:
                        pass

                cookies = context.cookies()
                cookie_names = set(c["name"] for c in cookies)

                # 카카오 및 티스토리 필수 인증 토큰 (TSSESSION) 감지
                has_tistory_token = "TSSESSION" in cookie_names
                reached_editor = any("manage/newpost" in u or "manage/post" in u for u in active_urls)

                if has_tistory_token and reached_editor:
                    print(f"\n🎉 [1단계 감지] 티스토리 정식 인증 토큰(TSSESSION) 및 에디터 확인 완료!", flush=True)
                    context.storage_state(path=STATE_FILE)
                    logged_in = True
                    break
                elif has_tistory_token and not any("accounts.kakao.com" in u for u in active_urls):
                    # 카카오 인증이 끝났으나 아직 에디터로 리다이렉트 중인 경우
                    pass
            except Exception:
                pass

        if not logged_in:
            # 2단계: 에디터 직접 이동 후 재검증
            print(f"🔍 [2단계 확인] 티스토리 글쓰기 에디터 진입 확인 중...", flush=True)
            target_page = context.pages[0] if context.pages else context.new_page()
            try:
                target_page.goto(f"https://{blog_name}.tistory.com/manage/newpost")
                time.sleep(3)
                cookies = context.cookies()
                cookie_names = set(c["name"] for c in cookies)
                if "TSSESSION" in cookie_names and not ("auth/login" in target_page.url or "accounts.kakao.com" in target_page.url):
                    print(f"✅ 티스토리 글쓰기 에디터 진입 성공! (URL: {target_page.url})", flush=True)
                    context.storage_state(path=STATE_FILE)
                    logged_in = True
                else:
                    print("⚠️ 글쓰기 페이지 진입 실패 (세션 만료 또는 권한 필요)", flush=True)
                    logged_in = False
            except Exception as e:
                print(f"ℹ️ 확인 중 안내: {e}", flush=True)

        if not logged_in:
            print("⚠️ 로그인이 완료되지 않았습니다. 다시 시도해 주세요.", flush=True)
            try:
                context.close()
            except Exception:
                pass
            return False

        if logged_in:
            context.storage_state(path=STATE_FILE)
            print(f"\n✅ 티스토리 로그인 세션이 안전하게 저장되었습니다: {STATE_FILE}", flush=True)
            print("3초 후 로그인 창이 자동으로 닫히며 즉시 정식 글 등록을 시작합니다...", flush=True)
            time.sleep(3)

        context.close()
        return logged_in

def main():
    parser = argparse.ArgumentParser(description="티스토리 Playwright 1회성 로그인 세션 도구")
    parser.add_argument("--blog", type=str, default=DEFAULT_BLOG, help=f"티스토리 서브도메인 (기본: {DEFAULT_BLOG})")
    args = parser.parse_args()
    setup_tistory_session(args.blog)

if __name__ == "__main__":
    main()
