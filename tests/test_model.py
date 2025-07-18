

from pathlib import Path
from src.model_demo.utils import LinearRegressionModel, load_data, synthesize_data, infer_model

from rich.console import Console
import torch
DATA_PATH = Path(__file__).parent.parent/"data/data_tensors.pt"
MODEL_PATH = Path(__file__).parent.parent/"/models/model_demo/demo_model_weights.pth" 

console = Console()


def test_synthesize_data() -> None:
    true_w = torch.tensor([2., -3.])
    true_b = torch.tensor(4.)
    X, y = synthesize_data(true_w, true_b, 1000)

    # assert isinstance(X, torch.Tensor)
    assert X.dtype == torch.float32
    assert len(X) == len(y)



def test_infer_model() -> None:

    tensors_dict = torch.load(DATA_PATH)

    X_test = tensors_dict['X_test']
    y_test = tensors_dict['y_test']

    # create an instance of the same model first
    model = LinearRegressionModel(2,1)


    model.load_state_dict(torch.load(MODEL_PATH, weights_only=True))

    model.to("cuda" if torch.cuda.is_available() else 
              "mps"  if torch.backends.mps.is_available() else 
              "cpu"
              )
    model.eval()

    # model inference
    outputs = infer_model(model, X_test).flatten().tolist()
    assert outputs.dtype == torch.float32
    assert len(outputs) == len(X_test)