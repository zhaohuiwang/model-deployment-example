




## Environment setup
### Poetry environment
There is venv in `/venvs/uv-venvs/pytorch` that can be used directly without creating it in this directory. The instruction is in `README.md` file inside the `pytorch` directory.
Create a new project directory and add at least the following python libraries.
```Bash
poetry add torch torchvision matplotlib seaborn 
poetry add fastapi[standard]
poetry add requests rich
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

## Data Preparation
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
## Model Training
I only configured and run `model_demo.py` as a module with `-m` option. 
```Bash
pytorchzhaohuiwang@WangFamily:/mnt/e/zhaohuiwang/dev/pytorch-projects$ python -m src.model_demo.model_demo
```
With the following import code (compare to the `data_prep.py` above)
```python
from src.model_demo.utils import LinearRegressionModel, load_data, infer_evaluate_model
```

## Model Inference
### 1. Model inference on server
To run the server from `pytorchzhaohuiwang@WangFamily:/mnt/e/zhaohuiwang/dev/pytorch-projects$ `

```Bash
python -m uvicorn src.model_demo.fast_api:app --reload --port 8000
```
If no port process is available, To list the PID `isof -i :8000`, to kill the process `kill -i <pid>`. 
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
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -d '{"feature_X_1": 1.0, "feature_X_2": 2.0}'
curl -X POST "http://localhost:8000/batch_predict" -H "Content-Type: application/json" -d '{"input_data": [[1.0, 2.0], [3.0, 4.0]]}'

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
