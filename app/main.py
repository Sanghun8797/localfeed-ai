from fastapi import FastAPI
import pandas as pd
import os
import sys
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


# -----------------------------
# 1. 경로 설정
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SRC_DIR = os.path.join(BASE_DIR, "src")

sys.path.append(SRC_DIR)

from hybrid_recommender import recommend_hybrid_for_user, recommend_hybrid_by_input


POSTS_PATH = os.path.join(DATA_DIR, "posts.csv")
INTERACTIONS_PATH = os.path.join(DATA_DIR, "interactions.csv")
USER_PREF_PATH = os.path.join(DATA_DIR, "user_preferences.csv")


# -----------------------------
# 2. 데이터 불러오기
# -----------------------------
posts_df = pd.read_csv(POSTS_PATH)
interactions_df = pd.read_csv(INTERACTIONS_PATH)
user_pref_df = pd.read_csv(USER_PREF_PATH)


# -----------------------------
# 3. FastAPI 앱 생성
# -----------------------------
app = FastAPI(
    title="LocalFeed AI Recommendation API",
    description="사용자 행동 로그와 게시글 정보를 활용한 동네 기반 개인화 피드 추천 API",
    version="1.0.0"
    
)

STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# -----------------------------
# 4. 기본 서버 확인 API
# -----------------------------
@app.get("/")
def read_root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


# -----------------------------
# 5. 게시글 목록 조회 API
# -----------------------------
@app.get("/posts")
def get_posts(limit: int = 20):
    result = posts_df.head(limit)

    return {
        "count": len(result),
        "posts": result.to_dict(orient="records")
    }


# -----------------------------
# 6. 사용자 목록 조회 API
# -----------------------------
@app.get("/users")
def get_users():
    user_ids = (
        interactions_df["user_id"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    user_ids = sorted(
        user_ids,
        key=lambda user_id: int(user_id.split("_")[1])
    )

    return {
        "user_count": len(user_ids),
        "users": user_ids
    }


# -----------------------------
# 7. 사용자 선호 정보 조회 API
# -----------------------------
@app.get("/user-preferences/{user_id}")
def get_user_preferences(user_id: str):
    user_pref = user_pref_df[user_pref_df["user_id"] == user_id]

    if user_pref.empty:
        return {
            "error": f"{user_id}에 해당하는 사용자 선호 정보가 없습니다."
        }

    return user_pref.iloc[0].to_dict()


# -----------------------------
# 8. 하이브리드 추천 API
# -----------------------------
@app.get("/recommend/hybrid/{user_id}")
def get_hybrid_recommendations(user_id: str, top_n: int = 10):
    result = recommend_hybrid_for_user(
        user_id=user_id,
        top_n=top_n,
        apply_diversity=True
    )

    if result.empty:
        return {
            "user_id": user_id,
            "message": "추천 결과가 없습니다.",
            "recommendations": []
        }

    return {
        "user_id": user_id,
        "top_n": top_n,
        "recommendations": result.to_dict(orient="records")
    }


# -----------------------------
# 9. 외부 입력 기반 추천 API
# -----------------------------
@app.get("/recommend/custom")
def get_custom_recommendations(
    category1: str,
    category2: str,
    dong: str,
    min_price: int,
    max_price: int,
    top_n: int = 10
):
    result = recommend_hybrid_by_input(
        preferred_category_1=category1,
        preferred_category_2=category2,
        preferred_dong=dong,
        min_price=min_price,
        max_price=max_price,
        top_n=top_n,
        apply_diversity=True
    )

    if result.empty:
        return {
            "message": "추천 결과가 없습니다.",
            "recommendations": []
        }

    return {
        "input": {
            "category1": category1,
            "category2": category2,
            "dong": dong,
            "min_price": min_price,
            "max_price": max_price,
            "top_n": top_n
        },
        "recommendations": result.to_dict(orient="records")
    }