#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
100% 동일 복제 포스팅 안전 정리 도구 (tools/clean_redundant_duplicates.py)

블로그 폴더(naver, tistory, wordpress) 내에서 SHA-256 해시가 100% 일치하는
중복 파일 중, 최초 생성된 원본 1편만 안전하게 보존하고
나머지 잉여 복제본(.md 및 .html)을 정리합니다.
"""

import os
import glob
import hashlib
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PLATFORMS = [
    ("네이버 (Naver)", os.path.join(BASE_DIR, "blog", "naver", "posts")),
    ("티스토리 (Tistory)", os.path.join(BASE_DIR, "blog", "tistory", "posts")),
    ("워드프레스 (WordPress)", os.path.join(BASE_DIR, "blog", "wordpress", "posts")),
]

def clean_platform_duplicates(name, posts_dir, dry_run=False):
    print(f"\n==========================================================", flush=True)
    print(f" 🧹 [{name}] 100% 중복 복제 파일 정리 {'(시뮬레이션)' if dry_run else ''}", flush=True)
    print(f"==========================================================", flush=True)

    md_files = sorted(glob.glob(os.path.join(posts_dir, "**", "*.md"), recursive=True))
    hashes = defaultdict(list)

    for f in md_files:
        with open(f, "rb") as fp:
            h = hashlib.sha256(fp.read()).hexdigest()
        hashes[h].append(f)

    deleted_md = 0
    deleted_html = 0

    for h, fl in sorted(hashes.items(), key=lambda x: x[1][0]):
        if len(fl) > 1:
            orig = fl[0]
            redundant = fl[1:]
            print(f"\n📌 원본 보존: {os.path.relpath(orig, BASE_DIR)}", flush=True)
            for dup in redundant:
                html_file = dup[:-3] + ".html"
                print(f"   🗑️ 삭제 대상: {os.path.relpath(dup, BASE_DIR)}", flush=True)
                if not dry_run:
                    if os.path.exists(dup):
                        os.remove(dup)
                        deleted_md += 1
                    if os.path.exists(html_file):
                        os.remove(html_file)
                        deleted_html += 1
                else:
                    deleted_md += 1
                    if os.path.exists(html_file):
                        deleted_html += 1

    print(f"\n✅ [{name}] 정리 결과: 잉여 복제본 MD {deleted_md}개, HTML {deleted_html}개 정리 완료", flush=True)
    return deleted_md, deleted_html

def main():
    import sys
    dry_run = "--dry-run" in sys.argv
    total_md, total_html = 0, 0
    for name, p_dir in PLATFORMS:
        m, h = clean_platform_duplicates(name, p_dir, dry_run=dry_run)
        total_md += m
        total_html += h

    print("\n==========================================================", flush=True)
    print(f" 🎉 전체 3대 블로그 중복 정리 완료: 총 MD {total_md}개, HTML {total_html}개 제거", flush=True)
    print("==========================================================", flush=True)

if __name__ == "__main__":
    main()
