# Workshop 10

## Table of Contents

- [Objective](#objective)
- [Learning Outcomes](#learning-outcomes)
- [Workshop Structure](#workshop-structure)
  1. [Recap of Lecture Content (10 mins)](#recap-of-lecture-content-10-mins)
  2. [Configuration and Setup (15 mins)](#configuration-and-setup-15-mins)
  3. [Run the Demo (60 mins)](#run-the-demo-60-mins)
  4. [Break Time (5 mins)](#break-time-5-mins)
  5. [Extension Tasks (30 mins)](#extension-tasks-30-mins)
     - [Task 1: Create a Custom Path with Response Headers](#task-1-create-a-custom-path-with-response-headers)
     - [Task 2: Path and Query Parameter Combination](#task-2-path-and-query-parameter-combination)
     - [Task 3: Handling Background Tasks](#task-3-handling-background-tasks)
     - [Task 4: Test the Custom Path with Postman](#task-4-test-the-custom-path-with-postman)



## Objective:

The primary objective of this workshop is to provide students with hands-on experience in setting up and using FastAPI, a modern Python web framework, and Postman, a popular API testing tool. By the end of the workshop, students will understand how to configure their environment, run a FastAPI server, and use Postman and Swagger to interact with and test API endpoints.



## Learning Outcomes:

By the end of this workshop, students will be able to:
- Set up and configure a local development environment for **FastAPI**.
- Understand the basic components and structure of a FastAPI application.
- Run a provided FastAPI demo application and test its endpoints.
- Use Postman to create and manage HTTP requests for testing API functionality.
- Use **Swagger UI** to test the FastAPI demo application.
- Interpret and debug API responses using Postman tools.
- Apply error handling and middleware techniques in FastAPI for robust API development.



## Workshop Structure:

### 1. Recap of Lecture Content (10 mins)
**Overview of FastAPI:**
- Brief recap of FastAPI’s main components: path operations, dependency injection, middleware, and exception handling.
- Explanation of ASGI and the role of Uvicorn as the server to run FastAPI applications.

**Introduction to Postman:**
- Recap on what Postman is, its core features, and why it is essential for API testing.
- Overview of Postman’s interface: creating requests, managing collections, and using environments.



### 2. Configuration and Setup (15 mins)

- **Install Python (Version 3.7+):** Ensure Python is installed on your system. Use the command `python --version` to check.
- **Install FastAPI and Uvicorn:** Open your terminal and run:
    ```
    pip install fastapi uvicorn
    ```

- **Install Postman:**
  - Download and install Postman from [Postman’s Official Website](https://www.postman.com/).
  - Brief walkthrough of setting up a new account and navigating the interface.



### 3. Run the Demo (60 mins)
**(1) Understanding the Demo Application (Main.py):**

> **Step 1: Importing Necessary Modules**
>
> ```python
> from fastapi import FastAPI, HTTPException, Depends, Request
> from pydantic import BaseModel
> from fastapi.responses import JSONResponse
> from fastapi import BackgroundTasks
> import time
> ```
>
> ​	•	FastAPI: Used to create the API instance.
>
> ​	•	HTTPException: Used to raise HTTP exceptions.
>
> ​	•	Depends: For injecting dependencies into path operations.
>
> ​	•	Request: To access request data.
>
> ​	•	JSONResponse: To send custom JSON responses.
>
> ​	•	BackgroundTasks: To handle background tasks.
>
> ​	•	time: To simulate time delays.
>
> **Step 2: Creating a FastAPI Instance**
>
> ```python
> app = FastAPI()
> ```
>
> **Step 3: Defining a Pydantic Model**
>
> The Pydantic model is used for data validation, ensuring that requests conform to the expected structure.
>
> ```python
> class Item(BaseModel):
>     name: str
>     price: float
>     is_offer: bool = None
> ```
>
> ​	•	Item: A data model for an item, requiring name, price, and an optional is_offer field.
>
> **Step 4: Simulating a Database Connection (Dependency)**
>
> This function simulates a connection to a database and will be injected into various path operations.
>
> ```python
> def get_db():
>     return {"db": "Simulated database connection"}
> ```
>
> **Step 5: Middleware to Log Request Processing Time**
>
> Middleware that logs how long each request takes to process.
>
> ```python
> @app.middleware("http")
> async def log_requests(request: Request, call_next):
>     start_time = time.time()
>     response = await call_next(request)
>     process_time = time.time() - start_time
>     print(f"Request: {request.url} - Duration: {process_time} seconds")
>     return response
> ```
>
> ​	•	Logs the time taken to process each request and prints it to the console.
>
> **Step 6: Exception Handling for HTTP Exceptions**
>
> Custom handler for HTTPException, providing a JSON response with additional error details.
>
> ```python
> @app.exception_handler(HTTPException)
> async def http_exception_handler(request: Request, exc: HTTPException):
>     return JSONResponse(
>         status_code=exc.status_code,
>         content={"detail": exc.detail, "error": "An error occurred"}
>     )
> ```
>
> **Step 7: GET Request to Fetch an Item by ID**
>
> Path operation that fetches an item by its item_id. If the item is not found, a 404 error is raised.
>
> ```python
> @app.get("/items/{item_id}")
> def get_item(item_id: int, db=Depends(get_db)):
>     if item_id not in [1, 2, 3]:  # Simulate item check
>         raise HTTPException(status_code=404, detail="Item not found")
>     return {"item_id": item_id, "db_connection": db["db"]}	
> ```
>
> ​	•	Simulates fetching an item from the database and returns the item ID.
>
> **Step 8: POST Request to Create a New Item**
>
> ```python
> @app.post("/items/")
> def create_item(item: Item, db=Depends(get_db)):
>     return {"item": item, "db_connection": db["db"]}
> ```
>
> **Step 9: PUT Request to Update an Existing Item**
>
> Path operation to update an existing item based on its item_id.
>
> ```python
> @app.put("/items/{item_id}")
> def update_item(item_id: int, item: Item, db=Depends(get_db)):
>     if item_id not in [1, 2, 3]:
>         raise HTTPException(status_code=404, detail="Item not found")
>     return {"item_id": item_id, "updated_item": item, "db_connection": db["db"]}
> ```
>
> **Step 10: DELETE Request to Remove an Item**
>
> Path operation to delete an item based on its item_id.
>
> ```python
> @app.delete("/items/{item_id}")
> def delete_item(item_id: int, db=Depends(get_db)):
>     if item_id not in [1, 2, 3]:
>         raise HTTPException(status_code=404, detail="Item not found")
>     return {"detail": "Item deleted", "item_id": item_id, "db_connection": db["db"]}
> ```
>
> **Step 11: Custom Path with Response Headers**
>
> Path operation created by the student to return custom headers along with a success message.
>
> ```python
> @app.get("/info/")
> def get_info():
>     headers = {"X-Info-Version": "1.0", "X-Student-Task": "Create Custom Path"}
>     return JSONResponse(content={"message": "Custom path created successfully!"}, headers=headers)
> ```
>
> **Step 12: GET Request with Query Parameter for Discount**
>
> Path operation to retrieve an item with an optional discount query parameter.
>
> ```python
> @app.get("/items/{item_id}/with-discount/")
> def get_item_with_discount(item_id: int, discount: float = None, db=Depends(get_db)):
>     if item_id not in [1, 2, 3]:
>         raise HTTPException(status_code=404, detail="Item not found")
>     item = {"item_id": item_id, "price": 100.0}  # Simulated item with price
>     if discount:
>         item["discounted_price"] = item["price"] * (1 - discount)
>     return {"item": item, "db_connection": db["db"]}
> ```
>
> ​	•	Fetches an item and optionally calculates the discounted price if the discount query parameter is provided.
>
> **Step 13: Background Task Simulation**
>
> This function simulates a long-running task such as sending an email.
>
> ```python
> def background_task(item_id: int):
>     time.sleep(5)  # Simulate long task
>     print(f"Background task completed for item {item_id}")
> ```
>
> **Step 14: POST Request to Trigger a Background Task**
>
> Path operation to trigger the background task for a given item_id.
>
> ```python
> @app.post("/items/{item_id}/background-task/")
> def run_background_task(item_id: int, background_tasks: BackgroundTasks, db=Depends(get_db)):
>     background_tasks.add_task(background_task, item_id)
>     return {"message": "Background task started", "item_id": item_id, "db_connection": db["db"]}
> ```
>
> ​	•	This starts the background task and immediately returns a response.

**(2) Test the Demo Application with Postman:**

In this session, we will test the FastAPI demo application using **Postman**. We will go through the following HTTP methods:
- **GET**: Retrieve data from the server.
- **POST**: Submit new data to the server.
- **PUT**: Update existing data.
- **DELETE**: Delete data from the server.

>**1. Setup**
>
>Before we start, ensure that your FastAPI server is running locally. If it's not running, start it using the command:
>
>```bash
>uvicorn main:app --reload
>```
>
>The application will be available at http://127.0.0.1:8000.
>
>**2. Testing with GET Request**
>
>The **GET** request is used to retrieve data from the server.
>
>***Example: Retrieve an Item***
>
>In Postman:
>
>1. Open Postman and create a new **GET** request.
>
>	2.	Set the request URL to:
>
>    ```
>    http://127.0.0.1:8000/items/1
>    ```
>
>    (This fetches the item with ID 1.)
>
>	3.	Click **Send**.
>
>***Response:***
>
>You should get a response similar to:
>
>```json
>{
>  "item_id": 1,
>  "db_connection": "Simulated database connection"
>}
>```
>
>**3. Testing with POST Request**
>
>The **POST** request is used to submit new data to the server.
>
>***Example: Create a New Item***
>
>In Postman:
>
>1. Create a new **POST** request.
>
> 2. Set the request URL to:
>
>    ```
>    http://127.0.0.1:8000/items/
>    ```
>
>3. In the **Body** tab, select **raw** and choose **JSON** format. Add the following JSON payload:
>
>   ```json
>   {
>     "name": "New Item",
>     "price": 19.99,
>     "is_offer": true
>   }
>   ```
>
>4. Click **Send**.
>
>***Response:***
>
>You should get a response like:
>
>```json
>{
>  "item": {
>    "name": "New Item",
>    "price": 19.99,
>    "is_offer": true
>  },
>  "db_connection": "Simulated database connection"
>}
>```
>
>**4. Testing with PUT Request**
>
>The **PUT** request is used to update existing data on the server.
>
>***Example: Update an Existing Item***
>
>In Postman:
>
>1. Create a new **PUT** request.
>
>	2.	Set the request URL to:
>
>    ```
>    http://127.0.0.1:8000/items/1
>    ```
>
>    (This updates the item with ID 1.)
>
>	3.	In the **Body** tab, select **raw** and choose **JSON** format. Add the following JSON payload to update the item:
>
>    ```json
>    {
>      "name": "Updated Item",
>      "price": 29.99,
>      "is_offer": false
>    }
>    ```
>
>4. Click **Send**.
>
>***Response:***
>
>You should get a response like:
>
>```json
>{
>  "item_id": 1,
>  "updated_item": {
>    "name": "Updated Item",
>    "price": 29.99,
>    "is_offer": false
>  },
>  "db_connection": "Simulated database connection"
>}
>```
>
>**5. Testing with DELETE Request**
>
>The **DELETE** request is used to remove data from the server.
>
>***Example: Delete an Item***
>
>In Postman:
>
>1. Create a new **DELETE** request.
>
>	2.	Set the request URL to:
>
>    ```
>    http://127.0.0.1:8000/items/1
>    ```
>
>    (This deletes the item with ID 1.)
>
>	3.	Click **Send**.
>
>***Response:***
>
>You should get a response like:
>
>```json
>{
>  "detail": "Item deleted",
>  "item_id": 1,
>  "db_connection": "Simulated database connection"
>}
>```

**(3) Testing FastAPI Demo Application with Swagger UI**

In this session, we will learn how to use **Swagger UI** to test the FastAPI demo application. Swagger UI is an interactive interface automatically provided by FastAPI that allows us to test API endpoints directly from the browser.

>**1. Accessing Swagger UI**
>
>Once your FastAPI application is running, Swagger UI will be available at the following URL:
>
>```
>http://127.0.0.1:8000/docs
>```
>
>To start the application, run the following command in your terminal:
>
>```bash
>uvicorn main:app --reload
>```
>
>This will start the FastAPI application, and Swagger UI will automatically generate documentation for all available endpoints.
>
>**2. Overview of Swagger UI**
>
>Swagger UI provides an easy way to interact with and test your API:
>
>​	•	**Available Endpoints**: A list of all available API endpoints.
>
>​	•	**Try it out**: A button that allows you to test any endpoint interactively.
>
>​	•	**Response details**: Shows the status code, headers, and body returned from the API call.
>
>**3. Testing with GET Request in Swagger UI**
>
>***Example: Retrieve an Item by ID***
>
>	1.	Open Swagger UI at http://127.0.0.1:8000/docs.
>	1.	In the list of available operations, find the **GET** request for /items/{item_id}.
>
>	3.	Click on the **GET** request to expand it.
>	3.	Click the **Try it out** button.
>
>	5.	Enter a valid item_id, for example 1, in the input box.
>	5.	 Click **Execute**.
>
>***Response:***
>
>Swagger will display the response, including the status code and the response body. If the item exists, you will see a response like this:
>
>```json
>{
>  "item_id": 1,
>  "db_connection": "Simulated database connection"
>}
>```
>
>**4. Testing with POST Request in Swagger UI**
>
>***Example: Create a New Item***
>
>	1.	In Swagger UI, find the **POST** request for /items/.
>	1.	Click the **POST** request to expand it.
>
>	3.	Click the **Try it out** button.
>	3.	 In the request body, enter the following JSON payload to create a new item:
>
>```json
>{
>  "name": "New Item",
>  "price": 19.99,
>  "is_offer": true
>}
>```
>
>5. Click **Execute**.
>
>***Response:***
>
>Swagger will display the response after the item is created:
>
>```json
>{
>  "item": {
>    "name": "New Item",
>    "price": 19.99,
>    "is_offer": true
>  },
>  "db_connection": "Simulated database connection"
>}
>```
>
>**5. Testing with PUT Request in Swagger UI**
>
>***Example: Update an Existing Item***
>
>	1.	In Swagger UI, find the **PUT** request for /items/{item_id}.
>	1.	Click the **PUT** request to expand it.
>
>	3.	Click the **Try it out** button.
>	3.	Enter the item_id of the item you want to update, for example 1.
>
>	5.	In the request body, enter the following JSON payload to update the item:
>
>```json
>{
>  "name": "Updated Item",
>  "price": 29.99,
>  "is_offer": false
>}
>```
>
>6. Click **Execute**.
>
>***Response:***
>
>Swagger will show the updated item in the response:
>
>```json
>{
>  "item_id": 1,
>  "updated_item": {
>    "name": "Updated Item",
>    "price": 29.99,
>    "is_offer": false
>  },
>  "db_connection": "Simulated database connection"
>}
>```
>
>***Example: Delete an Item***
>
>In Swagger UI, find the **DELETE** request for /items/{item_id}.
>
>	2.	Click the **DELETE** request to expand it.
>	2.	Click the **Try it out** button.
>
>	4.	Enter the item_id of the item you want to delete, for example 1.
>	4.	Click **Execute**.
>
>***Response:***
>
>Swagger will show the response indicating the item was deleted:
>
>```json
>{
>  "detail": "Item deleted",
>  "item_id": 1,
>  "db_connection": "Simulated database connection"
>}
>```
>
>**7. Inspecting API Response in Swagger UI**
>
>Swagger UI provides detailed information about the response for each API request:
>
>​	•	**Response Code**: Indicates whether the request was successful (200) or failed (e.g., 404 for “Not Found”).
>
>​	•	**Response Body**: Displays the actual data returned from the API.
>
>​	•	**Headers**: Shows metadata related to the API response.
>
>For example, after executing a GET request, you will see:
>
>​	•	**Response Code**: 200
>
>​	•	**Response Body**:
>
>```json
>{
>  "item_id": 1,
>  "db_connection": "Simulated database connection"
>}
>```
>
>​	•	**Response Headers**: Metadata related to the response, such as Content-Type.



### :rocket: Break Time (5 mins)



### 4. Extension Tasks (30 mins)

To further enhance understanding, here are some additional tasks for you to explore FastAPI's capabilities and deepen your knowledge of API development and testing with Postman.

#### Task 1: Create a Custom Path with Response Headers
**Objective:** Learn how to create a custom route and return custom HTTP headers.
**Instructions:** Add an endpoint that returns custom headers like `X-Custom-Header`.

**Hint:** 	

>- Use the JSONResponse class from FastAPI to return both the body and the headers.
>- Headers are sent as key-value pairs; you can add them to the response by passing them as a dictionary.

:bulb:**How to test in Postman?**



#### Task 2: Path and Query Parameter Combination

**Objective:** Practice combining path parameters with query parameters for more complex requests.
**Instructions:** Create an endpoint that takes an `item_id` as a path parameter and an optional `discount` as a query parameter. It should return the discounted price if the query parameter is provided.

**Hint:** 	

>- Path parameters are part of the URL, while query parameters are optional and come after the ? in the URL.
>- Use default values in the function definition to make query parameters optional.



#### Task 3: Handling Background Tasks

**Objective:** Learn to execute tasks in the background without blocking the request.
**Instructions:** Add an endpoint that triggers a background task (e.g., sending an email, performing a calculation) and returns immediately.

**Hint:** 	

>- Use the BackgroundTasks dependency to run tasks in the background.
>- Background tasks allow you to execute long-running processes without blocking the main API response.



#### Task 4: Test the Custom Path with Postman

**Objective:** Learn how to use Postman to test FastAPI routes and inspect response headers.
**Instructions:** Ask students to use Postman to send a GET request to the custom path they created (e.g., `/info/`). In Postman, after sending the request, they should:

- Check the response body for the message (e.g., "Custom path created successfully!").
- Inspect the response headers to verify that `X-Info-Version` and `X-Student-Task` headers 

**Hint:** 	

>- After sending a request in Postman, always check both the **Body** and **Headers** tabs to verify your response.
>
>- Remember that headers are not part of the response body but are included separately in the response metadata.