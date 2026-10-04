# COS30049 Course Map

## Current AI-use guidance

AI tools are permitted for this course under the current clarification recorded on 9 September 2026. Older Canvas materials that say otherwise are legacy versions that have not yet been updated. See `AI_USAGE_NOTE.md` and follow any newer dated instruction if one is published.

| Week | Topic | Main theory | Practical work | Important files | Assessment relevance |
|---|---|---|---|---|---|
| 1 | Orientation, project selection and initiation | Project lifecycle, business case, strategic fit, scope, requirements, risk, prototyping | Form a team of three, compare four cybersecurity topics, choose a topic and initial scope | `Course syllabus.pdf`; two Week 1 lecture PDFs; `Week 1 - workshop-1.pdf` | Starts Assignment 1 and fixes the topic used in all three assignments |
| 2 | Scope, time and communication management | Requirements, scope control, WBS/WBS Dictionary, dependencies, milestones and Gantt charts | Build the WBS, schedule and meeting records | `Week2_Scope_Management.pdf`; `Week2_Workshop.pdf` | Core evidence for Assignment 1 scope, schedule and communication |
| 3 | Monitoring, risk, quality, closure and usability | KPIs, change control, risk responses, acceptance criteria, Nielsen heuristics and usability evaluation | Create risk/change/closure artefacts and review the prototype | `Week3_Mornitor_Control_Usability_l1.pdf`; `Week3_Mornitor_Control_Usability_l2.pdf`; `Workshop_03.pdf` | Completes the Assignment 1 plan and prototype rationale |
| 4 | ML lifecycle and cybersecurity preprocessing | Problem framing, dataset quality, cleaning, privacy, regular expressions, feature engineering, scaling and imbalance | General preprocessing plus a security-log pipeline in Jupyter | `Week4_Lecture.pdf`; `Week4_Seminar.pdf`; `Cybersecurity_Preprocessing_Workshop.ipynb`; `synthetic_security_logs.csv` | Assignment 1 operative due date; Assignment 2 data/feature pipeline begins |
| 5 | Data transformation and visual analysis | ETL, pandas joins/reshaping, leakage avoidance, distributions, correlations and reproducible splitting | Run preprocessing and visualisation notebooks on security data | `Week5_Lecture.pdf`; `Week5_Seminar.pdf`; `week5_workshop-1.ipynb`; `Data_visualization-1.ipynb`; `cicids_synthetic_dataset.csv` | Directly supports Assignment 2 processing, analysis and rubric evidence |
| 6 | Regression and K-means | Loss, gradient descent, regression metrics, overfitting, cross-validation, scaling, inertia and silhouette | Type-along model workflow and student notebook on California Housing/Iris | `Week6_Lecture.pdf`; `Week6_Seminar.pdf`; `COS30049_Week6_live_demo.py`; `Week6_Workshop_student_version.ipynb` | Required clustering workflow and evaluation reasoning for Assignment 2 |
| 7 | DBSCAN and classification | Density clustering, logistic regression, KNN, confusion matrix, precision, recall and F1 | DBSCAN on `make_moons`; classification on Breast Cancer; optional trees/forest | `week7_lec.pdf`; `Week7_Seminar-1.pdf`; `Workshop_week7_stu.ipynb` | Final modelling week for Assignment 2; covers both required model families |
| 8 | Web architecture and React | Presentation/application/data layers, CSR/SSR, SPA/MPA, Node/npm, components, JSX, state and rendering | Set up React, modify components and build stateful UI | `Week8_Lecture_01.pdf`; `Week8_Lecture_02.pdf`; `Workshop_08.pdf`; `Basic_Datasets.zip` | Assignment 2 due; Assignment 3 front-end phase begins |
| 9 | UX/UI, Material UI and routing | User-centred design, accessibility, responsive Grid/Flexbox, breakpoints and SPA routes | Build MUI navigation, dark mode, feedback/dialogs/cards and React Router pages | `Week9_lecture01.pdf`; `Week9_Seminar(Lecture02).pdf`; both Week 9 Markdown guides | Assignment 3 usability, presentation and navigation |
| 10 | Back-end development with FastAPI | HTTP methods/messages/status, endpoints versus routes, validation, dependencies, middleware, exceptions and OpenAPI | Create a CRUD-style FastAPI service and test it with Swagger/Postman | `Week10-Lecture-01.pdf`; `Week10-Lecture-02.pdf`; `Week_10_FastAPI&Backend.md` | Assignment 3 API/application-server implementation |
| 11 | Full-stack AI integration and code quality | React API calls, CORS, model serving, D3/Chart.js, debugging, modularity, Git, documentation and refactoring | Build React → FastAPI → AI prediction flow and interactive charts | `Week11_Lecture_01.pdf`; `Week11_Lecture_02.pdf`; `Workshop_11_part_A.md`; `Workshop_11_part_B.md` | Central integration week for Assignment 3 |
| 12 | Software testing | Test levels/types, risk-based strategy, systematic case design, defect lifecycle, reporting and automation | Run unit, integration, system and acceptance tests; analyse an intentional failure | `Week12_lec1-1.pdf`; `Week12_lec2.pdf`; `Week12_Workshop.zip` | Assignment 3 verification, quality evidence and release readiness |

## How the weeks connect

The course is one continuous cybersecurity product rather than twelve isolated topics:

1. Weeks 1–3 define what the team will build, why it matters, how work will be scheduled and controlled, what the interface should communicate, and how success will be accepted.
2. Weeks 4–5 turn raw topic data into a documented feature table. Every later result depends on the quality, privacy, consistency and leakage controls established here.
3. Weeks 6–7 train and interpret the required clustering and classification models, evaluate them with appropriate metrics, and expose weaknesses through comparison and error analysis.
4. Weeks 8–9 turn the prototype into a stateful, responsive React interface with clear navigation and feedback.
5. Week 10 exposes back-end operations through a validated FastAPI contract.
6. Week 11 joins the trained model, API and interface, then visualises predictions and applies debugging and maintainability practices.
7. Week 12 checks the whole product at unit, integration, system and acceptance levels and produces evidence for release readiness.

Assignments mirror that progression: Assignment 1 is the plan and prototype; Assignment 2 is the reproducible model pipeline; Assignment 3 is the tested full-stack product.

## Most important weeks

- Week 4 is the technical foundation: weak raw-data handling or feature extraction cannot be repaired by a sophisticated model later.
- Weeks 6–7 supply the two mandatory Assignment 2 model families and the interpretation/evaluation language used in the rubric.
- Week 8 is both the Assignment 2 deadline and the transition into the website.
- Weeks 10–11 are the architectural core of Assignment 3 because they connect the React UI, FastAPI service and trained model.
- Week 12 provides the quality argument: tests should trace to requirements and risks established in Assignments 1 and 3.

Weeks 1–3 remain essential because they establish the assessed scope, schedule, risks, acceptance criteria, usability rationale and team evidence that govern every technical decision.

## Assessment-related weeks

- Assignment 1 (15%): Weeks 1–3, with the live Canvas due date in Week 4/5 transition. Read `Week-04/Assessment/Assignment-1-Specification.md`.
- Assignment 2 (40%): Weeks 4–7, due at the end of Week 8. Read `Week-08/Assessment/Assignment-2-Specification.md`.
- Assignment 3 (45%): Weeks 8–12 plus Week 13 submission work. Only the syllabus-level record is currently visible; see `Week-12/Assessment/Assignment-3-Status.md`.

The hurdle requires at least 40% on each of the three assignments and at least 50% overall. No quiz is visible in the COS30049 Assignments or Modules pages.

## Files to prioritise

1. `ASSESSMENTS.md` and the two visible assignment-specification Markdown files.
2. `Week-08/Assessment/Basic_Datasets.zip`; select only the folder matching the team's Assignment 2 topic.
3. `Week-04/Workshop/Cybersecurity_Preprocessing_Workshop.ipynb` with `Week-04/Dataset/synthetic_security_logs.csv`, then compare with the solution notebook.
4. `Week-05/Workshop/week5_workshop-1.ipynb` and `Data_visualization-1.ipynb` for the reproducible analysis pipeline.
5. `Week-06/Workshop/Week6_Workshop_student_version.ipynb` and `Week-07/Workshop/Workshop_week7_stu.ipynb` for required clustering/classification practice.
6. The two Week 9 Markdown tutorials, `Week_10_FastAPI&Backend.md`, and both Week 11 workshop guides; these contain copyable full-stack source examples.
7. `Week12_Workshop.zip` for the layered testing structure and deliberate security-related failing test.

## Missing, inaccessible or inconsistent resources

- Week 7: `Workshop_week7_Solution.ipynb` is named on the page but has no link or download control.
- Week 9: `react-mui-demo.zip` is named without a link. The two Markdown guides contain the implementation.
- Week 10: standalone `main.py` is named without a link. Its complete FastAPI source is embedded in `Week_10_FastAPI&Backend.md`.
- Week 11: `full-stack-demo.zip` and `react-d3-demo.zip` are named without links. Both implementations are embedded in the workshop Markdown files.
- Assignment 3: the syllabus lists its 45% weight and Week 13 deadline, but no student-visible assignment page, exact date, submission specification, files or rubric is currently available.
- Week 7's Canvas link label suggests a PPTX (`week7_lec-preview.pptx`), but Canvas supplied only `week7_lec.pdf`; the actual PDF is stored.
- The downloadable syllabus has an older Assignment 1 schedule. The live assignment page's 2 September 2026, 23:59 AEST date is the operative one.
- `Basic_Datasets.zip` and `Week12_Workshop.zip` contain macOS metadata/cache entries in addition to the meaningful course data and code; do not copy those artefacts into assignment submissions.

## Navigation

- `DOWNLOAD_MANIFEST.md` confirms all twelve weeks are complete.
- Every week folder contains `WEEK_SUMMARY.md` with resource purpose, classification, relationships and recommended study order.
- `ASSESSMENTS.md` consolidates weights, dates, requirements, downloaded templates and visibility gaps.
