# Designer Color Studio v2 - 개발 계획서

> 선정 기능: 3. Tint/Shade 생성기 + 5. 잠금 & 랜덤 + 9. 디자인 시스템 Export + 10. 접근성 리포트
> 워크플로우: 영감 탐색 -> 시스템화 -> 검증 -> 개발자 전달

## 1. 앱 컨셉
단일 페이지에서 모든 기능이 연결되는 "미니 디자인 시스템 빌더"를 목표로 한다. 탭 분할 없이 하나의 흐름으로 사용.

### 레이아웃 구상
```
[ 상단: 헤더 + 프로젝트 이름 입력 ]

[ 메인 영역 - 5개 컬러 카드 ]
| [🔒 #7C3AED] [ #EC4899 ] [🔒 #F59E0B] [ #10B981 ] [ #111827 ] |
Space바 누르면 잠금 해제된 색만 랜덤 (Coolors 방식)
각 카드 아래에 50~900 Tint/Shade 바 펼쳐짐

[ 중간: 2단 분할 ]
왼쪽: 접근성 리포트 매트릭스 - 5x5 조합 대비 점수 표, Fail이면 빨간 점
오른쪽: 선택된 컬러 상세 - HEX/RGB/HSL + Color Blind 시뮬레이션 썸네일

[ 하단: Export Dock - 항상 고정된 바 ]
> [ JSON ] [ CSS Variables ] [ Tailwind ] [ ASE ] [ Figma ]
```

### 핵심 상태 관리 (Streamlit session_state)
- `palette`: [{"hex": "#...", "locked": bool, "name": "primary"}] 5개 배열
- `shades`: 각 hex에서 생성된 10단계 tint/shade
- `contrast_matrix`: 5x5 대비 비율 계산 결과

## 2. 기술 스택 & 라이브러리
- **Core**: streamlit
- **색상 로직**: colorsys (내장) + colormath (정확한 LAB 변환)
- **랜덤 팔레트 로직**: Coolors 알고리즘 참고
  - H는 20~40도씩 이동, S/L은 50~80% 사이로 제한
- **Export**: json, asepfile (ASE 생성용)
- **접근성**: WCAG 공식 luminance 공식 직접 구현
- **부가 컴포넌트**: streamlit-keyup (Spacebar 이벤트), streamlit-sortables (드래그)

## 3. 개발 로드맵 (4단계)

### Phase 1 - 코어 엔진 (1일차)
- [ ] 잠금 & 랜덤 팔레트 완성
- [ ] Tint/Shade 생성 함수: hex -> 50~900 10단계
- [ ] White/Black과 mix하는 방식 (디자인 시스템 표준)

### Phase 2 - 검증 레이어 (2일차)
- [ ] 접근성 리포트 매트릭스: 5개 색상 간 25개 조합 contrast ratio 계산
- [ ] 시각화: st.dataframe 배경색 스타일링, 4.5 미만은 ❌ 표시
- [ ] AA(4.5:1), AAA(7:1) 기준 필터

### Phase 3 - Export 시스템 (3일차)
- [ ] Export Dock UI 구현 (하단 고정)
- [ ] 5가지 포맷 템플릿
  - tokens.json: Style Dictionary 규격
  - tailwind.config.js: colors: { primary: { 50:..., 500:... } }
  - CSS Variables: :root { --primary-500: #... }
  - ASE: Illustrator/Photoshop용
  - Figma Variables: JSON

### Phase 4 - 폴리싱 (4일차)
- [ ] 드래그로 순서 변경
- [ ] 프로젝트 저장/불러오기 (local JSON)
- [ ] 키보드 단축키 안내 툴팁
- [ ] 배포 (Streamlit Cloud)

## 4. 최종 폴더 구조
```
designer_tools/
├── app.py                 # 메인 UI, 상태관리, 레이아웃
├── core/
│   ├── palette.py         # 잠금/랜덤, 하모니 생성 로직
│   ├── shades.py          # Tint/Shade 50-900 생성
│   ├── contrast.py        # WCAG 대비 계산 & 매트릭스
│   └── exporters.py       # 5가지 포맷으로 변환
├── components/
│   ├── color_card.py      # 잠금 버튼 있는 컬러 카드
│   └── matrix.py          # 접근성 매트릭스 테이블
├── requirements.txt
├── design.md              # 본 계획서
└── README.md
```

## 5. 성공 기준
- Space바로 1초 안에 새로운 팔레트 탐색 가능
- 하나의 베이스 컬러로 10단계 시스템 자동 완성
- 25개 조합의 접근성 리포트를 한눈에 확인
- 클릭 한 번으로 개발자에게 전달 가능한 코드 Export
