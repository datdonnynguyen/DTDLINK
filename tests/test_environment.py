"""Small Stage 0 checks that do not read or analyse the project dataset."""

from urllib.parse import urlsplit

import joblib
import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
import sklearn
import tldextract
from sklearn.tree import DecisionTreeClassifier


def test_required_libraries_import() -> None:
    """Confirm that the main Assignment 2 libraries can be imported."""
    assert np.__version__
    assert pd.__version__
    assert sklearn.__version__
    assert joblib.__version__
    assert matplotlib.__version__
    assert sns.__version__
    assert tldextract.__version__


def test_toy_data_can_flow_through_a_model() -> None:
    """Verify pandas and scikit-learn work together using harmless toy data."""
    features = pd.DataFrame(
        {
            "url_length": [12, 18, 72, 95],
            "has_at_symbol": [0, 0, 1, 1],
        }
    )
    labels = np.array([0, 0, 1, 1])

    model = DecisionTreeClassifier(max_depth=1, random_state=42)
    model.fit(features, labels)

    predictions = model.predict(features)
    assert predictions.tolist() == labels.tolist()


def test_python_can_split_url_text_without_visiting_it() -> None:
    """Confirm the standard parser separates URL text locally."""
    parsed = urlsplit(
        "https://accounts.example.test/login/reset?source=email"
    )

    assert parsed.scheme == "https"
    assert parsed.hostname == "accounts.example.test"
    assert parsed.path == "/login/reset"
    assert parsed.query == "source=email"
