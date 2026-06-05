import os
import pickle
from datetime import datetime

import pandas as pd
import torch
import torch.nn as nn


# -----------------------------
# 1. 프로젝트 경로 설정
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")

POSTS_PATH = os.path.join(DATA_DIR, "posts.csv")
INTERACTIONS_PATH = os.path.join(DATA_DIR, "interactions.csv")

MODEL_PATH = os.path.join(MODEL_DIR, "torch_recommender.pt")
PREPROCESS_PATH = os.path.join(MODEL_DIR, "torch_preprocess.pkl")


# -----------------------------
# 2. 데이터 불러오기
# -----------------------------
posts_df = pd.read_csv(POSTS_PATH)
interactions_df = pd.read_csv(INTERACTIONS_PATH)

posts_df["created_at"] = pd.to_datetime(posts_df["created_at"])


# -----------------------------
# 3. PyTorch 모델 구조 정의
# train_torch_model.py와 같은 구조여야 함
# -----------------------------
class TorchRecommendationModel(nn.Module):
    def __init__(
        self,
        num_users,
        num_posts,
        num_categories,
        num_dongs,
        embedding_dim=16,
        numeric_dim=5
    ):
        super().__init__()

        self.user_embedding = nn.Embedding(num_users, embedding_dim)
        self.post_embedding = nn.Embedding(num_posts, embedding_dim)
        self.category_embedding = nn.Embedding(num_categories, embedding_dim)
        self.dong_embedding = nn.Embedding(num_dongs, embedding_dim)

        input_dim = embedding_dim * 4 + numeric_dim

        self.mlp = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.2),

            nn.Linear(64, 32),
            nn.ReLU(),

            nn.Linear(32, 1)
        )

    def forward(self, user_idx, post_idx, category_idx, dong_idx, numeric):
        user_emb = self.user_embedding(user_idx)
        post_emb = self.post_embedding(post_idx)
        category_emb = self.category_embedding(category_idx)
        dong_emb = self.dong_embedding(dong_idx)

        x = torch.cat(
            [
                user_emb,
                post_emb,
                category_emb,
                dong_emb,
                numeric
            ],
            dim=1
        )

        logits = self.mlp(x).squeeze(1)

        return logits


# -----------------------------
# 4. 모델과 전처리 객체 불러오기
# -----------------------------
def load_torch_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"모델 파일이 없습니다. 먼저 src/train_torch_model.py를 실행하세요: {MODEL_PATH}"
        )

    if not os.path.exists(PREPROCESS_PATH):
        raise FileNotFoundError(
            f"전처리 파일이 없습니다. 먼저 src/train_torch_model.py를 실행하세요: {PREPROCESS_PATH}"
        )

    checkpoint = torch.load(MODEL_PATH, map_location="cpu")

    model = TorchRecommendationModel(
        num_users=checkpoint["num_users"],
        num_posts=checkpoint["num_posts"],
        num_categories=checkpoint["num_categories"],
        num_dongs=checkpoint["num_dongs"],
        embedding_dim=checkpoint["embedding_dim"],
        numeric_dim=checkpoint["numeric_dim"]
    )

    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    with open(PREPROCESS_PATH, "rb") as f:
        preprocess_objects = pickle.load(f)

    return model, preprocess_objects


model, preprocess_objects = load_torch_model()


# -----------------------------
# 5. 추천 후보 데이터 생성
# -----------------------------
def build_candidate_posts_for_user(user_id):
    candidate_posts = posts_df.copy()

    # 사용자가 이미 본 게시글은 제외
    viewed_post_ids = interactions_df[
        interactions_df["user_id"] == user_id
    ]["post_id"].unique()

    candidate_posts = candidate_posts[
        ~candidate_posts["post_id"].isin(viewed_post_ids)
    ].copy()

    return candidate_posts


# -----------------------------
# 6. 모델 입력 데이터 생성
# -----------------------------
def prepare_model_input(user_id, candidate_posts):
    user_encoder = preprocess_objects["user_encoder"]
    post_encoder = preprocess_objects["post_encoder"]
    category_encoder = preprocess_objects["category_encoder"]
    dong_encoder = preprocess_objects["dong_encoder"]
    scaler = preprocess_objects["scaler"]
    numeric_features = preprocess_objects["numeric_features"]

    if user_id not in user_encoder.classes_:
        raise ValueError(f"학습 데이터에 없는 사용자입니다: {user_id}")

    input_df = candidate_posts.copy()

    # 학습 때와 같은 숫자 feature 생성
    now = datetime.now()
    input_df["days_since_created"] = (now - input_df["created_at"]).dt.days

    # 학습 때 본 post_id, category, dong만 사용
    input_df = input_df[
        input_df["post_id"].astype(str).isin(post_encoder.classes_)
        & input_df["category"].astype(str).isin(category_encoder.classes_)
        & input_df["dong"].astype(str).isin(dong_encoder.classes_)
    ].copy()

    if input_df.empty:
        return input_df, None

    input_df["user_idx"] = user_encoder.transform([user_id])[0]
    input_df["post_idx"] = post_encoder.transform(input_df["post_id"].astype(str))
    input_df["category_idx"] = category_encoder.transform(input_df["category"].astype(str))
    input_df["dong_idx"] = dong_encoder.transform(input_df["dong"].astype(str))

    # 화면/API 출력용 원본 데이터는 유지하고,
    # 모델 입력용 숫자 데이터만 별도로 정규화
    scaled_numeric = scaler.transform(input_df[numeric_features])

    model_input = {
        "user_idx": torch.tensor(input_df["user_idx"].values, dtype=torch.long),
        "post_idx": torch.tensor(input_df["post_idx"].values, dtype=torch.long),
        "category_idx": torch.tensor(input_df["category_idx"].values, dtype=torch.long),
        "dong_idx": torch.tensor(input_df["dong_idx"].values, dtype=torch.long),
        "numeric": torch.tensor(scaled_numeric, dtype=torch.float32)
    }

    return input_df, model_input

# -----------------------------
# 7. PyTorch 기반 추천 함수
# -----------------------------
def recommend_torch_for_user(user_id, top_n=10):
    candidate_posts = build_candidate_posts_for_user(user_id)

    if candidate_posts.empty:
        print(f"{user_id}에게 추천할 후보 게시글이 없습니다.")
        return pd.DataFrame()

    input_df, model_input = prepare_model_input(user_id, candidate_posts)

    if input_df.empty or model_input is None:
        print("모델 입력으로 사용할 수 있는 후보 게시글이 없습니다.")
        return pd.DataFrame()

    with torch.no_grad():
        logits = model(
            model_input["user_idx"],
            model_input["post_idx"],
            model_input["category_idx"],
            model_input["dong_idx"],
            model_input["numeric"]
        )

        probabilities = torch.sigmoid(logits).numpy()

    result_df = input_df.copy()
    result_df["interest_probability"] = probabilities

    result_df = result_df.sort_values(
        by="interest_probability",
        ascending=False
    )

    selected_columns = [
        "post_id",
        "title",
        "category",
        "price",
        "dong",
        "view_count",
        "like_count",
        "chat_count",
        "interest_probability"
    ]

    result_df = result_df.drop_duplicates(subset=["post_id"])

    return result_df[selected_columns].head(top_n)


# -----------------------------
# 8. 실행 테스트
# -----------------------------
if __name__ == "__main__":
    target_user_id = "user_1"

    print("\nPyTorch 추천 대상 사용자:", target_user_id)

    result = recommend_torch_for_user(
        user_id=target_user_id,
        top_n=10
    )

    print(f"\n{target_user_id} PyTorch 관심 확률 기반 추천 결과 TOP 10")
    print(result.to_string(index=False))

    result.to_csv(
        os.path.join(DATA_DIR, "torch_recommend_result.csv"),
        index=False,
        encoding="utf-8-sig"
    )

    print("\nPyTorch 추천 결과 CSV 저장 완료")
    print("저장 위치:", os.path.join(DATA_DIR, "torch_recommend_result.csv"))