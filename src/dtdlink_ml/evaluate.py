"""Evaluate the chosen classifier on test and save the model."""

import json
from datetime import datetime
from zoneinfo import ZoneInfo

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

from dtdlink_ml.data_cleaning import TARGET_MAPPING
from dtdlink_ml.feature_extraction import FEATURE_NAMES, file_sha256
from dtdlink_ml.predict import RawURLPipeline, load_pipeline
from dtdlink_ml.train_classifier import (FEATURE_INPUT, FEATURE_SHA256, MANIFEST_SHA256, ROOT, SELECTED_MODEL,
                                         SELECTED_THRESHOLD, SPLIT_MANIFEST, load_splits, load_train_val,
                                         make_models, score_predictions)

REPORT_DIR = ROOT / "reports/evaluation"
MODEL_DIR = ROOT / "models"
FIGURE_DIR = ROOT / "reports/figures"
SELECTION_FILE = ROOT / "reports/classification/validation_summary.json"


def load_test(feature_path=FEATURE_INPUT, manifest_path=SPLIT_MANIFEST,
              feature_hash=FEATURE_SHA256, manifest_hash=MANIFEST_SHA256):
    """Load the test rows (only used for the final evaluation)."""
    data, _ = load_splits(("test",), feature_path, manifest_path, feature_hash, manifest_hash)
    return data["test"]


def build_prediction_table(test, prob, threshold=SELECTED_THRESHOLD):
    """One row per test URL with its probability, prediction and TP/TN/FP/FN."""
    score_predictions(test["target"], prob, threshold)  # raises if prob has NaN or wrong length
    table = test[["url_id", "url", "type", "target"]].copy()
    table["probability"] = prob
    table["prediction"] = (table["probability"] >= threshold).astype(int)
    actual = table["target"]
    pred = table["prediction"]
    table["outcome"] = np.select([(actual == 1) & (pred == 1), (actual == 0) & (pred == 0), (actual == 0) & (pred == 1)],
                                 ["TP", "TN", "FP"], default="FN")
    return table


def subgroup_table(pred):
    """Results for each original label (benign, phishing, malware, defacement)."""
    rows = []
    for source in TARGET_MAPPING:
        group = pred[pred["type"] == source]
        if len(group) == 0:
            continue
        errors = int(group["outcome"].isin(["FP", "FN"]).sum())
        rows.append({
            "source_type": source,
            "rows": len(group),
            "correct": len(group) - errors,
            "correct_rate": 1 - errors / len(group),
            "missed_dangerous": int((group["outcome"] == "FN").sum()),
            "false_alarms": int((group["outcome"] == "FP").sum()),
            # for benign URLs every error is a false alarm, for the others every error is a miss
            "dangerous_recall": None if source == "benign" else 1 - errors / len(group),
            "benign_false_alarm_rate": errors / len(group) if source == "benign" else None,
        })
    return pd.DataFrame(rows)


def select_error_examples(test, pred, per_group=5):
    """Up to per_group FP/FN examples for each original label, sorted by URL id."""
    idx = []
    for outcome in ["FP", "FN"]:
        for source in TARGET_MAPPING:
            group = pred[(pred["outcome"] == outcome) & (pred["type"] == source)]
            idx += group.sort_values("url_id").head(per_group).index.tolist()
    examples = pred.loc[idx].copy()
    for col in ["url_length", "has_scheme", "uses_https", "has_ip_host",
                "has_suspicious_term", "query_parameter_count", "parse_ok"]:
        examples[col] = test.loc[idx, col].to_numpy()
    return examples


def write_report(metrics, groups, test, pred, examples, path):
    lines = [
        "# Stage 7 - Final evaluation", "",
        "Random Forest (100 trees), threshold 0.5, trained on the train split only.",
        "Positive = phishing/malware/defacement, negative = benign.", "",
        "## Test results", "", f"Test URLs: {len(test):,}.", "",
        "| Metric | Value |", "|---|---:|",
    ]
    for name in ["accuracy", "precision", "recall", "f1"]:
        lines.append(f"| {name} | {metrics[name]:.6f} |")
    for name in ["true_negative", "false_positive", "false_negative", "true_positive"]:
        lines.append(f"| {name} | {metrics[name]:,} |")

    lines += ["", "## By original label", "", "| Type | URLs | Correct | FN | FP | Correct rate |",
              "|---|---:|---:|---:|---:|---:|"]
    for row in groups.to_dict("records"):
        lines.append(f"| {row['source_type']} | {row['rows']} | {row['correct']} | {row['missed_dangerous']} "
                     f"| {row['false_alarms']} | {row['correct_rate']:.4f} |")

    lines += [
        "", "## Errors compared with correct predictions", "",
        "| Group | n | Median URL length | Has scheme | HTTPS | IP host | Suspicious term |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for outcome in ["TN", "FP", "TP", "FN"]:
        group = test[pred["outcome"] == outcome]
        if len(group):
            lines.append(f"| {outcome} | {len(group)} | {group.url_length.median():.1f} | {group.has_scheme.mean():.4f} "
                         f"| {group.uses_https.mean():.4f} | {group.has_ip_host.mean():.4f} "
                         f"| {group.has_suspicious_term.mean():.4f} |")

    lines += ["", "## Example errors", "", "Up to 5 per error type and label, taken in URL-id order.", ""]
    for row in examples.to_dict("records"):
        lines += [f"- {row['outcome']}, type={row['type']}, p={row['probability']:.4f}, length={row['url_length']}, "
                  f"scheme={row['has_scheme']}, suspicious_term={row['has_suspicious_term']}",
                  "", "```text", json.dumps(row["url"], ensure_ascii=True), "```", ""]

    lines += [
        "## Limitations", "",
        "- Labels come from the dataset and were not checked by visiting the URLs.",
        "- The split keeps domains apart but is not a split by time.",
        "- The probabilities are not calibrated.", "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def save_confusion_matrix(cm, path):
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.imshow(cm, cmap="Blues")
    for (r, c), count in np.ndenumerate(cm):
        color = "white" if count > cm.max() / 2 else "black"
        ax.text(c, r, f"{count:,}", ha="center", va="center", fontsize=15, color=color)
    ax.set(xticks=[0, 1], yticks=[0, 1], xticklabels=["Benign", "Dangerous"],
           yticklabels=["Benign", "Dangerous"], xlabel="Predicted label", ylabel="Actual label",
           title="Test set: Random Forest, threshold 0.5")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def run_stage7():
    """Fit the chosen model, score it on test, save reports and the model."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    # Reuse saved metrics instead of evaluating test again.
    if (REPORT_DIR / "test_metrics.json").exists():
        print("Stage 7 already done, loading the saved results.")
        return json.loads((REPORT_DIR / "test_metrics.json").read_text())

    selection = json.loads(SELECTION_FILE.read_text())
    if selection["selected_model"] != SELECTED_MODEL or selection["selected_threshold"] != SELECTED_THRESHOLD:
        raise ValueError("Stage 5 picked a different model/threshold than SELECTED_MODEL/SELECTED_THRESHOLD.")

    print("Fitting Random Forest on train.")
    train, _, counts = load_train_val()
    model = make_models()[SELECTED_MODEL]
    model.fit(train.loc[:, FEATURE_NAMES], train["target"])
    pipe = RawURLPipeline(model, threshold=SELECTED_THRESHOLD)

    print("Evaluating on test.")
    test = load_test()
    probabilities = pipe.probability_from_features(test.loc[:, FEATURE_NAMES])
    pred = build_prediction_table(test, probabilities)
    pred.to_csv(REPORT_DIR / "test_predictions.csv", index=False)
    metrics = score_predictions(test["target"], probabilities, SELECTED_THRESHOLD)
    groups = subgroup_table(pred)
    groups.to_csv(REPORT_DIR / "test_subgroups.csv", index=False)
    report = classification_report(test["target"], pred["prediction"], labels=[0, 1], output_dict=True,
                                target_names=["benign", "potentially_dangerous"], zero_division=0)
    pd.DataFrame(report).transpose().to_csv(REPORT_DIR / "classification_report.csv", index_label="class_or_average")
    examples = select_error_examples(test, pred)
    examples.to_csv(REPORT_DIR / "error_examples.csv", index=False)
    write_report(metrics, groups, test, pred, examples, REPORT_DIR / "stage-7-evaluation-report.md")
    cm = confusion_matrix(test["target"], pred["prediction"], labels=[0, 1])
    save_confusion_matrix(cm, FIGURE_DIR / "test_confusion_matrix.png")

    model_path = MODEL_DIR / "final_pipeline.joblib"
    joblib.dump(pipe, model_path, compress=3)
    meta = {
        "model": SELECTED_MODEL,
        "model_settings": model.get_params(),
        "threshold": SELECTED_THRESHOLD,
        "feature_names": list(FEATURE_NAMES),
        "label_mapping": TARGET_MAPPING,
        "split_counts": counts,
        "model_sha256": file_sha256(model_path),
    }
    (MODEL_DIR / "model_metadata.json").write_text(json.dumps(meta, indent=2) + "\n")

    # make sure the saved file gives the same answers as the model in memory
    reloaded = load_pipeline(model_path, MODEL_DIR / "model_metadata.json")
    if not np.allclose(reloaded.probability_from_features(test.loc[:, FEATURE_NAMES]), probabilities):
        raise ValueError("Reloaded model gives different probabilities.")

    summary = dict(metrics)
    summary.update({
        "evaluated_at": datetime.now(ZoneInfo("Australia/Melbourne")).isoformat(),
        "model": SELECTED_MODEL,
        "fit_split": "train",
        "evaluation_split": "test",
        "split_counts": counts,
    })
    (REPORT_DIR / "test_metrics.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    print(json.dumps(run_stage7(), indent=2))
