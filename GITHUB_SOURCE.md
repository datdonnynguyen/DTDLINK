# DTDLINK source on GitHub

Repository: https://github.com/datdonnynguyen/DTDLINK (branch `main`).

The current source snapshot includes the completed A2 code, notebooks, aggregate
reports and frozen model, the primary A3 React/FastAPI app, its separate optional
preview, and A3 model-experiment code and aggregate evidence. The primary app
retains the A2 model; no experimental candidate was promoted.

For the main application, follow [assignment3/README.md](assignment3/README.md).
It is self-contained and includes its pinned model and offline Swagger assets.
For the optional preview, follow
[assignment3/experimental-app/README.md](assignment3/experimental-app/README.md).

Installed environments, node_modules, builds, caches, candidate-model artifacts
and generated submission archives are not versioned. Install the declared
dependencies after cloning. Existing course resources and repository history
are retained.

Updated URL-level test predictions/error examples and the research stability
sample remain local. Automated approval review rejected publication of the
updated per-URL evaluation data to this public repo under the code-upload request.
The two previously tracked evaluation CSVs are removed from the current tree,
without deleting local copies or rewriting prior history. Aggregate metrics,
provenance hashes and scripts remain available. The GitHub source tree is not a
byte-for-byte substitute for the separately verified A2 submission ZIP, which
retains the complete local evaluation package.

Inference does not access destination websites, DNS or external analysis services.
Known false-positive limitations and actual AI assistance remain documented in
the application README and research findings.
