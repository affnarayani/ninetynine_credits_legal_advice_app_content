#!/usr/bin/env python3
import json
import os

def count_json_elements(json_file_path):
    """
    Count the number of elements in a JSON array file.
    
    Args:
        json_file_path (str): Path to the JSON file
        
    Returns:
        int: Number of elements in the JSON array
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        if isinstance(data, list):
            count = len(data)
            print(f"The JSON file contains {count} elements.")
            return count
        else:
            print("The JSON file does not contain a list/array at the root level.")
            return 0
            
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found.")
        return -1
    except json.JSONDecodeError:
        print(f"Error: '{json_file_path}' contains invalid JSON.")
        return -1
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return -1

if __name__ == "__main__":
    # Path to the history.json file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    history_file = os.path.join(current_dir, "content.json")
    
    # Count elements
    count_json_elements(history_file)