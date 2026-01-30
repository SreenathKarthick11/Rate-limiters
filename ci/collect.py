from pathlib import Path
import matplotlib.pyplot as plt

RESULTS = {
    "Token Bucket": Path("ci/results/token_bucket.txt"),
    "Leaky Bucket": Path("ci/results/leaky_bucket.txt"),
}

success = []
blocked = []

for name, path in RESULTS.items():
    codes = path.read_text().splitlines()
    success.append(codes.count("200"))
    blocked.append(codes.count("429"))

x = range(len(RESULTS))
labels = list(RESULTS.keys())

width = 0.35

plt.figure(figsize=(6, 4))

plt.bar(
    [i - width / 2 for i in x],
    success,
    width=width,
    label="200 OK",
)

plt.bar(
    [i + width / 2 for i in x],
    blocked,
    width=width,
    label="429 Too Many Requests",
)

plt.xticks(list(x), labels)
plt.ylabel("Request count")
plt.title("Rate Limiter Behavior Comparison")
plt.legend()

Path("ci/plots").mkdir(parents=True, exist_ok=True)
plt.tight_layout()
plt.savefig("ci/plots/rate_limit_comparison.png")
plt.close()
