import os
import pandas as pd
import numpy as np


# -----------------------------
# 1. 경로 설정
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

POSTS_PATH = os.path.join(DATA_DIR, "posts.csv")
USER_PREF_PATH = os.path.join(DATA_DIR, "user_preferences.csv")


# -----------------------------
# 2. 데이터 불러오기
# -----------------------------
posts_df = pd.read_csv(POSTS_PATH)
user_pref_df = pd.read_csv(USER_PREF_PATH)

posts_df["created_at"] = pd.to_datetime(posts_df["created_at"])


# -----------------------------
# 3. 공통 유틸 함수
# -----------------------------
def min_max_scale(series):
    min_value = series.min()
    max_value = series.max()

    if max_value == min_value:
        return pd.Series([0.0] * len(series), index=series.index)

    return (series - min_value) / (max_value - min_value)


def calculate_recency_score(created_at_series):
    latest_date = created_at_series.max()
    days_diff = (latest_date - created_at_series).dt.days

    max_days = days_diff.max()

    if max_days == 0:
        return pd.Series([1.0] * len(created_at_series), index=created_at_series.index)

    return 1 - (days_diff / max_days)


def calculate_price_score(price_series, min_price, max_price):
    if max_price <= min_price:
        return pd.Series([1.0] * len(price_series), index=price_series.index)

    mid_price = (min_price + max_price) / 2
    price_range = max_price - min_price

    score = 1 - (abs(price_series - mid_price) / price_range)
    score = score.clip(lower=0, upper=1)

    return score


def apply_diversity_filter(result_df, top_n):
    """
    동일 게시글이 중복 추천되는 것을 방지하고,
    우선순위 점수 기준으로 상위 결과를 반환한다.
    """
    result_df = result_df.drop_duplicates(subset=["post_id"])
    return result_df.head(top_n)


def get_selected_columns(result_df):
    selected_columns = [
        "post_id",
        "title",
        "description",
        "category",
        "price",
        "dong",
        "created_at",
        "view_count",
        "like_count",
        "chat_count",
        "hybrid_score"
    ]

    available_columns = [
        column for column in selected_columns
        if column in result_df.columns
    ]

    return result_df[available_columns]


# -----------------------------
# 4. 공통 추천 점수 계산 함수
# -----------------------------
def calculate_hybrid_score(
    candidate_posts,
    preferred_category_1,
    preferred_category_2,
    preferred_dong,
    min_price,
    max_price
):
    candidate_posts = candidate_posts.copy()

    # 카테고리 점수
    candidate_posts["category_score"] = candidate_posts["category"].apply(
        lambda category: 1.0
        if category in [preferred_category_1, preferred_category_2]
        else 0.0
    )

    # 동네 점수
    candidate_posts["dong_score"] = candidate_posts["dong"].apply(
        lambda dong: 1.0 if dong == preferred_dong else 0.0
    )

    # 가격 점수
    candidate_posts["price_score"] = calculate_price_score(
        candidate_posts["price"],
        min_price,
        max_price
    )

    # 인기도 점수
    candidate_posts["view_score"] = min_max_scale(candidate_posts["view_count"])
    candidate_posts["like_score"] = min_max_scale(candidate_posts["like_count"])
    candidate_posts["chat_score"] = min_max_scale(candidate_posts["chat_count"])

    candidate_posts["popularity_score"] = (
        candidate_posts["view_score"] * 0.3
        + candidate_posts["like_score"] * 0.4
        + candidate_posts["chat_score"] * 0.3
    )

    # 최신성 점수
    candidate_posts["recency_score"] = calculate_recency_score(
        candidate_posts["created_at"]
    )

    # 최종 하이브리드 점수
    candidate_posts["hybrid_score"] = (
        candidate_posts["category_score"] * 0.35
        + candidate_posts["dong_score"] * 0.20
        + candidate_posts["price_score"] * 0.20
        + candidate_posts["popularity_score"] * 0.15
        + candidate_posts["recency_score"] * 0.10
    )

    return candidate_posts


# -----------------------------
# 5. 사용자 ID 기반 하이브리드 추천
# -----------------------------
def recommend_hybrid_for_user(
    user_id,
    top_n=10,
    apply_diversity=True
):
    user_pref = user_pref_df[user_pref_df["user_id"] == user_id]

    if user_pref.empty:
        return pd.DataFrame()

    user_pref = user_pref.iloc[0]

    preferred_category_1 = user_pref["preferred_category_1"]
    preferred_category_2 = user_pref["preferred_category_2"]
    preferred_dong = user_pref["preferred_dong"]
    min_price = int(user_pref["min_price"])
    max_price = int(user_pref["max_price"])

    # 선택한 카테고리만 후보로 사용
    candidate_posts = posts_df[
        posts_df["category"].isin([
            preferred_category_1,
            preferred_category_2
        ])
    ].copy()

    # 선택한 가격 범위 안의 게시글만 후보로 사용
    candidate_posts = candidate_posts[
        (candidate_posts["price"] >= min_price)
        & (candidate_posts["price"] <= max_price)
    ].copy()

    if candidate_posts.empty:
        return pd.DataFrame()

    candidate_posts = calculate_hybrid_score(
        candidate_posts=candidate_posts,
        preferred_category_1=preferred_category_1,
        preferred_category_2=preferred_category_2,
        preferred_dong=preferred_dong,
        min_price=min_price,
        max_price=max_price
    )

    result = candidate_posts.sort_values(
        by="hybrid_score",
        ascending=False
    )

    if apply_diversity:
        result = apply_diversity_filter(result, top_n)
    else:
        result = result.drop_duplicates(subset=["post_id"]).head(top_n)

    return get_selected_columns(result)


# -----------------------------
# 6. 외부 입력 기반 하이브리드 추천
# -----------------------------
def recommend_hybrid_by_input(
    preferred_category_1,
    preferred_category_2,
    preferred_dong,
    min_price,
    max_price,
    top_n=10,
    apply_diversity=True
):
    min_price = int(min_price)
    max_price = int(max_price)

    # 선택한 카테고리만 후보로 사용
    candidate_posts = posts_df[
        posts_df["category"].isin([
            preferred_category_1,
            preferred_category_2
        ])
    ].copy()

    # 선택한 가격 범위 안의 게시글만 후보로 사용
    candidate_posts = candidate_posts[
        (candidate_posts["price"] >= min_price)
        & (candidate_posts["price"] <= max_price)
    ].copy()

    if candidate_posts.empty:
        return pd.DataFrame()

    candidate_posts = calculate_hybrid_score(
        candidate_posts=candidate_posts,
        preferred_category_1=preferred_category_1,
        preferred_category_2=preferred_category_2,
        preferred_dong=preferred_dong,
        min_price=min_price,
        max_price=max_price
    )

    result = candidate_posts.sort_values(
        by="hybrid_score",
        ascending=False
    )

    if apply_diversity:
        result = apply_diversity_filter(result, top_n)
    else:
        result = result.drop_duplicates(subset=["post_id"]).head(top_n)

    return get_selected_columns(result)


# -----------------------------
# 7. 단독 실행 테스트
# -----------------------------
if __name__ == "__main__":
    test_result = recommend_hybrid_by_input(
        preferred_category_1="유아용품",
        preferred_category_2="반려동물용품",
        preferred_dong="신림동",
        min_price=0,
        max_price=500000,
        top_n=10,
        apply_diversity=True
    )

    print(test_result)