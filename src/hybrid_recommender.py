import pandas as pd
import os
from datetime import datetime


# -----------------------------
# 1. pandas 출력 옵션 설정
# -----------------------------
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)
pd.set_option("display.max_colwidth", 25)


# -----------------------------
# 2. 프로젝트 경로 설정
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

POSTS_PATH = os.path.join(DATA_DIR, "posts.csv")
INTERACTIONS_PATH = os.path.join(DATA_DIR, "interactions.csv")
USER_PREF_PATH = os.path.join(DATA_DIR, "user_preferences.csv")


# -----------------------------
# 3. 데이터 불러오기
# -----------------------------
posts_df = pd.read_csv(POSTS_PATH)
interactions_df = pd.read_csv(INTERACTIONS_PATH)
user_pref_df = pd.read_csv(USER_PREF_PATH)

posts_df["created_at"] = pd.to_datetime(posts_df["created_at"])


# -----------------------------
# 4. 행동별 가중치 설정
# -----------------------------
ACTION_WEIGHTS = {
    "view": 1,
    "click": 2,
    "like": 4,
    "chat": 5,
    "hide": -3
}

interactions_df["action_weight"] = interactions_df["action_type"].map(ACTION_WEIGHTS)


# -----------------------------
# 5. 행동 로그와 게시글 데이터 결합
# -----------------------------
user_logs = interactions_df.merge(
    posts_df,
    on="post_id",
    how="left"
)


# -----------------------------
# 6. min-max 정규화 함수
# -----------------------------
def min_max_scale(series):
    min_value = series.min()
    max_value = series.max()

    if max_value == min_value:
        return series * 0

    return (series - min_value) / (max_value - min_value)


# -----------------------------
# 7. 사용자 행동 기반 선호도 계산 함수
# -----------------------------
def get_user_category_preference(user_id):
    user_data = user_logs[user_logs["user_id"] == user_id]

    if user_data.empty:
        return pd.Series(dtype=float)

    category_scores = user_data.groupby("category")["action_weight"].sum()

    return category_scores


def get_user_dong_preference(user_id):
    user_data = user_logs[user_logs["user_id"] == user_id]

    if user_data.empty:
        return pd.Series(dtype=float)

    dong_scores = user_data.groupby("dong")["action_weight"].sum()

    return dong_scores


# -----------------------------
# 8. 사용자 기본 선호 정보 가져오기
# -----------------------------
def get_user_profile(user_id):
    user_profile = user_pref_df[user_pref_df["user_id"] == user_id]

    if user_profile.empty:
        return None

    return user_profile.iloc[0]


# -----------------------------
# 9. 가격대 선호 점수 계산 함수
# -----------------------------
def calculate_price_match_score(price, min_price, max_price):
    if min_price <= price <= max_price:
        return 1.0

    if price < min_price:
        distance = min_price - price
    else:
        distance = price - max_price

    # 가격대에서 멀어질수록 점수 감소
    score = 1 / (1 + distance / 100000)

    return score


# -----------------------------
# 10. 최신성 점수 추가 함수
# -----------------------------
def add_recency_score(df):
    now = datetime.now()

    df["days_since_created"] = (now - df["created_at"]).dt.days
    df["recency_score"] = 1 / (df["days_since_created"] + 1)

    return df


# -----------------------------
# 11. 다양성 re-ranking 함수
# -----------------------------
def diversity_rerank(recommended_df, top_n=10, max_same_category=3):
    final_items = []
    category_count = {}

    for _, row in recommended_df.iterrows():
        category = row["category"]

        current_count = category_count.get(category, 0)

        if current_count < max_same_category:
            final_items.append(row)
            category_count[category] = current_count + 1

        if len(final_items) >= top_n:
            break

    # 다양성 제한 때문에 top_n을 못 채우면 남은 게시글로 채움
    if len(final_items) < top_n:
        selected_post_ids = [item["post_id"] for item in final_items]

        remaining_items = recommended_df[
            ~recommended_df["post_id"].isin(selected_post_ids)
        ]

        for _, row in remaining_items.iterrows():
            final_items.append(row)

            if len(final_items) >= top_n:
                break

    return pd.DataFrame(final_items)


# -----------------------------
# 12. 개선된 하이브리드 추천 함수
# -----------------------------
def recommend_hybrid_for_user(user_id, top_n=10, apply_diversity=True):
    user_data = user_logs[user_logs["user_id"] == user_id]

    if user_data.empty:
        print(f"{user_id}의 행동 로그가 없습니다.")
        return pd.DataFrame()

    user_profile = get_user_profile(user_id)

    if user_profile is None:
        print(f"{user_id}의 사용자 선호 정보가 없습니다.")
        return pd.DataFrame()

    # 사용자가 이미 본 게시글 제외
    viewed_post_ids = user_data["post_id"].unique()

    candidate_posts = posts_df[
        ~posts_df["post_id"].isin(viewed_post_ids)
    ].copy()

    # 사용자 행동 기반 선호도
    category_pref = get_user_category_preference(user_id)
    dong_pref = get_user_dong_preference(user_id)

    candidate_posts["category_score_raw"] = candidate_posts["category"].map(category_pref).fillna(0)
    candidate_posts["dong_score_raw"] = candidate_posts["dong"].map(dong_pref).fillna(0)

    # 사용자 프로필 기반 선호도
    candidate_posts["profile_category_score"] = candidate_posts["category"].apply(
        lambda category: 1.0
        if category == user_profile["preferred_category_1"]
        else 0.8
        if category == user_profile["preferred_category_2"]
        else 0.0
    )

    candidate_posts["profile_dong_score"] = candidate_posts["dong"].apply(
        lambda dong: 1.0 if dong == user_profile["preferred_dong"] else 0.0
    )

    candidate_posts["price_match_score"] = candidate_posts["price"].apply(
        lambda price: calculate_price_match_score(
            price,
            user_profile["min_price"],
            user_profile["max_price"]
        )
    )

    # 인기도 점수
    candidate_posts["popularity_score_raw"] = (
        candidate_posts["view_count"] * 0.3
        + candidate_posts["like_count"] * 2.0
        + candidate_posts["chat_count"] * 3.0
    )

    # 최신성 점수
    candidate_posts = add_recency_score(candidate_posts)

    # 점수 정규화
    candidate_posts["category_score"] = min_max_scale(candidate_posts["category_score_raw"])
    candidate_posts["dong_score"] = min_max_scale(candidate_posts["dong_score_raw"])
    candidate_posts["popularity_score"] = min_max_scale(candidate_posts["popularity_score_raw"])
    candidate_posts["recency_score_scaled"] = min_max_scale(candidate_posts["recency_score"])

    # 최종 하이브리드 점수
    candidate_posts["hybrid_score"] = (
        candidate_posts["category_score"] * 0.25
        + candidate_posts["dong_score"] * 0.15
        + candidate_posts["profile_category_score"] * 0.20
        + candidate_posts["profile_dong_score"] * 0.10
        + candidate_posts["price_match_score"] * 0.10
        + candidate_posts["popularity_score"] * 0.15
        + candidate_posts["recency_score_scaled"] * 0.05
    )

    ranked_posts = candidate_posts.sort_values(
        by="hybrid_score",
        ascending=False
    )

    if apply_diversity:
        recommended = diversity_rerank(
            ranked_posts,
            top_n=top_n,
            max_same_category=3
        )
    else:
        recommended = ranked_posts.head(top_n)

    selected_columns = [
        "post_id",
        "title",
        "category",
        "price",
        "dong",
        "category_score",
        "dong_score",
        "profile_category_score",
        "profile_dong_score",
        "price_match_score",
        "popularity_score",
        "recency_score_scaled",
        "hybrid_score"
    ]

    recommended = recommended.drop_duplicates(subset=["post_id"])

    return recommended[selected_columns].head(top_n)






# -----------------------------
# 13. 외부 입력 기반 하이브리드 추천 함수
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
    candidate_posts = posts_df[
        posts_df["category"].isin([preferred_category_1, preferred_category_2])
    ].copy()
    
    if candidate_posts.empty:
        candidate_posts = posts_df.copy()
    
    candidate_posts = candidate_posts[
        (candidate_posts["price"] >= min_price)
        & (candidate_posts["price"] <= max_price)
    ].copy()

    # 입력값 숫자 변환
    min_price = int(min_price)
    max_price = int(max_price)

    # 사용자 입력 기반 카테고리 점수
    candidate_posts["profile_category_score"] = candidate_posts["category"].apply(
        lambda category: 1.0
        if category == preferred_category_1
        else 0.8
        if category == preferred_category_2
        else 0.0
    )

    # 사용자 입력 기반 동네 점수
    candidate_posts["profile_dong_score"] = candidate_posts["dong"].apply(
        lambda dong: 1.0 if dong == preferred_dong else 0.0
    )

    # 사용자 입력 기반 가격대 적합도
    candidate_posts["price_match_score"] = candidate_posts["price"].apply(
        lambda price: calculate_price_match_score(
            price,
            min_price,
            max_price
        )
    )

    # 인기도 점수
    candidate_posts["popularity_score_raw"] = (
        candidate_posts["view_count"] * 0.3
        + candidate_posts["like_count"] * 2.0
        + candidate_posts["chat_count"] * 3.0
    )

    # 최신성 점수
    candidate_posts = add_recency_score(candidate_posts)

    # 점수 정규화
    candidate_posts["popularity_score"] = min_max_scale(candidate_posts["popularity_score_raw"])
    candidate_posts["recency_score_scaled"] = min_max_scale(candidate_posts["recency_score"])

    # 외부 입력 기반 최종 하이브리드 점수
    candidate_posts["hybrid_score"] = (
        candidate_posts["profile_category_score"] * 0.35
        + candidate_posts["profile_dong_score"] * 0.20
        + candidate_posts["price_match_score"] * 0.20
        + candidate_posts["popularity_score"] * 0.15
        + candidate_posts["recency_score_scaled"] * 0.10
    )

    ranked_posts = candidate_posts.sort_values(
        by="hybrid_score",
        ascending=False
    )

    if apply_diversity:
        recommended = diversity_rerank(
            ranked_posts,
            top_n=top_n,
            max_same_category=3
        )
    else:
        recommended = ranked_posts.head(top_n)

    selected_columns = [
        "post_id",
        "title",
        "category",
        "price",
        "dong",
        "profile_category_score",
        "profile_dong_score",
        "price_match_score",
        "popularity_score",
        "recency_score_scaled",
        "hybrid_score"
    ]

    return recommended[selected_columns]


# -----------------------------
# 14. 실행 테스트
# -----------------------------
if __name__ == "__main__":
    target_user_id = "user_1"

    print("\n하이브리드 추천 대상 사용자:", target_user_id)

    user_profile = get_user_profile(target_user_id)

    print("\n사용자 기본 선호 정보")
    print(user_profile.to_string())

    result = recommend_hybrid_for_user(
        target_user_id,
        top_n=10,
        apply_diversity=True
    )

    print(f"\n{target_user_id} 개선된 하이브리드 추천 결과 TOP 10")
    print(result.to_string(index=False))

    result.to_csv(
        os.path.join(DATA_DIR, "hybrid_recommend_result.csv"),
        index=False,
        encoding="utf-8-sig"
    )

    print("\n개선된 하이브리드 추천 결과 CSV 저장 완료")
    print("저장 위치:", os.path.join(DATA_DIR, "hybrid_recommend_result.csv"))
    
    
    
    print("\n외부 입력 기반 추천 테스트")

    custom_result = recommend_hybrid_by_input(
    preferred_category_1="디지털기기",
    preferred_category_2="게임/취미",
    preferred_dong="신림동",
    min_price=50000,
    max_price=200000,
    top_n=10,
    apply_diversity=True
    )

    print(custom_result.to_string(index=False))