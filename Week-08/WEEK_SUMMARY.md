# Week 8

## Current AI-use guidance

AI tools are permitted under the current course clarification recorded on 9 September 2026. Older contrary wording in downloaded materials is legacy content that has not yet been updated. See `../AI_USAGE_NOTE.md`.

## Topic

Web-application architecture and front-end development with HTML, CSS, JavaScript, Node.js, and React, followed by hands-on React setup, JSX rendering, and state management.

## What I should learn

- Describe the presentation, application, and data layers of a web application.
- Compare client-side and server-side rendering and single-page versus multi-page applications.
- Explain the roles of HTML, CSS, JavaScript, React, Node.js, npm, and `npx`.
- Navigate the main folders and files in a React project.
- Build reusable React components with JSX and understand one-way data flow.
- Use `useState` to create interactive interfaces and explain why state changes trigger re-rendering.

## Resources

### Week8_Lecture_01.pdf

- Type: PDF lecture slides (25 pages)
- Classification: MUST LEARN; ASSESSMENT RELATED
- Purpose: Introduces web-application layers, HTTP-driven browser rendering, CSR/SSR, SPA/MPA, front-end foundations, React, Node.js, and why Node/npm are used in React development.
- Required or optional: Required
- Related files: `Week8_Lecture_02.pdf`; `Workshop_08.pdf`
- Recommended order: 1

### Week8_Lecture_02.pdf

- Type: PDF seminar slides (27 pages)
- Classification: MUST LEARN; MUST DO; ASSESSMENT RELATED
- Purpose: Develops React in practice: components, styling, event handling, local state, conditional rendering, one-way data flow, project structure, JSX, rendering, and re-rendering. Points to MUI, Flexbox, Grid, and breakpoint references.
- Required or optional: Required
- Related files: `Week8_Lecture_01.pdf`; `Workshop_08.pdf`
- Recommended order: 2

### Workshop_08.pdf

- Type: PDF workshop guide (7 pages)
- Classification: MUST DO; ASSESSMENT RELATED
- Purpose: Guides Node.js/npm installation and verification, creation of a React project with Create React App, exploration of its folders, replacement of the default component, and construction of a stateful counter plus extension exercises.
- Required or optional: Required
- Related files: Both Week 8 lecture PDFs; the React project students create locally
- Recommended order: 3

### Assignment 2 resources

- `Assessment/Assignment-2-Specification.md` — ASSESSMENT RELATED; local record of deliverables, mandatory modelling rules, external links, and the 40-point rubric.
- `Assessment/Basic_Datasets.zip` — MUST DO; ASSESSMENT RELATED; 201 MB course-provided archive containing the four project topics' raw inputs and labels.
- `Assessment/Group Assessment Contribution Form-1.docx` — MUST DO; updated task/contribution/signature form for the team submission.
- Relationship: Weeks 4–7 preprocessing/modelling -> topic-specific folder in `Basic_Datasets.zip` -> final processed dataset/model/code/report -> Assignment 2.

## External resources not downloaded

- Title: Node.js downloads/package manager
- URL: https://nodejs.org/en/download/package-manager
- Purpose: Install the Node.js runtime and npm required for the workshop.
- Week: 8
- Title: MUI documentation
- URL: https://mui.com/material-ui/getting-started/
- Purpose: Reference for React UI components.
- Week: 8
- Title: CSS-Tricks Complete Guide to Flexbox
- URL: https://css-tricks.com/snippets/css/a-guide-to-flexbox/
- Purpose: Reference for flexible page layouts.
- Week: 8
- Title: MUI Grid
- URL: https://mui.com/material-ui/react-grid/
- Purpose: Reference for responsive grid layouts.
- Week: 8
- Title: MUI Breakpoints
- URL: https://mui.com/material-ui/customization/breakpoints/
- Purpose: Reference for responsive design thresholds.
- Week: 8
- Title: MUI Link
- URL: https://mui.com/material-ui/react-link/
- Purpose: Reference for styled links in React.
- Week: 8
- Title: React Playground
- URL: https://playcode.io/react
- Purpose: Browser-based environment for experimenting with React without a local project.
- Week: 8

## Recommended study order

1. Read `Week8_Lecture_01.pdf` to understand the web architecture and toolchain.
2. Read `Week8_Lecture_02.pdf`, concentrating on components, JSX, state, and render cycles.
3. Follow `Workshop_08.pdf` to install/verify Node.js and create the project.
4. Replace the starter interface and confirm saved changes trigger a re-render.
5. Build the counter and name-input extensions with `useState`.
6. Use the external layout/UI references while shaping the project interface.

## Resource relationships

`Week8_Lecture_01.pdf` -> web architecture and toolchain -> `Week8_Lecture_02.pdf` -> React concepts -> `Workshop_08.pdf` -> locally created React project

## Verification

Every visible Week 8 learning item was checked. All three course PDFs were downloaded and inspected. The separate Assignment 2 page was also inspected, and its base-dataset archive plus updated contribution form were downloaded into `Assessment/`.
