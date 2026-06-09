from fastapi import FastAPI
import pandas as pd
import os
import psycopg2
import sys
from dotenv import load_dotenv
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


# -----------------------------
# 1. 경로 설정
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SRC_DIR = os.path.join(BASE_DIR, "src")
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")

sys.path.append(SRC_DIR)

# .env 파일 불러오기
load_dotenv(os.path.join(BASE_DIR, ".env"))


from hybrid_recommender import recommend_hybrid_for_user, recommend_hybrid_by_input
from pytorch_recommender import recommend_torch_for_user


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
# 3. PostgreSQL 연결 함수
# -----------------------------
def get_postgres_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


# -----------------------------
# 4. FastAPI 앱 생성
# -----------------------------
app = FastAPI(
    title="LocalFeed AI Recommendation API",
    description="사용자 행동 로그와 게시글 정보를 활용한 동네 기반 개인화 피드 추천 API",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# -----------------------------
# 5. 기본 웹 화면
# -----------------------------
@app.get("/")
def read_root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


# -----------------------------
# 6. CSV 기반 게시글 목록 조회 API
# -----------------------------
@app.get("/posts")
def get_posts(limit: int = 20):
    result = posts_df.head(limit)

    return {
        "source": "csv",
        "count": len(result),
        "posts": result.to_dict(orient="records")
    }


# -----------------------------
# 7. 사용자 목록 조회 API
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
# 8. 사용자 선호 정보 조회 API
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
# 9. 하이브리드 추천 API
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
# 10. 외부 입력 기반 추천 API
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


# -----------------------------
# 11. PyTorch 관심 확률 기반 추천 API
# -----------------------------
@app.get("/recommend/torch/{user_id}")
def get_torch_recommendations(user_id: str, top_n: int = 10):
    result = recommend_torch_for_user(
        user_id=user_id,
        top_n=top_n
    )

    if result.empty:
        return {
            "user_id": user_id,
            "message": "PyTorch 추천 결과가 없습니다.",
            "recommendations": []
        }

    return {
        "user_id": user_id,
        "top_n": top_n,
        "model": "PyTorch interest probability model",
        "recommendations": result.to_dict(orient="records")
    }


# -----------------------------
# 12. CSV 기반 게시글 상세 조회 API
# -----------------------------
@app.get("/posts/{post_id}")
def get_post_detail(post_id: int):
    post = posts_df[posts_df["post_id"] == post_id]

    if post.empty:
        return {
            "error": f"{post_id}번 게시글을 찾을 수 없습니다."
        }

    return post.iloc[0].to_dict()


# -----------------------------
# 13. PostgreSQL 게시글 목록 조회 API
# -----------------------------
@app.get("/pg/posts")
def get_pg_posts(limit: int = 20):
    conn = get_postgres_connection()

    query = """
        SELECT
            post_id,
            title,
            category,
            price,
            dong,
            created_at,
            view_count,
            like_count,
            chat_count
        FROM posts
        ORDER BY created_at DESC
        LIMIT %s;
    """

    with conn.cursor() as cur:
        cur.execute(query, (limit,))
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()

    conn.close()

    posts = [dict(zip(columns, row)) for row in rows]

    return {
        "source": "postgresql",
        "count": len(posts),
        "posts": posts
    }


# -----------------------------
# 14. PostgreSQL 게시글 상세 조회 API
# -----------------------------
@app.get("/pg/posts/{post_id}")
def get_pg_post_detail(post_id: int):
    conn = get_postgres_connection()

    query = """
        SELECT
            post_id,
            title,
            description,
            category,
            price,
            dong,
            latitude,
            longitude,
            created_at,
            view_count,
            like_count,
            chat_count
        FROM posts
        WHERE post_id = %s;
    """

    with conn.cursor() as cur:
        cur.execute(query, (post_id,))
        row = cur.fetchone()

        if row is None:
            conn.close()
            return {
                "error": f"{post_id}번 게시글을 찾을 수 없습니다."
            }

        columns = [desc[0] for desc in cur.description]

    conn.close()

    return dict(zip(columns, row))


# -----------------------------
# 15. PostgreSQL 조건 검색 API
# -----------------------------
@app.get("/pg/search")
def search_pg_posts(
    category1: str,
    category2: str,
    dong: str,
    min_price: int = 0,
    max_price: int = 10000000,
    limit: int = 20
):
    conn = get_postgres_connection()

    query = """
        SELECT
            post_id,
            title,
            category,
            price,
            dong,
            created_at,
            view_count,
            like_count,
            chat_count
        FROM posts
        WHERE category IN (%s, %s)
          AND dong = %s
          AND price BETWEEN %s AND %s
        ORDER BY
            like_count DESC,
            chat_count DESC,
            view_count DESC,
            created_at DESC
        LIMIT %s;
    """

    with conn.cursor() as cur:
        cur.execute(
            query,
            (category1, category2, dong, min_price, max_price, limit)
        )
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()

    conn.close()

    posts = [dict(zip(columns, row)) for row in rows]

    return {
        "source": "postgresql",
        "count": len(posts),
        "posts": posts
    }