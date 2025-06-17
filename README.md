<!-- The back to top link -->
<a id="readme-top"></a>


<h2 align="center">Welcome to Zhaohui Wang's ML Model Deployment Example</h2>
In this example project, you can find some Python script files I wrote for variou propuses including synthetic data prepration, model training/evaluation using PyTorch, model server application using FastAPI, model inference and configurations. These scripts can be executed to test the model and model inference. The main goal is to provide an example on how to deploy a trained model through FastAPI on Web application and package everything including script files and dependencies into a Docker image. The web application scripts is organized in the `fast_api.py` file and Docker configurations are organized in `Dockerfile` and `compose.yml` files. All the execution steps with detaisl from environment setup to final model deployment are described below.

### Environment setup (uv)
It is recommended to setup the environment (`.venv`) inside the project directory but the downside is it comsume memory. The alternative is to create environments in a desinated directory so they maybe shared across projects. I have an environment in `/venvs/uv-venvs/pytorch` that can be used directly without creating a new one in this project directory. The instruction is in `README.md` file inside the `pytorch` directory. I still need the pyproject and lock files inside this project directory when I  build a Docker image, I just copy or syn them over from my environment directory using the following `cp` commands or `rsync` commands,
```Bash
cp -u ../venvs/uv-venvs/pytorch/pyproject.toml .
cp -u ../venvs/uv-venvs/pytorch/uv.lock .
# rsync -av --update ../venvs/uv-venvs/pytorch/pyproject.toml .
# rsync -av --update ../venvs/uv-venvs/pytorch/uv.lock .
```
Here is the tree structure section showing my project directory relative to the environment directory
```Bash
.
└──dev
   ├── model-deployment-example
   └── venvs
        ├── poetry-venvs
        └── uv-venvs
             └── pytorch
```
To start from scratch, first step is to create a project directory then to setup a environment (`.venv`) inside the new project directory.
```Bash
uv init <project-name>
cd <project-name>
uv add torch torchvision matplotlib seaborn 
uv add fastapi[standard]
uv add requests rich
```

With the environment available, before any coding work we need to direct our working directory to `/dev/pytorch-projects`. I use VSCode and I execute `code .` at teminal to start a instance. Next we select a Python interpreter (environment) following these steps:  Ctl(Command)+Shift+P > Click 'Python:Select Interpreter' in the drop down manual > select if available or click 'enter interpreter path ...'. For my case, as I use the one from another directory, I enter its absolute path which is `/mnt/e/zhaohuiwang/dev/venvs/uv-venvs/pytorch/.venv/bin/python`. You may need to activate the envoronment to execute any Python script from the terminal, the command is `source .venv/bin/activate` (for my case `source ../venvs/uv-venvs/pytorch/.venv/bin/activate`). You now expect to see `(selected-venv-name)` at the begining of the bash/szh prompt indicating you are inside that Python environment. 
You can then generate synthetic data, train a model and test the FastAPI by running the script file directly or in a module mode as describe in the next section.

Here is the tree structure showing how the files are organized in my project directory.
```Bash
.
├── .dockerignore
├── Dockerfile
├── README.md
├── compose.yml
├── .gitignore
├── data
│   └── model_demo ...
├── docs ...
├── models
│   └── model_demo ...
├── pyproject.toml
├── run.sh
├── src
│   ├── __init__.py
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
├── templates
│   ├── batch_predict.html
│   ├── main.html
│   └── predict.html
├── test
└── uv.lock
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Building a Demo Modle with PyTorch
#### Data Preparation
There are many ways to generate a synthetic data using code in `data_prep.py`. The simple option is to run script file as a module
```Bash
pytorchzhaohuiwang@WangFamily:/mnt/e/zhaohuiwang/dev/model-deployment-example$ python -m src.model_demo.data_prep
# with the alternative specification in the script
from src.model_demo.utils import synthesize_data, norm
```
The second option is to execute the `data_prep.py` as a script file or run line by line (for optimization/trouble shooting)
```Bash
pytorchzhaohuiwang@WangFamily:/mnt/e/zhaohuiwang/dev/model-deployment-example$ python  src/model_demo/data_prep.py
# with the following path specification in the script
import sys
sys.path.append('/src/model_demo')
from utils import synthesize_data, norm
```
#### Model Training
Similar to the data paration, either script or module mode can be executed on `model_demo.py` with or without modifications. For simplicity, I only describe the module mode here. 
```Bash
pytorchzhaohuiwang@WangFamily:/mnt/e/zhaohuiwang/dev/model-deployment-example$ python -m src.model_demo.model_demo
```
#### Model inference
When you want to perform model inference and evaluation, you can load the model and perform model inference by executing the Python script directly (the code snippet is in the comment section in `model_demo.py`). However the limitation for this approach is that you can only use the model in the same environment where the model was trained and can not be used by many other users. For more business values, high quanlity models should be deployed and the access be granded to all possible users, with consistency promise. Next two sections are examples for two model deployment approaches: Web application via FastAPI and containerization by Docker.

### Model Development Using Fast API
Deploying a model via an API means exposing its functionality as a web service that can be accessed and consumed by other applications. This is a common and efficient way to make trained ML models useful in real-world scenarios.  
#### 1. Model inference on server
With the FastAPI configuration in `fast_api.py` file, we can spin up a web application directly by executing any of the following code in the project directory or `dev/model-deployment-example`
```Bash
# via FastAPI development mode `dev` (default auto-reload enabled) 
fastapi dev src/model_demo/fast_api.py
# or production mode
fastapi run src/model_demo/fast_api.py
#  via unicorn
uvicorn src.model_demo.fast_api:app --reload --port 8000
python -m uvicorn src.model_demo.fast_api:app --reload --port 8000
```
Recommendation:
Use `fastapi dev ...` for development due to its simplicity and auto-reload. Use `uvicorn ...` for production or when you need fine-grained control over server settings.

You may encounter error message like `[Errno 98] Address already in use`. Here is the solution: To list which PID(s) is using the port - `lsof -i :8000`, to kill the process - `kill -i <pid>`. 

I alse created single data point inferene and bath data inference URLs. User can follow the instruction to input the data and <code style="color : blue">Predict</code> the outcomes. So once the web localhost URL is up running, we have at least three options to submit test data for inference: 
1. Through http://localhost:8000/docs by Swagger UI. (typical localhost IP address is 127.0.0.1, so alternatively you may use http://127.0.0.1:8000/docs instead. Run `cat /etc/hosts` from terminal to confirm the IP address). Go to Post > [Try it out] > input data into "Request body" box > [Execute]. The result will be displayed in the  "Response" section below.
2. Through http://localhost:8000/predict
3. Through http://localhost:8000/batch_predict

 `http://localhost:8000/predict` | `http://localhost:8000/batch_predict`
:---: | :---:
![](/docs/images/single_data_predict.png) | ![](/docs/images/batch_data_predict.png)

#### 2. Model inference through Python script
We still have the option to submit test data for inference through Python script
```Bash
# activate the environment (choose one according to you environment directory)
zhaohuiwang@WangFamily:/mnt/e/zhaohuiwang/dev/model-deployment-example$ source .venv/bin/activate 
zhaohuiwang@WangFamily:/mnt/e/zhaohuiwang/dev/model-deployment-example$ source ../venvs/uv-venvs/pytorch/.venv/bin/activate
(pytorch) zhaohuiwang@WangFamily:/mnt/e/zhaohuiwang/dev/model-deployment-example$ python src/model_demo/submit_for_inference.py
```
![](/docs/images/script_file_predict.png)

To see the prediction result from `http://localhost:8000/docs`
#### 3. Model inference via `curl`command to send POST request
Alternatively, we can use curl to execute prediction. Here are examples (optional: `&&echo` to add a blank line)
```Bash
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -d '{"feature_X_1": 1.0, "feature_X_2": 2.0}' &&echo
curl -X POST "http://localhost:8000/batch_predict" -H "Content-Type: application/json" -d '{"input_data": [[1.0, 2.0], [3.0, 4.0]]}' &&echo

```
![](/docs/images/curl_predict.png)

### Localhost URL Table
| Localhost URL                 | Description                    | 
| ------------------------------------- | ------------------------------ |
| http://localhost:8000/               | Root / main  | 
| http://localhost:8000/docs           | Interactive API documentation for a FastAPI application | 
| http://localhost:8000/redoc          | API documentation page generated by ReDoc | 
| http://localhost:8000/predict        | Single data prediction | 
| http://localhost:8000/batch_predict  | Batch data prediction | 
| The most common localhost address used for servers is 127.0.0.1. | 

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Model Development Using Docker

#### Dockerfile
Docker enables developers to package their applications and all of their dependencies into "containers", which can be easily shared and deployed across different systems. Anyone who has access to a docker container can run the model application without worrying about the environment dependencies, operation systems etc. This ensures that your model runs the same way (ensuring reproducibility and consistency) regardless of the underlying infrastructure, making collaboration and deployment much smoother. 
The first step is to create a Dockerfile with instructions on how to assemble a docker image, a snapshot of the model application and its dependencies. I also prefer to add a (optional) `.dockerignore` file to specify which files and directories to exclude from the build context sent to the Docker daemon during the image build process. In my file layout, I have both the `Dockerfile` file and the `.dockerignore` (content with `.venv` `.git`) file for this project inside the project directory.

If your environment was set up inside the project folder (most common), you can skip this step. Because I am using a Python environment from another directory, I need to copy/sync the `pyproject.toml` and `uv.lock` files from the environment directory to this project directory, using the follow command,
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
Once the Dockerfile is ready, we can then open the Docker Desktop app and create a docker image using the following command ("demoapp:v1" is the name/version of the image). 
```Bash
# To build a Docker images from the directory where Dockerfile lives
docker build -t myapp:v1 .
# To list all Docker images stored on your local system
docker images
# To remove a specific docker image
docker image rm <IMAGE ID>
```
Next to create and start a new container based on the Docker image (`myapp:v1`) with `-p` or `--publish` flag (syntax: `docker run -p [host_ip:]host_port:container_port[/protocol] [image_name]`). The publication flag ensures the access of the outside host to the Docker container's port.
```Bash
# Start with the default application CMD specified in the Dockerfile
docker run -p 8000:8000 -it --rm myapp:v1
# or with the override option (the same CMD as in Dockerfile for illustration propuse only)
docker run -p 8000:8000 -it --rm myapp:v1 fastapi run --host 0.0.0.0 src/model_demo/fast_api.py
# Note: Both the `-p` and the `--host 0.0.0.0` specifications are critical. 

# To overrides the image’s default command, and start an interactive Bash shell inside the container
docker run -it --rm myapp:v1 /bin/bash
# or start to run python executable inside the container
docker run -it --rm myapp:v1 python
# To list all the dirs and files including all children dirs  
docker run -it myapp:v1  ls -R /app

# Ctrl + d ot type `exist` to exist or detach from a container

# To kill a running container
docker kill <IMAGE ID>  
```
The model is now deployed in Docker! Everyone can pull this Docker image and run the application if Docker is installed on their machine and expect the promised consistent outcomes.


#### Docker compose
We can simplify the control of the entire application stack with docker compose. In the `compose.yml` file, I instruct Docker daemon to build a Docker image and run it with ports configuration (binds the host port to the port on the container system).
We can then build and run the application with a sigle command.
```Bash
# start all the services defined in the compose.yaml file
docker compose up
docker compose up -d    # suggested in detach mode
# list all the services along with their status
docker compose ps	
# stop and remove the running services (clean up) (or Ctrl + c) 
docker compose down

```

## Contact

Zhaohui Wang - X [@zhwang22](https://x.com/zhwang22) - ezhwang@gmail.com <br />
Project Link: [github.com/zhaohuiwang/model-deployment-example](https://github.com/zhaohuiwang/model-deployment-example)
<p align="right">(<a href="#readme-top">back to top</a>)</p>


## References:
 1. [Using uv in Docker ](https://github.com/astral-sh/uv-docker-example/blob/main/README.md)