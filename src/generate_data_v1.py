import pandas as pd
import random
from datetime import datetime, timedelta
import os




BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")



os.makedirs(DATA_DIR, exist_ok=True)










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
    "디지털기기": ["맥북 에어 M2 판매합니다", "아이폰 15 팝니다", "게이밍 모니터 판매", "에어팟 프로 2세대"],
    "생활가전": ["전자레인지 판매", "공기청정기 팝니다", "무선청소기 판매", "미니 냉장고"],
    "가구/인테리어": ["책상 판매합니다", "의자 팝니다", "원목 선반", "침대 프레임"],
    "의류": ["겨울 패딩 판매", "나이키 후드티", "청바지 팝니다", "운동화 판매"],
    "도서": ["파이썬 책 판매", "자바 입문서", "토익 교재", "소설책 묶음"],
    "스포츠/레저": ["자전거 판매", "헬스 덤벨", "캠핑 의자", "러닝화 팝니다"],
    "유아용품": ["유모차 판매", "아기 장난감", "아기 옷 묶음", "카시트 팝니다"],
    "반려동물용품": ["강아지 하우스", "고양이 캣타워", "반려동물 이동장", "강아지 옷"],
    "생활용품": ["수납함 판매", "조명 팝니다", "식기 세트", "청소용품 묶음"],
    "게임/취미": ["닌텐도 스위치", "플스5 타이틀", "보드게임 판매", "레고 세트"]
}








posts = []

for post_id in range(1, 1001):
    category = random.choice(categories)
    dong, lat, lon = random.choice(dongs)
    
    title = random.choice(sample_titles[category])
    description = f"{dong}에서 거래 가능한 {category} 상품입니다. 상태 좋고 빠른 거래 원합니다."
    
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



users = [f"user_{i}" for i in range(1, 101)]
action_types = ["view", "click", "like", "chat", "hide"]

interactions = []

for _ in range(5000):
    user_id = random.choice(users)
    post = posts_df.sample(1).iloc[0]
    
    action_type = random.choices(
        action_types,
        weights=[50, 25, 15, 8, 2],
        k=1
        )[0]
    
    
    timestamp = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
    
    
    interactions.append({
        "user_id": user_id,
        "post_id": post["post_id"],
        "action_type": action_type,
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    

interactions_df = pd.DataFrame(interactions)











posts_df.to_csv(os.path.join(DATA_DIR, "posts.csv"), index=False, encoding="utf-8-sig")
interactions_df.to_csv(os.path.join(DATA_DIR, "interactions.csv"), index=False, encoding="utf-8-sig")





print("데이터 생성 완료")
print("posts.csv:", posts_df.shape)
print("interactions.csv:", interactions_df.shape)
print("저장 폴더:", DATA_DIR)
print("posts.csv 저장 위치:", os.path.abspath("data/posts.csv"))
print("interactions.csv 저장 위치:", os.path.abspath("data/interactions.csv"))
print("현재 작업 폴더:", os.getcwd())


print("현재 작업 폴더:", os.getcwd())













































