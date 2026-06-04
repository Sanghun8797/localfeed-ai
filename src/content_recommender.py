import pandas as pd
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity








BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


POSTS_PATH = os.path.join(DATA_DIR, "posts.csv")









posts_df = pd.read_csv(POSTS_PATH)









posts_df["text"] = (
    posts_df["title"].fillna("") + " "
    + posts_df["description"].fillna("") + " "
    + posts_df["category"].fillna("") + " "
    + posts_df["dong"].fillna("")
)









vectorizer = TfidfVectorizer()

tfidf_matrix = vectorizer.fit_transform(posts_df["text"])










content_similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)










def recommend_similar_posts(post_id, top_n=10):
    target_index_list = posts_df.index[posts_df["post_id"] == post_id].tolist()
    
    if len(target_index_list) == 0:
        print(f"post_id {post_id}에 해당하는 게시글이 없습니다.")
        return pd.DataFrame()
    
    target_index = target_index_list[0]
    
    
    similarity_scores = list(enumerate(content_similarity[target_index]))
    
    
    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
        
    )
    
    similarity_scores = [
        item for item in similarity_scores
        if item[0] != target_index
    ]
    
    top_items = similarity_scores[:top_n]
    
    
    recommended_indices = [item[0] for item in top_items]
    recommended_scores = [item[1] for item in top_items]
    
    
    recommended_posts = posts_df.iloc[recommended_indices].copy()
    recommended_posts["similarity_score"] = recommended_scores
    
    selected_columns = [
        "post_id",
        "title",
        "category",
        "price",
        "dong",
        "similarity_score"
        
    
        
    ]
    
    return recommended_posts[selected_columns]
















if __name__ == "__main__":
    target_post_id = 1
    
    target_post = posts_df[posts_df["post_id"] == target_post_id]
    
    print("\n기준 게시글")
    print(target_post[["post_id", "title", "category", "price", "dong"]].to_string(index=False))
    
    result = recommend_similar_posts(post_id=target_post_id, top_n=10)
    
    print("\n콘텐츠 기반 유사 게시글추천 TOP 10")
    print(result.to_string(index=False))






