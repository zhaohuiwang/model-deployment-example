

from pathlib import Path
from src.model_demo.utils import synthesize_data, infer_model
from src.model_demo.configs.config import MetadataConfigSchema

from rich.console import Console
import torch

console = Console()

def test_synthesize_data() -> None:
    true_w = torch.tensor([2., -3.])
    true_b = torch.tensor(4.)
    X, y = synthesize_data(true_w, true_b, 1000)

    assert isinstance(X, torch.Tensor) and X.dtype == torch.float32
    assert len(X) == len(y)

def test_modelconfig() -> None:
    try:
        cfg = MetadataConfigSchema()
        model = cfg.modelinstance(2, 1)
    except Exception as e:
        pass

    assert isinstance(model, torch.nn.Module)

def test_dataload() -> None:
    cfg = MetadataConfigSchema()
    try:
        tensors_dict = torch.load(Path(__file__).parent.parent.parent.parent/cfg.path.data_dir/cfg.fname.data_fname)
    except Exception as e:
        pass

    assert isinstance(tensors_dict, dict)

def test_infer_model() -> None:
    cfg = MetadataConfigSchema()
    tensors_dict = torch.load(Path(__file__).parent.parent.parent.parent/cfg.path.data_dir/cfg.fname.data_fname)

    X_test = tensors_dict['X_test']
    y_test = tensors_dict['y_test']
    input_dim = X_test.shape[-1]
    output_dim = y_test.shape[-1]

    model = cfg.modelinstance(input_dim, output_dim)

    model_path = Path(__file__).parent.parent.parent.parent/cfg.path.model_dir/cfg.fname.model_fname

    model.load_state_dict(torch.load(model_path, weights_only=True))

    model.to("cuda" if torch.cuda.is_available() else 
              "mps"  if torch.backends.mps.is_available() else 
              "cpu"
              )
    model.eval()
    outputs = infer_model(model, X_test).flatten().tolist()

    assert isinstance(outputs, list)
    assert len(outputs) == len(X_test)