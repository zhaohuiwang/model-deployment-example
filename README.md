


## Welcome to Zhaohui Wang's ML Model Deployment Server API Demo

## Environment setup
### Poetry environment
There is venv in `/venvs/uv-venvs/pytorch` that can be used directly without creating it in this directory (without consuming additional GBs memory). The instruction is in `README.md` file inside the `pytorch` directory. When I need the pyproject and lock files inside this directory (e.g. building Docker), I execute the `cp` or `rsync` to syn them,
```Bash
cp -u ../venvs/uv-venvs/pytorch/pyproject.toml .
cp -u ../venvs/uv-venvs/pytorch/uv.lock .
# rsync -av --update ../venvs/uv-venvs/pytorch/pyproject.toml .
# rsync -av --update ../venvs/uv-venvs/pytorch/uv.lock .
```

Create a new project directory and add at least the following python libraries.
```Bash
uv init <project-name>
cd <project-name>
uv add torch torchvision matplotlib seaborn 
uv add fastapi[standard]
uv add requests rich
```

First, change the directory to your project `/dev/pytorch-projects`; start a VSCode  editor `code .`; you may need to activate the envoronment: `source .venv/bin/activate` (for my specific setting `source ../venvs/uv-venvs/pytorch/.venv/bin/activate`) after which you should expect `(venv-name)` at the begining of the bash/szh prompt indicating you are inside a Python environment. 
You can then generate synthetic data, train a model and test the FastAPI.

Here are the how the files are organized in my project directory.
```Bash
.
├── README.md
├── data
│   └── model_demo
│       ├── api_logfile.log
│       ├── data_logfile.log
│       ├── data_tensors.pt
│       ├── model_logfile.log
│       ├── predictions.csv
│       ├── predictions.npy
│       └── predictions.txt
├── models
│   └── model_demo
│       └── demo_model_weights.pth
├── src
│   └── model_demo
│       ├── __init__.py
│       ├── config.py
│       ├── data_prep.py
│       ├── fast_api.py
│       ├── model_demo.py
│       ├── submit_for_inference.py
│       └── utils.py
├── static
│   └── styles.css
└── templates
    ├── batch_predict.html
    ├── main.html
    └── predict.html
```
## Building a Demo Modle with PyTorch
### Data Preparation
If you like to execute the `data_prep.py` as a script file, follow this instruction
```Bash
pytorchzhaohuiwang@WangFamily:/mnt/e/zhaohuiwang/dev/pytorch-projects$ python  src/model_demo/data_prep.py
# with the following path specification in the scriptimport sys
sys.path.append('/src/model_demo')
from utils import synthesize_data, norm
```
or if you want to run it as a module
```Bash
pytorchzhaohuiwang@WangFamily:/mnt/e/zhaohuiwang/dev/pytorch-projects$ python -m src.model_demo.data_prep
# with the alternative specification in the script
from src.model_demo.utils import synthesize_data, norm
```
### Model Training
I only configured and run `model_demo.py` as a module with `-m` option. 
```Bash
pytorchzhaohuiwang@WangFamily:/mnt/e/zhaohuiwang/dev/pytorch-projects$ python -m src.model_demo.model_demo
```
With the following import code (compare to the `data_prep.py` above)
```python
from src.model_demo.utils import LinearRegressionModel, load_data, infer_evaluate_model
```
## Model inference
When you want to perform model inference and evaluation, you can load the model and infer through a Python script directly (with code snippet in the comment section in `model_demo.py`). However you can only use the model in the environment where the trained model exists and can not be used by many other users. Therefore, high quanlity models should be deployed to gain business values.
## Model Development Using Fast API
Deploying a model via an API means exposing its functionality as a web service that can be accessed and consumed by other applications. This is a common and efficient way to make trained machine learning models useful in real-world scenarios.  
### 1. Model inference on server

To run the server from `pytorchzhaohuiwang@WangFamily:/mnt/e/zhaohuiwang/dev/pytorch-projects$ `

```Bash
# via FastAPI development mode `dev` (default auto-reload enabled) or production mode
fastapi dev src/model_demo/fast_api.py
fastapi run src/model_demo/fast_api.py
#  via unicorn
uvicorn src.model_demo.fast_api:app --reload --port 8000
python -m uvicorn src.model_demo.fast_api:app --reload --port 8000
```
Recommendation:
Use `fastapi dev ...` for development due to its simplicity and auto-reload. Use `uvicorn ...` for production or when you need fine-grained control over server settings.

Recommendation:
Use fastapi dev myapp:app for development due to its simplicity and auto-reload.
Use uvicorn myapp:app for production or when you need fine-grained control over server settings

To list the PID `lsof -i :8000`, to kill the process `kill -i <pid>` (when there is no port available). 
To submit test data for inference through URL http://localhost:8000/docs by Swagger UI. (typical localhost IP address is 127.0.0.1, so alternatively you may through http://127.0.0.1:8000/docs instead. Run `cat /etc/hosts` from terminal to confirm the IP address). To access the ReDoc-generated page displaying your API’s documentation, navigate to http://localhost:8000/redoc

Go to Post > [Try it out] > input data into "Request body" box > [Execute]

### 2. Model inference on Localhost URL
I alse created single data point inferene and bath data inference URLs. User can follow the instruction to input the data and <code style="color : blue">Predict</code> the outcomes. 


 `http://localhost:8000/predict` | `http://localhost:8000/batch_predict`
:---: | :---:
![](/docs/images/single_data_predict.png) | ![](/docs/images/batch_data_predict.png)

### 3. Model inference through Python script
To submit test data for inference through Python script
```Bash
zhaohuiwang@WangFamily:/mnt/e/zhaohuiwang/dev/pytorch-projects$ source .venv/bin/activate
(pytorch) zhaohuiwang@WangFamily:/mnt/e/zhaohuiwang/dev/pytorch-projects$ python src/model_demo/submit_for_inference.py
```
![](/docs/images/script_file_predict.png)

To see the prediction result from `http://localhost:8000/docs`
### 4. Model inference via `curl`command to send POST request
Alternatively, use curl to execute prediction. Here are examples (optional: `&&echo` to add a blank line)
```Bash
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -d '{"feature_X_1": 1.0, "feature_X_2": 2.0}' &&echo
curl -X POST "http://localhost:8000/batch_predict" -H "Content-Type: application/json" -d '{"input_data": [[1.0, 2.0], [3.0, 4.0]]}' &&echo

```
![](/docs/images/curl_predict.png)
## Localhost URL
| Localhost URL                 | Description                    | 
| ------------------------------------- | ------------------------------ |
| http://localhost:8000/               | Root / main  | 
| http://localhost:8000/docs           | Interactive API documentation for a FastAPI application | 
| http://localhost:8000/redoc          | API documentation page generated by ReDoc | 
| http://localhost:8000/predict        | Single data prediction | 
| http://localhost:8000/batch_predict  | Batch data prediction | 
| The most common localhost address used for servers is 127.0.0.1. | 


## Model Development Using Docker
Docker enables developers to package their applications and all of their dependencies into "containers", which can be easily shared and deployed across different systems. Anyone who has access to a docker container can run the model application without worrying about the environment dependencies, operation systems etc. This ensures that your model runs the same way (reproducibility and consistency) regardless of the underlying infrastructure, making collaboration and deployment much smoother. 
The first step is to create a Dockerfile with instructions on how to assemble a docker image, a snapshot of the model application and its dependencies. An optional file called `.dockerignore` to specify which files and directories to exclude from the build context sent to the Docker daemon during the image build process. I created the `Dockerfile` for this project inside the project directory and included `.venv` `.git` into the `.dockerignore` file.

If your environment was set up inside the project folder (most common), you can skip this step. Because I am using a Python environment from another directory, I first copied/synced the `pyproject.toml` and `uv.lock` files from the environment directory to this project directory, using the follow command,
```Bash
cd model-deployment-example
# copy file to current dir via cp 
# -u: Only copy if the source is newer than the destination or if the destination file is missing.
cp -u ../venvs/uv-venvs/pytorch/pyproject.toml .
cp -u ../venvs/uv-venvs/pytorch/uv.lock .
# or rsync which is efficient for syncing files and only copies changes.
rsync -av --update ../venvs/uv-venvs/pytorch/pyproject.toml .
rsync -av --update ../venvs/uv-venvs/pytorch/uv.lock .
```
Once the Dockerfile is ready, we can create the image with the following command ("demoapp:v1" is the name/version of the image) with Docker Desktop open. 
```Bash
# To build a Docker images from the directory where Dockerfile lives
docker build -t myapp:v1 .
# To list all Docker images stored on your local system
docker images
# To remove a specific docker image
docker image rm <IMAGE ID>
# To create and start a new container based on the `myapp:v1` Docker image 
# with the default application CMD specified in the Dockerfile
docker run -p 8000:8000 -it --rm myapp:v1
# or with the override option (the same CMD here for illustration propuse )
docker run -p 8000:8000 -it --rm myapp:v1 fastapi run --host 0.0.0.0 src/model_demo/fast_api.py
# Note: Both the host binding `-p 8000:8000` [host]:[Docker] and the `--host 0.0.0.0` specifications are critical. 

# To overrides the image’s default command, and start an interactive Bash shell inside the container. -- to check file structure inside the docker
docker run -it --rm myapp:v1 /bin/bash
# or start to run python executable inside the container
docker run -it --rm myapp:v1 python
# To list all the dirs and files including all children dirs  
docker run -it myapp:v1  ls -R /app

# Ctrl + d ot type `exist` to exist or detach from a container

# to kill a running container
docker kill <IMAGE ID>  
```