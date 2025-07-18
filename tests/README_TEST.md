
# pytest

### How to invoke pytest


`pytest` execute all test in all files whose names follow the form `test_*.py` or `\*_test.py` in the current directory and subdirectories
```
# simple run - execute all test in all test files in the current dir or subdir 
pytest

# run tests in a module
pytest test_modulefile.py

# run tests in a directory
pytest testdirectory/

# run tests which contains names that match the given string expression (case sensitive)
pytest -k 'MyClass and not method'  

# run a specific test method
pytest testdirectory/testmodulefile.py::test_function
pytest testdirectory/testmodulefile.py:testClass::test_mothod

# run all tests in a class
pytest testdirectory/testmodulefile.py::testClass

# run a test with specific parameters
pytest testdirectory/test_modilefile::test_function[par1, par2]

# run test command line from a file (all the above can be read from a file using the @ prefix)
pytest @tests_to_run.txt

```
### test examples
```
# content of test_assert1.py
# import pytest

def f():
    return 3

def test_function():
    assert f() == 4
```
`Failures` returns from the execution of the command line `pytest test_assert1.py` 
```
def test_zero_division():
    with pytest.raises(ZeroDivisionError):
        1 / 0

```



### References
[Pytest Document](https://docs.pytest.org/en/stable/index.html)