# © 2025 Samarvir Singh Vasale

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
        self.config = self.load_config()
        self.provider = self.config.get("provider", None)
        self.api_keys = {
            "hf": self.config.get("hf_api_key", ""),
            "or": self.config.get("or_api_key", "")
        }
        self.model_info = self.config.get("model_info", {
            "hf": "Qwen/Qwen2.5-72B-Instruct",
            "or": "google/gemini-2.0-flash-thinking-exp:free"
        })

        if not self.provider:
            self.initial_provider_setup()
        
        self.setup_api_config()

    def initial_provider_setup(self):
        print("Welcome to AI Language Interpreter!")
        print("Please select which AI provider you want to use:")
        print("1. HuggingFace")
        print("2. OpenRouter")
        
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice == "1":
            self.provider = "hf"
            if not self.api_keys["hf"]:
                self.api_keys["hf"] = input("Please enter your HuggingFace API key: ")
                self.config["hf_api_key"] = self.api_keys["hf"]
        elif choice == "2":
            self.provider = "or"
            if not self.api_keys["or"]:
                self.api_keys["or"] = input("Please enter your OpenRouter API key: ")
                self.config["or_api_key"] = self.api_keys["or"]
        else:
            print(colored("Invalid choice. Defaulting to HuggingFace.", "yellow"))
            self.provider = "hf"
            if not self.api_keys["hf"]:
                self.api_keys["hf"] = input("Please enter your HuggingFace API key: ")
                self.config["hf_api_key"] = self.api_keys["hf"]
        
        self.config["provider"] = self.provider
        self.save_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        else:
            return {
                "provider": None,
                "hf_api_key": "",
                "or_api_key": "",
                "model_info": {
                    "hf": "Qwen/Qwen2.5-72B-Instruct",
                    "or": "google/gemini-2.0-flash-thinking-exp:free"
                }
            }

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=2)
        print(colored("Configuration saved successfully!", "green"))

    def setup_api_config(self):
        if self.provider == "hf" and not self.api_keys["hf"]:
            self.api_keys["hf"] = input("Please enter your HuggingFace API key: ")
            self.config["hf_api_key"] = self.api_keys["hf"]
            self.save_config()
        elif self.provider == "or" and not self.api_keys["or"]:
            self.api_keys["or"] = input("Please enter your OpenRouter API key: ")
            self.config["or_api_key"] = self.api_keys["or"]
            self.save_config()

        if self.provider == "hf":
            self.api_url = f"https://api-inference.huggingface.co/models/{self.model_info['hf']}"
            self.headers = {"Authorization": f"Bearer {self.api_keys['hf']}"}
        else: 
            self.api_url = "https://openrouter.ai/api/v1/chat/completions"
            self.headers = {
                "Authorization": f"Bearer {self.api_keys['or']}",
                "HTTP-Referer": "https://ailang.interpreter",
                "X-Title": "AI Language Interpreter"
            }

    def change_provider(self, provider):
        if provider not in ["hf", "or"]:
            print(colored(f"Invalid provider: {provider}. Use 'hf' for HuggingFace or 'or' for OpenRouter.", "red"))
            return False
        
        self.provider = provider
        self.config["provider"] = provider
        
        if provider == "hf" and not self.api_keys["hf"]:
            self.api_keys["hf"] = input("Please enter your HuggingFace API key: ")
            self.config["hf_api_key"] = self.api_keys["hf"]
        elif provider == "or" and not self.api_keys["or"]:
            self.api_keys["or"] = input("Please enter your OpenRouter API key: ")
            self.config["or_api_key"] = self.api_keys["or"]
        
        self.setup_api_config()
        self.save_config()
        
        provider_name = "HuggingFace" if provider == "hf" else "OpenRouter"
        model_name = self.model_info[provider]
        print(colored(f"Provider changed to {provider_name}. Using model: {model_name}", "green"))
        return True

    def change_model(self):
        if self.provider == "hf":
            print(f"Current HuggingFace model: {self.model_info['hf']}")
            use_custom_model = input("Would you like to use a different HuggingFace model? (y/n): ").strip().lower()
            if use_custom_model == 'y':
                model_id = input("Please enter the HuggingFace model ID: ").strip()
                self.model_info["hf"] = model_id
                self.config["model_info"]["hf"] = model_id
                self.save_config()
                self.setup_api_config()
                print(colored(f"HuggingFace model changed to: {model_id}", "green"))
        else:  
            print(f"Current OpenRouter model: {self.model_info['or']}")
            model_id = input("Please enter the OpenRouter model ID: ").strip()
            self.model_info["or"] = model_id
            self.config["model_info"]["or"] = model_id
            self.save_config()
            self.setup_api_config()
            print(colored(f"OpenRouter model changed to: {model_id}", "green"))

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

        if self.provider == "hf":
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
                    
                    golang_code = golang_code.replace("```go", "").replace("```golang", "").replace("```", "").strip()
                    
                    file_path = f"{file_name}.go"
                    with open(file_path, "w") as f:
                        f.write(golang_code)
                    
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
        else:  
            payload = {
                "model": self.model_info["or"],
                "messages": [
                    {"role": "system", "content": "You are an expert Golang developer."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2048
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            if response.status_code != 200:
                error_msg = colored(f"Failed to convert English to Golang: {response.text}", "red")
                print(error_msg)
                raise Exception(error_msg)
                
            try:
                result = response.json()
                golang_code = result["choices"][0]["message"]["content"]
                
                golang_code = golang_code.replace("```go", "").replace("```golang", "").replace("```", "").strip()
                
                file_path = f"{file_name}.go"
                with open(file_path, "w") as f:
                    f.write(golang_code)
                
                print(f"Golang code saved to {file_path}")
                return file_path
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

        if self.provider == "hf":
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
        else:  
            payload = {
                "model": self.model_info["or"],
                "messages": [
                    {"role": "system", "content": "You are an expert Golang developer."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2048
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            if response.status_code != 200:
                error_msg = colored(f"Failed to debug Golang code: {response.text}", "red")
                print(error_msg)
                raise Exception(error_msg)
                
            try:
                result = response.json()
                fixed_code = result["choices"][0]["message"]["content"]
                
                fixed_code = fixed_code.replace("```go", "").replace("```golang", "").replace("```", "").strip()
                
                with open(golang_file, "w") as f:
                    f.write(fixed_code)
                
                print(colored(f"Fixed code saved to {golang_file}", "green"))
                return True
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
            
            build_success = False
            debug_attempts = 0
            max_debug_attempts = 5 
            
            while not build_success and debug_attempts < max_debug_attempts:
                result = subprocess.run(["go", "build", golang_file], capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(colored("Build failed!", "red"))
                    print(colored(result.stderr, "red"))
                    
                    debug_choice = input("\nWould you like to debug and fix the errors? (y/n): ").strip().lower()
                    
                    if debug_choice == 'y':
                        debug_attempts += 1
                        print(colored(f"Debug attempt {debug_attempts}/{max_debug_attempts}", "yellow"))
                        
                        debug_success = self.debug_golang_code(golang_file, result.stderr)
                        
                        if not debug_success:
                            print(colored("Failed to debug the code. Please try again.", "red"))
                            break
                        
                        print(colored("\nAttempting to build with fixed code...", "yellow"))
                    else:
                        print("Debugging skipped.")
                        break
                else:
                    build_success = True
            
            if build_success:
                exe_file = f"{golang_file.removesuffix('.go')}.exe" if os.name == 'nt' else file_name
                print(colored(f"\nSuccess! Built your program at '{exe_file}'.", "green"))
                
                run_program = input("Do you want to run the program? (y/n): ").strip().lower()
                if run_program == 'y':
                    subprocess.run([f"./{exe_file}" if os.name != 'nt' else exe_file])
                else:
                    print("Program not run.")
            elif debug_attempts >= max_debug_attempts:
                print(colored(f"\nReached maximum number of debug attempts ({max_debug_attempts}).", "red"))
                print(colored("The code still has errors. You may need to manually fix the issues.", "red"))
            else:
                print(colored("\nBuild process was not successful.", "red"))

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
            command = input(f"The AI Lang Interpreter 0.0.3 at {cwd} -> \n").strip()
            
            if command.lower() == 'exit':
                break
            
            elif command.lower().startswith('make '):
                file_path = command[5:].strip()
                interpreter.process_file(file_path)
            
            elif command.lower() == 'clean':
                interpreter.clean_files()
            
            elif command.lower().startswith('config hf '):
                api_key = command[10:].strip()
                interpreter.api_keys["hf"] = api_key
                interpreter.config["hf_api_key"] = api_key
                interpreter.save_config()
                if interpreter.provider == "hf":
                    interpreter.setup_api_config()
            
            elif command.lower().startswith('config or '):
                api_key = command[10:].strip()
                interpreter.api_keys["or"] = api_key
                interpreter.config["or_api_key"] = api_key
                interpreter.save_config()
                if interpreter.provider == "or":
                    interpreter.setup_api_config()
            
            elif command.lower() == 'provider hf':
                interpreter.change_provider("hf")
            
            elif command.lower() == 'provider or':
                interpreter.change_provider("or")
            
            elif command.lower() == 'model':
                interpreter.change_model()
            
            elif command.lower() == 'status':
                provider_name = "HuggingFace" if interpreter.provider == "hf" else "OpenRouter"
                model_name = interpreter.model_info[interpreter.provider]
                print(f"Current provider: {provider_name}")
                print(f"Current model: {model_name}")
                print(f"HF API Key: {'Set' if interpreter.api_keys['hf'] else 'Not set'}")
                print(f"OR API Key: {'Set' if interpreter.api_keys['or'] else 'Not set'}")
            
            elif command.lower() == 'help':
                print("\nCommands:")
                print("make <file.ail>  - Process a .ail file")
                print("clean            - Remove all generated .go and .exe files")
                print("config hf <key>  - Set HuggingFace API key")
                print("config or <key>  - Set OpenRouter API key")
                print("provider hf      - Switch to HuggingFace provider")
                print("provider or      - Switch to OpenRouter provider")
                print("model            - Change the current model")
                print("status           - Show current provider and model settings")
                print("help             - Show this help message")
                print("exit             - Exit the program")
            
            else:
                print(colored("Invalid command. Type 'help' for the help menu.", "red"))
                
        except Exception as e:
            print(colored(f"Error: {str(e)}", "red"))

if __name__ == "__main__":
    main()
