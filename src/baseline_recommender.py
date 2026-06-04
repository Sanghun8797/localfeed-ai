import pandas as pd
from datetime import datetime
import os
















BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


POSTS_PATH = os.path.join(DATA_DIR, "posts.csv")









posts_df = pd.read_csv(POSTS_PATH)







posts_df["created_at"] = pd.to_datetime(posts_df["created_at"])










now = datetime.now()

posts_df["days_since_created"] = (now - posts_df["created_at"]).dt.days

posts_df["recency_score"] = 1 / (posts_df["days_since_created"] + 1)












posts_df["popularity_score"] = (
    posts_df["view_count"] * 0.3
    + posts_df["like_count"] * 2.0
    + posts_df["chat_count"] * 3.0
    + posts_df["recency_score"] * 100
    )











def recommend_popular_posts(top_n=10):
    recommended = posts_df.sort_values(
        by="popularity_score",
        ascending=False
    ).head(top_n)

    selected_columns = [
        "post_id",
        "title",
        "category",
        "price",
        "dong",
        "view_count",
        "like_count",
        "chat_count",
        "recency_score",
        "popularity_score"
    ]

    return recommended[selected_columns]








if __name__ == "__main__":
    result = recommend_popular_posts(top_n=10)
    
    print("인기글 기반 추천 결과 TOP 10")
    print(result.to_string(index=False))


