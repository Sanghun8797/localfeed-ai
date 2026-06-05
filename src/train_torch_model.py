import os
import pickle
import random
from datetime import datetime

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from torch.utils.data import Dataset, DataLoader


# -----------------------------
# 1. 랜덤 시드 고정
# -----------------------------
SEED = 42

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)


# -----------------------------
# 2. 프로젝트 경로 설정
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(MODEL_DIR, exist_ok=True)

POSTS_PATH = os.path.join(DATA_DIR, "posts.csv")
INTERACTIONS_PATH = os.path.join(DATA_DIR, "interactions.csv")

MODEL_PATH = os.path.join(MODEL_DIR, "torch_recommender.pt")
PREPROCESS_PATH = os.path.join(MODEL_DIR, "torch_preprocess.pkl")


# -----------------------------
# 3. 데이터 불러오기
# -----------------------------
posts_df = pd.read_csv(POSTS_PATH)
interactions_df = pd.read_csv(INTERACTIONS_PATH)

posts_df["created_at"] = pd.to_datetime(posts_df["created_at"])


# -----------------------------
# 4. 행동 로그와 게시글 데이터 결합
# -----------------------------
df = interactions_df.merge(
    posts_df,
    on="post_id",
    how="left"
)


# -----------------------------
# 5. 정답 라벨 생성
# -----------------------------
# click, like, chat은 관심 행동으로 보고 1
# view, hide는 비관심 또는 약한 관심으로 보고 0
positive_actions = ["click", "like", "chat"]

df["label"] = df["action_type"].apply(
    lambda action: 1 if action in positive_actions else 0
)


# -----------------------------
# 6. 최신성 관련 숫자 feature 생성
# -----------------------------
now = datetime.now()
df["days_since_created"] = (now - df["created_at"]).dt.days


# -----------------------------
# 7. 범주형 변수 인코딩
# -----------------------------
user_encoder = LabelEncoder()
post_encoder = LabelEncoder()
category_encoder = LabelEncoder()
dong_encoder = LabelEncoder()

df["user_idx"] = user_encoder.fit_transform(df["user_id"].astype(str))
df["post_idx"] = post_encoder.fit_transform(df["post_id"].astype(str))
df["category_idx"] = category_encoder.fit_transform(df["category"].astype(str))
df["dong_idx"] = dong_encoder.fit_transform(df["dong"].astype(str))


# -----------------------------
# 8. 숫자형 feature 정규화
# -----------------------------
numeric_features = [
    "price",
    "view_count",
    "like_count",
    "chat_count",
    "days_since_created"
]

scaler = StandardScaler()
df[numeric_features] = scaler.fit_transform(df[numeric_features])


# -----------------------------
# 9. 학습에 사용할 컬럼 정리
# -----------------------------
feature_columns = [
    "user_idx",
    "post_idx",
    "category_idx",
    "dong_idx",
    "price",
    "view_count",
    "like_count",
    "chat_count",
    "days_since_created"
]

X = df[feature_columns].copy()
y = df["label"].astype(np.float32).values


# -----------------------------
# 10. Train/Test 분리
# -----------------------------
train_df, test_df, train_y, test_y = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=SEED,
    stratify=y
)


# -----------------------------
# 11. PyTorch Dataset 정의
# -----------------------------
class RecommendationDataset(Dataset):
    def __init__(self, features, labels):
        self.user_idx = torch.tensor(features["user_idx"].values, dtype=torch.long)
        self.post_idx = torch.tensor(features["post_idx"].values, dtype=torch.long)
        self.category_idx = torch.tensor(features["category_idx"].values, dtype=torch.long)
        self.dong_idx = torch.tensor(features["dong_idx"].values, dtype=torch.long)

        self.numeric = torch.tensor(
            features[
                [
                    "price",
                    "view_count",
                    "like_count",
                    "chat_count",
                    "days_since_created"
                ]
            ].values,
            dtype=torch.float32
        )

        self.labels = torch.tensor(labels, dtype=torch.float32)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {
            "user_idx": self.user_idx[idx],
            "post_idx": self.post_idx[idx],
            "category_idx": self.category_idx[idx],
            "dong_idx": self.dong_idx[idx],
            "numeric": self.numeric[idx],
            "label": self.labels[idx]
        }


train_dataset = RecommendationDataset(train_df, train_y)
test_dataset = RecommendationDataset(test_df, test_y)

train_loader = DataLoader(
    train_dataset,
    batch_size=64,
    shuffle=True
)

test_loader = DataLoader(
    test_dataset,
    batch_size=64,
    shuffle=False
)


# -----------------------------
# 12. PyTorch 추천 모델 정의
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
# 13. 모델 생성
# -----------------------------
num_users = df["user_idx"].nunique()
num_posts = df["post_idx"].nunique()
num_categories = df["category_idx"].nunique()
num_dongs = df["dong_idx"].nunique()

model = TorchRecommendationModel(
    num_users=num_users,
    num_posts=num_posts,
    num_categories=num_categories,
    num_dongs=num_dongs
)


# -----------------------------
# 14. 학습 설정
# -----------------------------
criterion = nn.BCEWithLogitsLoss()
optimizer = torch.optim.Adam(
    model.parameters(),
    lr=0.001
)

EPOCHS = 30


# -----------------------------
# 15. 평가 함수
# -----------------------------
def evaluate_model(model, data_loader):
    model.eval()

    total_loss = 0
    correct = 0
    total = 0

    with torch.no_grad():
        for batch in data_loader:
            logits = model(
                batch["user_idx"],
                batch["post_idx"],
                batch["category_idx"],
                batch["dong_idx"],
                batch["numeric"]
            )

            loss = criterion(logits, batch["label"])
            total_loss += loss.item()

            probs = torch.sigmoid(logits)
            preds = (probs >= 0.5).float()

            correct += (preds == batch["label"]).sum().item()
            total += batch["label"].size(0)

    avg_loss = total_loss / len(data_loader)
    accuracy = correct / total

    return avg_loss, accuracy


# -----------------------------
# 16. 모델 학습
# -----------------------------
print("\nPyTorch 추천 모델 학습 시작")

for epoch in range(1, EPOCHS + 1):
    model.train()

    train_loss = 0

    for batch in train_loader:
        optimizer.zero_grad()

        logits = model(
            batch["user_idx"],
            batch["post_idx"],
            batch["category_idx"],
            batch["dong_idx"],
            batch["numeric"]
        )

        loss = criterion(logits, batch["label"])
        loss.backward()
        optimizer.step()

        train_loss += loss.item()

    avg_train_loss = train_loss / len(train_loader)
    test_loss, test_accuracy = evaluate_model(model, test_loader)

    print(
        f"Epoch {epoch:02d} | "
        f"Train Loss: {avg_train_loss:.4f} | "
        f"Test Loss: {test_loss:.4f} | "
        f"Test Accuracy: {test_accuracy:.4f}"
    )


# -----------------------------
# 17. 모델 저장
# -----------------------------
torch.save(
    {
        "model_state_dict": model.state_dict(),
        "num_users": num_users,
        "num_posts": num_posts,
        "num_categories": num_categories,
        "num_dongs": num_dongs,
        "embedding_dim": 16,
        "numeric_dim": 5
    },
    MODEL_PATH
)


# -----------------------------
# 18. 전처리 객체 저장
# -----------------------------
preprocess_objects = {
    "user_encoder": user_encoder,
    "post_encoder": post_encoder,
    "category_encoder": category_encoder,
    "dong_encoder": dong_encoder,
    "scaler": scaler,
    "numeric_features": numeric_features,
    "feature_columns": feature_columns
}

with open(PREPROCESS_PATH, "wb") as f:
    pickle.dump(preprocess_objects, f)


print("\nPyTorch 추천 모델 저장 완료")
print("모델 저장 위치:", MODEL_PATH)
print("전처리 객체 저장 위치:", PREPROCESS_PATH)