<!-- The back to top link -->
<a id="readme-top"></a>


<h2 align="center">Welcome to Zhaohui Wang's ML configuration Example</h2>
In this example project, 

### Options for model parameters/flag configuration
- argparse - Python built-in for basic command-line argument parsing. Ideal for smaller scripts or CLIs with limited numbers of parameters.
- Click - Build robust, multi-command CLI tools with decorators and advanced features.
- Hydra - External library primarily for dynamic hierarchical configuration management for complex application.
    1. configuration is organized in a structured and hierarchical way using YAML files, reducing boilerplate code. Configurations are seperated from the codebase and allowing breaking down into smaller components that can be composed hierarchically, promoting modularity and scalability.
    2. configurations can be dynamically created and overridden from the command line. 
    3. multiple runs features in the commandline, for example, `python -m main ++model.type= random_forest cnn --multirun` will run random_forest first following configuration in model.type followed by cnn.
    4. automatically logging


<p align="right">(<a href="#readme-top">back to top</a>)</p>