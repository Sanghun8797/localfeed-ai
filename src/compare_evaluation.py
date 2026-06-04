import pandas as pd
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

BEFORE_PATH = os.path.join(DATA_DIR, "evaluation_result_before.csv")
AFTER_PATH = os.path.join(DATA_DIR, "evaluation_result_after.csv")


before_df = pd.read_csv(BEFORE_PATH)
after_df = pd.read_csv(AFTER_PATH)


metrics = [
    "precision_at_k",
    "recall_at_k",
    "ndcg_at_k"
]

comparison = []

for metric in metrics:
    before_mean = before_df[metric].mean()
    after_mean = after_df[metric].mean()
    diff = after_mean - before_mean
    improvement_rate = (diff / before_mean * 100) if before_mean != 0 else None

    comparison.append({
        "metric": metric,
        "before": before_mean,
        "after": after_mean,
        "diff": diff,
        "improvement_rate_percent": improvement_rate
    })

comparison_df = pd.DataFrame(comparison)

print("\n평가 지표 개선 비교")
print(comparison_df.to_string(index=False))

comparison_df.to_csv(
    os.path.join(DATA_DIR, "evaluation_comparison.csv"),
    index=False,
    encoding="utf-8-sig"
)

print("\n비교 결과 저장 완료")
print("저장 위치:", os.path.join(DATA_DIR, "evaluation_comparison.csv"))