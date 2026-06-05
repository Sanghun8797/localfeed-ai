import pandas as pd
import random
from datetime import datetime, timedelta
import os


# -----------------------------
# 1. 프로젝트 경로 설정
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)


# -----------------------------
# 2. 기본 데이터 설정
# -----------------------------
categories = [
    "디지털기기",
    "생활가전",
    "가구/인테리어",
    "의류",
    "도서",
    "스포츠/레저",
    "유아용품",
    "반려동물용품",
    "생활용품",
    "게임/취미"
]

dongs = [
    ("신림동", 37.4842, 126.9290),
    ("봉천동", 37.4826, 126.9416),
    ("낙성대동", 37.4768, 126.9586),
    ("서울대입구", 37.4812, 126.9527),
    ("사당동", 37.4766, 126.9816),
    ("상도동", 37.4996, 126.9310),
    ("흑석동", 37.5088, 126.9636)
]

sample_titles = {
    "디지털기기": [
        "맥북 에어 M2 판매합니다", "아이폰 15 팝니다", "게이밍 모니터 판매",
        "에어팟 프로 2세대", "아이패드 미니 판매", "삼성 갤럭시 판매"
    ],
    "생활가전": [
        "전자레인지 판매", "공기청정기 팝니다", "무선청소기 판매",
        "미니 냉장고", "에어프라이어 판매", "제습기 팝니다"
    ],
    "가구/인테리어": [
        "책상 판매합니다", "의자 팝니다", "원목 선반",
        "침대 프레임", "소파 판매", "수납장 팝니다"
    ],
    "의류": [
        "겨울 패딩 판매", "나이키 후드티", "청바지 팝니다",
        "운동화 판매", "맨투맨 판매", "코트 팝니다"
    ],
    "도서": [
        "파이썬 책 판매", "자바 입문서", "토익 교재",
        "소설책 묶음", "알고리즘 책 판매", "경제경영 도서"
    ],
    "스포츠/레저": [
        "자전거 판매", "헬스 덤벨", "캠핑 의자",
        "러닝화 팝니다", "요가매트 판매", "등산가방 팝니다"
    ],
    "유아용품": [
        "유모차 판매", "아기 장난감", "아기 옷 묶음",
        "카시트 팝니다", "아기침대 판매", "분유포트 팝니다"
    ],
    "반려동물용품": [
        "강아지 하우스", "고양이 캣타워", "반려동물 이동장",
        "강아지 옷", "고양이 장난감", "강아지 배변패드"
    ],
    "생활용품": [
        "수납함 판매", "조명 팝니다", "식기 세트",
        "청소용품 묶음", "커튼 판매", "러그 팝니다"
    ],
    "게임/취미": [
        "닌텐도 스위치", "플스5 타이틀", "보드게임 판매",
        "레고 세트", "피규어 판매", "키보드 취미용품"
    ]
}


# -----------------------------
# 3. 사용자 선호도 생성
# -----------------------------
users = [f"user_{i}" for i in range(1, 101)]

user_preferences = []

for user_id in users:
    preferred_categories = random.sample(categories, 2)
    preferred_dong = random.choice(dongs)[0]

    min_price = random.randint(1, 15) * 10000
    max_price = min_price + random.randint(5, 25) * 10000

    user_preferences.append({
        "user_id": user_id,
        "preferred_category_1": preferred_categories[0],
        "preferred_category_2": preferred_categories[1],
        "preferred_dong": preferred_dong,
        "min_price": min_price,
        "max_price": max_price
    })

user_pref_df = pd.DataFrame(user_preferences)


# -----------------------------
# 4. 게시글 데이터 생성
# -----------------------------
posts = []

for post_id in range(1, 1001):
    category = random.choice(categories)
    dong, lat, lon = random.choice(dongs)

    title = random.choice(sample_titles[category])
    description = (
        f"{dong}에서 거래 가능한 {category} 상품입니다. "
        f"{title} 상품이고 상태 좋습니다. 빠른 거래 원합니다."
    )

    price = random.randint(5, 300) * 1000
    created_at = datetime.now() - timedelta(days=random.randint(0, 30))

    view_count = random.randint(10, 1000)
    like_count = random.randint(0, 100)
    chat_count = random.randint(0, 50)

    posts.append({
        "post_id": post_id,
        "title": title,
        "description": description,
        "category": category,
        "price": price,
        "dong": dong,
        "latitude": lat + random.uniform(-0.005, 0.005),
        "longitude": lon + random.uniform(-0.005, 0.005),
        "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "view_count": view_count,
        "like_count": like_count,
        "chat_count": chat_count
    })

posts_df = pd.DataFrame(posts)


# -----------------------------
# 5. 사용자 관심도 계산 함수
# -----------------------------
def calculate_interest_score(user_pref, post):
    score = 0

    if post["category"] == user_pref["preferred_category_1"]:
        score += 4

    if post["category"] == user_pref["preferred_category_2"]:
        score += 3

    if post["dong"] == user_pref["preferred_dong"]:
        score += 3

    if user_pref["min_price"] <= post["price"] <= user_pref["max_price"]:
        score += 2

    score += random.uniform(0, 1)

    return score


# -----------------------------
# 6. 관심도에 따른 행동 선택 함수
# -----------------------------
def choose_action_by_interest(interest_score):
    if interest_score >= 8:
        action_weights = [20, 30, 25, 20, 5]
    elif interest_score >= 5:
        action_weights = [40, 30, 18, 8, 4]
    elif interest_score >= 3:
        action_weights = [60, 25, 8, 3, 4]
    else:
        action_weights = [75, 15, 3, 1, 6]

    action_types = ["view", "click", "like", "chat", "hide"]

    return random.choices(
        action_types,
        weights=action_weights,
        k=1
    )[0]


# -----------------------------
# 7. 사용자 행동 로그 생성
# -----------------------------
interactions = []

for _ in range(5000):
    user_pref = user_pref_df.sample(1).iloc[0]
    user_id = user_pref["user_id"]

    sampled_posts = posts_df.sample(20).copy()

    sampled_posts["interest_score"] = sampled_posts.apply(
        lambda post: calculate_interest_score(user_pref, post),
        axis=1
    )

    selected_post = sampled_posts.sort_values(
        by="interest_score",
        ascending=False
    ).iloc[0]

    action_type = choose_action_by_interest(selected_post["interest_score"])

    timestamp = datetime.now() - timedelta(
        days=random.randint(0, 30),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )

    interactions.append({
        "user_id": user_id,
        "post_id": selected_post["post_id"],
        "action_type": action_type,
        "interest_score": round(selected_post["interest_score"], 3),
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
    })

interactions_df = pd.DataFrame(interactions)


# -----------------------------
# 8. CSV 저장
# -----------------------------
posts_df.to_csv(
    os.path.join(DATA_DIR, "posts.csv"),
    index=False,
    encoding="utf-8-sig"
)

interactions_df.to_csv(
    os.path.join(DATA_DIR, "interactions.csv"),
    index=False,
    encoding="utf-8-sig"
)

user_pref_df.to_csv(
    os.path.join(DATA_DIR, "user_preferences.csv"),
    index=False,
    encoding="utf-8-sig"
)


# -----------------------------
# 9. 생성 결과 출력
# -----------------------------
print("데이터 생성 완료")
print("posts.csv:", posts_df.shape)
print("interactions.csv:", interactions_df.shape)
print("user_preferences.csv:", user_pref_df.shape)
print("저장 폴더:", DATA_DIR)

print("\n행동 로그 분포")
print(interactions_df["action_type"].value_counts())

print("\n사용자 선호도 예시")
print(user_pref_df.head().to_string(index=False))