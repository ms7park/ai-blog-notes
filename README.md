# 📝 AI Blog Notes (ai-blog-notes)

> **"은퇴 후 인생 2막, AI를 파트너 삼아 안정적인 노후 수입을 만드는 블로그 운영 지침서 & 메모"**

---

## 💡 프로젝트 비전 (Vision)

은퇴 후 가장 가치 있는 자산은 **30~40년 동안 축적된 삶의 지혜와 경험**입니다.  
`ai-blog-notes`는 AI(Gemini, ChatGPT, Claude)를 유능한 비서로 활용하여, 글쓰기의 물리적 부담(자료 조사, 뼈대 잡기, 초안 작성)을 80% 줄이고, 나만의 스토리와 감성을 더해 **월 100만~300만 원 이상의 안정적인 노후 현금 흐름**을 만드는 실전 지침서이자 작업 공간입니다.

---

## 🎯 4대 핵심 축

| 축 | 핵심 내용 | 목표 |
| :--- | :--- | :--- |
| **1. 수익화 전략** | 구글 애드센스, 네이버 애드포스트, 제휴마케팅(쿠팡 등), 협찬 | 지속 가능한 노후 부수입 파이프라인 구축 |
| **2. 고단가 니치 주제** | 연금·절세, 시니어 건강, 재취업·창업, 은퇴 일상/취미(골프 등), 여행 | 단가가 높고 독자 충성도가 높은 주제 선점 |
| **3. AI + 휴먼 터치** | AI의 초안 작성 + 필자의 진솔한 경험담/감성 결합 | 검색엔진 최적화(SEO) 및 감동을 주는 글 완성 |
| **4. 시스템화 & 템플릿** | 클릭을 부르는 제목, 도입부 후킹, 본문 템플릿, 프롬프트 저장소 | 1시간 만에 고품질 포스팅 1편 발행 |

---

## 📂 프로젝트 디렉토리 구조

```
ai-blog-notes/
├── index.html                  # [포털] 멀티 블로그 통합 허브 (네이버, 티스토리, 워드프레스)
├── README.md                   # 프로젝트 소개 및 로드맵
├── HELP                        # 작업 요청 및 업데이트 히스토리
├── AGENTS.md / GEMINI.md       # AI 에이전트 자율 권한 설정
├── docs/                       # [지침서] 블로그 운영 가이드 & 뷰어
│   ├── index.html              # 브라우저 전용 마크다운 가이드 뷰어
│   ├── 01-strategy/            # [전략] 수익화 모델, 시니어 고단가 주제, 퍼스널 브랜딩
│   ├── 02-platforms/           # [플랫폼] 네이버 vs 티스토리 vs 워드프레스 비교 및 선택
│   ├── 03-ai-workflows/        # [워크플로우] 키워드 발굴부터 휴먼터치 퇴고까지 6단계
│   ├── 04-prompts/             # [프롬프트] 제목, 도입부, 본문, 경험 결합 실전 프롬프트 모음
│   ├── 05-templates/           # [템플릿] 정보형, 리뷰형, 비교분석형, 일상에세이형 글쓰기 틀
│   └── notes/                  # [메모] 블로그 아이디어 및 영감 기록장
├── workflow/                   # [워크플로우] 네이버·티스토리 공통 8단계 작업 절차
│   ├── daily-workflow.md       # 매일 수행할 작업 순서(Step 1~8)와 30분 시간 배분
│   ├── topic-selection.md      # 네이버·티스토리 주제 선정 규칙 및 100점 평가 루브릭
│   ├── article-production.md   # 주제 조사 1회 → 플랫폼별 원고 2편 제작·검증 절차
│   ├── publishing.md           # 발행 전 3대 팩트체크 및 플랫폼별 점검 체크리스트
│   └── performance-review.md   # 주간 성과 분석(노출·클릭·체류시간) 및 다음 주 계획
├── prompts/                    # [표준 프롬프트] 단계별 즉시 복사 AI 프롬프트
│   ├── topic-selection.md      # 통합 주제 선정 및 100점 평가 프롬프트
│   ├── naver-draft.md          # 네이버 블로그 품미인생 초안 작성 프롬프트
│   ├── tistory-draft.md        # 티스토리 7단계 검색형 정보 글 작성 프롬프트
│   └── fact-check.md           # 초안 사실관계·수치·가상 경험 검증 프롬프트
├── guidelines/                 # [가이드라인] 문체·SEO·출처 검증 원칙
│   ├── writing-style.md        # 공통 문체(결론 선제시, 가짜 경험 금지) 및 톤앤매너
│   ├── naver-blog.md           # 네이버 C-Rank & D.I.A 스마트블록 최적화 규칙
│   ├── tistory-seo.md          # 티스토리 구글 E-E-A-T SEO 및 애드센스 규칙
│   └── source-policy.md        # 1순위 공신력 출처 및 미확인 수치 처리 정책
├── topics/                     # [주제 관리] 백로그 및 주간·월간 캘린더
│   ├── topic-backlog.md        # 5대 카테고리별 미작성 유망 주제 대기열
│   └── topic-calendar.md       # 주간·월간 발행 스케줄 캘린더
├── logs/                       # [기록] 배치 로그 및 발행·성과 기록
│   ├── publishing-log.csv      # 일자별 네이버·티스토리 발행 이력 및 성과 CSV
│   └── weekly-review.md        # 주간 성과 리뷰 및 차주 확장 주제 기록
├── blog/                       # [발행] 3대 플랫폼별 블로그 작업 공간
│   ├── naver/                  # 🟢 네이버 블로그 일별 작업실 (캘린더, 실시간 검색어 Top 10)
│   │   ├── index.html          # 네이버 블로그 작업 대시보드
│   │   └── posts/              # 일별 포스팅 초안 (년월 YYYYMM/ 하위 .md, 서식 .html)
│   ├── tistory/                # 🟠 티스토리 블로그 작업실 (Google Trends 100점 평가 & 애드센스)
│   │   ├── index.html          # 티스토리 작업 대시보드 (주제 평가표, 5대 카테고리, 체크리스트)
│   │   └── posts/              # 티스토리 7단계 검색형 포스팅 (년월 YYYYMM/ 하위 .md, .html)
│   └── wordpress/              # 🔵 워드프레스(WP) 코너스톤 SEO 작업실 (구텐베르크 & Rank Math)
│       ├── index.html          # 워드프레스 작업 대시보드 (5대 필러 카테고리, 온페이지 SEO 체크리스트)
│       └── posts/              # 워드프레스 코너스톤 포스팅 (영문 Slug, 메타설명, 비교표, FAQ 스키마)
├── scripts/                    # [스케줄러] macOS 네이티브 배치 (initClaude 표준)
│   ├── daily-naver-blog.sh     # caffeinate 절전 차단 & 실행 래퍼 스크립트
│   ├── install-launchd.sh      # launchd LaunchAgent 적재 (매일 00:00 실행)
│   ├── uninstall-launchd.sh    # launchd 등록 해제 스크립트
│   └── launchd/                # com.user.daily-naver-blog.plist
└── tools/                      # [도구] 보조 분석 및 자동화 스크립트
    ├── daily_naver_batch.py    # 네이버 실시간 트렌드 수집 & 일별 포스팅 자동 생성 배치
    ├── daily_tistory_batch.py  # 티스토리 Google Trends 상승 검색어 평가 & 7단계 글 생성 배치
    ├── daily_wordpress_batch.py# 워드프레스 코너스톤 SEO(Slug/Meta/FAQ) 글 생성 배치
    ├── generate_html.py        # docs/index.html 가이드 뷰어 갱신 빌더
    └── blog_helper.py          # 글자수, 키워드 밀도, SEO 구조 분석 CLI 도구
```

---

## 🚀 AI 파트너와 함께 일하는 방법 (AI Native Workflow)

1. **포털 열람 (`open index.html`)**:
   - 브라우저에서 통합 포털을 열어 오늘의 네이버 블로그 포스팅과 실시간 검색어 Top 10을 확인합니다.
2. **원클릭 스마트에디터 복사**:
   - `blog/naver/posts/YYYYMM/YYYY-MM-DD.html`에서 **[🟢 네이버 스마트에디터 서식 복사]** 버튼을 눌러 `**` 기호 없이 서식 그대로 네이버 블로그에 붙여넣습니다.
3. **휴먼 터치 퇴고**:
   - AI가 작성한 초안에 나의 실제 경험담, 느낀 점, 사진을 1~2장 추가하여 나만의 특별한 글을 완성합니다.
4. **품질 점검**:
   - `python tools/blog_helper.py draft.md`로 글자수, 소제목 구조, 키워드 빈도를 확인하고 최종 발행합니다.

