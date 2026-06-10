# LocalFeed AI - 지역 기반 중고거래 추천 서비스

지역 기반 중고거래 서비스를 가정하여 사용자가 입력한 선호 조건을 바탕으로 맞춤형 게시글을 추천하는 AI 추천 서비스입니다.

사용자는 이름, 선호 카테고리, 선호 동네, 가격대를 입력할 수 있으며, 시스템은 선택한 카테고리와 가격 범위를 기준으로 후보 게시글을 먼저 필터링한 뒤, 동네 적합도, 가격대 적합도, 인기도, 최신성을 종합해 추천 게시글을 제공합니다.

## 배포 주소

* Web Demo: https://localfeed-ai.onrender.com/
* API Docs: https://localfeed-ai.onrender.com/docs
* GitHub Repository: https://github.com/Sanghun8797/localfeed-ai

## 프로젝트 개요

이 프로젝트는 지역 기반 중고거래 서비스의 피드 추천 문제를 가정하여 구현한 개인 포트폴리오 프로젝트입니다.

실제 서비스 데이터는 개인정보, 위치정보, 저작권, 서비스 약관 문제가 있을 수 있어 사용하지 않았습니다. 대신 실제 중고거래 서비스의 데이터 구조를 참고하여 가상 게시글 데이터, 사용자 선호 정보, 사용자 행동 로그를 직접 생성했습니다.

프로젝트는 데이터 생성, 추천 알고리즘 구현, PyTorch 모델 실험, FastAPI API 서버 개발, 웹 UI 구현, PostgreSQL 연동, Render 배포까지 end-to-end로 구성했습니다.

## 주요 기능

* 사용자 이름 입력 기반 맞춤 추천 화면
* 선호 카테고리 1, 선호 카테고리 2 선택
* 선호 동네 선택
* 최소 가격, 최대 가격 입력
* 추천 개수 선택
* 선택한 선호 카테고리 1, 2에 해당하는 게시글만 추천 후보로 사용
* 입력한 최소 가격과 최대 가격 범위 안의 게시글만 추천 후보로 사용
* 조건 기반 하이브리드 추천 결과 제공
* 추천 점수를 100점 만점으로 환산하여 표시
* 추천 적합도 라벨 제공

  * 매우 높음
  * 높음
  * 보통
  * 낮음
* 추천 결과가 없을 경우 사용자 안내 문구 표시
* 추천 게시글 카드형 UI 제공
* 추천 게시글 클릭 시 상세페이지 이동
* 상세페이지에서 게시글 설명, 가격, 동네, 조회수, 관심 수, 채팅 수 확인
* FastAPI 기반 API 문서 자동 제공
* PostgreSQL 기반 게시글 조회 API 구현
* Render 배포

## 추천 방식

추천 시스템은 사용자가 입력한 선호 조건을 기준으로 후보 게시글을 먼저 필터링한 뒤, 각 게시글에 대해 하이브리드 추천 점수를 계산합니다.

우선 사용자가 선택한 선호 카테고리 1, 선호 카테고리 2에 해당하는 게시글만 추천 후보로 사용합니다. 또한 입력한 최소 가격과 최대 가격 범위 안에 있는 게시글만 추천 후보로 사용합니다.

이후 남은 게시글을 대상으로 다음 요소를 종합하여 추천 점수를 계산합니다.

* 카테고리 적합도
* 동네 적합도
* 가격대 적합도
* 게시글 인기도

  * 조회수
  * 관심 수
  * 채팅 수
* 최신성

내부 추천 점수는 사용자가 이해하기 쉽도록 100점 만점으로 환산하여 화면에 표시했습니다.

예시:

```text
추천 적합도: 높음
추천 점수: 78점 / 100점
```

추천 조건에 맞는 게시글이 없을 경우에는 빈 화면을 보여주는 대신, 조건을 조정해 다시 추천을 받을 수 있도록 안내 문구를 표시합니다.

## 데이터 구성

프로젝트에서 사용하는 데이터는 CSV 기반으로 생성했습니다.

```text
data/
├── posts.csv
├── interactions.csv
└── user_preferences.csv
```

### posts.csv

게시글 데이터입니다.

주요 컬럼:

* post_id
* title
* description
* category
* price
* dong
* latitude
* longitude
* created_at
* view_count
* like_count
* chat_count

### interactions.csv

사용자 행동 로그 데이터입니다.

주요 컬럼:

* user_id
* post_id
* action_type
* interest_score
* timestamp

### user_preferences.csv

샘플 사용자 선호 정보 데이터입니다.

주요 컬럼:

* user_id
* preferred_category_1
* preferred_category_2
* preferred_dong
* min_price
* max_price

## 데이터 생성 방식

`src/generate_data.py`에서 가상 게시글, 사용자 선호 정보, 사용자 행동 로그를 생성합니다.

카테고리별 상품 후보와 상품별 가격 범위를 정의하여 게시글이 보다 현실적인 형태로 생성되도록 구성했습니다.

예를 들어, 생활가전 전체에 하나의 가격 범위를 적용하는 대신 상품별 가격 범위를 따로 설정했습니다.

```python
"헤어드라이기": (5000, 80000)
"로봇청소기": (80000, 500000)
"전자레인지": (20000, 120000)
```

이를 통해 헤어드라이기처럼 비교적 저가인 상품이 비현실적으로 높은 가격으로 생성되는 문제를 줄였습니다.

## PostgreSQL 연동

CSV로 생성한 게시글, 사용자 행동 로그, 사용자 선호 데이터를 PostgreSQL 테이블로 적재하고, FastAPI에서 SQL 기반 조회 API를 제공했습니다.

PostgreSQL 연동은 다음 흐름으로 구현했습니다.

```text
CSV 데이터 생성
→ PostgreSQL 테이블 생성
→ CSV 데이터 적재
→ FastAPI에서 SQL 조회
→ JSON 응답 반환
```

현재 배포된 웹 UI는 CSV 기반 추천 기능을 사용합니다. PostgreSQL API는 로컬 개발 환경에서 DB 연동과 SQL 조회 기능을 검증하기 위해 구현했습니다.

Render 서버에서는 로컬 PC의 PostgreSQL에 직접 접근할 수 없기 때문에, 배포 환경에서 PostgreSQL API까지 동작시키려면 Render PostgreSQL 또는 외부 클라우드 DB 연결이 추가로 필요합니다.

### PostgreSQL 테이블

* posts
* interactions
* user_preferences

### PostgreSQL 기반 API

* `GET /pg/posts` : PostgreSQL 게시글 목록 조회
* `GET /pg/posts/{post_id}` : PostgreSQL 게시글 상세 조회
* `GET /pg/search` : 카테고리, 동네, 가격대 기반 SQL 조건 검색

예시:

```text
GET /pg/posts?limit=10
```

```text
GET /pg/posts/1
```

```text
GET /pg/search?category1=디지털기기&category2=게임/취미&dong=신림동&min_price=0&max_price=200000&limit=10
```

## PyTorch 추천 모델

사용자 행동 로그와 게시글 메타데이터를 기반으로 PyTorch 관심 확률 예측 모델도 구현했습니다.

현재 웹 UI는 외부 사용자가 직접 입력한 선호 조건 기반 추천을 중심으로 구성했으며, PyTorch 추천 API는 모델 실험 및 확장 기능으로 제공합니다.

### PyTorch 기반 API

* `GET /recommend/torch/{user_id}`

## 기술 스택

### Backend

* Python
* FastAPI
* Uvicorn
* Pandas

### Recommendation

* 조건 기반 하이브리드 추천
* 카테고리, 동네, 가격대, 인기도, 최신성 기반 점수 계산
* PyTorch 기반 관심 확률 예측 모델

### Database

* PostgreSQL
* SQL
* psycopg2-binary
* python-dotenv

### Frontend

* HTML
* CSS
* JavaScript

### Deployment

* GitHub
* Render

## 프로젝트 구조

```text
localfeed-ai/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── static/
│       ├── index.html
│       ├── detail.html
│       ├── script.js
│       ├── detail.js
│       ├── style.css
│       └── logoImage.png
├── data/
│   ├── posts.csv
│   ├── interactions.csv
│   └── user_preferences.csv
├── src/
│   ├── __init__.py
│   ├── generate_data.py
│   ├── hybrid_recommender.py
│   ├── train_torch_model.py
│   ├── pytorch_recommender.py
│   └── load_postgres.py
├── models/
│   ├── torch_recommender.pt
│   └── torch_preprocess.pkl
├── requirements.txt
├── .gitignore
└── README.md
```

## 주요 API

### 메인 화면

```text
GET /
```

웹 UI를 반환합니다.

### 게시글 목록 조회

```text
GET /posts
```

CSV 기반 게시글 목록을 조회합니다.

### 게시글 상세 조회

```text
GET /posts/{post_id}
```

CSV 기반 특정 게시글의 상세 정보를 조회합니다.

### 사용자 목록 조회

```text
GET /users
```

샘플 사용자 목록을 조회합니다.

### 사용자 선호 정보 조회

```text
GET /user-preferences/{user_id}
```

샘플 사용자의 선호 정보를 조회합니다.

### 조건 기반 추천

```text
GET /recommend/custom
```

사용자가 입력한 카테고리, 동네, 가격대를 기준으로 추천 결과를 제공합니다.

예시:

```text
/recommend/custom?category1=디지털기기&category2=게임/취미&dong=신림동&min_price=0&max_price=200000&top_n=10
```

### PyTorch 관심 확률 기반 추천

```text
GET /recommend/torch/{user_id}
```

사용자 행동 로그 기반으로 학습한 PyTorch 모델을 통해 게시글 관심 확률을 예측합니다.

### PostgreSQL 게시글 목록 조회

```text
GET /pg/posts
```

PostgreSQL에 저장된 게시글 목록을 SQL로 조회합니다.

### PostgreSQL 게시글 상세 조회

```text
GET /pg/posts/{post_id}
```

PostgreSQL에 저장된 특정 게시글의 상세 정보를 SQL로 조회합니다.

### PostgreSQL 조건 검색

```text
GET /pg/search
```

카테고리, 동네, 가격대를 기준으로 SQL 조건 검색을 수행합니다.

## 실행 방법

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 데이터 생성

```bash
python src/generate_data.py
```

### 3. PyTorch 모델 학습

```bash
python src/train_torch_model.py
```

### 4. PostgreSQL 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 아래 내용을 입력합니다.

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=localfeed_ai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

`.env` 파일에는 DB 비밀번호가 포함되므로 GitHub에 업로드하지 않습니다.

### 5. PostgreSQL 데이터 적재

```bash
python src/load_postgres.py
```

### 6. FastAPI 서버 실행

```bash
uvicorn app.main:app --reload
```

### 7. 접속

```text
http://127.0.0.1:8000
```

API 문서:

```text
http://127.0.0.1:8000/docs
```

## 구현 과정에서 개선한 점

* 샘플 사용자 선택 방식에서 사용자 이름 직접 입력 방식으로 변경
* 카테고리 중복 선택 방지
* 사용자가 선택한 선호 카테고리 1, 2에 해당하는 게시글만 추천되도록 후보군 필터링 강화
* 입력한 최소 가격과 최대 가격 범위 안의 게시글만 추천되도록 가격 조건 필터링 적용
* 조건에 맞는 추천 결과가 없을 경우, 추천 게시글 영역에 사용자 안내 문구를 표시하도록 개선
* 상품별 가격 범위 설정으로 비현실적인 가격 생성 문제 개선
* 추천 점수를 100점 만점으로 환산하여 사용자 이해도 개선
* 추천 카드 클릭 시 상세페이지로 이동하는 서비스 흐름 구현
* 첫 화면에서는 추천 결과 영역을 숨기고, 추천 실행 후 표시되도록 UI 개선
* CSV 기반 데이터 구조에 PostgreSQL 연동 추가
* SQL 기반 게시글 목록 조회, 상세 조회, 조건 검색 API 구현
* GitHub와 Render를 활용한 배포

## 프로젝트 의의

이 프로젝트는 단순 게시글 목록 출력이 아니라, 사용자가 입력한 조건을 바탕으로 추천 결과를 계산하고, 카드형 UI와 상세페이지 흐름까지 구현한 개인화 추천 서비스입니다.

또한 CSV 기반 데이터 생성에서 끝나지 않고 PostgreSQL 테이블 적재와 SQL 조회 API까지 구현하여, 데이터 저장 계층과 API 계층을 분리하는 경험을 포함했습니다.

추천 점수 계산, 데이터 생성, 데이터베이스 연동, API 설계, 웹 UI, 배포까지 end-to-end로 구현했다는 점에서 AI 서비스 개발 포트폴리오로 활용할 수 있습니다.

## 향후 개선 방향

* Render PostgreSQL을 연결하여 배포 환경에서도 PostgreSQL API 동작 지원
* 자연어 기반 추천 챗봇 추가
* 중고거래 안전 가이드 문서를 활용한 RAG 챗봇 확장
* 사용자 행동 로그를 실시간으로 저장하는 기능 추가
* 추천 결과 클릭, 관심, 채팅 행동을 반영한 재추천 기능 고도화
