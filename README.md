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
├── scripts/                    # [스케줄러 & 업로더] 원클릭 실행 및 자동 업로드 도구
│   ├── daily-naver-blog.sh     # caffeinate 절전 차단 & 00시 통합 배치 실행 래퍼
│   ├── write-post.sh           # 블로그 수시(온디맨드) 글작성 원클릭 도구
│   ├── upload-naver.sh         # 🟢 네이버 블로그 Playwright 자동 등록 스크립트
│   ├── upload-tistory.sh       # 🟠 티스토리 블로그 Playwright 자동 등록 스크립트
│   ├── upload-wordpress.sh     # 🔵 워드프레스 블로그 Playwright 자동 등록 스크립트
│   ├── install-launchd.sh      # launchd LaunchAgent 적재 (매일 00:00 실행)
│   ├── uninstall-launchd.sh    # launchd 등록 해제 스크립트
│   └── launchd/                # com.user.daily-naver-blog.plist
└── tools/                      # [도구] 배치 엔진 및 브라우저 세션 도구
    ├── daily_naver_batch.py    # 네이버 실시간 트렌드 수집 & 일별 포스팅 자동 생성 배치
    ├── daily_tistory_batch.py  # 티스토리 Google Trends 상승 검색어 평가 & 글 생성 배치
    ├── daily_wordpress_batch.py# 워드프레스 코너스톤 SEO 글 생성 배치
    ├── upload_naver_playwright.py      # 네이버 스마트에디터 ONE 서식복사 자동 업로더
    ├── upload_tistory_playwright.py    # 티스토리 에디터 서식복사 자동 업로더
    ├── upload_wordpress_playwright.py  # 워드프레스 구텐베르크 네이티브 블록 자동 업로더
    ├── setup_browser_login.py  # 네이버 1회 브라우저 로그인 세션 생성기
    ├── setup_tistory_login.py  # 티스토리 1회 브라우저 로그인 세션 생성기
    ├── setup_wordpress_login.py# 워드프레스 1회 브라우저 로그인 세션 생성기
    ├── write_ondemand.py       # 온디맨드(수시) 포스팅 생성 엔진
    ├── generate_html.py        # docs/index.html 가이드 뷰어 갱신 빌더
    └── blog_helper.py          # 글자수, 키워드 밀도, SEO 구조 분석 CLI 도구
```

---

## ⚡ 플랫폼별 일일 자동 발행 목표 기준

| 플랫폼 | 주중 (월~금) | 주말 (토/일) | 핵심 전략 및 알고리즘 타겟 |
| :--- | :---: | :---: | :--- |
| **🟢 네이버 블로그** | **15개** | **30개** | 실시간 검색어 Top 3 의무 반영 + 스마트블록/시니어 헬스케어·연금 집중 유입 |
| **🟠 티스토리** | **15개** | **15개** | Google Trends 급상승 검색어 기반 Q&A 검색형 정보성 글 (주중/주말 균등 공급) |
| **🔵 워드프레스** | **15개** | **30개** | E-E-A-T 기반 장기 코너스톤 SEO 심층 가이드 & 구글 자연 검색 자산화 |

---

## 🛠️ 배치 수동 실행 및 Playwright 자동 등록 명령어

### 1. 배치 수동 실행 명령어 (원고 생성 및 대시보드 갱신)

터미널에서 언제든지 수동으로 당일자 포스팅을 생성하고 대시보드를 갱신할 수 있습니다.

```bash
# 1) 3대 플랫폼 전체 통합 배치 즉시 실행 (네이버 15/30, 티스토리 15, WP 15/30)
python3 tools/daily_naver_batch.py --force
# 또는 원클릭 스크립트 실행
./scripts/write-post.sh --batch

# 2) 플랫폼별 개별 수동 배치 실행
python3 tools/daily_naver_batch.py --naver-only --force   # 네이버만 실행 (주중 15 / 주말 30)
python3 tools/daily_tistory_batch.py --force             # 티스토리만 실행 (매일 15편)
python3 tools/daily_wordpress_batch.py --force           # 워드프레스만 실행 (주중 15 / 주말 30)

# 3) 수시(온디맨드) 단건 또는 N건 추가 작성
./scripts/write-post.sh                                  # 대화형 대시보드 메뉴 실행
./scripts/write-post.sh -p naver                         # 네이버 1편 추가
./scripts/write-post.sh -p tistory -k "기초연금 신청"     # 티스토리 특정 키워드 1편 작성
./scripts/write-post.sh -p wordpress                     # 워드프레스 1편 추가
./scripts/write-post.sh -p all -c 2                      # 3대 플랫폼에 2편씩 동시 추가
```

---

### 2. 포스팅 등록 명령어 & 네이버 계정 보호 가이드

Playwright 브라우저 자동화 엔진을 통해 로컬 뷰어의 **에디터 서식복사 기능**을 호출하여, 마크다운 기호(`**`, `---` 등) 없이 **초록/파랑 요약 콜아웃 박스, 포인트 바 소제목(▍), 비교표(Table), 볼드 서식**이 완벽히 유지된 상태로 등록됩니다.

> ⚠️ **네이버 계정 보호 중요 공지 (보호조치 원천 차단)**:  
> 네이버 블로그는 단시간 대량 등록(도배) 시 어뷰징 시스템에 의해 '계정 보호조치(아이디 잠금)'가 발동합니다.  
> 따라서 **네이버는 [방안 A] 1-Click 서식 복사 수동 등록을 1순위로 권장**하며, 자동화 시에는 **[방안 C] 안티디텍트 안전 모드(1회 1편 제한 / 예약발행)**로만 실행됩니다.

---

#### 🛡️ [방안 A · 강력 추천] 네이버 1-Click 서식 복사 수동 등록 (보호조치 0% 원천 차단)
평소 쓰시는 일반 브라우저(사파리/크롬)로 로컬 뷰어와 네이버 글쓰기 화면을 동시에 띄워 **단 30초 만에 100% 안전하게 등록**합니다.
```bash
# 🟢 네이버 오늘자 1번 포스트 뷰어 & 스마트에디터 ONE 글쓰기 즉시 오픈
./scripts/copy-naver.sh

# 🟢 2번 포스트 열람 및 복사
./scripts/copy-naver.sh 2
```
> **등록 순서**: 뷰어 상단 [초록 서식 복사] 클릭 ➔ 네이버 글쓰기 창 제목 입력 ➔ 본문에 `Cmd+V` ➔ [발행] 클릭 끝!

---

#### 🌟 [방안 C] 3대 플랫폼 원클릭 통합 자동 발행 (All-in-One)
```bash
# 🚀 3대 플랫폼 통합 발행 (네이버 1편 안전제한 + 티스토리 15편 + WP 15/30편)
./scripts/upload-all.sh

# 🛡️ [추천] 네이버는 수동으로 하고 티스토리·워드프레스만 전자동 발행할 때
./scripts/upload-all.sh --skip-naver

# ⏰ 네이버 등록 시 예약 발행(Schedule) 모드 적용
./scripts/upload-all.sh --reserve

# 🔐 3대 플랫폼 로그인 세션 상태 일괄 점검
./scripts/upload-all.sh --login

# 🧪 3대 플랫폼 1번 글 단건 시험 발행 (정상 동작 테스트)
./scripts/upload-all.sh --test
```

---

#### 📌 네이버 블로그 개별 안전 등록 명령어 (방안 C)
네이버는 실제 브라우저 화면 표시(Headless 해제), 안티디텍트 스크립트 주입, 인간 타이핑 지연 모방이 기본 적용됩니다.
```bash
# 🟢 네이버 상위 1편 안전 정식 발행 (1회 1편 하드 리밋)
./scripts/upload-naver.sh

# ⏰ 즉시 발행 대신 '예약 발행'으로 등록
./scripts/upload-naver.sh --reserve

# 📝 2번 포스트만 단건 발행
./scripts/upload-naver.sh --single 2

# 💾 임시저장(Draft) 모드로 등록
./scripts/upload-naver.sh --draft
```

---

#### 📌 플랫폼별 개별 실행 명령어 (필요 시)

##### 1단계: 최초 1회 브라우저 로그인 세션 생성 (영구 저장)
```bash
./scripts/upload-naver.sh --login        # 네이버 1회 브라우저 로그인 (state.json 저장)
./scripts/upload-tistory.sh --login      # 티스토리 1회 카카오 계정 로그인
./scripts/upload-wordpress.sh --login    # 워드프레스 1회 계정 로그인
```
> 세션 파일(`.browser_session/*/state.json`)이 한 번 생성되면 이후에는 로그인 창 없이 백그라운드에서 바로 자동 글쓰기 및 발행이 진행됩니다.

##### 2단계: 오늘 작성된 글 전체 즉시 정식 발행 (기본 모드: PUBLISH)
```bash
# 🟢 네이버 블로그 전체 정식 발행 (주중 15편 / 주말 30편)
./scripts/upload-naver.sh --publish

# 🟠 티스토리 블로그 전체 정식 발행 (매일 15편)
./scripts/upload-tistory.sh --publish

# 🔵 워드프레스 블로그 전체 정식 발행 (주중 15편 / 주말 30편)
./scripts/upload-wordpress.sh --publish
```

##### 3단계: 단건 시험 발행 및 기타 옵션
```bash
# 1번 포스트만 1편 시험 정식 발행
./scripts/upload-naver.sh --test
./scripts/upload-tistory.sh --test
./scripts/upload-wordpress.sh --test

# 정식 발행이 아닌 임시저장(Draft)으로 등록할 때
./scripts/upload-naver.sh --draft
./scripts/upload-tistory.sh --draft
./scripts/upload-wordpress.sh --draft
```

---

## 🚀 AI 파트너와 함께 일하는 방법 (AI Native Workflow)

1. **포털 열람 (`open index.html`)**:
   - 브라우저에서 통합 포털을 열어 오늘의 네이버, 티스토리, 워드프레스 포스팅과 실시간 트렌드를 확인합니다.
2. **원클릭 자동 발행**:
   - `./scripts/upload-naver.sh`, `./scripts/upload-tistory.sh`, `./scripts/upload-wordpress.sh` 명령어로 각 플랫폼에 정식 서식으로 즉시 발행합니다.
3. **휴먼 터치 퇴고**:
   - AI가 작성한 글에 나의 실제 경험담, 느낀 점, 사진을 1~2장 추가하여 나만의 특별한 글을 완성합니다.
4. **품질 점검**:
   - `python tools/blog_helper.py draft.md`로 글자수, 소제목 구조, 키워드 빈도를 확인하고 주간 성과를 분석합니다.