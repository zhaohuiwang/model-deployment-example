

"""
Python introduced dataclasses in version 3.7 to simplify the creation of classes that store data. They reduce boilerplate by automatically generating methods like __init__, __repr__, and __eq__. However, native dataclasses lack built-in validation, meaning you must write custom validation logic to ensure data correctness.

This is where Pydantic comes in. By extending Python's dataclasses, Pydantic adds the ability to validate and parse data directly. 


Pydantic
Bring schema and sanity to your data.
Automatic data validation for type safe and data integrity - Pydantic automatcally validates the incoming data against the field definations (Native Python types, advanced types and custom validators) and performs necessary coercion when possible, otherwise raises `ValidationError`.

Pydantic works by using the `BaseModel` class - the core class. By defining Python classes that inherit from `Basemodel` you can specify the fields your model should contain, including their types, optional fields, default values and validation rules.

Model Configuration: You can customize model behavior using the Config class.
JSON Schema Generation: Pydantic can automatically generate JSON Schema from models, which is useful for API documentation.

Pydantic raises clear and informative error messages when validation fails, showing exactly which field is invalid and why.

Immutable: Once a Pydantic model is instantiated, it is immutable by default, ensuring consistency in your data objects.


BaseModel vs. RootModel: Key Differences
    BaseModel is used for models with nested data structures. It allows you to define multiple fields, each with their own types and validations.
    RootModel is used when the model is one single value, like a list or scalar type, without needing to nest it inside fields.



https://medium.com/@kishanbabariya101/episode-1-introduction-to-pydantic-python-data-validation-simplified-398a30528891

"""
from pydantic import BaseModel, ValidationError
from typing import List

class User(BaseModel):
    name: str
    email: str
    age: int
    is_active: bool = True
    roles: List[str] = None

# Example data
user_data = {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "age": '30',
    "is_active": True
}

# Create a User instance and validate the data
try:
    user = User(**user_data)
except ValidationError as e:
    print(e)
else:
    print(user)


# When a dictionary (user_data) is passed to the User model, Pydantic automatically validates that the data matches the expected types.
# If "age": '30' - coercion resluting in `type(user.age)` <class 'int'> 
# If "age": '30year" - Validation error


"""
The Heart of Pydantic: BaseModel
All Pydantic models inherit from BaseModel, and it serves as the foundation for defining your data structure, applying validations, and enabling automatic parsing.
Automatic Data Validation: Pydantic validates data types automatically when you create an instance of the model.
Serialization and Parsing: Pydantic models can easily convert to and from various data formats (e.g., JSON, dict, etc.), making it perfect for APIs or data-driven applications.

"""

from pydantic import BaseModel, EmailStr, Field

class RegistrationRequest(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=8)
    age: int = Field(..., ge=18)
# This model validates the following:
# The email field must be a valid email (thanks to EmailStr).
# The password field must have at least 8 characters.
# The age field must be greater than or equal to 18.

try:
    request = RegistrationRequest(username="john_doe", email="john@example.com", password="securepassword123", age=25)
except ValidationError as e:
    print(e)
else:
    print(request)

# same data in he JSON form
import json

config_json = '{"username": "john_doe", "email": "john@example.com", "password": "securepassword123", "age": "25"}'

config_data = json.loads(config_json)

try:
    request = RegistrationRequest(**config_data)
except ValidationError as e:
    print(e)
else:
    print(request)
# note:  age: '25' was coerced to 25
# type(request.age) returns <class 'int'>
"""
JSON (JavaScript Object Notation):
JSON is a data interchange format. It is a string-based, language-independent (language-agnostic) standard used for representing structured data in a human-readable and machine-readable way. It's primarily used for transmitting data between different systems or applications, such as between a web server and a web browser. 

JSON has strict syntax rules, including:
    Keys must be strings enclosed in double quotes.
    Values can be strings, numbers, booleans (true/false), null, arrays, or other JSON objects.
    Strings must use double quotes.

Python dictionary keys can be any hashable object.

Boolean/Null Representation:
    JSON uses true, false, and null; 
    Python dictionaries use True, False, and None.

json.dumps() converts a Python dictionary to a JSON string.
json.loads() converts a JSON string to a Python dictionary.
"""

from pydantic import RootModel

class ProductIds(RootModel[list[int]]):
    pass

# Example usage
try:
    product_ids = ProductIds([101, 102, 103])
except ValidationError as e:
    print(e)
else:
    print(product_ids)
# returns root=[101, 102, 103]

# Working with JSON Array
json_array = '[101, 102, 103]'

parsed_data = ProductIds.model_validate_json(json_array)
print(parsed_data)
# This parses the raw JSON array and directly maps it into a Python object that is easy to work with.




# parse environment variables
from pydantic.dataclasses import dataclass
from typing import Optional
import os

@dataclass
class Config:
    app_name: str
    debug: bool
    max_connections: int
    database_url: Optional[str]
# Simulate environment variables
os.environ["APP_NAME"] = "MyApp"
os.environ["DEBUG"] = "true"
os.environ["MAX_CONNECTIONS"] = "100"
# Create a config instance
config = Config(
    app_name=os.environ["APP_NAME"],
    debug=os.environ["DEBUG"].lower() == "true",
    max_connections=int(os.environ["MAX_CONNECTIONS"]),
    database_url=os.getenv("DATABASE_URL")  # Optional
)
print(config)
# Config(app_name='MyApp', debug=True, max_connections=100, database_url=None)

"""
When to Use Pydantic Dataclasses vs. BaseModel vs RootModel

    Use Pydantic Dataclasses: When you need a lightweight, dataclass-style structure with validation. Ideal for scenarios where simplicity and type enforcement are key.
    
    Use BaseModel: When you need more advanced features like field aliases, validators, and custom serialization logic.
    
    BaseModel is used for models with nested data structures. It allows you to define multiple fields, each with their own types and validations.
    
    RootModel is used when the model is one single value, like a list or scalar type, without needing to nest it inside fields.

"""

# TypeAdapter, a powerful utility in Pydantic for defining custom types and converting between models. It is suited for quick validation of data structures without creating full Pydantic models.

from pydantic import TypeAdapter
from typing import List, Dict

# Define the expected structure of the API response
ApiResponseType = Dict[str, List[Dict[str, str]]]
# Create a TypeAdapter
api_adapter = TypeAdapter(ApiResponseType)
# Sample API response
api_response = {
    "results": [{"name": "Alice", "email": "alice@example.com"}, {"name": "Bob", "email": "bob@example.com"}]
}
# validation OK
validated_response = api_adapter.validate_python(api_response)
print(validated_response)

# validation error
try:
    validated_response = api_adapter.validate_python({"results": [{"name": "Alice", "email": 123}]})
except Exception as e:
    print(e)  # Validation error
else:
    print(validated_response)


# TypeAdapter can also be used to convert data between different Pydantic models or even standard Python data structures.

from pydantic import BaseModel, TypeAdapter

# Define a Pydantic model
class User(BaseModel):
    id: int
    name: str
# Create a TypeAdapter for the model
adapter = TypeAdapter(User)
# Parse and validate raw data into the model
data = {"id": 123, "name": "Alice"}
user = adapter.validate_python(data)
print(user)  # User(id=123, name='Alice')
# Serialize the model into JSON
json_data = adapter.dump_json(user)
print(json_data)  # {"id":123,"name":"Alice"}


"""
Validation Mechanisms in Pydantic
    1. validate_call is a decorator introduced in Pydantic v2 that allows you to validate function or method inputs using Pydantic models. It’s an elegant way to ensure that your functions receive correctly formatted data.

    2. Functional validators are external functions designed to validate or transform data before it's processed further. They are especially useful for scenarios where validation logic is complex or needs to be reused across models.

    3. Standard validators are methods defined within a BaseModel using the @field_validator or @model_validator decorators. They are the most common way to enforce custom validation rules for specific fields or the entire model.

"""

from pydantic import validate_call

@validate_call
def process_order(order_id: int, amount: float, priority: str = "normal"):
    print(f"Processing order {order_id} with amount {amount} and priority {priority}")
# Valid call
process_order(123, "299.99", priority="high")

# Invalid call
try:
    process_order("123", "t299.99")
except Exception as e:
    print(e)
'''
Arguments are validated against their type hints.
Default values are respected and validated.
Invalid inputs raise a ValidationError.

Note: without the @validate_call, Python does not force type check or validate even though type hints are specified.

Due to coercion between "299.99" and 299.99, there is no error for the first but a validation error due to "t299.99"   
'''


from pydantic import BaseModel, EmailStr, ValidationError
from typing import Callable

# Functional validator
def validate_email(email: str) -> EmailStr:
    if "@" not in email:
        raise ValueError("Invalid email format")
    return email
# note EmailStr is a data type from Pydantic

class User(BaseModel):
    username: str
    email: str
    # Custom validation with functional validator
    def validate_email_field(self):
        self.email = validate_email(self.email)

 # apply an external function for validation. It is defined seperately first then was called into the pydantic model (class), and performs type validation at class instantiation. 

# Valid case
user = User(username="johndoe", email="john@example.com")
user.validate_email_field()
print(user)

# Invalid case
try:
    invalid_user = User(username="johndoe", email="invalidemail")
    invalid_user.validate_email_field()
except ValidationError as e:
    print(e)


# Field-Level Validation
from pydantic import BaseModel, Field, field_validator

class Product(BaseModel):
    name: str
    price: float = Field(gt=0)  # Built-in validation for positive values
    @field_validator("name")
    def name_must_not_be_empty(cls, value):
        if not value.strip():
            raise ValueError("Name cannot be empty")
        return value
    
# Valid product
product = Product(name="Laptop", price=999.99)
print(product)

# Invalid product
try:
    Product(name=" ", price=-20)
except Exception as e:
    print(e)

# Model-level validation 
from pydantic import BaseModel, model_validator

class Order(BaseModel):
    order_id: int
    items: int
    @model_validator(mode="after")
    def check_items(cls, values):
        if values["items"] <= 0:
            raise ValueError("Items must be greater than 0")
        return values
# Valid case
order = Order(order_id=123, items=5)
print(order)
# Invalid case
try:
    Order(order_id=124, items=0)
except Exception as e:
    print(e)

# Field Validators: Apply to individual fields and run during parsing.
# Model Validators: Apply to the entire model and run after all fields are validated.

'''
Pydantic's Field function is your go-to tool for adding metadata and constraints to model attributes. It is used to 
1. Set metadata such as default values and descriptions.
2. Apply constraints like length, range, or regex validation.
3. Document and annotate your models for clarity and compatibility.

Common Field Arguments:
1. min_length and max_length: Enforce string length constraints.
2. ge (greater than or equal) and gt (greater than): Validate numerical ranges.
3. regex: Match strings against a regular expression.


Use default for static, immutable values (e.g., str, int, None).
Use default_factory for mutable objects (list, dict) or dynamic values (e.g., current date).
Always use Field(default_factory=...) syntax for default_factory in Pydantic.

Feature	       default	                default_factory
Value Type	 Static value (e.g., 0, "text")	   Callable that generates a value
Mutable Objects	Shared across instances (problematic)	Unique per instance (safe)
Use Case	Immutable, fixed values	    Mutable objects or dynamic values
Syntax	field: type = value	    field: type = Field(default_factory=callable)
Example 	name: str = "John"	  items: List[int] = Field(default_factory=list)
'''


from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(min_length=3, max_length=50, description="The product name")
    price: float = Field(ge=0.0, description="The product price, must be non-negative")
    stock: int = Field(gt=0, description="The available stock, must be greater than zero")

# Valid case
product = Product(name="Laptop", price=1299.99, stock=10)
print(product)

# Invalid case
try:
    Product(name="TV", price=-200, stock=0)
    # stock should be > 0
except Exception as e:
    print(e)

# Aliases let you define alternative names for model attributes, enabling seamless data compatibility with external systems like APIs or databases.

class User(BaseModel):
    full_name: str = Field(alias="name")
    email_address: str = Field(alias="email")

data = {"name": "Alice Johnson", "email": "alice@example.com"}
user = User(**data)
print(user)

# The input data uses the aliases name and email. The Pydantic model maps these to full_name and email_address.

class User(BaseModel):
    full_name: str = Field(alias="name")
    email_address: str = Field(alias="email")

class Config:
        allow_population_by_field_name = True

data = {"name": "Alice Johnson", 
        "email": "alice@example.com"} # validation ok
user = User(**data)
print(user)

data = {"full_name": "Alice Johnson", 
        "email_address": "alice@example.com"} # validation error

user = User(**data)
print(user)


# Field Customization: exclude, include, and by_alias

user = User(full_name="Alice Johnson", email_address="alice@example.com")

# Serialize with aliases
print(user.model_dump(by_alias=True))
# {'name': 'Alice Johnson', 'email': 'alice@example.com'}

# Include only specific fields
print(user.model_dump(include={"email_address"}))
# {'email_address': 'alice@example.com'}

# Exclude specific fields
print(user.model_dump(exclude={"email_address"}))
# {'email_address': 'alice@example.com'}


from pydantic.dataclasses import dataclass

@dataclass
class Config_error:
    my_list: list = []  # Mutable default, raises ValueError

@dataclass
class Config_ok1:
    my_list: list = Field(default_factory=list)  # default_factory creates new instances for mutable fields, OK, safe


# An immutable default is an object that cannot be modified after creation, such as integers, strings, tuples (with immutable contents), or None.
@dataclass
class Config_ok2:
    my_str: str = "default"  # Immutable, safe
    my_int: int = 42         # Immutable, safe
    my_tuple: tuple = (1, 2) # Immutable, safe

# Syntax comparisons default vs default_factory
# Field(default=value)
# Suitable for immutable types (e.g., str, int, float, tuple, None).

# Field(default_factory=callable) 
# where callable returns a new instance (e.g., list, dict, or a custom class constructor).
# Required for mutable types (e.g., list, dict, set, Pydantic dataclasses, custom objects).


'''
Behaviour of pydantic can be controlled via the model_config attribute on a BaseModel. Previous vesion was config class within the BaseModel

Object-Relational Mapping (ORM)


JSON Schema is a specification for defining the structure, constraints, and documentation of JSON data. 

FastAPI uses Pydantic's JSON Schema generation to create interactive API documentation via Swagger UI and ReDoc. This makes your APIs self-documenting and easy to use.

You can use the Field function to add metadata like descriptions and examples to your schema.

 '''

from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    is_active: bool = True
print(User.model_json_schema())

{
    'properties': {
        'id': {'title': 'Id', 'type': 'integer'},
        'name': {'title': 'Name', 'type': 'string'},
        'is_active': {'default': True, 'title': 'Is Active', 'type': 'boolean'}}, 
    'required': ['id', 'name'], 
    'title': 'User', 
    'type': 'object'
 }

# Pydantic supports nested models, arrays, and custom types, all of which are reflected in the generated JSON Schema
class Address(BaseModel):
    street: str
    city: str
    zipcode: str

class User(BaseModel):
    id: int
    name: str
    address: Address
print(User.model_json_schema())


{
    '$defs': {
        'Address': {
            'properties': {
                'street': {'title': 'Street', 'type': 'string'},
                'city': {'title': 'City', 'type': 'string'},
                'zipcode': {'title': 'Zipcode', 'type': 'string'}
                },
                'required': ['street', 'city', 'zipcode'],
                'title': 'Address',
                'type': 'object'
            }
        },
    'properties': {
        'id': {'title': 'Id', 'type': 'integer'},
        'name': {'title': 'Name', 'type': 'string'},
        'address': {'$ref': '#/$defs/Address'}
        },
        'required': ['id', 'name', 'address'], 
        'title': 'User',
        'type': 'object'
}

# Example: JSON Validation with jsonschema
from jsonschema import validate
from jsonschema.exceptions import ValidationError

schema = User.model_json_schema()
# Valid data
data = {
    "id": 1,
    "name": "John Doe",
    "address": {
        "street": "123 Elm St",
        "city": "Metropolis",
        "zipcode": "54321"
    }
}
validate(instance=data, schema=schema)  # Passes validation
# Invalid data
invalid_data = {
    "id": 1,
    "name": "John Doe",
}
try:
    validate(instance=invalid_data, schema=schema)
except ValidationError as e:
    print(e.message)
# 'address' is a required property


'''
Serialization refers to converting an object into a format that can be easily stored or transferred. In Pydantic:

Default Serialization: Models have a built-in .model_dump() method (formerly .dict()) to serialize data into Python dictionaries.
Custom Serialization: You can extend serialization logic using @model_serializer decorators or by overriding methods like .model_dump().

'''

from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
user = User(id=1, name="Alice", email="alice@example.com")
# Default Serialization
print(user.model_dump())



# Custom Serialization with @model_serializer
from pydantic import BaseModel, model_serializer

class User(BaseModel):
    id: int
    name: str
    email: str
    @model_serializer
    def serialize(self):
        return {"id": self.id, "name": self.name}  
    # Exclude email - Hiding Sensitive Data
user = User(id=1, name="Alice", email="alice@example.com")
print(user.model_dump())

## Serializing to Custom Formats (e.g., CSV)
class Product(BaseModel):
    id: int
    name: str
    price: float

    @model_serializer
    def to_csv(self):
        return f"{self.id},{self.name},{self.price:.2f}"
product = Product(id=1, name="Laptop", price=999.99)
print(product.to_csv())


# Overriding model_dump for Global Customization
class User(BaseModel):
    id: int
    name: str
    email: str

def model_dump(self):
        return {
            "user_id": self.id,
            "full_name": self.name.upper(),
        }
user = User(id=1, name="Alice", email="alice@example.com")
print(user.model_dump())



"""
Hydra is an open-source Python framework that simplifies the development of research and other complex applications. The key feature is the ability to dynamically create a hierarchical configuration by composition and override it through config files and the command line. The name Hydra comes from its ability to run multiple similar jobs - much like a Hydra with multiple heads.


import hydra
from omegaconf import DictConfig, OmegaConf

@hydra.main(version_base=None, config_path="conf", config_name="config")
def my_app(cfg : DictConfig) -> None:
    print(OmegaConf.to_yaml(cfg))

if __name__ == "__main__":
    my_app()


The resulting cfg object is a composition of configs from defaults with configs specified in your config.yaml.
pathlib Path many be applied in config_path but the object should be converted to string first using str(Path_object). 
@hydra.main(version_base=None, config_path=".", config_name="config")

Hydra configuration files are yaml files and should have the .yaml file extension. But when you specify the config name by passing a config_name parameter to the @hydra.main() decorator, you should omit the .yaml extension.


from omegaconf import DictConfig, OmegaConf
import hydra

@hydra.main(
      config_path=str(Path(__file__).parent.parent/"configs"), 
      config_name="infer_config",  # configuration file name without extension
      version_base="1.1"
      )
   
config.yaml
defaults:
  - db: mysql

$ python my_app.py
$ python my_app.py db=postgresql db.timeout=20  # Override a default

"""