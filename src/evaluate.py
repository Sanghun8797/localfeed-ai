import pandas as pd
import os
import math

from hybrid_recommender import recommend_hybrid_for_user


# -----------------------------
# 1. 프로젝트 경로 설정
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

INTERACTIONS_PATH = os.path.join(DATA_DIR, "interactions.csv")


# -----------------------------
# 2. 행동 로그 데이터 불러오기
# -----------------------------
interactions_df = pd.read_csv(INTERACTIONS_PATH)


# -----------------------------
# 3. 정답 데이터 생성
# like, chat을 긍정 행동으로 간주
# -----------------------------
positive_actions = ["like", "chat"]

positive_logs = interactions_df[
    interactions_df["action_type"].isin(positive_actions)
]


# -----------------------------
# 4. Precision@K
# -----------------------------
def precision_at_k(recommended_post_ids, actual_post_ids, k=10):
    recommended_k = recommended_post_ids[:k]

    if len(recommended_k) == 0:
        return 0

    hit_count = len(set(recommended_k) & set(actual_post_ids))

    return hit_count / k


# -----------------------------
# 5. Recall@K
# -----------------------------
def recall_at_k(recommended_post_ids, actual_post_ids, k=10):
    recommended_k = recommended_post_ids[:k]

    if len(actual_post_ids) == 0:
        return 0

    hit_count = len(set(recommended_k) & set(actual_post_ids))

    return hit_count / len(actual_post_ids)


# -----------------------------
# 6. NDCG@K
# -----------------------------
def ndcg_at_k(recommended_post_ids, actual_post_ids, k=10):
    recommended_k = recommended_post_ids[:k]

    dcg = 0

    for i, post_id in enumerate(recommended_k):
        if post_id in actual_post_ids:
            dcg += 1 / math.log2(i + 2)

    ideal_hit_count = min(len(actual_post_ids), k)

    idcg = 0

    for i in range(ideal_hit_count):
        idcg += 1 / math.log2(i + 2)

    if idcg == 0:
        return 0

    return dcg / idcg


# -----------------------------
# 7. 특정 사용자 평가 함수
# -----------------------------
def evaluate_user(user_id, k=10):
    actual_post_ids = positive_logs[
        positive_logs["user_id"] == user_id
    ]["post_id"].tolist()

    if len(actual_post_ids) == 0:
        return None

    recommended_df = recommend_hybrid_for_user(user_id, top_n=k)

    if recommended_df.empty:
        return None

    recommended_post_ids = recommended_df["post_id"].tolist()

    precision = precision_at_k(recommended_post_ids, actual_post_ids, k)
    recall = recall_at_k(recommended_post_ids, actual_post_ids, k)
    ndcg = ndcg_at_k(recommended_post_ids, actual_post_ids, k)

    return {
        "user_id": user_id,
        "precision_at_k": precision,
        "recall_at_k": recall,
        "ndcg_at_k": ndcg,
        "actual_positive_count": len(actual_post_ids)
    }


# -----------------------------
# 8. 전체 사용자 평가
# -----------------------------
def evaluate_all_users(k=10):
    user_ids = positive_logs["user_id"].unique()

    results = []

    for user_id in user_ids:
        result = evaluate_user(user_id, k)

        if result is not None:
            results.append(result)

    results_df = pd.DataFrame(results)

    return results_df


# -----------------------------
# 9. 실행 테스트
# -----------------------------
if __name__ == "__main__":
    k = 10

    results_df = evaluate_all_users(k=k)

    print(f"\nHybrid 추천 모델 평가 결과 @ {k}")
    print(results_df.head(10).to_string(index=False))

    print("\n평균 평가 지표")
    print("Precision@K:", results_df["precision_at_k"].mean())
    print("Recall@K:", results_df["recall_at_k"].mean())
    print("NDCG@K:", results_df["ndcg_at_k"].mean())

    results_df.to_csv(
        os.path.join(DATA_DIR, "evaluation_result.csv"),
        index=False,
        encoding="utf-8-sig"
    )

    print("\n평가 결과 CSV 저장 완료")
    print("저장 위치:", os.path.join(DATA_DIR, "evaluation_result.csv"))