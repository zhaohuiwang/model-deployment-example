"""
Note:
hydra is used in data_prep.py configuration file config.yaml
pydantic is used in model_demo.py configuration file config.py

"""

import logging
from pathlib import Path

from omegaconf.dictconfig import DictConfig
import numpy as np
import torch
import torch.nn as nn

from src.model_demo.utils import load_data, infer_evaluate_model, get_device, setup_logger
from src.model_demo.configs.config import MetadataConfigSchema
from src.model_demo.configs.config import LinearRegressionModel as LR

def get_data() -> dict:
    """ Fetch data from the data dir """
    try:
        tensors_dict = torch.load(Path(__file__).parent.parent.parent.parent/cfg.path.data_dir/cfg.fname.data_fname)
    except FileNotFoundError:
        logger.error('Data or path not fund!')
    return tensors_dict

def train(model, cfg: DictConfig) -> None:
    # Step 1: Get data ready
    tensors_dict = get_data()

    X_train = tensors_dict['X_train']
    y_train = tensors_dict['y_train']

    ## Model training
    # Step 1: Create model class
    # in the utils.py

    # Step 2: Get model ready
    input_dim = X_train.shape[-1]
    output_dim = y_train.shape[-1]

    # Instantiate the model, the default of modelinstance in MetadataConfigSchema is an instance already not a callable 
    model = model(input_dim, output_dim)


    logger.info(f"Using {model} ")

    device = get_device()
    logger.info(f"Using {device} device")

    model.to(device)

    # Step 3: Instantiate Loss class and Optimizer class
    # learning_rate = 0.01
    optimizer = torch.optim.SGD(model.parameters(), lr=cfg.modelinstance.learning_rate)
    criterion = nn.MSELoss()

    # Step 4: Train the model
    # batch_size = 100   # batch_size should be a positive integer value
    # epochs = 100

    # Data loader combines a dataset and a sampler, and provides an iterable over the given dataset.
    data_iter = load_data((X_train, y_train), cfg.modelinstance.batch_size)

    for epoch in range(cfg.modelinstance.epochs):
        epoch += 1 # Logging starts at 1 instead of 0
        for X, y in data_iter:
            X = X.to(device)
            y = y.to(device)
        
        optimizer.zero_grad() # Clear gradients w.r.t. parameters
        outputs = model(X) # Forward to get output
        loss = criterion(outputs, y) # Calculate Loss

        # loss_list.append(loss.item())
        # epoch_list.append(epoch)
        logger.info('epoch {}, loss {}'.format(epoch, loss.item())) # Logging
        
        loss.backward() # Getting gradients w.r.t. parameters
        optimizer.step() # Updating parameters

    # step 5: Persist the trained model 
    model_path = Path(__file__).parent.parent.parent.parent/cfg.path.model_dir/cfg.fname.model_fname
    torch.save(model.state_dict(), model_path)
    
    logger.info("Model training accomplished!")
    logger.info(f"Model is saved as {model_path}")
    return model

## Model inference
if __name__ == "__main__":

    device = get_device()
    cfg = MetadataConfigSchema()

    ## Logger setup
    logger = setup_logger(logger_name=__name__, log_file=Path(__file__).parent.parent.parent.parent/cfg.path.data_dir/"api_logfile.log")

    try:
        model = train(LR, cfg)
        logger.info("Model training accomplished.")
    except Exception as e:
        logging.error(f"An error occurred during training: {e}", exc_info=True)


    if cfg.modelinstance.test_after_training:
        logger.info("Starting the model-demo inference")

        # Set model to evaluation mode
        model.eval()
        model.to(device)

        # Process the test data set
        tensors_dict = get_data()

        X_test = tensors_dict['X_test'].to(device)
        y_test = tensors_dict['y_test'].to(device)

        test_data_iter = load_data((X_test, y_test), cfg.modelinstance.batch_size, is_train=False)

        # Perform inference
        predictions, avg_loss = infer_evaluate_model(model, test_data_iter, nn.MSELoss())

        # Convert to NumPy and save
        numpy_predictions = predictions.cpu().numpy()

        np.save(Path(cfg.path.data_dir) / 'predictions.npy', numpy_predictions)
        np.savetxt(Path(cfg.path.data_dir) / 'predictions.csv', numpy_predictions, delimiter=',', fmt='%d')
        logger.info(f"Inference result is saved in directory: {cfg.path.data_dir}")


"""
To save the trained model for later use
# PyTorch models store the learned parameters in an internal state dictionary, called state_dict. These can be persisted via the torch.save method
torch.save(model.state_dict(), 'model_weights.pth')

# To load model weights, you need to create an instance of the same model first, and then load the parameters using load_state_dict() method.

model = nn.Linear(1, 1)
model.load_state_dict(torch.load('model_weights.pth', weights_only=True))
# Using weights_only=True is considered a best practice when loading weights.
model.to(device)

# Remember to call model.eval() to set dropout and batch normalization layers to evaluation mode before running inference. Failing to do this will yield inconsistent inference results. If you wish to resuming training, call model.train() to set these layers to training mode.
model.eval()

# Load .npy file
loaded_npy = np.load('mnist_predictions.npy')
print("Loaded .npy:", loaded_npy[:5])

# Load .csv file
loaded_csv = np.loadtxt('mnist_predictions.csv', delimiter=',')
print("Loaded .csv:", loaded_csv[:5])


### Model inference through Python script
# Load the trained model weights, weights_only=True as a best practice.
try:
    model.load_state_dict(torch.load(Path(model_dir) / model_fname, weights_only=True))
except FileNotFoundError:
    logger.error("Model file not found")
    raise RuntimeError("Model file not found")
model.to(device)
model.eval()  # Set to evaluate mode

# Load data
try:
    tensors_dict = torch.load(Path(data_dir) / data_fname)
except FileNotFoundError:
    logger.error('Data or path not fund!')


X_test = tensors_dict['X_test']
y_test = tensors_dict['y_test']

# Process the test data set
X_test = X_test.to(device)
y_test = y_test.to(device)

test_data_iter = load_data((X_test, y_test), batch_size, is_train=False)

# Perform inference
predictions, avg_loss = infer_evaluate_model(model, test_data_iter, criterion)

# Convert model output to NumPy and save
numpy_predictions = predictions.cpu().numpy()

"""
