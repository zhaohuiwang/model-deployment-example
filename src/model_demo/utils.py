import logging
import numpy as np
import numpy.typing as npt
import torch
import torch.optim as optim
from pathlib import Path
from logging.handlers import RotatingFileHandler
from pydantic import BaseModel
from typing import Iterator, List, Any, Tuple, Union

def find_directory(target_dir_name="logs", start_path=None):
    """
    Search for the first occurrence of a directory by traversing up the parent directories.
    
    Parameters:
        target_dir_name (str): Name of the directory to search for.
        start_path (str or Path, optional): Starting directory path. Defaults to current working directory.
    
    Returns:
        Path: Absolute path to the first matching directory found, or None if not found.
    """
    # Use current working directory if no start path is provided
    current_path = Path(start_path).resolve() if start_path else Path.cwd()
    
    # Continue until we reach the root directory
    while current_path != current_path.parent:
        # Check if the target directory exists in current path
        target_path = current_path / target_dir_name
        if target_path.is_dir():
            return target_path
        
        # Move up to parent directory
        current_path = current_path.parent
    
    # Check the root directory
    target_path = current_path / target_dir_name
    if target_path.is_dir():
        return target_path
        
    return None

def setup_logger(logger_name: str='MyAppLogger', log_file:str='app.log', log_level=logging.DEBUG):
    """
    Create a centralized logger configuration.
    List of logging levels: DEBUG (10) > INFO (20) > WARNING (30) > ERROR (40) > CRITICAL (50)
    Parameters:
        logger_name (str): a user defined name for the logger
        log_file (str): a file path to save logs.
        log_level (logging): a selected level for logging.
    Returns:
        A logger object.
    """
    # Create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    
    # Prevent adding handlers if logger is already configured
    if not logger.handlers:
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler with rotation (max 5MB, keep 5 backups)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5*1024*1024,
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_device():
    """Get the computer Chip device """
    device = ("cuda" if torch.cuda.is_available() else 
              "mps"  if torch.backends.mps.is_available() else 
              "cpu"
              )
    return device

# Define a function to generate noisy data
def synthesize_data(w: torch.Tensor, b: torch.Tensor, sample_size) -> Tuple[torch.Tensor, torch.Tensor]:
  """ Generate y = xW^T + bias or noise """
  X = torch.normal(10, 3, (sample_size, len(w)))
  y = torch.matmul(X, w) + b # adding noise
  y += torch.normal(0, 0.01, y.shape)
  
  return X, y.reshape((-1, 1))

def norm(x:npt.NDArray) -> npt.NDArray:
    """ normalize the original data values """
    return (x - np.mean(x)) / np.std(x)

# Define the request body format for predictions
class PredictionFeatures(BaseModel):
    feature_X_1: Union[int, float]
    feature_X_2: Union[int, float]
    
class PredictionFeaturesBatch(BaseModel):
    input_data: List[Tuple[Union[int, float], Union[int, float]]]


def load_data(tensors: torch.Tensor, batch_size:torch.Tensor, is_train: bool=True) -> Iterator[Any]:
   """ Construct a PyTorch data iterator."""
   dataset = torch.utils.data.TensorDataset(*tensors)
   return torch.utils.data.DataLoader(dataset, batch_size, shuffle=is_train, num_workers=2, pin_memory=True)


# Function for inference and loss calculation
def infer_evaluate_model(model, test_loader, criterion, device='cuda' if torch.cuda.is_available() else 'cpu') -> Tuple[torch.Tensor, float]:
    model.eval()  # Set model to evaluation mode
    model.to(device)

    predictions = torch.tensor([])

    total_loss = 0.0
    total_samples = 0
    
    with torch.no_grad():  # Disable gradients for inference
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            # Forward pass (inference)
            outputs = model(inputs)
            # Append using torch.cat
            
            predictions = torch.cat((predictions, outputs))
            # Alternatively, use torch.hstack (same for 1D tensors)
            # predictions = torch.hstack((predictions, outputs))

            # Calculate loss
            loss = criterion(outputs, labels)
            
            # Accumulate loss
            total_loss += loss.item() * inputs.size(0)
            total_samples += inputs.size(0)
    
    # Calculate average loss
    avg_loss = total_loss / total_samples
    return predictions, avg_loss

# Function for inference 
def infer_model(model, inputs, device='cuda' if torch.cuda.is_available() else 'cpu') -> torch.Tensor:

    model.eval()  # Set model to evaluation mode
    model.to(device)

    with torch.no_grad():  # Disable gradients for inference
        inputs  = inputs.type(torch.float).to(device) 
        # Forward pass (inference)
        outputs = model(inputs)
    
    return torch.squeeze(outputs)
