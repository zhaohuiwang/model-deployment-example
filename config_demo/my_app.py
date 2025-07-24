

"""
# Hydra creates an empty cfg object and passes it to the function annotated with @hydra.main.
import logging
import os
from omegaconf import DictConfig, OmegaConf
import hydra

# A logger for this file
log = logging.getLogger(__name__)

@hydra.main(version_base=None)
def my_app(cfg: DictConfig) -> None:
    print(OmegaConf.to_yaml(cfg))
    print(f"Working directory : {os.getcwd()}")
    print(f"Output directory  : {hydra.core.hydra_config.HydraConfig.get().runtime.output_dir}")

    log.info("Info level message")
    log.debug("Debug level message")
    

if __name__ == "__main__":
    my_app()

"""

'''
(pytorch) pytorchzhaohuiwang@WangFamily:/mnt/e/zhaohuiwang/dev/model-deployment-example/src/config_demo$ python my_app.py +db.driver=mysql +db.user=omry +db.password=secret
Hydra creates an empty cfg object and passes it to the function annotated with @hydra.main. You can add config values via the command line. The + indicates that the field is new.

Every time you run the app, a new output directory (runtime dir) is created. 
in a format lie `outputs/yyyy-mm-dd/hh-mm-ss/.hydra/`
We have the Hydra output directory ( by default), and the application log file. Inside the Hydra output directory we have:
config.yaml: A dump of the user specified configuration
hydra.yaml: A dump of the Hydra configuration
overrides.yaml: The command line overrides used
And in the main output directory:
my_app.log: A log file created for this run

outputs/2025-06-19/10-29-36
├── .hydra
│   ├── config.yaml
│   ├── hydra.yaml
│   └── overrides.yaml
└── my_app.log

'''


"""
# It can get tedious to type all those command line arguments. You can solve it by creating a configuration file next to my_app.py. Hydra configuration files are yaml files and should have the .yaml file extension.

# configs/config.yaml

node:                         # Config is hierarchical
  loompa: 10                  # Simple value
  zippity: ${node.loompa}     # Value interpolation
  do: "oompa ${node.loompa}"  # String interpolation
  waldo: ???                  # Missing value, must be populated prior to access


import os
from omegaconf import DictConfig, OmegaConf
import hydra

os.environ["HYDRA_FULL_ERROR"] = "1"
@hydra.main(version_base=None, config_path="configs", config_name="config")
def my_app(cfg: DictConfig):
    assert cfg.node.loompa == 10          # attribute style access
    assert cfg["node"]["loompa"] == 10    # dictionary style access

    assert cfg.node.zippity == 10         # Value interpolation
    assert isinstance(cfg.node.zippity, int)  # Value interpolation type
    assert cfg.node.do == "oompa 10"      # string interpolation

    #cfg.node.waldo                        # raises an exception
    print(OmegaConf.to_yaml(cfg))

if __name__ == "__main__":
    my_app()

$ python my_app.py
config.yaml is loaded automatically when you run your application.

$ python my_app.py node.looma=20
You can override values in the loaded config from the command line. Note the lack of the + prefix.

$ python my_app.py ++node.looma=20
Use ++ to override a config value if it's already in the config, or add it otherwise.


"""


"""
from typing import Any
from dataclasses import dataclass, field

import hydra
from hydra.core.config_store import ConfigStore
from omegaconf import DictConfig, OmegaConf

@dataclass
class MySQLConfig:
    driver: str = "mysql"
    host: str = "localhost"
    port: int = 3306

@dataclass
class PostGreSQLConfig:
    driver: str = "postgresql"
    host: str = "localhost"
    port: int = 5432
    timeout: int = 10

@dataclass
class Config:
    # We will populate db using composition.
    db: Any
    db2: MySQLConfig = field(default_factory=MySQLConfig)
    ui: PostGreSQLConfig = field(default_factory=PostGreSQLConfig)

# Create config group `db` with options 'mysql' and 'postgreqsl'
cs = ConfigStore.instance()
cs.store(name="config", node=Config)
cs.store(name="mysql", node=MySQLConfig, group="db")
cs.store(name="postgresql", node=PostGreSQLConfig, group="db")

@hydra.main(version_base=None, config_name="config")
def my_app(cfg: Config) -> None:
    confs = OmegaConf.to_yaml(cfg)
    print(confs)
    print(cfg)

if __name__ == "__main__":
    my_app()
"""
    
'''
cfg is nested dictionaries. OmegaConf.to_yaml() method converts the object into a YAML formatted string.
(pytorch) pytorchzhaohuiwang@WangFamily:/mnt/e/zhaohuiwang/dev/model-deployment-example/src/config_demo$ python my_app.py
print(confs) # returns
db: ???
db2:
  driver: mysql
  host: localhost
  port: 3306
ui:
  driver: postgresql
  host: localhost
  port: 5432
  timeout: 10

print(cfg) # returns
{'db': '???', 'db2': {'driver': 'mysql', 'host': 'localhost', 'port': 3306}, 'ui': {'driver': 'postgresql', 'host': 'localhost', 'port': 5432, 'timeout': 10}}


pytorch) pytorchzhaohuiwang@WangFamily:/mnt/e/zhaohuiwang/dev/model-deployment-example/src/config_demo$ python my_app.py +db=postgresql

# db was not assigned in the config class, when we run the above command, we select/override db with postgresql
db:
  driver: postgresql
  host: localhost
  port: 5432
  timeout: 10
db2:
  driver: mysql
  host: localhost
  port: 3306
ui:
  driver: postgresql
  host: localhost
  port: 5432
  timeout: 10

(pytorch) pytorchzhaohuiwang@WangFamily:/mnt/e/zhaohuiwang/dev/model-deployment-example/src/config_demo$ python my_app.py
db: ???
db2:
  driver: mysql
  host: localhost
  port: 3306
ui:
  driver: postgresql
  host: localhost
  port: 5432
  timeout: 10

'''
'''
Main advantages of Hydra:
Developers do not need to setup boilerplate code for command line flags, loading configuration files, setting directory paths, logging, etc. with Hydra
Configurations can be set dynamically and can be overridden from the command line as needed.
It has a pluggable architecture that allows developers to integrate Hydra with other infrastructures.
'''


from dataclasses import dataclass
from hydra.core.config_store import ConfigStore

# this configuration section with config dataclasses can be in a seperate file e.g. config.py and can be imported via this code `from config import ExperimentConfig`
# Define a configuration for a model
@dataclass
class ModelConfig:
    name: str = "resnet"
    #num_layers: int = 118
    num_layers: str = '118'
    pretrained: bool = True

# Define a configuration for a dataset
@dataclass
class DatasetConfig:
    name: str = "imagenet"
    batch_size: int = 32
    shuffle: bool = True

# Define a top-level configuration that combines model and dataset
@dataclass
class ExperimentConfig:
    model: ModelConfig
    dataset: DatasetConfig


# Instantiate ConfigStore
cs = ConfigStore.instance()

# Register configurations
# call store() method to add your dataclasses as configuration nodes.
cs.store(name="resnet", node=ModelConfig, group="model")
cs.store(name="imagenet", node=DatasetConfig, group="dataset")
# cs.store(name="experiment", node=ExperimentConfig)
'''
 ConfigStore helps validate your configuration against defined schemas (dataclasses), type checking. Without this section, Hydra can still provide the raw data from the path specification in the decocator. With this section, Hydra actually provides the data as a class (specified by node) instance  
 '''
import hydra
from omegaconf import OmegaConf

@hydra.main(config_path="configs", config_name="experiment", version_base="1.3")
def main(cfg: ExperimentConfig) -> None:
# Hydra loads data from the specified location in th decorator and put it into the object cfg.     
    # Print the configuration as YAML
    print(OmegaConf.to_yaml(cfg))
    # Access configuration fields
    print(f"Model: {cfg.model.name}, Layers: {cfg.model.num_layers}")
    print(f"Dataset: {cfg.dataset.name}, Batch Size: {cfg.dataset.batch_size}")

if __name__ == "__main__":
    main()


"""
python my_app.py

model:
  name: resnet
  num_layers: 18
  pretrained: true
dataset:
  name: imagenet
  batch_size: 32
  shuffle: true

Model: resnet, Layers: 18
Dataset: imagenet, Batch Size: 32


python my_app.py model.num_layers=50 dataset.batch_size=64

model:
  name: resnet
  num_layers: 50
  pretrained: true
dataset:
  name: imagenet
  batch_size: 64
  shuffle: true

Model: resnet, Layers: 50
Dataset: imagenet, Batch Size: 64


If a paramer has different values, here is the override privilege order 
1. command line,
2. file specified by @hydra.main(config_path="configs", config_name="experiment")
3. ConfigStore

but the data type always follows the configuration by @dataclass. For example, if you input an integer in the command line (e.g. 20) or provides an integer value in the config_name YAML file (e.g. 20) but specifies str in the dataclass, the runtime parameter value will be "20" instead of 20.


path:
  run =./run
  data: ${hydra:runtime.cwd}/../data/raw 
# ${hydra:runtime.cwd} returns the current working dir
# run path is the run dir in the current working dir
# data path is the dir data/row located one level up 



cs = ConfigStore.instance()
cs.store(
    name: str,
    node: Any,
    group: Optional[str] = None,
    package: Optional[str] = "_group_",
    provider: Optional[str] = None,
) -> None

name: A string representing the name you want to give to the config node within the ConfigStore.
node: The config node itself. This can be:
A dataclass (which represents a structured config).
An instance of a dataclass.
A dictionary or list (though using dataclasses provides type safety).
group (optional): A string specifying a config group to categorize the config node. You can use / to specify subgroups (e.g., hydra/launcher).
package (optional): A string defining the parent hierarchy of the config node. Use . as a separator (e.g., foo.bar.baz).
provider (optional): A string identifying the module or app providing this config, which helps with debugging. 


Hydra's working directory behavior ensure run-Specific Isolation:
Hydra automatically creates a new output directory for each application run. This directory serves as a dedicated space to store application outputs, like database dumps or generated files, and Hydra's own outputs, such as configuration files and logs. 

Customization: You can customize the working directory pattern by setting hydra.run.dir for single runs and hydra.sweep.dir / hydra.sweep.subdir for multi-runs.

Accessing the Directory: You can access the path of the output directory through the `hydra.runtime.output_dir` variable at runtime. You can also retrieve the original working directory (where you started the Python process) using `hydra.utils.get_original_cwd()` or by inspecting `hydra.runtime.cwd`. 

"""
