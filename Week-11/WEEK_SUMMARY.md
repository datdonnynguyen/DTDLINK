# Week 11

## Current AI-use guidance

AI tools are permitted under the current course clarification recorded on 9 September 2026. Older contrary wording in downloaded materials is legacy content that has not yet been updated. See `../AI_USAGE_NOTE.md`.

## Topic

Full-stack integration of a React front end, FastAPI back end, and AI model; browser-based data visualisation; systematic debugging; and maintainable team-development practices.

## What I should learn

- Trace data from a React event through an HTTP request, FastAPI route, model prediction, JSON response, state update, and chart.
- Choose between XMLHttpRequest, Fetch, and Axios and handle loading and error states.
- Configure CORS for the front-end origin and expose a trained model through a validated API.
- Build interactive visualisations with Chart.js or D3.js and preserve clarity, information, and interpretability.
- Debug React, FastAPI, network requests, validation, and cross-origin errors systematically.
- Structure front-end and back-end code into focused modules, use version control well, document decisions, review code, and refactor duplication.

## Resources

### Week11_Lecture_01.pdf

- Type: PDF lecture slides (43 pages)
- Classification: MUST LEARN; MUST DO; ASSESSMENT RELATED
- Purpose: Connects React to FastAPI using browser API calls, introduces D3.js and Chart.js, walks through a full-stack AI-prediction flow, CORS, and common integration failures.
- Required or optional: Required
- Related files: `Workshop_11_part_A.md`; `Workshop_11_part_B.md`; Weeks 6–7 models; Weeks 8–10 web stack
- Recommended order: 1

### Week11_Lecture_02.pdf

- Type: PDF lecture slides (23 pages)
- Classification: MUST LEARN; ASSESSMENT RELATED
- Purpose: Covers repeatable debugging for React/FastAPI/full-stack failures and code-quality practices: formatting, project structure, Git workflow, documentation, complexity control, code review, and refactoring.
- Required or optional: Required
- Related files: Both workshop guides; the team's assignment repository
- Recommended order: 2

### Workshop_11_part_A.md

- Type: Markdown full-stack workshop with embedded Python and React source
- Classification: MUST DO; ASSESSMENT RELATED
- Purpose: Builds a two-part application: a scikit-learn linear-regression model and FastAPI prediction endpoint in `backend/`, then a React/MUI/Chart.js interface in `frontend/`. Includes CORS, Axios calls, charting, testing/debugging, validation/logging extensions, and improvement ideas.
- Required or optional: Required; optimisation section is an advanced extension
- Related files: `backend/model.py`, `backend/main.py`, generated `simple_model.pkl`, `frontend/src/App.js`; Weeks 6, 8, 9, and 10
- Recommended order: 3

### Workshop_11_part_B.md

- Type: Markdown React/D3 workshop with embedded JavaScript and JSON
- Classification: MUST DO; REFERENCE; ASSESSMENT RELATED
- Purpose: Builds a reusable `D3Chart` component supporting a file-backed bar chart, multi-dimensional line chart, interactive pie chart, and zoomable sunburst. Explains hooks, SVG construction, scales, axes, transitions, data loading, file structure, and troubleshooting.
- Required or optional: Required visualisation practice; advanced chart types may be treated as reference
- Related files: `src/App.js`, `src/D3Chart.js`, `public/data/barChartData.json`; `Week11_Lecture_01.pdf`
- Recommended order: 4

### full-stack-demo.zip

- Type: Mentioned sample-solution archive
- Classification: REFERENCE; ASSESSMENT RELATED
- Purpose: Intended packaged version of the Part A React/FastAPI/AI example.
- Required or optional: Reference
- Related files: `Workshop_11_part_A.md`
- Recommended order: After completing Part A
- Availability: Visible as text only; no link or download control is provided.

### react-d3-demo.zip

- Type: Mentioned sample-solution archive
- Classification: REFERENCE
- Purpose: Intended packaged version of the Part B D3 application.
- Required or optional: Reference
- Related files: `Workshop_11_part_B.md`
- Recommended order: After completing Part B
- Availability: Visible as text only; no link or download control is provided.

## External resources not downloaded

- Title: Local React application
- URL: http://localhost:3000
- Purpose: Runs the workshop front end and sends prediction requests to FastAPI.
- Week: 11
- Title: Local FastAPI prediction service
- URL: http://localhost:8000
- Purpose: Serves the trained model's prediction endpoint for the React application.
- Week: 11

## Recommended study order

1. Revisit the Week 6 regression workflow and Weeks 8–10 React/FastAPI foundations.
2. Read `Week11_Lecture_01.pdf` and draw the end-to-end request/data flow.
3. Read `Week11_Lecture_02.pdf` and adopt its debugging and project-structure checklist.
4. Build and test `Workshop_11_part_A.md`, keeping model, API, and UI code in separate modules.
5. Build `Workshop_11_part_B.md` and verify the external JSON file loads before adding complex charts.
6. Apply the same integration, validation, error handling, visualisation, documentation, and refactoring practices to the assessed team project.

## Resource relationships

Week 6/7 AI model -> Week 10 FastAPI -> `Workshop_11_part_A.md` backend -> React/Axios -> Chart.js result visualisation

`Workshop_11_part_B.md` -> `barChartData.json` -> D3 component -> interactive charts

`Week11_Lecture_02.pdf` -> debugging and quality -> both workshop applications -> assignment-quality repository

## Verification

Every visible Week 11 item was checked. Four downloadable files were saved and inspected. Both sample ZIP filenames are visible without links, so they are recorded as inaccessible; their implementation details remain available in the Markdown tutorials.
