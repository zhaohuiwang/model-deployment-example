from typing import Any
from dataclasses import dataclass, field
from pydantic import BaseModel
import torch.nn as nn




class LinearRegressionModel(nn.Module):
    """ PyTorch model using nn.Linear """
    def __init__(self, input_dim: int=2, output_dim: int=1):
        super().__init__()
        self.linear = nn.Linear(
            in_features =input_dim,
            out_features=output_dim
            )  # Linear layer: y = xW^T + b

    def forward(self, x):
        out = self.linear(x)  # Apply linear transformation
        return out


class PredictionFeatures(BaseModel):
    """ Define the request body format for predictions """
    feature_X_1: int | float
    feature_X_2: int | float
    
class PredictionFeaturesBatch(BaseModel):
    input_data: list[tuple[int | float]]

@dataclass
class ModelParametersConfigSchema:
    """ Configuration schema for the model training parameters. """
    test_after_training: bool =True
    train_size: float = 0.8
    batch_size: int = 100   # batch_size should be a positive integer value
    epochs: int = 100
    learning_rate: float = 0.01

@dataclass
class PathConfigSchema:
    """ Configuration schema for paths.  """
    data_dir: str = "data/model_demo"
    model_dir: str = "models/model_demo"
# Default values for fields can be provided using the normal assignment syntax or by providing a value to the default argument


@dataclass
class FNameConfigSchema:
    """ Configuration schema for file names. """
    # non-default argument should preceed default argument
    data_fname: str = field(default="data_tensors.pt")
    data_prep_log_fname: str = field(default="data_logfile.log")
    model_fname: str = field(default="demo_model_weights.pth")

@dataclass
class MetadataConfigSchema:
    """
    Hierarchical Configurations: Configuration schema for the full training workflow including data and model configs.
    """
    path: PathConfigSchema = field(default_factory=PathConfigSchema)
    fname: FNameConfigSchema = field(default_factory=FNameConfigSchema)
    modelparameters: ModelParametersConfigSchema = field(default_factory=ModelParametersConfigSchema)
    modelinstance: Any = LinearRegressionModel
    # The modelinstance is left as a callable (class) for flexibility in dimensions when instantiated.

# Pydantic is unable to generate a schema for a custom class torch.nn.Linear    

""""
Comparison:
from pydantic.dataclasses import dataclass, Field
from dataclasses import dataclass, field
1. dataclasses.dataclass does not provide built-in data validation, does not automatically coerce types. You have to do manual validation.
2. pydantic.dataclasses.dataclass performs automatic type validation and coercion
3. pydantic.dataclasses.Field is the counterpart of the dataclasses.field.

@dataclass decorator from dataclasses.dataclass is implementing __init__(constructor), (object string representation), __eq__( equality operator) classes behind the scenes
Data classes require type hints but types aren't actually enforced due to Python not dataclass itself. Data classes also allow default values in fields. Keep in mind that non-default fields can't follow default fields.

In practice, you will rarely define defaults with `name: type = value` syntax. Instead, you will use the **field function**, which allows more control of each field definition. Syntax: 
`name: type = Field(default=value)`
The default_factory parameter accepts a function that returns an initial value for a data class field. It accepts any arbitratary funciton, including tuple, list, dict, set, and any user-defined custum function or lambda <arguments>  : expression
We can add methods to data classes as we do for regular classes.
"""
