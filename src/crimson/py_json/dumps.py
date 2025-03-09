import json
from typing import Any, Literal, Optional

def stringify_keys(data: Any) -> Any:
    """
    Recursively converts all dictionary keys to strings.
    
    Traverses through nested dictionaries, lists, and tuples to ensure
    all dictionary keys at any level are converted to string type.
    
    Args:
        data (Any): The input data structure to process.
        
    Returns:
        Any: The processed data with all dictionary keys converted to strings.
    """
    if isinstance(data, dict):
        return {str(k): stringify_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [stringify_keys(item) for item in data]
    elif isinstance(data, tuple):
        return tuple(stringify_keys(item) for item in data)
    else:
        return data


class AllStringEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that converts non-serializable objects to strings.
    
    Extends the standard JSONEncoder to handle objects that are not normally
    JSON serializable (like datetime, functions, custom objects, etc.) by
    converting them to their string representation.
    
    Attributes:
        Inherits all attributes from json.JSONEncoder
    """
    def default(self, obj: Any) -> Any:
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)
        
        
class OutputHandler:
    """
    Handles the output of serialized JSON data in different modes.
    
    Provides flexibility in how the JSON output is handled: printed to console,
    saved to a file, or returned as a string.
    
    Attributes:
        mode (Literal["print", "save_file", "return"]): The output handling mode.
        save_file_path (str, optional): Path to save the output file when in "save_file" mode.
    """
    def __init__(self, mode: Literal["print", "save_file", "return"] = "print", save_file_path: str = None):
        """
        Initialize the OutputHandler with specified mode and file path.
        
        Args:
            mode (Literal["print", "save_file", "return"]): How to handle the output.
                Defaults to "print".
            save_file_path (str, optional): Path where the file will be saved when
                mode is "save_file". Required when mode is "save_file".
        """
        self.mode = mode
        self.save_file_path = save_file_path

    def print(self, data: str) -> None:
        """
        Print the data to the console.
        
        Args:
            data (str): The data to print.
        """
        print(data)

    def save_file(self, data: str) -> None:
        """
        Save the data to a file at the specified path.
        
        Args:
            data (str): The data to save to file.
            
        Raises:
            FileNotFoundError: If the directory doesn't exist or isn't writable.
        """
        with open(self.save_file_path, "w") as file:
            file.write(data)

    def return_output(self, data: str) -> str:
        """
        Return the data as is.
        
        Args:
            data (str): The data to return.
            
        Returns:
            str: The input data unchanged.
        """
        return data

    def handle_output(self, data: str) -> Optional[str]:
        """
        Process the data according to the configured mode.
        
        Args:
            data (str): The data to handle.
            
        Returns:
            Optional[str]: The data if mode is "return", otherwise None.
            
        Raises:
            ValueError: If an invalid mode is specified.
        """
        if self.mode == "print":
            self.print(data)
        elif self.mode == "save_file":
            self.save_file(data)
        elif self.mode == "return":
            return self.return_output(data)
        else:
            raise ValueError("Invalid mode selected for output handling")


def dumps_object_safe(data: Any, indent: int = 2, output_handler: OutputHandler = OutputHandler(mode="return")) -> Optional[str]:
    """
    Safely converts any Python object to a JSON-formatted string.
    
    This function handles complex data structures that might not be directly
    JSON serializable by:
    1. Converting all dictionary keys to strings
    2. Converting non-serializable objects to their string representations
    3. Processing the output according to the specified output handler
    
    Args:
        data (Any): The input data to serialize, can be any Python object.
        indent (int, optional): Number of spaces for indentation in JSON formatting.
            Defaults to 2.
        output_handler (OutputHandler, optional): Handler that determines how the
            output is processed. Defaults to returning the string.
            
    Returns:
        Optional[str]: A JSON-formatted string if the output_handler is set to "return",
            otherwise None.
            
    Examples:
        [Example Notebook](https://github.com/crimson206/py-json/blob/main/example/dumps/object_safe.py)
    """
    # Convert all dictionary keys to strings
    stringified_data = stringify_keys(data)

    # Serialize to JSON with custom encoder
    output = json.dumps(stringified_data, cls=AllStringEncoder, indent=indent)

    # Process the output according to the handler's mode
    return output_handler.handle_output(output)

