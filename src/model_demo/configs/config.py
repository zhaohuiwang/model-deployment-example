
from typing import Iterator, List, Any, Tuple, Union

# from dataclasses import dataclass, field
from pydantic import BaseModel
from pydantic.dataclasses import dataclass, Field
import torch.nn as nn


class LinearRegressionModel(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(nn.Module, self).__init__()
        self.linear = nn.Linear(input_dim, output_dim)  

    def forward(self, x):
        out = self.linear(x)
        return out

# Define the request body format for predictions
class PredictionFeatures(BaseModel):
    feature_X_1: Union[int, float]
    feature_X_2: Union[int, float]
    
class PredictionFeaturesBatch(BaseModel):
    input_data: List[Tuple[Union[int, float], Union[int, float]]]


@dataclass
class PathConfigSchema:
    """
    Configuration schema for paths.
    """
    data_dir: str = Field(default="data/model_demo")
    model_dir: str = Field(default="models/model_demo")

@dataclass
class FNameConfigSchema:
    """
    Configuration schema for file names.
    """
    # non-default argument should preceed default argument
    data_fname: str = Field(default="data_tensors.pt")
    data_prep_log_fname: str = Field(default="data_logfile.log")
    model_fname: str = Field(default="demo_model_weights.pth")
    


@dataclass
class ModelParametersConfigSchema:
    """
    Configuration schema for the model training parameters.
    """
    test_after_training: bool
    train_size: float = Field(default=0.8)
    batch_size: int = Field(default=100)   # batch_size should be a positive integer value
    epochs: int = Field(default=100)
    learning_rate: float = Field(default=0.01)


@dataclass
class MetadataConfigSchema:
    """
    Hierarchical Configurations: Configuration schema for the full training workflow including data and model configs.
    """
    path: PathConfigSchema
    fname: FNameConfigSchema
    model: ModelParametersConfigSchema


""""
@dataclass decorator is implementing __init__(constructor), (object string representation), __eq__( equality operator) classes behind the scenes
Data classes require type hints but types aren't actually enforced due to Python not dataclass itself. Data classes also allow default values in fields. Keep in mind that non-default fields can't follow default fields.

In practice, you will rarely define defaults with `name: type = value` syntax. Instead, you will use the **field function**, which allows more control of each field definition. Syntax: 
`name: type = Field(default=value)`
The default_factory parameter accepts a function that returns an initial value for a data class field. It accepts any arbitratary funciton, including tuple, list, dict, set, and any user-defined custum function or lambda <arguments>  : expression
We can add methods to data classes as we do for regular classes.

Comparison:
from pydantic.dataclasses import dataclass, Field
from dataclasses import dataclass, field
1. dataclasses.dataclass does not provide built-in data validation, does not automatically coerce types. You have to do manual validation.
2. pydantic.dataclasses.dataclass performs automatic type validation and coercion
3. pydantic.dataclasses.Field is the counterpart of the dataclasses.field.
"""
