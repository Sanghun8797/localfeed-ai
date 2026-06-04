import pandas as pd
import os






BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


POSTS_PATH = os.path.join(DATA_DIR, "posts.csv")
INTERACTIONS_PATH = os.path.join(DATA_DIR, "interactions.csv")









posts_df = pd.read_csv(POSTS_PATH)
interactions_df = pd.read_csv(INTERACTIONS_PATH)







ACTION_WEIGHTS = {
    "view": 1,
    "click": 2,
    "like": 4,
    "chat": 5,
    "hide": -3
}






interactions_df["action_weight"] = interactions_df["action_type"].map(ACTION_WEIGHTS)







user_logs = interactions_df.merge(
    posts_df,
    on="post_id",
    how="left"
)










def get_user_category_preference(user_id):
    user_data = user_logs[user_logs["user_id"] == user_id]
    
    if user_data.empty:
        return pd.Series(dtype=float)
    
    
    category_scores = user_data.groupby("category")["action_weight"].sum()
    
    return category_scores.sort_values(ascending=False)











def get_user_dong_preference(user_id):
    user_data = user_logs[user_logs["user_id"] == user_id]
    
    if user_data.empty:
        return pd.Series(dtype=float)
    
    
    dong_scores = user_data.groupby("dong")["action_weight"].sum()
    
    return dong_scores.sort_values(ascending=False)












def recommend_for_user(user_id, top_n=10):
    user_data = user_logs[user_logs["user_id"] == user_id]
    
    if user_data.empty:
        print(f"{user_id}의 행동 로그가 없습니다. 인기글 추천으로 대체해야 합니다.")
        return pd.DataFrame()
    
    
    
    viewed_post_ids = user_data["post_id"].unique()
    
    
    candidate_posts = posts_df[
        ~posts_df["post_id"].isin(viewed_post_ids)
    ].copy()
    
    
    
    
    category_pref = get_user_category_preference(user_id)
    
    
    
    
    dong_pref = get_user_dong_preference(user_id)
    
    
    
    
    
    candidate_posts["category_score"] = candidate_posts["category"].map(category_pref).fillna(0)
    candidate_posts["dong_score"] = candidate_posts["dong"].map(dong_pref).fillna(0)
    
    
    
    
    
    
    
    candidate_posts["popularity_score"] = (
        candidate_posts["view_count"] * 0.3
        + candidate_posts["like_count"] * 2.0
        + candidate_posts["chat_count"] * 3.0
    )
    
    
    
    
    
    
    
    candidate_posts["personalized_score"] = (
        candidate_posts["category_score"] * 2.0
        + candidate_posts["dong_score"] * 1.5
        + candidate_posts["popularity_score"] * 0.1
    )
    
    
    
    
    
    
    
    
    recommended = candidate_posts.sort_values(
        by="personalized_score",
        ascending=False
    ).head(top_n)
    
    
    selected_columns = [
        "post_id",
        "title",
        "category",
        "price",
        "dong",
        "category_score",
        "dong_score",
        "popularity_score",
        "personalized_score"
    ]
    
    return recommended[selected_columns]























if __name__ == "__name__":
    target_user_id = "user_1"
    
    print("\n사용자 카테고리 선호도")
    print(get_user_category_preference(target_user_id).to_string())
    
    print("\n사용자 동네 선호도")
    print(get_user_dong_preference(target_user_id).to_string())
    
    result = recommend_for_user(target_user_id, top_n=10)
    
    print(f"\n{target_user_id} 개인화 추천 결과 TOP 10")
    print(result.to_string(index=False))
    
    result.to_csv(
        os.path.join(DATA_DIR, "personalized_recommend_result.csv"),
        index=False,
        encoding="utf-8-sig"
        
    )
    
    
    
    
    print("\n개인화 추천 결과 CSV 저장 완료")






















