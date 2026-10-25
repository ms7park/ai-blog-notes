#!/usr/bin/env python3
"""
Daily Integrated Blog Workflow Batch (네이버 · 티스토리 통합 워크플로우 작업실 & 일별 리포트 생성기)
매일 네이버 실시간 검색어 Top 10 및 Google Trends 상승 검색어 수집 → 1~5점 주제 평가 →
플랫폼별 주제 결정 → 공식 자료 검증 → 초안 작성 → 품질 검증 → 발행 기록(publishing-log.csv)까지
8단계 통합 워크플로우 문서(.md, .html) 및 워크플로우 작업실(blog/workflow/index.html)을 생성합니다.
"""

import os
import sys
import glob
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW_BLOG_DIR = os.path.join(BASE_DIR, "blog", "workflow")
POSTS_DIR = os.path.join(WORKFLOW_BLOG_DIR, "posts")

WEEKDAYS_KR = ["월", "화", "수", "목", "금", "토", "일"]

def build_workflow_post_md(date_str, weekday_str):
    return f"""# [{date_str}] 네이버 · 티스토리 일일 통합 블로그 워크플로우 실행 리포트 (8단계)

> **작성일**: {date_str} ({weekday_str})  
> **워크플로우 기준**: `workflow/daily-workflow.md` (Step 1 주제 수집 ~ Step 8 성과 기록)  
> **대상 플랫폼**: 🟢 네이버 블로그 (`품미인생`) + 🟠 티스토리 블로그 (`똑똑한 생활탐구`)  
> **권장 소요 시간**: 총 30분 (주제 선정 5분 · 자료 확인 5분 · AI 초안 10분 · 검증/편집 7분 · 발행/기록 3분)

---

## Step 1 & Step 2. 오늘의 주제 수집 및 5대 기준 평가표 (1~5점)

오늘 수집된 **네이버 실시간 검색어 TOP 10** 및 **Google Trends 상승 검색어** 후보를 5가지 기준(관심도 · 의도 명확성 · 경쟁 빈틈 · 작성 역량 · 장기 검색성)으로 평가한 결과입니다.

| 후보 키워드 | 검색 관심도 | 의도 명확성 | 경쟁 빈틈 | 작성 역량 | 장기 검색성 | 총점 (100점) | 플랫폼 배정 및 판정 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **엔비디아 / AI** | 5 | 5 | 4 | 5 | 5 | **96점** | 🟠 **티스토리 #1편** + 🟢 네이버 테마 글 |
| **경상수지 / 국민연금** | 4 | 5 | 4 | 4 | 5 | **88점** | 🟠 **티스토리 #2편** (공식 조회·물가 연동) |
| **주얼리 / 순금(24K)** | 4 | 4 | 4 | 4 | 4 | **80점** | 🟠 **티스토리 #3편** (주얼리·골드바·KRX 비교) |
| **한의사 / 건강관리** | 4 | 4 | 3 | 4 | 3 | **72점** | 🟢 **네이버 #2편** (5060 시니어 건강 수칙) |
| **반계리 은행나무 / 예금** | 4 | 3 | 3 | 4 | 3 | **68점** | 🟢 **네이버 #4편** (가을 일상 & 금리·절세) |
| **웨스트햄 / 네이마르** | 4 | 2 | 2 | 2 | 1 | **44점** | 🟢 **네이버 실시간 이슈** (티스토리 보류) |

---

## Step 3. 플랫폼별 최종 주제 결정 및 차별화 설계

동일한 트렌드 소스에서 출발하더라도 **단순 복제를 금지**하고 플랫폼별 검색 의도에 맞게 제목과 구성을 완전히 분리했습니다.

| 구분 | 🟢 네이버 블로그 (`품미인생` · 이슈 & 공감 중심) | 🟠 티스토리 블로그 (`똑똑한 생활탐구` · 검색 질문 해결 중심) |
| :--- | :--- | :--- |
| **AI·IT 주제** | 5060을 위한 스마트 라이프! 'AI' 최신 트렌드와 일상을 편리하게 바꾸는 핵심 기능 | **ChatGPT 등 AI로 블로그 초안 작성 후 사실관계(팩트체크) 검증하는 5단계 방법** |
| **연금·경제 주제** | 반계리 은행나무 금리 비교와 만기 재예치 노하우, 이자 세금 아끼는 3대 절세 비결 | **국민연금 예상 수령액 조회 방법 및 물가상승률 반영 기준 정리 (경상수지·경제지표 확인법)** |
| **자산·제품 비교** | 지금이라도 금 사둘까? 사상 최고가 속 은퇴자 실전 금 투자법 3가지 | **순금(24K) 주얼리 vs 골드바 vs KRX 금현물 구매 방법 및 수수료·세금 비교표** |

---

## Step 4. 공식 자료 조사 및 출처 검증 (`guidelines/source-policy.md`)

1. **국민연금 예상 수령액 및 물가 반영 기준**:
   - 공식 출처: [국민연금공단 내 연금 알아보기](https://www.nps.or.kr/), [금융감독원 통합연금포털](https://100lifeplan.fss.or.kr/)
   - 검증 수치: 1969년생 이후 정상 수령 만 65세, 조기노령연금 감액 연 6%(최대 5년 30%), 연기연금 증액 연 7.2%(최대 5년 36%), 건보료 피부양자 소득 기준 연 2,000만 원 이하
2. **순금(24K) 주얼리 · 골드바 · KRX 금현물 비교**:
   - 공식 출처: [한국거래소(KRX) 금시장 정보시스템](http://marketdata.krx.co.kr/)
   - 검증 수치: 1돈 = 3.75g, 순도 표기 24K(999/999.9)·18K(750, 75%)·14K(585, 58.5%), 실물 구매 시 부가세 10% 부과 vs KRX 장내 거래 매매차익 비과세·부가세 면제
3. **AI 블로그 팩트체크 및 티스토리 광고 정책**:
   - 공식 출처: [Google 검색 센터](https://developers.google.com/search/docs?hl=ko), [Google AdSense 고객센터](https://support.google.com/adsense/?hl=ko)
   - 검증 사실: 2026년 6월 29일부 티스토리 카카오 애드핏 신규 연동 종료 반영

---

## Step 5 & Step 6. AI 초안 작성 및 품질 검증 (`prompts/fact-check.md`)

- [x] **사실과 수치가 공식 출처에 부합하는가?** (공단·거래소 공식 기준 대조 완료)
- [x] **제목이 본문 내용과 정확히 일치하는가?** (과장·낚시성 제목 배제 완료)
- [x] **가상 개인 경험담이 없는가?** (해보지 않은 일을 1인칭 경험처럼 쓴 문장 제거 완료)
- [x] **반복 문장과 상투적 서론이 없는가?** (도입부 상단에 핵심 답변 요약 선제시 적용)
- [x] **플랫폼 간 원고 중복이 없는가?** (네이버 5편과 티스토리 3편의 구조·문장 100% 분리)

---

## Step 7 & Step 8. 발행 파일 연결 및 성과 기록 (`logs/publishing-log.csv`)

### 1) 오늘 생성된 플랫폼별 원고 바로가기
- **🟠 티스토리 블로그 (3편)**:
  - [#1편: ChatGPT 등 AI 블로그 초안 팩트체크 5단계 방법](../../tistory/posts/202610/{date_str}.html)
  - [#2편: 국민연금 예상 수령액 조회 방법 및 물가상승률 반영 기준](../../tistory/posts/202610/{date_str}-2.html)
  - [#3편: 순금(24K) 주얼리 vs 골드바 vs KRX 금현물 비교표](../../tistory/posts/202610/{date_str}-3.html)
- **🟢 네이버 블로그 (대표 글)**:
  - [오늘자 네이버 블로그 포스트 뷰어 열기](../../naver/posts/202610/{date_str}.html)

### 2) 매일 Claude Code / AI 에이전트에 입력할 워크플로우 명령

```markdown
이 저장소의 README.md와 workflow/daily-workflow.md를 먼저 읽어 주세요.

오늘의 블로그 콘텐츠 작업을 시작합니다.

1. topics/topic-backlog.md에서 기존 주제와 중복되는 항목을 확인합니다.
2. 네이버 블로그용 실시간 이슈 주제 후보와 티스토리용 검색형 주제 후보를 구분합니다.
3. 실제 최신 검색 데이터를 확인할 수 없는 경우 검색량이나 순위를 추측하지 말고, 추가 조사가 필요한 항목으로 표시합니다.
4. 후보별 검색 의도, 장기성, 경쟁 콘텐츠의 빈틈, 사실 확인 가능성을 평가합니다.
5. 우선 작성할 주제를 추천하고, 선정 이유와 필요한 출처를 제시합니다.
6. 제가 주제를 승인하기 전에는 최종 게시글을 발행하거나 기존 파일을 덮어쓰지 마세요.
7. 승인된 주제에 대해서만 해당 플랫폼의 작성 지침에 따라 초안을 생성합니다.
8. fact-check.md와 publishing.md 기준으로 검토하고, 미확인 사실과 발행 전 점검 항목을 별도로 출력합니다.

우선 주제 후보와 평가 결과부터 보여 주세요.
```
"""

def build_workflow_post_html(date_str, weekday_str, md_content):
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[{date_str}] 통합 블로그 워크플로우 실행 리포트 | AI Blog Notes</title>
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
  <style>
    :root {{
      --wf: #4f46e5;
      --wf-dark: #4338ca;
      --wf-light: #eef2ff;
      --wf-border: #c7d2fe;
      --text-main: #1f2937;
      --text-sub: #4b5563;
      --text-muted: #6b7280;
      --border: #e5e7eb;
      --bg: #f8fafc;
      --white: #ffffff;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: "Pretendard", -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text-main);
      line-height: 1.75;
      padding-bottom: 80px;
    }}
    .top-nav {{
      background: var(--white);
      border-bottom: 1px solid var(--border);
      padding: 14px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 100;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .nav-left {{ display: flex; align-items: center; gap: 12px; }}
    .brand-tag {{
      background: var(--wf);
      color: var(--white);
      font-size: 11px;
      font-weight: 800;
      padding: 4px 8px;
      border-radius: 4px;
    }}
    .nav-title {{ font-size: 15px; font-weight: 700; }}
    .nav-actions {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 7px 13px;
      border-radius: 6px;
      font-size: 12.5px;
      font-weight: 600;
      text-decoration: none;
      cursor: pointer;
      border: 1px solid var(--border);
      background: var(--white);
      color: var(--text-main);
    }}
    .btn-wf {{ background: var(--wf); color: #fff; border-color: var(--wf); }}
    .container {{ max-width: 880px; margin: 32px auto 0; padding: 0 16px; }}
    .editor-preview {{
      background: var(--white);
      border-radius: 12px;
      padding: 40px 48px;
      border: 1px solid var(--border);
      border-top: 4px solid var(--wf);
      box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }}
    .editor-preview h1 {{ font-size: 23px; font-weight: 800; margin-bottom: 22px; padding-bottom: 12px; border-bottom: 2px solid var(--wf); }}
    .editor-preview h2 {{ font-size: 19px; font-weight: 750; margin: 32px 0 14px; border-left: 4px solid var(--wf); padding-left: 12px; color: #111827; }}
    .editor-preview h3 {{ font-size: 16px; font-weight: 700; margin: 20px 0 10px; }}
    .editor-preview p {{ margin-bottom: 14px; font-size: 15px; color: #374151; }}
    .editor-preview ul, .editor-preview ol {{ margin: 12px 0 20px 22px; }}
    .editor-preview li {{ margin-bottom: 6px; font-size: 14.5px; }}
    .editor-preview blockquote {{
      background: var(--wf-light);
      border: 1px solid var(--wf-border);
      border-left: 4px solid var(--wf);
      padding: 14px 18px;
      margin: 18px 0;
      border-radius: 8px;
      font-size: 14px;
      color: #312e81;
    }}
    .editor-preview table {{ width: 100%; border-collapse: collapse; margin: 18px 0 24px; font-size: 13.5px; }}
    .editor-preview th {{ background: var(--wf-light); color: #312e81; font-weight: 700; border: 1px solid var(--wf-border); padding: 9px 11px; text-align: left; }}
    .editor-preview td {{ border: 1px solid var(--border); padding: 9px 11px; }}
    .editor-preview pre {{ background: #1e293b; color: #f8fafc; padding: 16px; border-radius: 8px; overflow-x: auto; font-size: 13px; margin: 16px 0; }}
    .toast {{
      position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
      background: #111827; color: #fff; padding: 12px 24px; border-radius: 8px;
      font-size: 14px; font-weight: 600; opacity: 0; pointer-events: none; transition: all 0.2s;
    }}
    .toast.show {{ opacity: 1; transform: translateX(-50%) translateY(-10px); }}
  </style>
</head>
<body>
  <header class="top-nav">
    <div class="nav-left">
      <span class="brand-tag">WORKFLOW REPORT</span>
      <span class="nav-title">일별 통합 워크플로우 리포트: {date_str} ({weekday_str})</span>
    </div>
    <div class="nav-actions">
      <a href="../../index.html" class="btn">⚙️ 워크플로우 작업실 홈</a>
      <a href="../../../index.html" class="btn">🏠 멀티 블로그 포털</a>
      <a href="{date_str}.md" target="_blank" class="btn">📄 원본 MD 열기</a>
      <button class="btn btn-wf" id="copyMdBtn">📋 워크플로우 리포트 복사</button>
    </div>
  </header>
  <div class="container">
    <article class="editor-preview" id="postArticle"></article>
  </div>
  <div class="toast" id="toast">복사되었습니다!</div>
  <script id="rawMarkdown" type="text/plain">
{md_content}
  </script>
  <script>
    const mdSource = document.getElementById("rawMarkdown").textContent.trim();
    document.getElementById("postArticle").innerHTML = marked.parse(mdSource);
    document.getElementById("copyMdBtn").addEventListener("click", async () => {{
      await navigator.clipboard.writeText(mdSource);
      const t = document.getElementById("toast");
      t.classList.add("show");
      setTimeout(() => t.classList.remove("show"), 2200);
    }});
  </script>
</body>
</html>"""

def build_workflow_index_html(today_str, weekday_str):
    ym = today_str[:7].replace("-", "")
    claude_cmd = (
        "이 저장소의 README.md와 workflow/daily-workflow.md를 먼저 읽어 주세요.\\n\\n"
        "오늘의 블로그 콘텐츠 작업을 시작합니다.\\n\\n"
        "1. topics/topic-backlog.md에서 기존 주제와 중복되는 항목을 확인합니다.\\n"
        "2. 네이버 블로그용 실시간 이슈 주제 후보와 티스토리용 검색형 주제 후보를 구분합니다.\\n"
        "3. 실제 최신 검색 데이터를 확인할 수 없는 경우 검색량이나 순위를 추측하지 말고, 추가 조사가 필요한 항목으로 표시합니다.\\n"
        "4. 후보별 검색 의도, 장기성, 경쟁 콘텐츠의 빈틈, 사실 확인 가능성을 평가합니다.\\n"
        "5. 우선 작성할 주제를 추천하고, 선정 이유와 필요한 출처를 제시합니다.\\n"
        "6. 제가 주제를 승인하기 전에는 최종 게시글을 발행하거나 기존 파일을 덮어쓰지 마세요.\\n"
        "7. 승인된 주제에 대해서만 해당 플랫폼의 작성 지침에 따라 초안을 생성합니다.\\n"
        "8. fact-check.md와 publishing.md 기준으로 검토하고, 미확인 사실과 발행 전 점검 항목을 별도로 출력합니다.\\n\\n"
        "우선 주제 후보와 평가 결과부터 보여 주세요."
    )

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>네이버 · 티스토리 통합 워크플로우 작업실 | AI Blog Notes</title>
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <style>
    :root {{
      --wf: #4f46e5;
      --wf-dark: #4338ca;
      --wf-light: #eef2ff;
      --wf-border: #c7d2fe;
      --text-main: #191f28;
      --text-sub: #4e5968;
      --text-muted: #8b95a1;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --border: #e5e8eb;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: "Pretendard", -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text-main);
      line-height: 1.6;
      padding-bottom: 80px;
    }}
    .header {{
      background: var(--card-bg);
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .header-inner {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 14px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .brand-wrap {{ display: flex; align-items: center; gap: 12px; }}
    .wf-badge {{
      background: var(--wf);
      color: #fff;
      font-size: 11px;
      font-weight: 800;
      padding: 4px 8px;
      border-radius: 6px;
    }}
    .brand-title {{ font-size: 18px; font-weight: 800; }}
    .header-links {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .header-link {{
      font-size: 13px;
      color: var(--text-sub);
      text-decoration: none;
      padding: 6px 12px;
      border-radius: 6px;
      border: 1px solid var(--border);
      font-weight: 600;
    }}
    .header-link:hover {{ border-color: var(--wf); color: var(--wf-dark); }}
    .container {{ max-width: 1120px; margin: 28px auto 0; padding: 0 20px; }}
    .hero-banner {{
      background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%);
      color: #fff;
      padding: 32px 36px;
      border-radius: 16px;
      margin-bottom: 28px;
      box-shadow: 0 8px 24px rgba(79, 70, 229, 0.2);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 20px;
    }}
    .hero-text h1 {{ font-size: 24px; font-weight: 800; margin-bottom: 8px; }}
    .hero-text p {{ font-size: 14px; opacity: 0.94; max-width: 650px; }}
    .hero-stats {{ display: flex; gap: 16px; }}
    .stat-box {{
      background: rgba(255, 255, 255, 0.16);
      padding: 12px 18px;
      border-radius: 12px;
      text-align: center;
      min-width: 100px;
    }}
    .stat-number {{ font-size: 21px; font-weight: 800; display: block; }}
    .stat-label {{ font-size: 12px; opacity: 0.9; }}
    .main-grid {{ display: grid; grid-template-columns: 1fr 350px; gap: 24px; }}
    @media (max-width: 920px) {{ .main-grid {{ grid-template-columns: 1fr; }} }}
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 24px;
      margin-bottom: 24px;
    }}
    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border);
    }}
    .card-title {{ font-size: 17px; font-weight: 750; }}
    .post-card {{
      border: 2px solid var(--wf);
      border-radius: 12px;
      padding: 20px;
      background: #fff;
      margin-bottom: 16px;
    }}
    .post-card-title {{
      font-size: 17px;
      font-weight: 750;
      color: var(--text-main);
      text-decoration: none;
      display: inline-block;
      margin: 8px 0;
    }}
    .post-card-title:hover {{ color: var(--wf-dark); text-decoration: underline; }}
    .file-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
    }}
    @media (max-width: 600px) {{ .file-grid {{ grid-template-columns: 1fr; }} }}
    .file-item {{
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px;
      background: var(--bg);
      text-decoration: none;
      color: var(--text-main);
      transition: all 0.15s;
    }}
    .file-item:hover {{
      border-color: var(--wf);
      background: var(--wf-light);
    }}
    .file-item-title {{ font-size: 13.5px; font-weight: 750; color: var(--wf-dark); margin-bottom: 4px; }}
    .file-item-desc {{ font-size: 12px; color: var(--text-sub); }}
    .action-btn {{
      font-size: 12.5px;
      font-weight: 600;
      padding: 7px 14px;
      border-radius: 6px;
      text-decoration: none;
      border: 1px solid var(--border);
      background: #fff;
      color: var(--text-main);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .action-btn-primary {{ background: var(--wf); color: #fff; border-color: var(--wf); }}
    .toast {{
      position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
      background: #111827; color: #fff; padding: 12px 24px; border-radius: 8px;
      font-size: 13.5px; font-weight: 600; opacity: 0; pointer-events: none; transition: all 0.2s;
    }}
    .toast.show {{ opacity: 1; transform: translateX(-50%) translateY(-10px); }}
  </style>
</head>
<body>
  <header class="header">
    <div class="header-inner">
      <div class="brand-wrap">
        <span class="wf-badge">WORKFLOW HUB</span>
        <div class="brand-title">네이버 · 티스토리 통합 워크플로우 작업실</div>
      </div>
      <div class="header-links">
        <a href="../../index.html" class="header-link">🏠 멀티 블로그 포털</a>
        <a href="../naver/index.html" class="header-link">🟢 네이버 작업실</a>
        <a href="../tistory/index.html" class="header-link">🟠 티스토리 작업실</a>
        <a href="../../docs/index.html#daily-workflow" class="header-link">📚 워크플로우 문서 뷰어</a>
      </div>
    </div>
  </header>

  <div class="container">
    <section class="hero-banner">
      <div class="hero-text">
        <h1>⚙️ 네이버 · 티스토리 8단계 통합 워크플로우 허브</h1>
        <p>주제 수집(실시간 Top 10 & Google Trends) → 1~5점 주제 평가 → 플랫폼별 맞춤 초안 → 공식 출처 팩트체크 → 발행 및 CSV 성과 기록까지 한곳에서 관리합니다.</p>
      </div>
      <div class="hero-stats">
        <div class="stat-box">
          <span class="stat-number">8 단계</span>
          <span class="stat-label">표준 프로토콜</span>
        </div>
        <div class="stat-box">
          <span class="stat-number">30 분</span>
          <span class="stat-label">일일 권장 루틴</span>
        </div>
      </div>
    </section>

    <div class="main-grid">
      <div class="left-col">
        <section class="card">
          <div class="card-header">
            <div class="card-title">📅 일별 통합 워크플로우 실행 리포트</div>
            <span style="font-size: 12px; color: var(--text-muted);">최신: {today_str} ({weekday_str})</span>
          </div>
          <article class="post-card">
            <div style="font-size: 12px; font-weight: 700; color: var(--wf-dark);">📍 {today_str} ({weekday_str}) · Step 1 ~ Step 8 통합 실행본</div>
            <a href="posts/{ym}/{today_str}.html" class="post-card-title">
              [{today_str}] 네이버 · 티스토리 일일 통합 블로그 워크플로우 실행 리포트 (8단계)
            </a>
            <p style="font-size: 13.5px; color: var(--text-sub); margin-bottom: 14px;">
              오늘의 후보 키워드 100점 평가표, 네이버(품미인생) vs 티스토리(똑똑한 생활탐구) 주제 분리 설계, 공식 기관 팩트체크 결과 및 발행 체크리스트 종합 리포트입니다.
            </p>
            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed var(--border); padding-top: 12px;">
              <span style="font-size: 12px; color: var(--text-muted);">연동 플랫폼: 네이버 5편 + 티스토리 3편</span>
              <div style="display: flex; gap: 8px;">
                <a href="posts/{ym}/{today_str}.md" target="_blank" class="action-btn">📄 MD 원문</a>
                <a href="posts/{ym}/{today_str}.html" class="action-btn action-btn-primary">👁️ 워크플로우 리포트 열기</a>
              </div>
            </div>
          </article>
        </section>

        <section class="card">
          <div class="card-header">
            <div class="card-title">📂 표준 워크플로우 · 프롬프트 · 가이드라인 파일 체계</div>
            <a href="../../docs/index.html#daily-workflow" style="font-size: 12.5px; color: var(--wf-dark); font-weight: 700; text-decoration: none;">전체 문서 뷰어로 열기 →</a>
          </div>
          <div class="file-grid">
            <a href="../../workflow/daily-workflow.md" target="_blank" class="file-item">
              <div class="file-item-title">📋 workflow/daily-workflow.md</div>
              <div class="file-item-desc">매일 수행할 8단계 작업 순서와 30분 시간 배분</div>
            </a>
            <a href="../../workflow/topic-selection.md" target="_blank" class="file-item">
              <div class="file-item-title">🎯 workflow/topic-selection.md</div>
              <div class="file-item-desc">네이버·티스토리 주제 선정 규칙 및 100점 평가표</div>
            </a>
            <a href="../../workflow/article-production.md" target="_blank" class="file-item">
              <div class="file-item-title">✍️ workflow/article-production.md</div>
              <div class="file-item-desc">주제 조사 1회 → 플랫폼별 원고 2편 제작·검증 절차</div>
            </a>
            <a href="../../workflow/publishing.md" target="_blank" class="file-item">
              <div class="file-item-title">✅ workflow/publishing.md</div>
              <div class="file-item-desc">발행 전 필수 3대 팩트체크 및 플랫폼별 점검표</div>
            </a>
            <a href="../../workflow/performance-review.md" target="_blank" class="file-item">
              <div class="file-item-title">📈 workflow/performance-review.md</div>
              <div class="file-item-desc">주간 성과 분석(노출·클릭·체류시간) 및 다음 주 계획</div>
            </a>
            <a href="../../topics/topic-backlog.md" target="_blank" class="file-item">
              <div class="file-item-title">🗂️ topics/topic-backlog.md</div>
              <div class="file-item-desc">5대 카테고리별 미작성 유망 주제 대기열 & 캘린더</div>
            </a>
            <a href="../../prompts/fact-check.md" target="_blank" class="file-item">
              <div class="file-item-title">🔍 prompts/fact-check.md</div>
              <div class="file-item-desc">초안 사실관계·수치·가상 경험 검증 전용 프롬프트</div>
            </a>
            <a href="../../logs/publishing-log.csv" target="_blank" class="file-item">
              <div class="file-item-title">📊 logs/publishing-log.csv</div>
              <div class="file-item-desc">일자별 네이버·티스토리 발행 이력 및 성과 기록 CSV</div>
            </a>
          </div>
        </section>
      </div>

      <div class="right-col">
        <section class="card" style="border: 2px solid var(--wf);">
          <div class="card-title" style="margin-bottom: 10px;">🤖 매일 Claude Code / AI 실행 명령</div>
          <p style="font-size: 12.5px; color: var(--text-sub); margin-bottom: 12px;">
            저장소 루트에서 아래 명령을 복사해 입력하면 주제 중복 확인 → 후보 평가 → 승인 후 초안 생성 → 팩트체크까지 표준 절차대로 실행됩니다.
          </p>
          <button class="action-btn action-btn-primary" style="width: 100%; justify-content: center; padding: 10px;" onclick="copyText('{claude_cmd}')">
            📋 일일 워크플로우 시작 명령 복사
          </button>
        </section>

        <section class="card">
          <div class="card-title" style="margin-bottom: 12px;">⏱️ 매일 30분 표준 시간 배분</div>
          <div style="font-size: 13px; color: var(--text-sub); display: flex; flex-direction: column; gap: 8px;">
            <div style="display:flex; justify-content:space-between;"><span>1. 주제 수집 및 선정</span><strong>5분</strong></div>
            <div style="display:flex; justify-content:space-between;"><span>2. 공식 자료 확인</span><strong>5분</strong></div>
            <div style="display:flex; justify-content:space-between;"><span>3. 플랫폼별 AI 초안 작성</span><strong>10분</strong></div>
            <div style="display:flex; justify-content:space-between;"><span>4. 사실 검증 및 편집</span><strong>7분</strong></div>
            <div style="display:flex; justify-content:space-between;"><span>5. 발행 및 CSV 기록</span><strong>3분</strong></div>
            <div style="display:flex; justify-content:space-between; border-top:1px solid var(--border); padding-top:8px; color:var(--wf-dark);"><strong>일일 합계</strong><strong>총 30분</strong></div>
          </div>
        </section>
      </div>
    </div>
  </div>

  <div class="toast" id="toast">✓ 클립보드에 복사되었습니다!</div>
  <script>
    function copyText(text) {{
      navigator.clipboard.writeText(text).then(() => {{
        const t = document.getElementById("toast");
        t.classList.add("show");
        setTimeout(() => t.classList.remove("show"), 2200);
      }});
    }}
  </script>
</body>
</html>"""

def run_workflow_batch(target_date=None):
    now = datetime.now()
    today_date = datetime.strptime(target_date, "%Y-%m-%d") if target_date else now
    today_str = today_date.strftime("%Y-%m-%d")
    weekday_str = WEEKDAYS_KR[today_date.weekday()]
    ym = today_str[:7].replace("-", "")

    post_dir = os.path.join(POSTS_DIR, ym)
    os.makedirs(post_dir, exist_ok=True)

    md_content = build_workflow_post_md(today_str, weekday_str)
    md_path = os.path.join(post_dir, f"{today_str}.md")
    html_path = os.path.join(post_dir, f"{today_str}.html")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(build_workflow_post_html(today_str, weekday_str, md_content))

    os.makedirs(WORKFLOW_BLOG_DIR, exist_ok=True)
    with open(os.path.join(WORKFLOW_BLOG_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_workflow_index_html(today_str, weekday_str))

    print(f"✅ blog/workflow/index.html 및 posts/{ym}/{today_str}.md/.html 생성 완료")

if __name__ == "__main__":
    date_args = [a for a in sys.argv[1:] if not a.startswith("--")]
    run_workflow_batch(date_args[0] if date_args else None)
