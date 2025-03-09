import json
import re
from typing import Any, Literal, Optional, Pattern
import os

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
        remove_addresses (bool): Whether to remove memory addresses from string representations.
        Inherits all attributes from json.JSONEncoder
    """
    def __init__(self, *args, remove_addresses: bool = False, **kwargs):
        """
        Initialize the encoder with options for handling memory addresses.
        
        Args:
            *args: Arguments to pass to the parent JSONEncoder.
            remove_addresses (bool): If True, memory addresses in string representations 
                                     will be completely removed.
            **kwargs: Keyword arguments to pass to the parent JSONEncoder.
        """
        self.remove_addresses = remove_addresses
        self._address_pattern: Optional[Pattern] = None
        if remove_addresses:
            self._address_pattern = re.compile(r' at 0x[0-9a-f]+')
        super().__init__(*args, **kwargs)
    
    def default(self, obj: Any) -> Any:
        try:
            return super().default(obj)
        except TypeError:
            string_repr = str(obj)
            if self.remove_addresses and self._address_pattern:
                # Remove memory addresses completely
                string_repr = self._address_pattern.sub('', string_repr)
            return string_repr
        
import os
import json
from typing import Any, Literal, Optional, Dict, Union

class OutputHandler:
    """
    Handles the output of serialized JSON data in different modes.
    
    Provides flexibility in how the JSON output is handled: printed to console,
    saved to a file, returned as a string, or returned as a dictionary.
    
    Attributes:
        mode (Literal["print", "save_file", "return_str", "return_dict"]): The output handling mode.
        save_file_path (str, optional): Path to save the output file when in "save_file" mode.
    """
    def __init__(self, mode: Literal["print", "save_file", "return_str", "return_dict"] = "return_str", save_file_path: str = None):
        """
        Initialize the OutputHandler with specified mode and file path.
        
        Args:
            mode (Literal["print", "save_file", "return_str", "return_dict"]): How to handle the output.
                - "print": Print the JSON string to console
                - "save_file": Save the JSON string to a file
                - "return_str": Return the JSON string
                - "return_dict": Return the parsed JSON as a Python dictionary
                Defaults to "print".
            save_file_path (str, optional): Path where the file will be saved when
                mode is "save_file". Required when mode is "save_file".
        """
        self.mode = mode
        self.save_file_path = save_file_path
        
        # Validate parameters
        if mode == "save_file" and not save_file_path:
            raise ValueError("save_file_path must be provided when mode is 'save_file'")

    def print(self, data: str) -> None:

        print(data)

    def save_file(self, data: str) -> None:
        # Create directory if it doesn't exist
        directory = os.path.dirname(self.save_file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        with open(self.save_file_path, "w") as file:
            file.write(data)

    def return_str(self, data: str) -> str:
        return data
    
    def return_dict(self, data: str) -> Dict[str, Any]:
        return json.loads(data)

    def handle_output(self, data: str) -> Optional[Union[str, Dict[str, Any]]]:
        if self.mode == "print":
            self.print(data)
            return None
        elif self.mode == "save_file":
            self.save_file(data)
            return None
        elif self.mode == "return_str":
            return self.return_str(data)
        elif self.mode == "return_dict":
            return self.return_dict(data)
        else:
            raise ValueError(f"Invalid mode '{self.mode}' selected for output handling")


def dumps_object_safe(data: Any, indent: int = 2, 
                     output_handler: OutputHandler = OutputHandler(mode="return_str"),
                     remove_addresses: bool = False) -> Optional[str]:
    """
    Safely converts any Python object to a JSON-formatted string or dictionary.

    For Quick start, see the [Example Notebook](https://github.com/crimson206/py-json/blob/main/example/dumps/object_safe.py).
    
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
        remove_addresses (bool, optional): If True, memory addresses in string 
            representations will be completely removed. Useful for testing.
            
    Returns:
        Optional[Union[str, Dict[str, Any]]]: 
            - If output_handler mode is "return_str": A JSON-formatted string 
            - If output_handler mode is "return_dict": A Python dictionary
            - If output_handler mode is "print" or "save_file": None

    Examples:
        [Example Notebook](https://github.com/crimson206/py-json/blob/main/example/dumps/object_safe.py)
    """
    # Convert all dictionary keys to strings
    stringified_data = stringify_keys(data)

    # Serialize to JSON with custom encoder
    output = json.dumps(stringified_data, 
                        cls=AllStringEncoder, 
                        indent=indent,
                        remove_addresses=remove_addresses)

    # Process the output according to the handler's mode
    return output_handler.handle_output(output)