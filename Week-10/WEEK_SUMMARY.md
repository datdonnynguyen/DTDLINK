# Week 10

## Current AI-use guidance

AI tools are permitted under the current course clarification recorded on 9 September 2026. Older contrary wording in downloaded materials is legacy content that has not yet been updated. See `../AI_USAGE_NOTE.md`.

## Topic

Back-end development and HTTP APIs with FastAPI: request/response structure, routes and endpoints, Pydantic validation, dependency injection, middleware, error handling, background tasks, and API testing.

## What I should learn

- Explain how the browser/client, web server, application server, and database interact.
- Read HTTP methods, URLs, headers, bodies, status codes, and JSON responses.
- Distinguish an API endpoint from the method-specific routes that operate on it.
- Build FastAPI path operations for GET, POST, PUT, and DELETE.
- Validate request data with Pydantic and use dependencies, middleware, and `HTTPException` safely.
- Run the application with Uvicorn and test it through Swagger UI and Postman.
- Connect this back end to the React interface developed in Weeks 8–9.

## Resources

### Week10-Lecture-01.pdf

- Type: PDF lecture slides (23 pages)
- Classification: MUST LEARN; ASSESSMENT RELATED
- Purpose: Introduces back-end responsibilities, server/application/database layers, HTTP requests and responses, status codes, APIs, endpoints, routes, and the security importance of method-specific code paths.
- Required or optional: Required
- Related files: `Week10-Lecture-02.pdf`; `Week_10_FastAPI&Backend.md`
- Recommended order: 1

### Week10-Lecture-02.pdf

- Type: PDF seminar slides (28 pages)
- Classification: MUST LEARN; MUST DO; ASSESSMENT RELATED
- Purpose: Develops FastAPI with Starlette/Uvicorn, path operations, Pydantic models, dependency injection, middleware, exception handling, Swagger/OpenAPI, Postman, and a CRUD-style demonstration. Explicitly links FastAPI to the application-server component required by the course assignment.
- Required or optional: Required
- Related files: `Week_10_FastAPI&Backend.md`; the `main.py` implementation embedded in the guide
- Recommended order: 2

### Week_10_FastAPI&Backend.md

- Type: Markdown workshop/tutorial with a complete embedded Python application
- Classification: MUST DO; ASSESSMENT RELATED
- Purpose: Provides the full FastAPI demo and guided tests for GET/POST/PUT/DELETE, Swagger UI, and Postman. Extension tasks cover custom response headers, path-plus-query parameters, background tasks, and response inspection.
- Required or optional: Required
- Related files: Both Week 10 lecture PDFs; `main.py` reconstructed from its embedded code; Weeks 8–9 React front end
- Recommended order: 3

### main.py

- Type: Mentioned Python sample solution
- Classification: REFERENCE; ASSESSMENT RELATED
- Purpose: Intended runnable FastAPI demo corresponding to the code in `Week_10_FastAPI&Backend.md`.
- Required or optional: Reference
- Related files: `Week_10_FastAPI&Backend.md`
- Recommended order: After reading the guide
- Availability: The filename is visible on the page but has no link or download control. The workshop Markdown nevertheless contains the complete application code needed to create it locally.

## External resources not downloaded

- Title: FastAPI documentation / generated Swagger UI
- URL: http://127.0.0.1:8000/docs
- Purpose: Local interactive API documentation and endpoint testing once the student's server is running.
- Week: 10
- Title: Postman
- URL: https://www.postman.com/
- Purpose: Install the API client used to exercise methods, bodies, headers, and responses.
- Week: 10

## Recommended study order

1. Read `Week10-Lecture-01.pdf` and trace one request through every architecture layer.
2. Read `Week10-Lecture-02.pdf`, focusing on how FastAPI maps types and decorators to an API contract.
3. Work through `Week_10_FastAPI&Backend.md` and create `main.py` from the embedded example.
4. Run the server with Uvicorn and exercise every route in Swagger UI.
5. Repeat the tests in Postman, checking status codes, response bodies, and headers.
6. Complete the extension routes and then connect the API contract to the Week 9 React interface.

## Resource relationships

`Week10-Lecture-01.pdf` -> HTTP/back-end architecture -> `Week10-Lecture-02.pdf` -> FastAPI design -> `Week_10_FastAPI&Backend.md` -> locally created `main.py` -> Swagger/Postman tests -> React integration

## Verification

Every visible Week 10 item was checked. Three downloadable files were saved and inspected. `main.py` is mentioned without a link, but its full source is embedded in the workshop guide; the missing standalone copy is recorded explicitly.
