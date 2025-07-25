
""" 
FastAPI: web framework for building APIs for creating server-side applications
Built on Starlette (for web handling) and Pydantic (for data validation), with support for asynchronous programming using async/await.
Ideal for creating production-ready APIs with automatic documentation (Swagger UI, ReDoc) and type safety.
Runs on an ASGI server like Uvicorn, typically on http://localhost:8000 during development.

"""
from datetime import datetime
import os
from pathlib import Path

from fastapi import HTTPException, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import numpy as np
import pandas as pd
import torch
import uvicorn

from src.model_demo.configs.config import MetadataConfigSchema
from src.model_demo.utils import PredictionFeatures, PredictionFeaturesBatch, infer_model, setup_logger, get_device

cfg = MetadataConfigSchema()

device = get_device()

## Logger setup
logger = setup_logger(logger_name=__name__, log_file=f'{cfg.path.data_dir}/api_logfile.log')

# Initialize FastAPI app
app = FastAPI(
    title="Demo model API", # title on Swagger UI URL
    description="API for simple linear model prediction",
    version="1.0.0",
    docs_url="/docs",  # Custom URL for Swagger UI
    )

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

logger.info(f"Using {device} device")
logger.info(f"Running at: {Path.cwd()}")


# create an instance of the same model first
model = cfg.modelinstance(2,1)

# Load the trained model weights, weights_only=True as a best practice.
try:
    model.load_state_dict(torch.load(Path(cfg.path.model_dir) / cfg.fname.model_fname, weights_only=True))
except FileNotFoundError:
    logger.error("Model file not found")
    raise RuntimeError("Model file not found")
model.to(device)
model.eval()  # Set to evaluate mode

# Define a get endpoint for URL path `/`- HTTP method for data requests
@app.get("/", response_class=HTMLResponse) # HTMLResponse renders a web page
async def root(request: Request):
    #return {"message": "Welcome to my API"} # when applying the default response_class is JSON
    return templates.TemplateResponse(
        "main.html",  # Template file
        {"request": request}  # Context data passed to the template
    )

# API End point for data request from API prediction 
@app.get("/predict", response_class=HTMLResponse)
async def root(request: Request):
    #return {"message": "Welcome to my API"} # when applying the default response_class is JSON
    return templates.TemplateResponse(
        "predict.html",
        {"request": request}  # Context data passed to the template
    )

@app.get("/batch_predict", response_class=HTMLResponse)
async def batch(request: Request):
    return templates.TemplateResponse(
        "batch_predict.html",  # Template file for batch prediction
        {"request": request}  # Context data passed to the template
    )


# API end point for data submission for API prediction (HTTP post) 
@app.post("/predict", description="Predict using a single set of features (X_1, X_2).")
async def predict(features: PredictionFeatures):
# defined an asynchronous function named prediction - allowing other tasks to run while it waits for I/O-bound operations
    try:
        # Create input DataFrame for prediction
        input_df = pd.DataFrame([{
            "X_1": features.feature_X_1,
            "X_2": features.feature_X_2
        }])

        # Convert DataFrame to NumPy array
        np_array = input_df.to_numpy()  # or df.values

        # Convert NumPy array to PyTorch tensor
        inputs = torch.tensor(np_array, dtype=torch.float32)

        # model inference
        outputs = infer_model(model, inputs).tolist()

        with open(Path(cfg.path.data_dir) / 'predictions.txt', 'a') as f:
            f.write(f"{datetime.now()}\nInput:\n{input_df}\nPrediction:\n{outputs}\n\n")

        logger.info(f"Input: {input_df}, Prediction: {outputs}")

        return {
            "Model prediction": outputs
        }
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")

# # API end point for data submission for API Batch prediction
@app.post("/batch_predict", description="Predict using batch input like [[X_1, X_2], ...]")
async def batch_predict(features: PredictionFeaturesBatch):
# defined an asynchronous function named prediction - allowing other tasks to run while it waits for I/O-bound operations
    try:
        # Create input data for prediction
        inputs = np.array(features.input_data)

        # Validate input shape
        if inputs.ndim != 2 or inputs.shape[1] != 2:
            raise ValueError("Input must be a 2D array with 2 features per row")

        # Convert NumPy array to PyTorch tensor
        inputs = torch.tensor(inputs, dtype=torch.float32)

        # model inference
        outputs = infer_model(model, inputs).flatten().tolist()

        with open(Path(cfg.path.data_dir) / 'predictions.txt', 'a') as f:
            f.write(f"{datetime.now()}\nInput:\n{inputs}\nPrediction:\n{outputs}\n\n")

        logger.info(f"Input: {inputs}, Prediction: {outputs}")

        return {
            "Model prediction": outputs
        }
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Batch prediction failed: {str(e)}")

if __name__ == "__main__":
    # Option: If "API_PORT" was set as a environment variables or in a config file, default is 8000 is not found.
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)