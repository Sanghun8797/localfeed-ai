import pandas as pd
import os







BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


POSTS_PATH = os.path.join(DATA_DIR, "posts.csv")
INTERACTIONS_PATH = os.path.join(DATA_DIR, "interactions.csv")











posts_df = pd.read_csv(POSTS_PATH)

interactions_df = pd.read_csv(INTERACTIONS_PATH)










print("게시글 데이터 크기:", posts_df.shape)
print("행동 로그 데이터 크기:", interactions_df.shape)

print("\n게시글 데이터 컬럼")
print(posts_df.columns)

print("\n행동 로그 데이터 컬럼")
print(interactions_df.columns)














print("\n게시글 데이터 상위 5개")
print(posts_df.head())

print("\n행동 로그 데이터 상위 5개")
print(interactions_df.head())












print("\n게시글 데이터 결측치")
print(posts_df.isnull().sum())

print("\n행동 로그 데이터 결측치")
print(interactions_df.isnull().sum())












print("\n카테고리별 게시글 수")
print(posts_df["category"].value_counts())










print("\n행동 종류별 로그 수")
print(interactions_df["action_type"].value_counts())











print("\n사용자 수:", interactions_df["user_id"].nunique())
print("행동 로그에 등장한 게시글 수:", interactions_df["post_id"].nunique())
print("전체 게시글 수:", posts_df["post_id"].nunique())