"""
COS30049 Week 5 — live coding walkthrough, part 2
Data processing operations: sorting, reshaping, joining, concatenating

This is the companion to the modelling walkthrough. It works on the same SMS
dataset and covers the transformation operations from the Week 5 lecture,
slides 12 to 18, plus the cleaning material from the seminar.

Two of these operations are named directly in the Assignment 2 rubric under
Innovation in data processing: joining an additional source onto your base
dataset, and reconciling sources whose columns do not line up.

    pip install pandas numpy scikit-learn
"""

# %% ─────────────────────────────────────────────────────────────
# SETUP  Same data as part 1
# ────────────────────────────────────────────────────────────────
import pandas as pd
import numpy as np

URL = ("https://raw.githubusercontent.com/justmarkham/"
       "pycon-2016-tutorial/master/data/sms.tsv")
df = pd.read_csv(URL, sep="\t", header=None, names=["label_text", "message"])
df["label"] = (df["label_text"] == "spam").astype(int)
df["length"] = df["message"].str.len()
df["n_digits"] = df["message"].str.count(r"\d")

print(df.shape)


# %% ─────────────────────────────────────────────────────────────
# STEP 1  Sorting
# Lecture: Data Transformation, Manipulate the form of the data
# ────────────────────────────────────────────────────────────────
print(df.sort_values("length", ascending=False).head(3)[["length", "message"]])

# Sorting is how you find the extremes, and the extremes are where the
# problems live. Look at the longest and the shortest rows in your own data
# before you trust any average.
print("\nshortest messages:")
print(df.nsmallest(3, "length")[["length", "message"]])


# %% ─────────────────────────────────────────────────────────────
# STEP 2  Group and aggregate: turn many rows into a summary table
# ────────────────────────────────────────────────────────────────
summary = df.groupby("label_text").agg(
    n=("message", "size"),
    mean_length=("length", "mean"),
    mean_digits=("n_digits", "mean"),
    max_length=("length", "max"),
).round(1)

print(summary)

# groupby is the operation behind most of the tables you will put in your
# report. It is also the first half of a join: you aggregate one table down
# to one row per key, then attach it to another.


# %% ─────────────────────────────────────────────────────────────
# STEP 3  Long to wide: pivot
# Lecture: Data Transformation, Reshaping Your Table
# ────────────────────────────────────────────────────────────────
df["length_band"] = pd.cut(df["length"], [0, 50, 100, 200, 10000],
                           labels=["short", "medium", "long", "very long"])

long_form = (df.groupby(["length_band", "label_text"], observed=True)
               .size().reset_index(name="count"))
print("long form:\n", long_form, "\n")

wide_form = long_form.pivot(index="length_band", columns="label_text",
                            values="count").fillna(0).astype(int)
print("wide form:\n", wide_form)

# Long form is what you store and what most plotting libraries want.
# Wide form is what a human reads. Same numbers, different shape.


# %% ─────────────────────────────────────────────────────────────
# STEP 4  Wide back to long: melt
# ────────────────────────────────────────────────────────────────
back = wide_form.reset_index().melt(id_vars="length_band",
                                    var_name="label_text", value_name="count")
print(back.head())

# Worth showing both directions so students know pivot is reversible.
# You will need melt whenever a source arrives with one column per category.


# %% ─────────────────────────────────────────────────────────────
# STEP 5  Extract the key you are going to join on
# ────────────────────────────────────────────────────────────────
df["first_word"] = df["message"].str.extract(r"^(\w+)")[0].str.lower()

print("rows with a first word:", f"{df['first_word'].notna().mean():.1%}")
print("distinct first words:", df["first_word"].nunique())

counts = df.groupby("first_word")["label"].agg(["size", "mean"]).query("size >= 20")
print("\nmost spam-heavy openers:")
print(counts.nlargest(4, "mean").round(3))
print("\nmost ham-heavy openers:")
print(counts.nsmallest(4, "mean").round(3))

df = df.dropna(subset=["first_word"]).reset_index(drop=True)

# How a message opens turns out to carry a lot. "Urgent" and "Free" are
# almost always spam; "Yeah" and "Yup" never are. That makes it a usable key
# for a second table.
#
# YOUR TOPIC: the equivalent key is
#   Phishing URL       the TLD, or the registered domain
#   Log anomaly        the component name, or the event template id
#   Prompt injection   the first instruction verb


# %% ─────────────────────────────────────────────────────────────
# STEP 6  Build the second table, from TRAINING DATA ONLY
# Lecture: Data Transformation, Combine the Table
# ────────────────────────────────────────────────────────────────
from sklearn.model_selection import train_test_split

train, test = train_test_split(df, test_size=0.3, stratify=df["label"],
                               random_state=42)

reputation = (train.groupby("first_word")
                   .agg(times_seen=("label", "size"),
                        spam_rate=("label", "mean"))
                   .reset_index())

print(reputation.sort_values("times_seen", ascending=False).head(8))
print("\nlookup table has", len(reputation), "rows")

# Note what we did NOT do: we did not build this from the whole dataset.
# The reason comes two steps from now.


# %% ─────────────────────────────────────────────────────────────
# STEP 7  The join itself
# Lecture: Data Transformation, Combine the Table
# ────────────────────────────────────────────────────────────────
train = train.merge(reputation, on="first_word", how="left")
test = test.merge(reputation, on="first_word", how="left")

print(train[["first_word", "times_seen", "spam_rate"]].dropna().head(5))

print("\nunmatched rows after the join:")
print("  train:", f"{train['spam_rate'].isna().mean():.1%}")
print("  test :", f"{test['spam_rate'].isna().mean():.1%}")

# how="left" keeps every message and fills the rest with NaN. Use inner and
# you silently drop every message whose opening word never appeared in the
# training half. Say that out loud, because inner is what people reach for.


# %% ─────────────────────────────────────────────────────────────
# STEP 8  What to do with the rows that did not match
# Lecture: Missing or incomplete data
# ────────────────────────────────────────────────────────────────
# Three defensible choices. They are not equivalent.
#   1. fill with 0        says "never seen" means "definitely safe"
#   2. fill with the mean says "never seen" means "average risk"
#   3. add a flag column  says "never seen" is itself information

train["seen_before"] = train["spam_rate"].notna().astype(int)
test["seen_before"] = test["spam_rate"].notna().astype(int)

prior = train["label"].mean()          # from training data, not from test
train["spam_rate"] = train["spam_rate"].fillna(prior)
test["spam_rate"] = test["spam_rate"].fillna(prior)
train["times_seen"] = train["times_seen"].fillna(0)
test["times_seen"] = test["times_seen"].fillna(0)

print("filled unmatched rows with the training prior:", round(prior, 3))
print(train[["spam_rate", "times_seen", "seen_before"]].describe().round(3))

# Option 3 is usually the strongest, and it costs one line. A shortcode you
# have never seen is a different situation from one you have seen and know
# to be clean.


# %% ─────────────────────────────────────────────────────────────
# STEP 9  The trap. Build the same table from ALL the data.
# ────────────────────────────────────────────────────────────────
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score

FEATS = ["length", "n_digits", "spam_rate", "times_seen", "seen_before"]

honest = RandomForestClassifier(n_estimators=200, random_state=42,
                                n_jobs=-1).fit(train[FEATS], train["label"])
f_honest = f1_score(test["label"], honest.predict(test[FEATS]))

# Now do it the wrong way: build the lookup from every row, test included.
leaky_rep = (df.groupby("first_word")
               .agg(times_seen=("label", "size"),
                    spam_rate=("label", "mean")).reset_index())
d2 = df.merge(leaky_rep, on="first_word", how="left")
d2["seen_before"] = d2["spam_rate"].notna().astype(int)
d2[["spam_rate", "times_seen"]] = d2[["spam_rate", "times_seen"]].fillna(0)

a, b = train_test_split(d2, test_size=0.3, stratify=d2["label"],
                        random_state=42)
leaky = RandomForestClassifier(n_estimators=200, random_state=42,
                               n_jobs=-1).fit(a[FEATS], a["label"])
f_leaky = f1_score(b["label"], leaky.predict(b[FEATS]))

print(f"lookup built from training data only : F1 {f_honest:.3f}")
print(f"lookup built from all data           : F1 {f_leaky:.3f}")
print(f"free marks from leaking the label    : {f_leaky - f_honest:+.3f}")

# The second number is not real. Those test messages contributed their own
# labels to the table the model then looked them up in. Any feature you
# build by aggregating the label has to be built on the training split and
# applied to the test split, never both at once.


# %% ─────────────────────────────────────────────────────────────
# STEP 10  Concatenating: a second source that does not line up
# Lecture: Data Transformation, Combine the Table
# ────────────────────────────────────────────────────────────────
# Simulating a second source here, because the real thing is what you will
# go and find for the Innovation marks. What matters is that its columns
# are deliberately wrong: different names, different label encoding, and an
# extra column the first source does not have.
other = pd.DataFrame({
    "text": ["Win a FREE iPhone now, click here",
             "Your parcel is waiting, confirm at bit.ly/x9",
             "see you at 6 then",
             "Can you pick up milk on the way home"],
    "is_spam": [True, True, False, False],
    "collected_from": ["forum", "forum", "donation", "donation"],
})
print(other, "\n")

# Reconcile before stacking, never after.
aligned = pd.DataFrame({
    "message": other["text"],
    "label": other["is_spam"].astype(int),
    "label_text": np.where(other["is_spam"], "spam", "ham"),
})
aligned["length"] = aligned["message"].str.len()
aligned["n_digits"] = aligned["message"].str.count(r"\d")

combined = pd.concat([df[["message", "label", "label_text", "length",
                          "n_digits"]], aligned], ignore_index=True)

print("before:", len(df), " after:", len(combined))
print(combined.tail(4))

# We dropped `collected_from` because the first source has nothing to put
# there. Keeping it would leave 5,572 NaNs and a column that quietly tells
# the model which source a row came from, which it can learn instead of
# learning about spam.


# %% ─────────────────────────────────────────────────────────────
# STEP 11  What happens if you concat without aligning first
# ────────────────────────────────────────────────────────────────
careless = pd.concat([df.head(3), other], ignore_index=True)
print(careless)
print("\ncolumns now:", list(careless.columns))
print("NaN count:\n", careless.isna().sum())

# pandas will not stop you. It unions the columns and fills the gaps with
# NaN, and you end up with `message` half empty and `text` half empty
# describing the same thing. This is the failure the rubric is asking you
# to avoid, so show it before you show the fix.


# %% ─────────────────────────────────────────────────────────────
# STEP 12  Text normalisation before matching
# Seminar: Inconsistent data, different naming representations
# ────────────────────────────────────────────────────────────────
messy = pd.Series(["Swinburne University of Technology", "swinburne uni",
                   "SWINBURNE UNIVERSITY  OF TECHNOLOGY ", "Swinburne  Uni."])

cleaned = (messy.str.lower()
                .str.replace(r"[^\w\s]", "", regex=True)
                .str.replace(r"\s+", " ", regex=True)
                .str.strip())
print(pd.DataFrame({"before": messy, "after": cleaned}).to_string())

# Four spellings, two entities, and a join key that will match none of them
# until you normalise. Do this before the merge, not after you notice the
# join produced nothing.


# %% ─────────────────────────────────────────────────────────────
# STEP 13  Outliers with the IQR rule
# Seminar: Outlier Analysis
# ────────────────────────────────────────────────────────────────
q1, q3 = df["length"].quantile([0.25, 0.75])
iqr = q3 - q1
lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr

out = df[(df["length"] < lo) | (df["length"] > hi)]
print(f"Q1 {q1:.0f}  Q3 {q3:.0f}  IQR {iqr:.0f}  bounds [{lo:.0f}, {hi:.0f}]")
print(f"outliers: {len(out)} rows, {len(out) / len(df):.1%}")
print(f"spam rate among outliers: {out['label'].mean():.1%} "
      f"vs {df['label'].mean():.1%} overall")

print("\nthe longest message:")
print(" ", out.nlargest(1, "length")["message"].iloc[0][:110])

# Read that message out. The IQR rule flagged it as an outlier, and it is a
# perfectly ordinary long personal message. In this dataset the outliers are
# almost entirely ham, which is the opposite of what students expect.
#
# So the rule found something real, but "unusual" and "suspicious" are not
# the same thing. Deleting these rows would throw away the only examples of
# long legitimate messages you have, and your model would start flagging
# every long message as spam. Keep, cap, or drop is a judgement about your
# problem, and the report has to say which you chose and why.


# %% ─────────────────────────────────────────────────────────────
# STEP 14  Recap of what each operation was for
# ────────────────────────────────────────────────────────────────
print("""
sort / nlargest   find the extremes, because that is where the problems are
groupby + agg     many rows into one row per key, the first half of a join
pivot / melt      same numbers, reshaped for storage or for reading
merge (left)      attach a second source without losing rows
fillna + a flag   an unmatched row is a fact, not a hole to paper over
concat            stack sources, but reconcile the columns first
normalise text    or your join key matches nothing
IQR               find outliers, then decide, and say why
""")
