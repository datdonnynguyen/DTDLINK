"""
COS30049 Week 6 - live coding
Regression and clustering, on one dataset

HOW THIS CONNECTS TO WEEK 5
In week 5 you took raw text and built a feature table by hand. That was the
hard part, and it is what Assignment 2 marks. This week the features arrive
ready-made as numbers, on purpose: with the extraction out of the way you can
watch the algorithms themselves.

Step 5 below still builds a feature from scratch, so the thread is not lost.
Everything else assumes the table already exists.

Run it in cells. Every printed number below matches the lecture slides.

    pip install pandas numpy scikit-learn matplotlib
"""

# %% ─────────────────────────────────────────────────────────────
# STEP 1  Load, and check the room can run it
# ────────────────────────────────────────────────────────────────
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn

URL = ("https://raw.githubusercontent.com/plotly/"
       "datasets/master/winequality-red.csv")
wine = pd.read_csv(URL)

print("sklearn", sklearn.__version__)      # 1.2 or above
print("shape  ", wine.shape)               # (1599, 12)
print(wine.columns.tolist())


# %% ─────────────────────────────────────────────────────────────
# STEP 2  Look at it before you model it
# ────────────────────────────────────────────────────────────────
print(wine.head(3))
print()
print("dtypes      ", set(wine.dtypes.astype(str)))     # all numeric
print("missing     ", wine.isnull().sum().sum())        # 0
print("duplicates  ", wine.duplicated().sum())          # 240

# Those 240 duplicates are a decision, not a detail. Identical wines, or the
# same wine typed twice? Whatever you choose, choose it BEFORE the split, or
# the same row lands in train and test and your score is inflated.


# %% ─────────────────────────────────────────────────────────────
# STEP 3  Ask the data a question. groupby is the whole of pandas.
# ────────────────────────────────────────────────────────────────
print(wine.groupby("quality").alcohol.mean().round(2))
print()
print(wine.groupby("quality").size())

# Better wines have more alcohol: 9.90 at quality 5, rising to 12.09 at 8.
# But quality 3 and 4 break the pattern, and there are only 10 and 53 of them.
# Always print the group sizes next to the group means.


# %% ─────────────────────────────────────────────────────────────
# STEP 4  Look at the target
# ────────────────────────────────────────────────────────────────
print(wine.quality.value_counts().sort_index())

wine.quality.hist(bins=6)
plt.xlabel("quality"); plt.ylabel("count")
plt.show()

# Most wines are 5 or 6. A model can score respectably while never predicting
# an extreme at all, which is exactly what we will catch it doing in step 10.


# %% ─────────────────────────────────────────────────────────────
# STEP 5  Build a feature that was not there
# This is the week 5 move, on numeric columns instead of raw text.
# ────────────────────────────────────────────────────────────────
wine["acid_ratio"] = wine["fixed acidity"] / wine["volatile acidity"]
wine["so2_ratio"] = wine["free sulfur dioxide"] / wine["total sulfur dioxide"]

for col in ["alcohol", "acid_ratio", "so2_ratio", "pH"]:
    print(f"{col:<12} {wine[col].corr(wine.quality):+.3f}")

# alcohol      +0.476     the strongest raw column
# acid_ratio   +0.343     did not exist sixty seconds ago
# so2_ratio    +0.194
# pH           -0.058
#
# You made information out of arithmetic. In Assignment 2 the raw input is a
# URL or a log line rather than two numeric columns, but the move is identical:
# combine what you have into something that separates the classes better.


# %% ─────────────────────────────────────────────────────────────
# STEP 6  X, y, and the split
# ────────────────────────────────────────────────────────────────
from sklearn.model_selection import train_test_split

X = wine[["alcohol"]]        # DataFrame: double brackets
y = wine["quality"]          # Series: single brackets

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42)

print(type(X).__name__, X.shape)
print(len(X_train), "train rows,", len(X_test), "test rows")

# Single brackets give a Series and fit() raises
#     ValueError: Expected 2D array, got 1D array instead
# Try it once on purpose so you recognise the message later.


# %% ─────────────────────────────────────────────────────────────
# STEP 7  Fit, and read every attribute it hands back
# ────────────────────────────────────────────────────────────────
from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(X_train, y_train)

print("slope     ", model.coef_)            # [0.3770]
print("intercept ", model.intercept_)       # 1.6947
print(f"score      {model.score(X_test, y_test):.4f}")      # 0.1848

print("a 12% wine scores", model.predict([[12.0]]).round(2))  # [6.22]

# coef_ and intercept_ are b1 and b0 from the lecture. The whole model is
# those two numbers. The trailing underscore is the sklearn convention for
# attributes that only exist after fit; read coef_ first and you get an
# AttributeError.


# %% ─────────────────────────────────────────────────────────────
# STEP 8  Measure it four ways
# ────────────────────────────────────────────────────────────────
from sklearn.metrics import (mean_squared_error, mean_absolute_error,
                             r2_score)

y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
print(f"MSE   {mse:.3f}")           # 0.517
print(f"RMSE  {mse ** 0.5:.3f}")    # 0.719
print(f"MAE   {mean_absolute_error(y_test, y_pred):.3f}")   # 0.578
print(f"R2    {r2_score(y_test, y_pred):.3f}")              # 0.185

# MAE 0.578 sits below RMSE 0.719 because RMSE squares the errors, so a few
# badly missed wines pull it up. When those two are far apart, go and read the
# worst predictions individually. Step 9 does that.


# %% ─────────────────────────────────────────────────────────────
# STEP 9  The plot no metric can replace
# ────────────────────────────────────────────────────────────────
plt.scatter(y_test, y_pred, s=10, alpha=0.35)
plt.plot([3, 8], [3, 8], "r--", label="a perfect model")
plt.xlabel("actual quality"); plt.ylabel("predicted quality")
plt.legend()
plt.show()

worst = (y_test - y_pred).abs().nlargest(5)
print(wine.loc[worst.index, ["alcohol", "quality"]])

# Real wines run 3 to 8. Almost every prediction lands between 5 and 6.5.
# The model learned to play safe near the middle, because guessing the average
# is rarely badly wrong. R2 did not tell you that. Only the picture did.


# %% ─────────────────────────────────────────────────────────────
# STEP 10  All eleven features, then a reality check
# ────────────────────────────────────────────────────────────────
from sklearn.model_selection import cross_val_score

FEATURES = [c for c in wine.columns
            if c not in ("quality", "acid_ratio", "so2_ratio")]
X = wine[FEATURES]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42)
full = LinearRegression().fit(X_train, y_train)
print(f"single split R2  {r2_score(y_test, full.predict(X_test)):.3f}")

scores = cross_val_score(LinearRegression(), X, y, cv=5, scoring="r2")
print("five folds      ", scores.round(3))
print(f"mean {scores.mean():.3f}   std {scores.std():.3f}")

# One split says 0.351. Five splits say anything from 0.132 to 0.369, mean
# 0.290. Quote the mean and the spread, or you are reporting luck.


# %% ─────────────────────────────────────────────────────────────
# STEP 11  Clustering. First, why scaling is not optional.
# ────────────────────────────────────────────────────────────────
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

X = wine[FEATURES]                       # labels are gone from here on

raw = KMeans(3, n_init=10, random_state=42).fit_predict(X)
X_scaled = StandardScaler().fit_transform(X)
scaled = KMeans(3, n_init=10, random_state=42).fit_predict(X_scaled)

print("without scaling", np.bincount(raw))       # [240 843 516]
print("with scaling   ", np.bincount(scaled))    # [722 502 375]

# Different groups entirely. Unscaled, K-means is really clustering on total
# sulfur dioxide alone, because it spans 283 while density spans 0.014.
# Ten of the eleven features had almost no say.


# %% ─────────────────────────────────────────────────────────────
# STEP 12  Choosing k, both measures in one loop
# ────────────────────────────────────────────────────────────────
from sklearn.metrics import silhouette_score

ks, inertias, sils = [], [], []
for k in range(2, 9):
    km = KMeans(k, n_init=10, random_state=42)
    lab = km.fit_predict(X_scaled)
    ks.append(k); inertias.append(km.inertia_)
    sils.append(silhouette_score(X_scaled, lab))
    print(f"k={k}  inertia {km.inertia_:>7.0f}  silhouette {sils[-1]:.3f}")

fig, ax = plt.subplots(1, 2, figsize=(10, 3.5))
ax[0].plot(ks, inertias, "o-"); ax[0].set_xlabel("k"); ax[0].set_ylabel("inertia")
ax[1].plot(ks, sils, "o-"); ax[1].set_xlabel("k"); ax[1].set_ylabel("silhouette")
plt.tight_layout(); plt.show()

# Inertia falls smoothly with no clear elbow, and every silhouette sits near
# 0.2. That is the data saying these wines do not form separated groups.
# Reporting that honestly beats picking k=3 and pretending.


# %% ─────────────────────────────────────────────────────────────
# STEP 13  Describe each cluster. This is what Assignment 2 marks.
# ────────────────────────────────────────────────────────────────
labels = KMeans(3, n_init=10, random_state=42).fit_predict(X_scaled)
wine["cluster"] = labels

overall, spread = X.mean(), X.std()
for c in sorted(wine.cluster.unique()):
    g = wine[wine.cluster == c]
    z = (g[FEATURES].mean() - overall) / spread      # in standard deviations
    print(f"\ncluster {c}   n={len(g)}")
    print("   more:", z.nlargest(2).round(2).to_dict())
    print("   less:", z.nsmallest(2).round(2).to_dict())

# Dividing by the standard deviation is the whole trick. Without it, total
# sulfur dioxide wins every comparison because it is measured in tens while
# pH is measured in units.
#
# Now the clusters have names: one is the high-acid group, one is the heavily
# preserved group. A cluster you cannot name in a sentence is not a finding.


# %% ─────────────────────────────────────────────────────────────
# STEP 14  Eleven dimensions on a flat screen
# ────────────────────────────────────────────────────────────────
from sklearn.decomposition import PCA

P = PCA(n_components=2, random_state=42).fit_transform(X_scaled)
plt.scatter(P[:, 0], P[:, 1], c=labels, s=8, cmap="viridis")
plt.xlabel("first principal component"); plt.ylabel("second")
plt.show()

# The groups touch rather than separate, which is the silhouette of 0.19 made
# visible. Use PCA for looking, never for deciding: both axes are mixtures of
# all eleven features and mean nothing on their own.


# %% ─────────────────────────────────────────────────────────────
# STEP 15  Recap, and what changes next week
# ────────────────────────────────────────────────────────────────
print("""
Regression
    fit, coef_, intercept_, predict
    MSE, RMSE, MAE, R2, and why they differ
    cross_val_score, because one split is one number

Clustering
    scale first, always
    n_init because K-means can land badly
    inertia and silhouette disagree, and neither is the answer
    describing the clusters is the deliverable

Next week: the same eleven columns, but the question becomes good or bad,
and we finish by saving a model to a file that Assignment 3 can load.
""")
