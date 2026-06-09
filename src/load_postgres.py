import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

load_dotenv(BASE_DIR / ".env")


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS interactions;")
        cur.execute("DROP TABLE IF EXISTS user_preferences;")
        cur.execute("DROP TABLE IF EXISTS posts;")

        cur.execute("""
            CREATE TABLE posts (
                post_id INTEGER PRIMARY KEY,
                title TEXT,
                description TEXT,
                category TEXT,
                price INTEGER,
                dong TEXT,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                created_at TIMESTAMP,
                view_count INTEGER,
                like_count INTEGER,
                chat_count INTEGER
            );
        """)

        cur.execute("""
            CREATE TABLE interactions (
                interaction_id INTEGER PRIMARY KEY,
                user_id TEXT,
                post_id INTEGER,
                action_type TEXT,
                interest_score DOUBLE PRECISION,
                timestamp TIMESTAMP
            );
        """)

        cur.execute("""
            CREATE TABLE user_preferences (
                user_id TEXT PRIMARY KEY,
                preferred_category_1 TEXT,
                preferred_category_2 TEXT,
                preferred_dong TEXT,
                min_price INTEGER,
                max_price INTEGER
            );
        """)

    conn.commit()


def insert_posts(conn):
    posts_df = pd.read_csv(DATA_DIR / "posts.csv")

    with conn.cursor() as cur:
        for _, row in posts_df.iterrows():
            cur.execute("""
                INSERT INTO posts (
                    post_id, title, description, category, price, dong,
                    latitude, longitude, created_at,
                    view_count, like_count, chat_count
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                int(row["post_id"]),
                row["title"],
                row["description"],
                row["category"],
                int(row["price"]),
                row["dong"],
                float(row["latitude"]),
                float(row["longitude"]),
                row["created_at"],
                int(row["view_count"]),
                int(row["like_count"]),
                int(row["chat_count"])
            ))

    conn.commit()
    print(f"posts 적재 완료: {len(posts_df)} rows")


def insert_interactions(conn):
    interactions_df = pd.read_csv(DATA_DIR / "interactions.csv")

    with conn.cursor() as cur:
        for idx, row in interactions_df.iterrows():
            cur.execute("""
                INSERT INTO interactions (
                    interaction_id, user_id, post_id, action_type,
                    interest_score, timestamp
                )
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (
                idx + 1,
                row["user_id"],
                int(row["post_id"]),
                row["action_type"],
                float(row["interest_score"]),
                row["timestamp"]
            ))

    conn.commit()
    print(f"interactions 적재 완료: {len(interactions_df)} rows")


def insert_user_preferences(conn):
    user_preferences_df = pd.read_csv(DATA_DIR / "user_preferences.csv")

    with conn.cursor() as cur:
        for _, row in user_preferences_df.iterrows():
            cur.execute("""
                INSERT INTO user_preferences (
                    user_id, preferred_category_1, preferred_category_2,
                    preferred_dong, min_price, max_price
                )
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (
                row["user_id"],
                row["preferred_category_1"],
                row["preferred_category_2"],
                row["preferred_dong"],
                int(row["min_price"]),
                int(row["max_price"])
            ))

    conn.commit()
    print(f"user_preferences 적재 완료: {len(user_preferences_df)} rows")


def main():
    conn = get_connection()

    create_tables(conn)
    insert_posts(conn)
    insert_interactions(conn)
    insert_user_preferences(conn)

    conn.close()
    print("PostgreSQL 데이터 적재 완료")


if __name__ == "__main__":
    main()