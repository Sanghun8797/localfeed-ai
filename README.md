# LocalFeed AI - 동네 기반 개인화 피드 추천 시스템

## 1. 프로젝트 개요

LocalFeed AI는 당근마켓과 같은 지역 기반 서비스의 홈 피드를 가정하여 만든 개인화 추천 시스템입니다.

사용자 행동 로그, 게시글 정보, 사용자 선호 카테고리, 선호 동네, 가격대 정보를 활용하여 사용자별로 다른 추천 피드를 제공합니다.

이 프로젝트는 단순 인기글 추천에서 시작해 콘텐츠 기반 추천, 사용자 행동 기반 개인화 추천, 하이브리드 추천 모델까지 단계적으로 구현했습니다.

## 2. 문제 정의

지역 기반 서비스에서는 모든 사용자에게 동일한 인기글을 보여주는 방식만으로는 충분하지 않습니다.

사용자마다 관심 있는 카테고리, 선호하는 동네, 가격대, 반응한 게시글이 다르기 때문입니다.

따라서 이 프로젝트에서는 다음 문제를 해결하고자 했습니다.

- 사용자별 관심 카테고리를 반영한 추천
- 사용자별 선호 동네를 반영한 추천
- 가격대 선호를 반영한 추천
- 인기글과 최신성을 함께 고려한 추천
- 특정 카테고리에 추천이 과도하게 몰리지 않도록 다양성 반영

## 3. 사용 데이터

실제 서비스 데이터는 개인정보와 약관 문제로 사용할 수 없기 때문에, 추천 시스템 실험을 위한 가상 데이터를 직접 생성했습니다.

생성한 데이터는 다음과 같습니다.

### posts.csv

중고거래 게시글 데이터입니다.

주요 컬럼:

- post_id
- title
- description
- category
- price
- dong
- latitude
- longitude
- created_at
- view_count
- like_count
- chat_count

### interactions.csv

사용자 행동 로그 데이터입니다.

주요 컬럼:

- user_id
- post_id
- action_type
- interest_score
- timestamp

행동 유형:

- view
- click
- like
- chat
- hide

### user_preferences.csv

사용자별 선호 정보 데이터입니다.

주요 컬럼:

- user_id
- preferred_category_1
- preferred_category_2
- preferred_dong
- min_price
- max_price

## 4. 추천 시스템 구성

이 프로젝트는 여러 추천 방식을 단계적으로 구현했습니다.

### 4.1 인기글 기반 추천

파일: `src/baseline_recommender.py`

조회수, 찜 수, 채팅 수, 최신성을 기반으로 인기 점수를 계산합니다.

```text
popularity_score =
view_count * 0.3
+ like_count * 2.0
+ chat_count * 3.0
+ recency_score * 100
```


### 4.2 콘텐츠 기반 추천

파일: `src/content_recommender.py`

게시글의 제목, 설명, 카테고리, 동네 정보를 하나의 텍스트로 결합한 뒤 TF-IDF 벡터화를 적용했습니다.

이후 코사인 유사도를 활용해 특정 게시글과 비슷한 게시글을 추천합니다.



### 4.3 사용자 행동 기반 개인화 추천

파일: `src/personalized_recommender.py`

사용자 행동 로그에 행동별 가중치를 부여했습니다.

```text
view  = 1
click = 2
like  = 4
chat  = 5
hide  = -3
```

사용자별 카테고리 선호도와 동네 선호도를 계산하고, 사용자가 이미 본 게시글은 추천 후보에서 제외했습니다.

이를 통해 모든 사용자에게 같은 게시글을 보여주는 방식이 아니라, 사용자별 행동 이력에 따라 다른 추천 결과를 제공합니다.

### 4.4 하이브리드 추천

파일: `src/hybrid_recommender.py`

최종 추천 모델입니다.

다음 요소를 결합해 사용자별 추천 점수를 계산했습니다.

- 행동 기반 카테고리 선호도
- 행동 기반 동네 선호도
- 사용자 프로필 기반 선호 카테고리
- 사용자 프로필 기반 선호 동네
- 가격대 적합도
- 게시글 인기도
- 최신성
- 다양성 re-ranking

```text
hybrid_score =
category_score * 0.25
+ dong_score * 0.15
+ profile_category_score * 0.20
+ profile_dong_score * 0.10
+ price_match_score * 0.10
+ popularity_score * 0.15
+ recency_score_scaled * 0.05
```



## 5. 평가 지표

파일: `src/evaluate.py`

추천 모델 평가를 위해 다음 지표를 사용했습니다.

- Precision@K
- Recall@K
- NDCG@K

`like`, `chat` 행동을 긍정 행동으로 간주하고, 추천 결과가 긍정 행동 게시글을 얼마나 잘 맞히는지 평가했습니다.

### 평가 지표 의미

Precision@K는 추천한 K개 게시글 중 실제 긍정 행동 게시글이 얼마나 포함되었는지를 나타냅니다.

Recall@K는 사용자가 실제로 긍정 행동한 게시글 중 추천 결과에 얼마나 포함되었는지를 나타냅니다.

NDCG@K는 정답 게시글이 추천 순위 상단에 위치할수록 높은 점수를 주는 지표입니다.

## 6. 개선 전후 비교

파일: `src/compare_evaluation.py`

`evaluation_result_before.csv`와 `evaluation_result_after.csv`를 비교하여 추천 모델 개선 전후의 평균 평가 지표 변화를 확인했습니다.

비교 대상 지표:

- precision_at_k
- recall_at_k
- ndcg_at_k

## 7. FastAPI 서버

파일: `app/main.py`

추천 모델을 API 형태로 제공하기 위해 FastAPI 서버를 구현했습니다.

### 실행 방법

```bash
cd /d D:\SanghunKim\localfeed-ai
uvicorn app.main:app --reload
```



서버 실행 후 접속 주소:

```text
http://127.0.0.1:8000
```

API 문서:

```text
http://127.0.0.1:8000/docs
```

## 8. API 목록

### 서버 상태 확인

```text
GET /
```

### 게시글 목록 조회

```text
GET /posts
```

예시:

```text
http://127.0.0.1:8000/posts?limit=5
```

### 사용자 목록 조회

```text
GET /users
```

예시:

```text
http://127.0.0.1:8000/users
```

### 사용자 선호 정보 조회

```text
GET /user-preferences/{user_id}
```

예시:

```text
http://127.0.0.1:8000/user-preferences/user_1
```

### 하이브리드 추천 조회

```text
GET /recommend/hybrid/{user_id}
```

예시:

```text
http://127.0.0.1:8000/recommend/hybrid/user_1?top_n=5
```

## 9. 프로젝트 구조

```text
localfeed-ai/
├── app/
│   ├── __init__.py
│   └── main.py
│
├── data/
│   ├── posts.csv
│   ├── interactions.csv
│   ├── user_preferences.csv
│   ├── baseline_recommend_result.csv
│   ├── hybrid_recommend_result.csv
│   ├── evaluation_result.csv
│   └── evaluation_comparison.csv
│
├── src/
│   ├── generate_data.py
│   ├── generate_data_v1.py
│   ├── check_data.py
│   ├── baseline_recommender.py
│   ├── content_recommender.py
│   ├── personalized_recommender.py
│   ├── hybrid_recommender.py
│   ├── evaluate.py
│   └── compare_evaluation.py
│
└── README.md
```

## 10. 사용 기술

- Python
- Pandas
- scikit-learn
- FastAPI
- Uvicorn
- TF-IDF
- Cosine Similarity
- Recommendation System
- REST API

## 11. 실행 순서

### 1. 데이터 생성

```bash
python src/generate_data.py
```

### 2. 데이터 확인

```bash
python src/check_data.py
```

### 3. 인기글 추천

```bash
python src/baseline_recommender.py
```

### 4. 콘텐츠 기반 추천

```bash
python src/content_recommender.py
```

### 5. 개인화 추천

```bash
python src/personalized_recommender.py
```

### 6. 하이브리드 추천

```bash
python src/hybrid_recommender.py
```

### 7. 평가

```bash
python src/evaluate.py
```

### 8. FastAPI 서버 실행

```bash
uvicorn app.main:app --reload
```

## 12. 프로젝트에서 배운 점

이 프로젝트를 통해 추천 시스템 개발의 전체 흐름을 경험했습니다.

- 추천 문제 정의
- 가상 데이터 설계
- 사용자 행동 로그 생성
- Baseline 모델 구현
- 콘텐츠 기반 추천 구현
- 사용자 행동 기반 개인화 추천 구현
- 하이브리드 추천 모델 구현
- 추천 모델 평가
- FastAPI API 서버화

## 13. 한계점 및 개선 방향

현재 프로젝트는 실제 서비스 데이터가 아닌 가상 데이터를 기반으로 합니다.

향후 개선 방향은 다음과 같습니다.

- 실제 공개 데이터셋 기반 실험
- Train/Test 시간 분리 기반 평가 방식 적용
- Sentence-BERT 기반 게시글 임베딩 적용
- Vector DB 기반 유사 게시글 검색
- 추천 결과 카드형 웹 UI 구현
- Docker 기반 실행 환경 구성
- Render 또는 클라우드 배포
