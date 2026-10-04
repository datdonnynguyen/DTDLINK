# Week 9

## Current AI-use guidance

AI tools are permitted under the current course clarification recorded on 9 September 2026. Older contrary wording in downloaded materials is legacy content that has not yet been updated. See `../AI_USAGE_NOTE.md`.

## Topic

User-centred UX/UI, responsive front-end implementation with Material UI, and page navigation in React single-page applications using React Router.

## What I should learn

- Distinguish UX from UI and apply consistency, simplicity, feedback, accessibility, and responsive-design principles.
- Select and customise Material UI components rather than treating a component library as a substitute for design decisions.
- Build responsive layouts with containers, Grid/Flexbox, spacing, and breakpoints.
- Implement app bars, drawers, cards, forms, dialogs, snackbars, themes, and dark mode.
- Configure React Router, define routes, and add navigation links without full-page reloads.
- Turn the Week 8 starter project into a structured, navigable interface for the team project.

## Resources

### Week9_lecture01.pdf

- Type: PDF lecture slides (18 pages)
- Classification: MUST LEARN; ASSESSMENT RELATED
- Purpose: Introduces UX/UI roles and principles, explains why Material UI should be grounded in user needs, surveys React component libraries, and previews responsive layouts, React Router, and later API calls.
- Required or optional: Required
- Related files: `Week9_Seminar(Lecture02).pdf`; both workshop guides
- Recommended order: 1

### Week9_Seminar(Lecture02).pdf

- Type: PDF seminar slides (29 pages)
- Classification: MUST LEARN; MUST DO; ASSESSMENT RELATED
- Purpose: Demonstrates Material UI's design system, component library, Grid/Flexbox layouts, breakpoints, app bars, `sx` styling, and React Router concepts for SPA navigation.
- Required or optional: Required
- Related files: `Week 9 - MUI React Project Setup and Demo.md`; `Week 9 - Additional Resource for Router.md`
- Recommended order: 2

### Week 9 - MUI React Project Setup and Demo.md

- Type: Markdown workshop/tutorial with complete React code
- Classification: MUST DO; ASSESSMENT RELATED
- Purpose: Builds a `react-mui-demo` project incrementally: MUI installation, AppBar, Drawer, dark mode, feedback Snackbar, contact Dialog, cards/grid, form controls, footer, floating action button, ThemeProvider, and CssBaseline.
- Required or optional: Required
- Related files: Week 8 environment setup; `Week 9 - Additional Resource for Router.md`; the locally created React project
- Recommended order: 3

### Week 9 - Additional Resource for Router.md

- Type: Markdown extension tutorial with complete React code
- Classification: MUST DO; ASSESSMENT RELATED
- Purpose: Extends the MUI demo with `react-router-dom`, `BrowserRouter`, `Routes`, an About component, and navigation from the Drawer and AppBar.
- Required or optional: Required extension
- Related files: `Week 9 - MUI React Project Setup and Demo.md`
- Recommended order: 4

### react-mui-demo.zip

- Type: Mentioned sample-solution archive
- Classification: REFERENCE
- Purpose: Intended completed sample project corresponding to the Markdown tutorial.
- Required or optional: Reference
- Related files: Both Week 9 Markdown guides
- Recommended order: After completing the tutorial independently
- Availability: The filename is visible on the page, but it has no link or download control and could not be accessed.

## External resources not downloaded

- Title: Material UI documentation
- URL: https://mui.com/getting-started/usage/
- Purpose: Component setup and usage reference for the workshop project.
- Week: 9
- Title: React documentation
- URL: https://reactjs.org/docs/getting-started.html
- Purpose: General React reference cited by the workshop guide.
- Week: 9
- Title: MUI Breakpoints
- URL: https://mui.com/material-ui/customization/breakpoints/
- Purpose: Responsive-layout reference cited in the seminar.
- Week: 9

## Recommended study order

1. Read `Week9_lecture01.pdf` and frame the interface around user needs and accessibility.
2. Read `Week9_Seminar(Lecture02).pdf` while identifying which components and responsive patterns the team project needs.
3. Follow `Week 9 - MUI React Project Setup and Demo.md` step by step in the Week 8 React environment.
4. Add routing with `Week 9 - Additional Resource for Router.md`.
5. Test the interface at multiple breakpoints and check keyboard-accessible navigation and feedback.
6. Adapt the demo structure to the team's real project rather than copying cosmetic choices unchanged.

## Resource relationships

Week 8 React setup -> `Week9_lecture01.pdf` -> `Week9_Seminar(Lecture02).pdf` -> MUI workshop Markdown -> Router Markdown -> team-project front end

## Verification

Every visible Week 9 item was checked. Four downloadable files were saved and inspected. `react-mui-demo.zip` is mentioned as a sample solution but is plain text without a link or download control, so it is recorded as inaccessible.
