#!/usr/bin/env python3
"""
AI Blog Notes - HTML Viewer Generator
docs/ 폴더 내 마크다운 파일들을 브라우저에서 바로 열람할 수 있는 docs/index.html 생성기
"""

import os
import json
import glob
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
README_PATH = os.path.join(BASE_DIR, "README.md")
OUTPUT_PATH = os.path.join(DOCS_DIR, "index.html")

DOC_METADATA = [
    {
        "id": "readme",
        "category": "소개 & 가이드",
        "category_icon": "📌",
        "title": "프로젝트 개요 (README)",
        "file_path": "README.md",
        "url_path": "../README.md",
        "desc": "프로젝트 목표, 디렉토리 구조 및 AI 워크플로우 종합 안내"
    },
    {
        "id": "monetization-models",
        "category": "01. 수익화 전략",
        "category_icon": "💰",
        "title": "수익화 모델 4단계 총정리",
        "file_path": "docs/01-strategy/01-monetization-models.md",
        "url_path": "01-strategy/01-monetization-models.md",
        "desc": "애드센스, 제휴마케팅, 협찬, 지식창업 단계별 디지털 연금 파이프라인"
    },
    {
        "id": "senior-niche-topics",
        "category": "01. 수익화 전략",
        "category_icon": "💰",
        "title": "은퇴/시니어 고단가 니치 주제 30선",
        "file_path": "docs/01-strategy/02-senior-niche-topics.md",
        "url_path": "01-strategy/02-senior-niche-topics.md",
        "desc": "연금/절세, 건강/액티브시니어, 재취업, 라이프스타일 고단가 키워드"
    },
    {
        "id": "platform-comparison",
        "category": "02. 플랫폼 비교",
        "category_icon": "🌐",
        "title": "블로그 플랫폼 완벽 비교 & 추천",
        "file_path": "docs/02-platforms/01-platform-comparison.md",
        "url_path": "02-platforms/01-platform-comparison.md",
        "desc": "티스토리 vs 워드프레스 vs 네이버 블로그 장단점 및 병행 전략"
    },
    {
        "id": "tistory-guide",
        "category": "02. 플랫폼 비교",
        "category_icon": "🟠",
        "title": "티스토리 개설·운영 & Google Trends 실전 가이드",
        "file_path": "docs/02-platforms/02-tistory-guide.md",
        "url_path": "02-platforms/02-tistory-guide.md",
        "desc": "티스토리 개설부터 서치콘솔, 애드센스 준비, Google Trends 상승 검색어 100점 평가 및 7단계 템플릿"
    },
    {
        "id": "six-step-pipeline",
        "category": "03. AI 워크플로우",
        "category_icon": "⚙️",
        "title": "AI 활용 블로그 작성 6단계 파이프라인",
        "file_path": "docs/03-ai-workflows/01-six-step-pipeline.md",
        "url_path": "03-ai-workflows/01-six-step-pipeline.md",
        "desc": "기획부터 SEO 점검까지 1시간 완성 표준 AI 글쓰기 프로세스"
    },
    {
        "id": "daily-workflow",
        "category": "03. AI 워크플로우",
        "category_icon": "⚙️",
        "title": "일일 통합 블로그 워크플로우 (daily-workflow)",
        "file_path": "workflow/daily-workflow.md",
        "url_path": "../workflow/daily-workflow.md",
        "desc": "네이버·티스토리 주제 수집부터 팩트체크·발행·성과 기록까지 8단계 표준 절차"
    },
    {
        "id": "wf-topic-selection",
        "category": "03. AI 워크플로우",
        "category_icon": "🎯",
        "title": "주제 선정 규칙 및 100점 평가표 (topic-selection)",
        "file_path": "workflow/topic-selection.md",
        "url_path": "../workflow/topic-selection.md",
        "desc": "실시간 이슈 vs 장기 검색 질문 구분 기준 및 5대 평가 루브릭"
    },
    {
        "id": "wf-article-production",
        "category": "03. AI 워크플로우",
        "category_icon": "✍️",
        "title": "초안 생성·검증·편집 절차 (article-production)",
        "file_path": "workflow/article-production.md",
        "url_path": "../workflow/article-production.md",
        "desc": "주제 조사 1회 → 플랫폼별 원고 2편 분리 제작 및 팩트체크 프로세스"
    },
    {
        "id": "wf-publishing",
        "category": "03. AI 워크플로우",
        "category_icon": "✅",
        "title": "발행 전 최종 체크리스트 (publishing)",
        "file_path": "workflow/publishing.md",
        "url_path": "../workflow/publishing.md",
        "desc": "발행 전 3대 팩트체크 질문 및 네이버·티스토리 점검표"
    },
    {
        "id": "wf-performance-review",
        "category": "03. AI 워크플로우",
        "category_icon": "📈",
        "title": "주간 성과 분석 및 개선 가이드 (performance-review)",
        "file_path": "workflow/performance-review.md",
        "url_path": "../workflow/performance-review.md",
        "desc": "노출·클릭·체류시간 분석 및 다음 주 확장 주제 선정 루프"
    },
    {
        "id": "practical-prompts",
        "category": "04. 실전 프롬프트",
        "category_icon": "💬",
        "title": "블로그 작성 실전 프롬프트 라이브러리",
        "file_path": "docs/04-prompts/01-practical-prompts.md",
        "url_path": "04-prompts/01-practical-prompts.md",
        "desc": "후킹 제목, 도입부, 본문 확장, SEO 메타태그 복사-붙여넣기 템플릿"
    },
    {
        "id": "prompt-topic-selection",
        "category": "04. 실전 프롬프트",
        "category_icon": "💬",
        "title": "통합 주제 선정 프롬프트 (prompts/topic-selection)",
        "file_path": "prompts/topic-selection.md",
        "url_path": "../prompts/topic-selection.md",
        "desc": "실시간 Top 10 & Google Trends 상승 검색어 100점 평가 프롬프트"
    },
    {
        "id": "prompt-naver-draft",
        "category": "04. 실전 프롬프트",
        "category_icon": "🟢",
        "title": "네이버 초안 작성 프롬프트 (prompts/naver-draft)",
        "file_path": "prompts/naver-draft.md",
        "url_path": "../prompts/naver-draft.md",
        "desc": "품미인생 페르소나 및 스마트블록 최적화 초안 생성 프롬프트"
    },
    {
        "id": "prompt-tistory-draft",
        "category": "04. 실전 프롬프트",
        "category_icon": "🟠",
        "title": "티스토리 검색형 초안 프롬프트 (prompts/tistory-draft)",
        "file_path": "prompts/tistory-draft.md",
        "url_path": "../prompts/tistory-draft.md",
        "desc": "구글 검색 유입용 7단계 정보 글 & 비교표 생성 프롬프트"
    },
    {
        "id": "prompt-fact-check",
        "category": "04. 실전 프롬프트",
        "category_icon": "🔍",
        "title": "팩트체크 & 품질 검증 프롬프트 (prompts/fact-check)",
        "file_path": "prompts/fact-check.md",
        "url_path": "../prompts/fact-check.md",
        "desc": "할루시네이션 수치, 가상 경험담, 과장 제목 교정 프롬프트"
    },
    {
        "id": "blog-templates",
        "category": "05. 글쓰기 템플릿 & 가이드라인",
        "category_icon": "📑",
        "title": "고수익 블로그 글쓰기 4대 표준 템플릿",
        "file_path": "docs/05-templates/01-blog-templates.md",
        "url_path": "05-templates/01-blog-templates.md",
        "desc": "정보형, 솔직 리뷰형, 경험 에세이형, 가이드북형 마크다운 구조"
    },
    {
        "id": "guide-writing-style",
        "category": "05. 글쓰기 템플릿 & 가이드라인",
        "category_icon": "✒️",
        "title": "공통 문체 및 글쓰기 원칙 (guidelines/writing-style)",
        "file_path": "guidelines/writing-style.md",
        "url_path": "../guidelines/writing-style.md",
        "desc": "결론 선제시, 가짜 경험 금지, 플랫폼별 톤앤매너 구분"
    },
    {
        "id": "guide-naver-blog",
        "category": "05. 글쓰기 템플릿 & 가이드라인",
        "category_icon": "🟢",
        "title": "네이버 블로그 가이드라인 (guidelines/naver-blog)",
        "file_path": "guidelines/naver-blog.md",
        "url_path": "../guidelines/naver-blog.md",
        "desc": "C-Rank & D.I.A 스마트블록 상위 노출 및 해시태그 규칙"
    },
    {
        "id": "guide-tistory-seo",
        "category": "05. 글쓰기 템플릿 & 가이드라인",
        "category_icon": "🟠",
        "title": "티스토리 SEO & 애드센스 가이드 (guidelines/tistory-seo)",
        "file_path": "guidelines/tistory-seo.md",
        "url_path": "../guidelines/tistory-seo.md",
        "desc": "구글 E-E-A-T 7대 규칙, 비교표, 서치 콘솔 색인 관리"
    },
    {
        "id": "guide-source-policy",
        "category": "05. 글쓰기 템플릿 & 가이드라인",
        "category_icon": "🏛️",
        "title": "공식 출처 검증 및 인용 정책 (guidelines/source-policy)",
        "file_path": "guidelines/source-policy.md",
        "url_path": "../guidelines/source-policy.md",
        "desc": "1순위 공신력 기관 목록 및 가정 조건·미확인 수치 처리 원칙"
    },
    {
        "id": "topic-backlog",
        "category": "06. 주제 백로그 & 주간 리뷰",
        "category_icon": "🗂️",
        "title": "유망 주제 대기열 (topics/topic-backlog)",
        "file_path": "topics/topic-backlog.md",
        "url_path": "../topics/topic-backlog.md",
        "desc": "5대 카테고리별 100점 평가 완료된 미작성 주제 목록"
    },
    {
        "id": "topic-calendar",
        "category": "06. 주제 백로그 & 주간 리뷰",
        "category_icon": "📅",
        "title": "주간·월간 발행 캘린더 (topics/topic-calendar)",
        "file_path": "topics/topic-calendar.md",
        "url_path": "../topics/topic-calendar.md",
        "desc": "요일별 네이버·티스토리 발행 리듬 및 차주 예정 스케줄"
    },
    {
        "id": "weekly-review",
        "category": "06. 주제 백로그 & 주간 리뷰",
        "category_icon": "📊",
        "title": "주간 블로그 성과 리뷰 (logs/weekly-review)",
        "file_path": "logs/weekly-review.md",
        "url_path": "../logs/weekly-review.md",
        "desc": "주간 발행 요약, 노출·클릭 점검 및 차주 확장 주제 기록"
    },
    {
        "id": "memo-ideas",
        "category": "아이디어 메모",
        "category_icon": "📝",
        "title": "블로그 아이디어 & 영감 메모장",
        "file_path": "docs/notes/memo-ideas.md",
        "url_path": "notes/memo-ideas.md",
        "desc": "일상 속 경험과 아이디어를 메모하고 AI 초안으로 연결하는 스크래치패드"
    }
]

def load_documents():
    data = {}
    for doc in DOC_METADATA:
        file_path = os.path.join(BASE_DIR, doc["file_path"])
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            data[doc["id"]] = {
                "metadata": doc,
                "content": content
            }
        else:
            print(f"Warning: File not found {file_path}")
    return data

def generate_html():
    docs_data = load_documents()
    docs_json = json.dumps(docs_data, ensure_ascii=False)
    meta_json = json.dumps(DOC_METADATA, ensure_ascii=False)

    html_template = f'''<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Blog Notes | 블로그 운영 지침서 & 가이드 뷰어</title>
  
  <!-- Pretendard Web Font -->
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  
  <!-- Marked.js (Markdown Parser) & Highlight.js -->
  <script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github.min.css" id="hljs-theme">
  <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>

  <style>
    :root {{
      --primary: #2563eb;
      --primary-dark: #1d4ed8;
      --primary-light: #eff6ff;
      --text-main: #1f2937;
      --text-muted: #6b7280;
      --bg-body: #f8fafc;
      --bg-sidebar: #ffffff;
      --bg-content: #ffffff;
      --border-color: #e2e8f0;
      --card-hover: #f1f5f9;
      --accent: #10b981;
    }}

    [data-theme="dark"] {{
      --primary: #3b82f6;
      --primary-dark: #60a5fa;
      --primary-light: #1e293b;
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --bg-body: #0f172a;
      --bg-sidebar: #1e293b;
      --bg-content: #1e293b;
      --border-color: #334155;
      --card-hover: #334155;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: "Pretendard", -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
      color: var(--text-main);
      background-color: var(--bg-body);
      line-height: 1.6;
      display: flex;
      height: 100vh;
      overflow: hidden;
    }}

    /* Sidebar */
    aside {{
      width: 320px;
      min-width: 280px;
      background: var(--bg-sidebar);
      border-right: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      height: 100vh;
      transition: all 0.2s ease;
      z-index: 20;
    }}

    .sidebar-header {{
      padding: 20px 18px 16px;
      border-bottom: 1px solid var(--border-color);
    }}

    .logo-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--primary-light);
      color: var(--primary);
      font-size: 11px;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: 6px;
      margin-bottom: 8px;
    }}

    .site-title {{
      font-size: 17px;
      font-weight: 800;
      color: var(--text-main);
      letter-spacing: -0.3px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .site-desc {{
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 4px;
      line-height: 1.4;
    }}

    .search-box {{
      padding: 12px 18px;
      border-bottom: 1px solid var(--border-color);
    }}

    .search-box input {{
      width: 100%;
      padding: 8px 12px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
      background: var(--bg-body);
      color: var(--text-main);
      font-size: 13px;
      outline: none;
      transition: border 0.15s;
    }}

    .search-box input:focus {{
      border-color: var(--primary);
      box-shadow: 0 0 0 2px var(--primary-light);
    }}

    .nav-list {{
      flex: 1;
      overflow-y: auto;
      padding: 12px 10px;
    }}

    .nav-category {{
      font-size: 11px;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      padding: 12px 10px 4px;
      letter-spacing: 0.5px;
    }}

    .nav-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 500;
      color: var(--text-main);
      cursor: pointer;
      text-decoration: none;
      margin-bottom: 2px;
      transition: background 0.15s, color 0.15s;
    }}

    .nav-item:hover {{
      background: var(--card-hover);
      color: var(--primary);
    }}

    .nav-item.active {{
      background: var(--primary-light);
      color: var(--primary);
      font-weight: 700;
    }}

    .nav-item-title {{
      flex: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      margin-right: 8px;
    }}

    .nav-file-link {{
      color: var(--text-muted);
      font-size: 12px;
      padding: 2px 6px;
      border-radius: 4px;
      text-decoration: none;
      border: 1px solid transparent;
      opacity: 0.6;
      transition: opacity 0.15s, background 0.15s;
    }}

    .nav-file-link:hover {{
      opacity: 1;
      background: var(--border-color);
      color: var(--primary);
    }}

    .sidebar-footer {{
      padding: 14px 18px;
      border-top: 1px solid var(--border-color);
      font-size: 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      color: var(--text-muted);
    }}

    .theme-toggle-btn {{
      background: none;
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 4px 8px;
      font-size: 12px;
      color: var(--text-main);
      cursor: pointer;
    }}

    /* Main Content */
    main {{
      flex: 1;
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
      background: var(--bg-content);
    }}

    .top-bar {{
      height: 56px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
      background: var(--bg-sidebar);
    }}

    .doc-meta {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .badge-category {{
      font-size: 11px;
      font-weight: 600;
      background: var(--border-color);
      color: var(--text-main);
      padding: 2px 8px;
      border-radius: 12px;
    }}

    .doc-path {{
      font-size: 13px;
      font-family: monospace;
      color: var(--text-muted);
    }}

    .doc-actions {{
      display: flex;
      gap: 8px;
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      font-weight: 600;
      padding: 6px 12px;
      border-radius: 6px;
      border: 1px solid var(--border-color);
      background: var(--bg-sidebar);
      color: var(--text-main);
      text-decoration: none;
      cursor: pointer;
      transition: all 0.15s;
    }}

    .btn:hover {{
      border-color: var(--primary);
      color: var(--primary);
      background: var(--primary-light);
    }}

    .btn-home {{
      background: #f1f5f9;
      color: #334155;
    }}

    .btn-naver {{
      background: #03c75a;
      color: #fff;
      border-color: #03c75a;
    }}
    .btn-naver:hover {{
      background: #02b14f;
      color: #fff;
    }}

    .content-area {{
      flex: 1;
      overflow-y: auto;
      padding: 36px 48px 80px;
      max-width: 980px;
      width: 100%;
      margin: 0 auto;
    }}

    /* Markdown Styling */
    .markdown-body {{
      font-size: 15px;
      line-height: 1.75;
      color: var(--text-main);
    }}

    .markdown-body h1 {{
      font-size: 26px;
      font-weight: 800;
      margin: 24px 0 16px;
      padding-bottom: 10px;
      border-bottom: 2px solid var(--border-color);
      color: var(--text-main);
    }}

    .markdown-body h2 {{
      font-size: 20px;
      font-weight: 700;
      margin: 32px 0 12px;
      padding-bottom: 6px;
      border-bottom: 1px solid var(--border-color);
      color: var(--text-main);
    }}

    .markdown-body h3 {{
      font-size: 16px;
      font-weight: 700;
      margin: 20px 0 8px;
    }}

    .markdown-body p {{ margin-bottom: 14px; }}
    .markdown-body ul, .markdown-body ol {{ margin-bottom: 16px; padding-left: 24px; }}
    .markdown-body li {{ margin-bottom: 6px; }}

    .markdown-body blockquote {{
      border-left: 4px solid var(--primary);
      background: var(--card-hover);
      padding: 12px 18px;
      margin: 16px 0;
      border-radius: 0 8px 8px 0;
      color: var(--text-main);
    }}

    .markdown-body table {{
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
      font-size: 13.5px;
    }}

    .markdown-body th, .markdown-body td {{
      border: 1px solid var(--border-color);
      padding: 10px 14px;
      text-align: left;
    }}

    .markdown-body th {{
      background: var(--card-hover);
      font-weight: 700;
    }}

    .markdown-body pre {{
      background: #1e1e1e !important;
      color: #d4d4d4;
      padding: 16px;
      border-radius: 8px;
      overflow-x: auto;
      margin: 18px 0;
      position: relative;
    }}

    .markdown-body code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 13px;
    }}

    .markdown-body p code, .markdown-body li code {{
      background: var(--card-hover);
      color: #e11d48;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 12.5px;
    }}

    .markdown-body hr {{
      border: none;
      height: 1px;
      background: var(--border-color);
      margin: 28px 0;
    }}

    .markdown-body a {{
      color: var(--primary);
      text-decoration: underline;
      text-underline-offset: 3px;
    }}

    .copy-btn {{
      position: absolute;
      top: 8px;
      right: 8px;
      background: rgba(255, 255, 255, 0.15);
      border: 1px solid rgba(255, 255, 255, 0.3);
      color: #fff;
      font-size: 11px;
      padding: 4px 8px;
      border-radius: 4px;
      cursor: pointer;
      transition: background 0.15s;
    }}
    .copy-btn:hover {{
      background: rgba(255, 255, 255, 0.3);
    }}

    @media (max-width: 768px) {{
      body {{ flex-direction: column; }}
      aside {{ width: 100%; height: auto; max-height: 240px; }}
      .content-area {{ padding: 20px; }}
    }}
  </style>
</head>
<body>

  <!-- Sidebar -->
  <aside>
    <div class="sidebar-header">
      <div class="logo-badge">📚 AI Blog Notes 지침서 뷰어</div>
      <div class="site-title">📝 블로그 운영 가이드</div>
      <div class="site-desc">시니어/은퇴자를 위한 AI 수익형 블로그 지침서 & 프롬프트</div>
    </div>

    <div class="search-box">
      <input type="text" id="searchInput" placeholder="문서 또는 키워드 검색...">
    </div>

    <nav class="nav-list" id="navList">
      <!-- Generated dynamically -->
    </nav>

    <div class="sidebar-footer">
      <span>8개 문서 연결됨</span>
      <button class="theme-toggle-btn" id="themeBtn">🌓 테마 전환</button>
    </div>
  </aside>

  <!-- Main Content -->
  <main>
    <header class="top-bar">
      <div class="doc-meta">
        <span class="badge-category" id="currentCategory">01. 수익화 전략</span>
        <span class="doc-path" id="currentPath">01-strategy/01-monetization-models.md</span>
      </div>
      <div class="doc-actions">
        <a href="../index.html" class="btn btn-home" title="메인 블로그 포털 홈으로 이동">
          🏠 홈 포털
        </a>
        <a href="../blog/naver/index.html" class="btn btn-naver" title="네이버 블로그 일별 작성 포털 이동">
          🟢 네이버 블로그
        </a>
        <a href="#" target="_blank" class="btn" id="rawMdLink" title="브라우저 새 탭에서 마크다운 원본 열기">
          📄 원본 .md 열기
        </a>
        <a href="#" download class="btn" id="downloadMdLink" title="마크다운 파일 다운로드">
          💾 다운로드
        </a>
      </div>
    </header>

    <div class="content-area">
      <article class="markdown-body" id="contentView">
        <!-- Rendered markdown content -->
      </article>
    </div>
  </main>

  <script>
    // Embedded Documents Store
    const DOCS_DATA = {docs_json};
    const DOC_METADATA = {meta_json};

    let activeDocId = "readme";

    marked.setOptions({{
      gfm: true,
      breaks: true,
      highlight: function(code, lang) {{
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, {{ language }}).value;
      }}
    }});

    function renderNav(filter = "") {{
      const navEl = document.getElementById("navList");
      navEl.innerHTML = "";

      let currentCat = "";
      DOC_METADATA.forEach(doc => {{
        if (filter) {{
          const q = filter.toLowerCase();
          const matchTitle = doc.title.toLowerCase().includes(q);
          const matchDesc = doc.desc.toLowerCase().includes(q);
          const matchCat = doc.category.toLowerCase().includes(q);
          if (!matchTitle && !matchDesc && !matchCat) return;
        }}

        if (doc.category !== currentCat) {{
          currentCat = doc.category;
          const catHeader = document.createElement("div");
          catHeader.className = "nav-category";
          catHeader.innerHTML = `${{doc.category_icon}} ${{doc.category}}`;
          navEl.appendChild(catHeader);
        }}

        const item = document.createElement("div");
        item.className = "nav-item" + (doc.id === activeDocId ? " active" : "");
        item.onclick = (e) => {{
          if (e.target.tagName.toLowerCase() === 'a') return;
          loadDoc(doc.id);
        }};

        const titleSpan = document.createElement("span");
        titleSpan.className = "nav-item-title";
        titleSpan.textContent = doc.title;
        item.appendChild(titleSpan);

        // Direct link to the .md file
        const directLink = document.createElement("a");
        directLink.className = "nav-file-link";
        directLink.href = doc.url_path;
        directLink.target = "_blank";
        directLink.title = `원본 파일 열기: ${{doc.url_path}}`;
        directLink.innerHTML = "🔗 md";
        directLink.onclick = (e) => e.stopPropagation();
        item.appendChild(directLink);

        navEl.appendChild(item);
      }});
    }}

    async function loadDoc(id) {{
      const doc = DOCS_DATA[id];
      if (!doc) return;

      activeDocId = id;
      renderNav(document.getElementById("searchInput").value);

      document.getElementById("currentCategory").textContent = `${{doc.metadata.category_icon}} ${{doc.metadata.category}}`;
      document.getElementById("currentPath").textContent = doc.metadata.file_path;

      const rawLink = document.getElementById("rawMdLink");
      rawLink.href = doc.metadata.url_path;
      
      const downloadLink = document.getElementById("downloadMdLink");
      downloadLink.href = doc.metadata.url_path;
      downloadLink.download = doc.metadata.file_path.split('/').pop();

      let mdText = doc.content;

      if (window.location.protocol.startsWith("http")) {{
        try {{
          const res = await fetch(doc.metadata.url_path);
          if (res.ok) {{
            mdText = await res.text();
          }}
        }} catch(e) {{
          console.warn("Using embedded fallback", e);
        }}
      }}

      const html = marked.parse(mdText);
      const container = document.getElementById("contentView");
      container.innerHTML = html;

      container.querySelectorAll("pre").forEach(pre => {{
        const btn = document.createElement("button");
        btn.className = "copy-btn";
        btn.textContent = "복사";
        btn.onclick = () => {{
          const code = pre.querySelector("code") ? pre.querySelector("code").innerText : pre.innerText;
          navigator.clipboard.writeText(code).then(() => {{
            btn.textContent = "✓ 복사됨!";
            setTimeout(() => {{ btn.textContent = "복사"; }}, 1500);
          }});
        }};
        pre.appendChild(btn);
      }});

      document.querySelector(".content-area").scrollTop = 0;
      window.location.hash = id;
    }}

    document.getElementById("searchInput").addEventListener("input", (e) => {{
      renderNav(e.target.value);
    }});

    const themeBtn = document.getElementById("themeBtn");
    let isDark = false;
    themeBtn.addEventListener("click", () => {{
      isDark = !isDark;
      document.body.setAttribute("data-theme", isDark ? "dark" : "light");
      const hljsTheme = document.getElementById("hljs-theme");
      if (isDark) {{
        hljsTheme.href = "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github-dark.min.css";
      }} else {{
        hljsTheme.href = "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github.min.css";
      }}
    }});

    window.addEventListener("DOMContentLoaded", () => {{
      const hash = window.location.hash.replace("#", "");
      if (hash && DOCS_DATA[hash]) {{
        loadDoc(hash);
      }} else {{
        loadDoc("readme");
      }}
    }});
  </script>
</body>
</html>'''

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"Successfully generated {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_html()
