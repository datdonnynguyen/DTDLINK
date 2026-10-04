# Week 12

## Current AI-use guidance

AI tools are permitted under the current course clarification recorded on 9 September 2026. Older contrary wording in downloaded materials is legacy content that has not yet been updated. See `../AI_USAGE_NOTE.md`.

## Topic

Software quality and testing: testing levels and types, risk-based planning, systematic test design, test execution and defect reporting, automation, and practical unit-to-acceptance testing with Python.

## What I should learn

- Distinguish verification from validation and functional, non-functional, structural, and change-related testing.
- Select unit, integration, system, and acceptance tests for different risks in the full-stack project.
- Plan testing with scope, environments, data, entry/exit criteria, responsibilities, risks, and traceability.
- Design efficient cases using equivalence partitioning, boundary values, decision tables, state transitions, pairwise combinations, error guessing, and exploratory testing.
- Record actual versus expected results, manage defect severity/priority/lifecycle, and report coverage and outcomes.
- Automate repeatable tests with Python frameworks and use failures to expose gaps in design rather than merely forcing green results.

## Resources

### Week12_lec1-1.pdf

- Type: PDF lecture slides, Part I (25 pages)
- Classification: MUST LEARN; ASSESSMENT RELATED
- Purpose: Establishes testing's role in project success, functional and non-functional test types, test levels, performance/scalability/security/usability/compatibility testing, test plans, strategy, and risk-based prioritisation.
- Required or optional: Required
- Related files: `Week12_lec2.pdf`; `Week12_Workshop.zip`; the team's full-stack project
- Recommended order: 1

### Week12_lec2.pdf

- Type: PDF lecture slides, Part II (23 pages)
- Classification: MUST LEARN; MUST DO; ASSESSMENT RELATED
- Purpose: Covers black-box and experience-based test design, execution phases, defect management, test reports and metrics, automated frameworks, and common automation tools.
- Required or optional: Required
- Related files: `Week12_Workshop.zip`
- Recommended order: 2

### Week12_Workshop.zip

- Type: ZIP workshop project (Python source, README, requirements, and automated tests)
- Classification: MUST DO; ASSESSMENT RELATED
- Purpose: Provides a runnable calculator/user-management system with unit, integration, system, and user-story acceptance tests. The README explains discovery commands and HTML reporting; one unauthenticated-use integration test is deliberately expected to fail to reveal a missing security boundary.
- Required or optional: Required
- Related files: `src/calculator.py`; `src/user_management.py`; `tests/unit/`; `tests/integration/test_user_calculator_integration.py`; `tests/system/test_system.py`; `acceptance_tests/test_acceptance.py`; `requirements.txt`; `Readme.md`
- Recommended order: 3

## Recommended study order

1. Read `Week12_lec1-1.pdf` and create a risk-based test plan for the team's AI web application.
2. Read `Week12_lec2.pdf` and derive representative boundary, partition, state, and interaction cases.
3. Extract `Week12_Workshop.zip` and read `Week12Workshop/Readme.md` before running tests.
4. Trace each unit test to one source function, then trace integration/system/acceptance tests across both source modules.
5. Run all tests, investigate the intentionally failing unauthenticated-calculation case, and decide where authorisation belongs architecturally.
6. Generate a report, add edge cases, and transfer the same layered strategy to the assessed project.

## Resource relationships

`Week12_lec1-1.pdf` -> testing strategy and risk -> `Week12_lec2.pdf` -> test-case design/execution -> `Week12_Workshop.zip`

`src/calculator.py` + `src/user_management.py` -> unit tests -> integration test -> system workflow -> acceptance user stories

Deliberately failing unauthenticated-use test -> exposed security/design gap -> implementation decision -> regression test

## Archive notes

- The ZIP contains 142 entries because it also includes macOS metadata, bytecode, and pytest cache files; the meaningful learning materials are the README, two source modules, requirements, and four test layers.
- The README documents both `unittest` discovery and `pytest` HTML reporting.
- The archive is preserved under its original filename; its internal structure and key source/test files were inspected without modifying them.

## Verification

Every visible Week 12 item was checked. Both PDFs and the workshop ZIP were downloaded and inspected, including the archive structure, README, source-to-test relationships, and intentional failing-test rationale. No other visible Week 12 resource is present.

## Assessment link

`Assessment/Assignment-3-Status.md` records the limited Assignment 3 information currently visible in the syllabus. Its specification, rubric, exact calendar date, and submission page are not yet visible to the student.
