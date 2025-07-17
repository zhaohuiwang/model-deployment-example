import logging
import os

import hydra
from omegaconf import OmegaConf
from pathlib import Path

import numpy as np
import numpy.typing as npt
from src.model_demo.utils import synthesize_data, norm
from src.model_demo.configs.config import MetadataConfigSchema
import torch


# A logger for this file
# By default, Hydra logs at the INFO level to both the console and a log file in the automatic working directory.
logger = logging.getLogger(__name__)

# a complete stack trace
os.environ["HYDRA_FULL_ERROR"] = "1"

# Instantiate ConfigStore
cs = hydra.core.config_store.ConfigStore.instance()

# Register configurations
# call store() method to add your dataclasses as configuration nodes.
cs.store(name="meta_configs", node=MetadataConfigSchema)

'''
 ConfigStore helps validate your configuration against defined schemas (dataclasses), or type checking. With this section, Hydra actually provides the data as a class (specified by node) instance. Without this section, Hydra can still provide the raw data from the path specification in the decocator. 
 If both hydra configstore and decorator are absent, we can still instantiate the data class and get the configuration attributes like normal classes. for instance
 config =  MetadataConfigSchema()
 data_dir = config.data.data_dir
 ...
 '''
@hydra.main(
      config_path=str(Path(__file__).parent.parent/"configs"), # path to the configuration file 
      config_name="config",  # configuration file name in YAML
      version_base="1.1"
      )
def main(cfg: MetadataConfigSchema) -> None:
    logger.info(f"\nConfiguration\n{OmegaConf.to_yaml(cfg)}") 

    ## Setup - data preparation
    # for synthesizing data following y = xW^T + bias
    true_w = torch.tensor([2., -3.])
    true_b = torch.tensor(4.)

    X, y = synthesize_data(true_w, true_b, 1000)

    size = int(X.shape[-2]*cfg.model.train_size)

    # np.random.choice() generates a random sample from a given 1D array. here is is sampling size/total_size 
    index = np.random.choice(X.shape[-2], size=size, replace=False) 

    # Prepare the traing set. Note the synthetic data are torch.Tensors. Here it is transform into NumpyArray first for norm operation then reverse back to Tensor.
    X_train = torch.from_numpy(norm(X[index].numpy()))
    y_train = y[index]

    ## Prepare the test set.
    X_test = torch.from_numpy(norm(np.delete(X, index, axis=0).numpy()))
    y_test = np.delete(y, index, axis=0)
    # Store tensors in a dictionary
    tensors_dict = {
       'X_train': X_train,
       'X_test': X_test,
       'y_train': y_train,
       'y_test': y_test
       }
    # Save to a file - A common PyTorch convention is to save tensors using .pt file extension.
    torch.save(tensors_dict, f"{hydra.utils.get_original_cwd()}/{cfg.path.data_dir}/{cfg.fname.data_fname}") 
    # Hydra automatically changing directories behaviour may cause issues, so it is advised to specify path with get_original_cwd()

    logger.info(f"Data is saved as: {hydra.utils.get_original_cwd()}/{cfg.path.data_dir}/{cfg.fname.data_fname})")
    # Output dir is the current working dir.
   
    logger.info(f"Output directory: {hydra.core.hydra_config.HydraConfig.get().runtime.output_dir}")
    logger.info(f"Current (runtime) working directory: {os.getcwd()}")
    logger.info(f"Original working directory: {hydra.utils.get_original_cwd()}")

if __name__ == "__main__":
  
  main()

 
"""
When you run this script at `dev/model-deployment-example$ python -m src.model_demo.data_prep`, by default hydra will create a new directory, for example, outputs/2025-06-20/20-21-27, and execute data_prep.py from within this new directory.

`os.getcwd()` would return `dev/model-deployment-example/outputs/2025-06-20/20-21-27`.
`hydra.utils.get_original_cwd()` would return `dev/model-deployment-example`. 

Hydra specific outputs 
├── outputs
│   └── 2025-06-20
│       └── 20-21-27
│           ├── .hydra
│           │   ├── config.yaml
│           │   ├── hydra.yaml
│           │   └── overrides.yaml
│           ├── app.log
│           └── data_prep.log

UserWarning: Future Hydra versions will no longer change working directory at job runtime by default

In future Hydra versions, when you run a Hydra-based Python application, it will not automatically changes the working directory to a unique output folder and stay within the original working directory.
There are ways to set this behaviour
1. in config.yaml file
hydra:
  job:
    chdir: true 
    # or false

2. python -m src.model_demo.data_prep  hydra.job.chdir=true
#or python -m src.model_demo.data_prep  hydra.job.chdir=false 

"""



"""
Alternatively
# Store tensors in a list
tensors_dict = {
    'train': [X_train, y_train],
    'test': [X_test, y_test]
    }
# to access: X_train = tensors_dict['train'][0]; y_train = tensors_dict['train'][1]

# Stack tensors into a single tensor (adds a new dimension)
tensors_dict = {
    'train': torch.stack([X_train, y_train]),
    'test': torch.stack([X_test, y_test])
    }
# to access, same as the list: X_train = tensors_dict['train'][0]; y_train = tensors_dict['train'][1]

# Load tensor
tensors_dict = torch.load(saved_path)
"""