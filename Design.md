# Chroma Studio Pro - 개발 계획서

> 무드보드 이미지에서 팔레트를 뽑고, 잠금으로 다듬고, 실제 UI와 색맹 관점에서 검증한 뒤, 바로 Figma로 넘기는 디자이너 전용 스튜디오

## 1. 프로젝트 개요

- **프로젝트명:** Chroma Studio Pro (가안)
- **목표:** 단순 색 추출을 넘어, 실무 핸드오프까지 가능한 올인원 색상 스튜디오 구축
- **핵심 4대 기능:** 이미지 잠금 추출 + 라이브 UI 목업 + 색맹 시뮬레이터 + Figma Tokens 내보내기

### 핵심 사용자 시나리오
1. 클라이언트 레퍼런스 이미지 2~3장 업로드
2. 마음에 드는 키 컬러 1개 잠금(Lock)
3. 나머지 색상을 재생성하며 톤 탐색
4. 랜딩페이지/대시보드에 어떻게 보이는지 라이브 목업으로 확인
5. 색맹 모드로 문제 없는지 체크
6. Figma Tokens JSON으로 내보내기 → Figma에 붙여넣기 끝

---

## 2. 기능별 상세 기획

### 기능 A: 이미지 잠금 추출 (Image Lock Extraction)
- **동작 방식:**
  - 이미지 업로드 → K-Means 클러스터링으로 5색 추출
  - 각 색상 카드에 자물쇠 아이콘 제공
  - 잠긴 색상은 고정, 잠금 해제된 색상만 재생성 버튼으로 다시 추출
- **상태 관리:** `palette = [{hex: "#6C5CE7", locked: False}, ...]`
- **UX 포인트:**
  - 드래그 앤 드롭으로 팔레트 순서 변경 지원 (순서가 Primary/Secondary 역할을 함)
  - 추출된 색상 외에 유사색/보색 변형 제안

### 기능 B: 라이브 UI 목업 (Live UI Mockup)
- **동작 방식:**
  - 현재 팔레트를 변수로 받아 3가지 목업에 실시간 적용
  - Type 1: SaaS 대시보드 (사이드바, 차트, 버튼)
  - Type 2: 이커머스 상품 카드 리스트
  - Type 3: 랜딩페이지 Hero 섹션
- **로직:**
  - 자동 매핑 규칙: [0]=Primary, [1]=Background, [2]=Accent, [3]=Text, [4]=Muted
  - 사용자가 매핑을 직접 변경할 수 있는 매핑 에디터 제공
- **UX 포인트:**
  - 목업 위에 마우스 호버 시 어떤 토큰이 쓰였는지 툴팁 표시
  - 라이트/다크 모드 토글로 팔레트 활용도 확인

### 기능 C: 색맹 시뮬레이터 (Color Blindness Simulator)
- **동작 방식:**
  - 토글 4개: 원본 / 적녹색맹(Deuteranopia) / 적색맹(Protanopia) / 청황색맹(Tritanopia)
  - RGB 변환 행렬을 이용해 필터 적용
- **검증 로직:**
  - 시뮬레이터 활성화 시 WCAG 대비율 재계산
  - 대비가 깨지는 조합에 경고 배지 표시 (예: "Accent와 Background 구분이 어려움")
- **UX 포인트:**
  - 팔레트 카드와 목업 전체에 필터 동시 적용

### 기능 D: Figma Tokens 내보내기 (Export)
- **지원 포맷:**
  1. Figma Tokens (JSON) - Figma Tokens 플러그인 표준
  2. CSS Variables
  3. Tailwind Config
  4. Adobe ASE (추후 확장)
- **표준 JSON 구조 예시:**
  ```json
  {
    "global": {
      "primary": { "value": "#6C5CE7", "type": "color" },
      "accent": { "value": "#00CEC9", "type": "color" }
    }
  }
  ```
- **UX 포인트:**
  - 내보내기 전 토큰 이름 직접 수정 가능 (primary → brand-purple)
  - 원클릭 복사 및 .json 파일 다운로드

---

## 3. 기술 스택 & 아키텍처

- **Framework:** Streamlit
- **Image Processing:** Pillow, numpy
- **Color Extraction:** scikit-learn (KMeans)
- **State Management:** `st.session_state`
- **Mockup Rendering:** `st.components.v1.html` + HTML/CSS 템플릿

### 화면 레이아웃 (3단 구조)
- **Left Sidebar:** 이미지 업로드, 색상 개수 슬라이더, 색맹 시뮬레이터 토글, 내보내기 버튼
- **Center Area:** 팔레트 편집 (잠금, 드래그, 재생성, HEX 코드)
- **Right / Bottom Area:** 라이브 UI 목업 프리뷰 3종 + 경고 메시지

---

## 4. 개발 로드맵 (5일 플랜)

### Day 1 - 코어 추출 모듈
- [ ] K-Means 기반 색상 추출 구현
- [ ] `session_state`로 잠금 상태 유지 로직
- [ ] 재생성(Regenerate) 알고리즘

### Day 2 - 목업 시스템
- [ ] 3가지 목업용 HTML/CSS 템플릿 제작
- [ ] 팔레트 변수 주입 시스템
- [ ] 자동 매핑 + 수동 매핑 에디터

### Day 3 - 검증 시스템
- [ ] 색맹 변환 행렬 적용 (Deuteranopia, Protanopia, Tritanopia)
- [ ] WCAG 대비율 체크 로직 통합
- [ ] 경고 시스템 UI

### Day 4 - 내보내기 & 폴리싱
- [ ] Figma Tokens JSON 생성기
- [ ] 토큰 네이밍 에디터
- [ ] 전체 앱 디자인 시스템 통일 (폰트, 간격, 라운드)

### Day 5 - 테스트 & 배포
- [ ] 엣지 케이스 테스트 (풍경, 인물, UI 스크린샷 등 다양한 이미지)
- [ ] Streamlit Community Cloud 배포
- [ ] 사용성 피드백 수집용 폼 추가

---

## 5. 성공 지표 (KPI)

- **탐색성:** 사용자가 팔레트를 재생성하는 평균 횟수
- **실무성:** Figma 내보내기 클릭률
- **접근성:** 색맹 모드 활성화 후 팔레트를 수정하는 비율
- **체류 시간:** 목업 프리뷰에서 머무는 시간

---

## 6. 추후 확장 아이디어

- Coolors / Colormind API 연동 (AI 팔레트 추천)
- 웹사이트 URL 입력 시 자동 컬러 크롤링
- 브랜드 가이드 PDF 자동 생성
- 팀 공유 링크 생성 (팔레트 스토리 포함)

*Generated: 2026-05-13 / Chroma Studio Pro Planning*
