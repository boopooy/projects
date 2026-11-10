# projects
## 빅데이터프로그래밍응용 수업
[교재 : 누구나 만드는 웹 래피드 프로토타이핑 with AI(서대우교수 저)](https://wikidocs.net/book/19592)   
※ 실습 환경이 Cursor에서 Github Codespace(VS Code)로 대체됨.

### Codespace 실행  
1. **projects** Repository 선택
2. "<> Code" 버튼 - Codespaces 탭 선택
3. "Create codespace on main" 버튼 클릭

### 초기화 단계  
터미널에서 아래 명령 입력  
1. `pip install uv` (이후 uv sync로 세 줄 대체 가능)
2. `uv init` 
3. `uv add streamlit pandas seaborn plotly`   

### streamlit 파일 실행  
`uv run streamlit run geyser.py`

### Google gemini flash 추가 방법
1. Continue 확장 설치
1. aistudio.google.com 에서 API 키 발급 후 복사
1. Continue "Add chat model" 메뉴 클릭
1. Google Genimi를 선택 후 API 키를 붙여 넣기
1. config.yaml 파일에서 Gemini 버전을 2.5에서 현재 지원하는 버전(3 등)으로 수정

### git 충돌날 때

`git pull --rebase origin main`  
`git push origin main`

이후 기본값으로 쓰려면  
`git config --global pull.rebase true`  


### matplotlib, seaborn 차트 한글 사용
쉬운 방법 - koreanize_matplotlib 사용  
아래 모듈을 설치한다.
> setuptools, koreanize-matplotlib  
소스 파일 상단에 `koreanize_matplotlib`를 import 한다. 이 모듈은 NanumGothic 폰트를 포함하고 있다.

※ 굳이 다른 글꼴을 사용하고 싶다면 ...  
글꼴 직접 선택하기 - fonts-nanum 설치
터미널에서 아래 명령을 실행한다.
>sudo apt-get install -y fonts-nanum  
>sudo fc-cache -fv  
>rm ~/.cache/matplotlib -rf

코드 내에서 아래 코드를 포함시킨다.  
> import matplotlib.pyplot as plt  
> plt.rc('font', family='NanumGothic')  
> plt.rc('axes', unicode_minus=False)

사용 가능한 글꼴 종류
- NanumBarunGothic
- NanumGothic
- NanumGothicCoding
- NanumMyeongjo
- NanumSquare
- NanumSquare Bold
- NanumSquareRound
- NanumSquareRound Bold
- NanumSquareRound Regular
