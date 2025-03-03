import os
import time
import requests
import json
import subprocess
from pathlib import Path
from termcolor import colored

CONFIG_FILE = "ailconfig.json"

class AILanguageInterpreter:
    def __init__(self):
        self.api_key = self.load_api_key()
        self.api_url = self.get_model_url()
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def load_api_key(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                return config.get("api_key", "")
        else:
            api_key = input("Please enter your HuggingFace API key: ")
            self.save_api_key(api_key)
            return api_key

    def save_api_key(self, key):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"api_key": key}, f)
        print("API key saved successfully! You can change your API key using the 'config' command. Check the help menu for more information.")

    def get_model_url(self):
        use_custom_model = input("Would you like to use a custom Hugging Face model? (Default: Qwen/Qwen2.5-72B-Instruct) (y/n): ").strip().lower()
        if use_custom_model == 'y':
            model_id = input("Please enter the model ID: ").strip()
            return f"https://api-inference.huggingface.co/models/{model_id}"
        else:
            return "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-72B-Instruct"

    def convert_to_golang(self, english_text, file_name):
        prompt = f"""You are an expert Golang developer. Convert the following English description into clean, efficient, and idiomatic Golang code. The code should:
1. Follow Go best practices and conventions
2. Include proper error handling
3. Be well-documented with comments
4. Use appropriate data structures and algorithms
5. Be production-ready and performant

English description:
{english_text}

Generate only the Golang code without any explanations. The code should be complete and ready to compile:"""

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.95,
                "return_full_text": False
            }
        }
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            error_msg = colored(f"Failed to convert English to Golang: {response.text}", "red")
            print(error_msg)
            raise Exception(error_msg)
            
        try:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                golang_code = result[0]["generated_text"]
                
                stripped_code = '\n'.join(golang_code.split('\n')[1:-1])

                file_path = f"{file_name}.go"
                with open(file_path, "w") as f:
                    f.write(stripped_code)
                
                print(f"Golang code saved to {file_path}")
                return file_path
            else:
                error_msg = colored(f"Unexpected response format: {result}", "red")
                print(error_msg)
                raise Exception(error_msg)
        except Exception as e:
            error_msg = colored(f"Error processing response: {str(e)}\nResponse: {response.text}", "red")
            print(error_msg)
            raise Exception(error_msg)

    def debug_golang_code(self, golang_file, error_message):
        """
        Send the error message and file contents to the AI for debugging
        and update the file with the fixed code.
        """
        print(colored("\nSending code to AI for debugging...", "yellow"))
        
        with open(golang_file, "r") as f:
            file_content = f.read()
            
        prompt = f"""You are an expert Golang developer. Debug and fix the following Go code that has compilation errors.

ERROR MESSAGE:
{error_message}

CURRENT CODE:
{file_content}

Please provide ONLY the complete fixed code without any explanations or markdown formatting. The code should be ready to compile:"""

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.95,
                "return_full_text": False
            }
        }
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            error_msg = colored(f"Failed to debug Golang code: {response.text}", "red")
            print(error_msg)
            raise Exception(error_msg)
            
        try:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                fixed_code = result[0]["generated_text"]

                fixed_code = fixed_code.replace("```go", "").replace("```golang", "").replace("```", "").strip()
                
                with open(golang_file, "w") as f:
                    f.write(fixed_code)
                
                print(colored(f"Fixed code saved to {golang_file}", "green"))
                return True
            else:
                error_msg = colored(f"Unexpected response format: {result}", "red")
                print(error_msg)
                raise Exception(error_msg)
        except Exception as e:
            error_msg = colored(f"Error processing response: {str(e)}\nResponse: {response.text}", "red")
            print(error_msg)
            raise Exception(error_msg)

    def build_program(self, golang_file):
        print("\nBuilding your program...")
        estimated_time = os.path.getsize(golang_file) / 1000
        print(f"Estimated build time: {estimated_time:.1f} seconds")
        time.sleep(min(estimated_time, 3))
        return True

    def process_file(self, file_path):
        if not file_path.endswith('.ail'):
            raise ValueError("Only .ail files are supported")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r') as f:
            english_text = f.read()
        
        file_name = input("\nEnter the name for your project: ").strip()
        print("\nConverting English to Golang...")
        golang_file = self.convert_to_golang(english_text, file_name)
        
        success = self.build_program(golang_file)
        
        if success:
            print("\nGoLang file built! Converting to executable...")
            
            result = subprocess.run(["go", "build", golang_file], capture_output=True, text=True)

            if result.returncode != 0:
                print(colored("Build failed!", "red"))
                print(colored(result.stderr, "red"))
                
                debug_choice = input("\nWould you like to debug and fix the errors? (y/n): ").strip().lower()
                
                if debug_choice == 'y':
                    debug_success = self.debug_golang_code(golang_file, result.stderr)
                    
                    if debug_success:
                        print(colored("\nAttempting to build with fixed code...", "yellow"))
                        result = subprocess.run(["go", "build", golang_file], capture_output=True, text=True)
                        
                        if result.returncode != 0:
                            print(colored("Build still failed after debugging attempt.", "red"))
                            print(colored(result.stderr, "red"))
                        else:
                            exe_file = f"{golang_file.removesuffix('.go')}.exe" if os.name == 'nt' else file_name
                            print(colored(f"\nSuccess! Fixed the code and built your program at '{exe_file}'.", "green"))
                            
                            run_program = input("Do you want to run the program? (y/n): ").strip().lower()
                            if run_program == 'y':
                                subprocess.run([f"./{exe_file}" if os.name != 'nt' else exe_file])
                            else:
                                print("Program not run.")
                else:
                    print("Debugging skipped.")
            else:
                exe_file = f"{golang_file.removesuffix('.go')}.exe" if os.name == 'nt' else file_name
                print(colored(f"Successfully built your program at '{exe_file}'.\n", "green"))
                
                run_program = input("Do you want to run the program? (y/n): ").strip().lower()
                if run_program == 'y':
                    subprocess.run([f"./{exe_file}" if os.name != 'nt' else exe_file])
                else:
                    print("Program not run.")

    def clean_files(self):
        deleted_files = 0
        for ext in [".go", ".exe"]:
            for file in Path(os.getcwd()).glob(f"*{ext}"):
                file.unlink()
                deleted_files += 1
        print(f"Deleted {deleted_files} generated files.")

def main():
    interpreter = AILanguageInterpreter()
    cwd = os.getcwd()
    
    while True:
        try:
            command = input(f"The AI Lang Interpreter 0.0.2 at {cwd} -> \n").strip()
            
            if command.lower() == 'exit':
                break
            
            elif command.lower().startswith('make '):
                file_path = command[5:].strip()
                interpreter.process_file(file_path)
            
            elif command.lower() == 'clean':
                interpreter.clean_files()
            
            elif command.lower().startswith('config '):
                api_key = command[7:].strip()
                interpreter.save_api_key(api_key)
            
            elif command.lower() == 'help':
                print("\nCommands:")
                print("make <file.ail> - Process a .ail file")
                print("clean           - Remove all generated .go and .exe files")
                print("config <key>    - Set Hugging Face API key persistently")
                print("help            - Show this help message")
                print("exit            - Exit the program")
            
            else:
                print(colored("Invalid command. Type 'help' for the help menu.", "red"))
                
        except Exception as e:
            print(colored(f"Error: {str(e)}", "red"))

if __name__ == "__main__":
    main()
