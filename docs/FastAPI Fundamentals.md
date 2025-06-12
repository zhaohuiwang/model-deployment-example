
# FastAPI Fundamentals

If you are building a CLI app to be used in the terminal instead of a web API, check out **Typer** which is FastAPI's little sibling. And it's intended to be the FastAPI of CLIs. 

**FastAPI** is a modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints. FastAPI stands on the shoulders of giants:
- Starlette for the web parts.
- Pydantic for the data parts.

## 1. The Core of FastAPI Fast API is built on two major foundations: 
- **Asynchronous programming:** Leveraging Python’s async and await, FastAPI can handle many requests at the same time, making it efficient for applications that require concurrency.
- **Type Annotations:** FastAPI uses Python’s type hints to validate and serialize request and response data automatically, which makes development faster and safer.

## 2. Uvicorn: The ASGI Server
Uvicorn is a lightning-fast ASGI server, optimized for handling asynchronous code. It’s essential for running FastAPI applications because it handles incoming HTTP requests and manages the lifecycle of these requests.
To run your FastAPI app with Uvicorn, use the following command: `uvicorn main:app --reload`
-	`main:app` specifies that Uvicorn should look for an app instance in the `main.py` file.
-	`--reload` enables hot-reloading during development, so the server reloads automatically whenever you save changes.
When you run this command, Uvicorn will start serving your FastAPI app, and you can access it at `http://127.0.0.1:8000`

## 3. Starlette: FastAPI's Web Framework Foundation
FastAPI is built on top of Starlette, a lightweight ASGI framework that handles the core HTTP operations, including routing, middleware, and WebSockets support. Starlette provides the low-level tools that FastAPI uses to manage HTTP requests, making it a stable and performant foundation for building web applications.
FastAPI leverages Starlette’s routing system to define API endpoints. For example:
```
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```
-	`@app.get("/items/{item_id}")` defines a route with a path parameter item_id.
-	FastAPI handles this path parameter type (int here) by integrating Starlette's routing system with its type checking and validation.

Starlette also allows you to add middleware for various operations, such as handling CORS (Cross-Origin Resource Sharing), request logging, or custom authentication:

```
from starlette.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
This flexibility in Starlette makes FastAPI highly configurable, allowing developers to easily add custom middlewares as needed.

## 4. Swagger UI: Interactive API Documentation
FastAPI automatically generates interactive API documentation with Swagger UI. This documentation is available by default at /docs and allows developers to test endpoints directly from the browser.
To see this in action, start up your FastAPI app and visit `http://127.0.0.1:8000/docs`. You’ll see an interactive Swagger UI that lists all of your routes, their parameters, and the expected responses.
Another documentation interface, ReDoc, is also provided at /redoc by default, offering a more detailed view of API specifications.
## 5. Pydantic: Data Validation and Serialization
Pydantic models allow you to define the structure of request and response data with strict type constraints and automatic validation. For example,
```
from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()

# Define a Pydantic model
class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = False
# Use the model in an endpoint
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, "item": item}
```

- The `Item` model inherits from `BaseModel` and defines three fields: `name`, `price`, and `is_offer`. These fields have specific data types and an optional default value for `is_offer`.
- When you send a request to `/items/{item_id}` with JSON data, FastAPI uses Pydantic to validate the data against the Item model, automatically converting data types if possible.
Try sending a request like this using Swagger UI at `/docs`:

```
{
  "name": "Sample Item",
  "price": 29.99
}
```
FastAPI will validate the data and automatically return any errors if the data doesn’t match the expected types.

## 6. Putting It All Together
```
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

# Define a Pydantic model
class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = False

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Home route
@app.get("/")
async def read_root():
    return {"Hello": "World"}

# Get an item by ID
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    if item_id == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "q": q}

# Update an item
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, "item": item}


```

## 7. Uvicorn Configuration (Server-Level Tweaks)
Development - Auto-Reloading: Great for Development, Not for Production<p>
`uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

Production - Debug Mode introduces overhead in production. Turn this off to improve performance.<p>
`uvicorn main:app --host 0.0.0.0 --port 8000 --no-debug`

Managing Workers: Tuning Concurrency for Efficiency - too few workers cause bottlenecks, while too many waste resources.<p>
`uvicorn main:app --host 0.0.0.0 --port 8000 --workers 8`

Streamlining Access Logs - Access logs are invaluable during debugging but can strain performance in production. Use the `--log-config` option to fine-tune logging or disable unnecessary logs.<p>
`uvicorn main:app --host 0.0.0.0 --port 8000 --log-config logging.ini`

`logging.ini` file
```
[loggers]
keys = root

[handlers]
keys = consoleHandler

[formatters]
keys = formatter

[logger_root]
level = WARNING
handlers = consoleHandler

[handler_consoleHandler]
class = StreamHandler
level = WARNING
formatter = formatter
args = (sys.stderr,)

[formatter_formatter]
format = %(asctime)s - %(levelname)s - %(message)s
datefmt = %Y-%m-%d %H:%M:%S
```
## 8. FastAPI Configuration (Application-Level Tweaks)
disable OpenAPI reduces unnecessary communication overhead, improving performance.
```
app = FastAPI(
    openapi_url=None  # Disable OpenAPI documentation in production
)
```
Middleware for Performance Tweaks. FastAPI supports middleware for tasks like caching, compression, and security enhancements. Adding caching middleware reduces load by serving frequently requested data from a cache.

```
app = FastAPI(
    middleware=[
        CacheMiddleware(
            cache_backend="redis",
            cache_url="redis://localhost:6379",
            cache_prefix="my_app",
            cache_expire=3600  # Cache for 1 hour
        )
    ]
)
```
Customize FastAPI’s response class to add headers or handle specific response types more efficiently. 
```
from fastapi import FastAPI, Response

app = FastAPI()

class CustomResponse(Response):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers["X-Custom-Header"] = "My custom header"
app.response_class = CustomResponse 
```


List of operations:
```
@app.get() : to read data.
@app.post() : to create data.
@app.put() : to update data.
@app.delete() : to delete data.
```
And the more exotic ones:
```
@app.options()
@app.head()
@app.patch()
@app.trace()
```
### References
1. Understanding FastAPI Fundamentals: A Guide to FastAPI, Uvicorn, Starlette, Swagger UI, and Pydantic [URL](https://dev.to/kfir-g/understanding-fastapi-fundamentals-a-guide-to-fastapi-uvicorn-starlette-swagger-ui-and-pydantic-2fp7)
2. FastAPI Under the Hood: 10 Configuration Tweaks for Blazing-Fast APIs [URL](https://medium.com/@b.antoine.se/fastapi-under-the-hood-10-configuration-tweaks-for-blazing-fast-apis-54a51fd4c837 )
3. Basic README reference [GitHub Pages](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax).