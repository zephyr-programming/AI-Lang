# © 2025 Samarvir Singh Vasale

import os
import time
import requests
import json
import subprocess
from pathlib import Path
from termcolor import colored
import re

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "ailconfig.json")

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
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(colored("Error: ailconfig.json is corrupted. Creating a new one.", "red"))
                return self.create_default_config()
        else:
            return self.create_default_config()

    def create_default_config(self):
        return {
            "provider": None,
            "hf_api_key": "",
            "or_api_key": "",
            "model_info": {
                "hf": "Qwen/Qwen2.5-72B-Instruct",
                "or": "google/gemini-2.0-flash-thinking-exp:free"
            },
            "project_dirs": []
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

    def convert_to_golang(self, english_text, project_dir):
        prompt = f"""You are an expert Golang developer. Convert the following English description into clean, efficient, and idiomatic Golang code. The code should:
1. Follow Go best practices and conventions
2. Include proper error handling
3. Be well-documented with comments
4. Use appropriate data structures and algorithms
5. Be production-ready and performant

English description:
{english_text}

Generate only the Golang code without any explanations. The code should be complete and ready to compile:"""

        try:
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
                    raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    golang_code = result[0]["generated_text"]
                else:
                    raise Exception(f"Unexpected response format: {result}")

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
                    raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

                result = response.json()
                golang_code = result["choices"][0]["message"]["content"]

            golang_code = golang_code.replace("```go", "").replace("```golang", "").replace("```", "").strip()

            file_name = "main.go"
            file_path = os.path.join(project_dir, file_name)
            with open(file_path, "w") as f:
                f.write(golang_code)

            print(f"Golang code saved to {file_path}")
            return file_path

        except Exception as e:
            print(colored(f"Error converting English to Golang: {e}", "red"))
            self.explain_error(str(e))  # Pass the error message to explain_error
            raise

    def debug_golang_code(self, golang_file, error_message):
        """Send the error message and file contents to the AI for debugging
        and update the file with the fixed code.
        """
        print(colored("\nSending code to AI for debugging...", "yellow"))

        try:
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
                    raise Exception(f"API request failed with status code {response.status_code}: {response.text}")


                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    fixed_code = result[0]["generated_text"]
                else:
                    raise Exception(f"Unexpected response format: {result}")

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
                    raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

                result = response.json()
                fixed_code = result["choices"][0]["message"]["content"]


            fixed_code = fixed_code.replace("```go", "").replace("```golang", "").replace("```", "").strip()

            with open(golang_file, "w") as f:
                f.write(fixed_code)

            print(colored(f"Fixed code saved to {golang_file}", "green"))
            return True

        except Exception as e:
            print(colored(f"Error debugging Golang code: {e}", "red"))
            self.explain_error(str(e))
            return False


    def infer_and_install_dependencies(self, golang_file, project_dir):
        """Infer dependencies from the Go code and install them."""
        print(colored("\nInferring and installing dependencies...", "yellow"))
        try:
            with open(golang_file, 'r') as f:
                code = f.read()

            imports = re.findall(r'import\s+"([^"]+)"|import\s+\(([^)]+)\)', code, re.MULTILINE)
            dependencies = set()
            for match in imports:
                if match[0]:
                    dependencies.add(match[0])
                elif match[1]:
                    for dep in match[1].split():
                        dep = dep.strip().replace('"', '')
                        if dep:
                            dependencies.add(dep)

            filtered_dependencies = [dep for dep in dependencies if "." in dep]

            if not filtered_dependencies:
                print(colored("No external dependencies found.", "green"))
                return

            print(colored(f"Found dependencies: {', '.join(filtered_dependencies)}", "cyan"))

            # Install dependencies using go get
            for dep in filtered_dependencies:
                print(colored(f"Installing {dep}...", "yellow"))
                result = subprocess.run(["go", "get", dep], cwd=project_dir, capture_output=True, text=True)
                if result.returncode != 0:
                    print(colored(f"Failed to install {dep}: {result.stderr}", "red"))
                    self.explain_error(result.stderr) # Explain dependency install error
                else:
                    print(colored(f"Successfully installed {dep}", "green"))

        except FileNotFoundError:
            error_msg = f"Error: Go file not found: {golang_file}"
            print(colored(error_msg, "red"))
            self.explain_error(error_msg)
            raise
        except Exception as e:
            print(colored(f"Error inferring/installing dependencies: {str(e)}", "red"))
            self.explain_error(str(e))
            raise

    def build_program(self, golang_file, project_dir):
        print("\nBuilding your program...")
        estimated_time = os.path.getsize(golang_file) / 1000
        print(f"Estimated build time: {estimated_time:.1f} seconds")
        time.sleep(min(estimated_time, 3))  # Simulate build time
        return True


    def show_interactive_commands(self):
        """Display the list of available interactive commands."""
        print("""
Commands:
show     - Display current code
modify   - Make specific changes to the code
explain  - Explain the current code
optimize - Optimize the current code
add      - Add new functionality
done     - Exit interactive mode
        """)

    def interactive_session(self, ail_file):
        """Start an interactive session based on a .ail file."""
        if not ail_file.endswith('.ail'):
            print(colored("Error: File must have .ail extension", "red"))
            return

        if not os.path.exists(ail_file):
            print(colored(f"Error: File '{ail_file}' not found", "red"))
            return

        print(colored(f"\nStarting interactive mode with {ail_file}", "green"))

        try:
            with open(ail_file, 'r') as f:
                english_text = f.read()

            project_name = input("\nEnter the name for your project: ").strip()
            project_dir = os.path.join(os.getcwd(), project_name)
            os.makedirs(project_dir, exist_ok=True)

            # Add project directory to config
            if "project_dirs" not in self.config:
                self.config["project_dirs"] = []
            if project_dir not in self.config["project_dirs"]:
                self.config["project_dirs"].append(project_dir)
                self.save_config()


            print("\nConverting English to Golang...")
            golang_file = self.convert_to_golang(english_text, project_dir)

            # Create go.mod and install dependencies
            subprocess.run(["go", "mod", "init", project_name], cwd=project_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.infer_and_install_dependencies(golang_file, project_dir)

            self.show_interactive_commands()

            while True:
                command = input(colored("\nEnter your command -> ", "cyan")).strip().lower()

                if command == 'done':
                    self.build_and_debug_on_exit(golang_file, project_dir)
                    break
                elif command == 'show':
                    with open(golang_file, 'r') as f:
                        print("\nCurrent code:")
                        print(colored(f.read(), "yellow"))
                elif command == 'help':
                    self.show_interactive_commands()
                elif command == 'explain':
                    self.handle_interactive_command(command, golang_file)
                elif command in ['modify', 'optimize', 'add']:
                    self.handle_interactive_command(command, golang_file)
                    # Attempt to build after modification
                    result = subprocess.run(["go", "build", golang_file], cwd=project_dir, capture_output=True, text=True)
                    if result.returncode != 0:
                        print(colored("Build failed!", "red"))
                        print(colored(result.stderr, "red"))
                        self.explain_error(result.stderr) # Explain build error
                        debug_choice = input("\nWould you like to debug and fix the errors? (y/n): ").strip().lower()
                        if debug_choice == 'y':
                            self.debug_golang_code(golang_file, result.stderr)
                    # Re-install dependencies after modification
                    self.infer_and_install_dependencies(golang_file, project_dir)

                else:
                    print(colored("Unknown command. Type 'help' to see available commands.", "red"))

        except Exception as e:
            print(colored(f"An unexpected error occurred: {e}", "red"))
            self.explain_error(str(e))


    def build_and_debug_on_exit(self, golang_file, project_dir):
        """Build the program and offer debugging options on exit from interactive mode."""

        build_success = False
        debug_attempts = 0
        max_debug_attempts = 5

        while not build_success and debug_attempts < max_debug_attempts:
            result = subprocess.run(["go", "build", golang_file], cwd=project_dir, capture_output=True, text=True)

            if result.returncode != 0:
                print(colored("Build failed!", "red"))
                print(colored(result.stderr, "red"))
                self.explain_error(result.stderr) # Explain build error

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
            exe_file = golang_file.removesuffix('.go')
            print(colored(f"\nSuccess! Built your program at '{os.path.join(project_dir, exe_file)}'.", "green"))

            run_program = input("Do you want to run the program? (y/n): ").strip().lower()
            if run_program == 'y':
                subprocess.run([os.path.join(project_dir, exe_file)], cwd=project_dir)
            else:
                print("Program not run.")
        elif debug_attempts >= max_debug_attempts:
            print(colored(f"\nReached maximum number of debug attempts ({max_debug_attempts}).", "red"))
            print(colored("The code still has errors. You may need to manually fix the issues.", "red"))
        else:
            print(colored("\nBuild process was not successful.", "red"))

    def handle_interactive_command(self, command, golang_file):
        """Handle different interactive commands."""
        try:
            with open(golang_file, 'r') as f:
                current_code = f.read()

            if command == 'explain':
                user_input = ""  # No additional input needed for explain
                prompt = f"Explain this Golang code:\n{current_code}"
            else:
                user_input = input(colored("Describe your task: ", "cyan"))
                prompt_map = {
                    'modify': f"Modify this Golang code according to the following request: '{user_input}'. Return only the complete modified code:\n{current_code}",
                    'optimize': f"Optimize this Golang code, focusing on: {user_input}. Return only the optimized code:\n{current_code}",
                    'add': f"Add the following functionality to this Golang code: '{user_input}'. Return only the complete modified code:\n{current_code}"
                }
                prompt = prompt_map[command]


            if self.provider == "hf":
                response = self.send_to_hf(prompt)
            else:
                response = self.send_to_or(prompt)

            if command == 'explain':
                print("\nExplanation:")
                print(colored(response, "yellow"))
            else:
                with open(golang_file, 'w') as f:
                    f.write(response)
                print(colored("\nCode updated successfully!", "green"))

        except Exception as e:
            print(colored(f"Error during interactive mode: {str(e)}", "red"))
            self.explain_error(str(e))


    def send_to_hf(self, prompt):
        """Send prompt to HuggingFace and process response."""
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
            raise Exception(f"API request failed: {response.text}")

        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0]["generated_text"].replace("```go", "").replace("```golang", "").replace("```", "").strip()
        raise Exception(f"Unexpected response format: {result}")

    def send_to_or(self, prompt):
        """Send prompt to OpenRouter and process response."""
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
            raise Exception(f"API request failed: {response.text}")

        result = response.json()
        return result["choices"][0]["message"]["content"].replace("```go", "").replace("```golang", "").replace("```", "").strip()

    def process_file(self, file_path):
        if not file_path.endswith('.ail'):
            raise ValueError("Only .ail files are supported")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, 'r') as f:
                english_text = f.read()

            project_name = input("\nEnter the name for your project: ").strip()
            project_dir = os.path.join(os.getcwd(), project_name)
            os.makedirs(project_dir, exist_ok=True)  # Create project directory

            # Add project directory to config
            if "project_dirs" not in self.config:
                self.config["project_dirs"] = []
            if project_dir not in self.config["project_dirs"]:
                self.config["project_dirs"].append(project_dir)
                self.save_config()

            print("\nConverting English to Golang...")
            golang_file = self.convert_to_golang(english_text, project_dir)

            # Create go.mod and install dependencies
            subprocess.run(["go", "mod", "init", project_name], cwd=project_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.infer_and_install_dependencies(golang_file, project_dir)

            success = self.build_program(golang_file, project_dir)

            if success:
                print("\nGoLang file built! Converting to executable...\n")

                build_success = False
                debug_attempts = 0
                max_debug_attempts = 5

                while not build_success and debug_attempts < max_debug_attempts:
                    result = subprocess.run(["go", "build", golang_file], cwd=project_dir, capture_output=True, text=True)

                    if result.returncode != 0:
                        print(colored("Build failed!", "red"))
                        print(colored(result.stderr, "red"))
                        self.explain_error(result.stderr) # Explain build error

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
                    exe_file = golang_file.removesuffix('.go')
                    print(colored(f"\nSuccess! Built your program at '{os.path.join(project_dir, exe_file)}'.", "green"))

                    run_program = input("Do you want to run the program? (y/n): ").strip().lower()
                    if run_program == 'y':
                        subprocess.run([os.path.join(project_dir, exe_file)], cwd=project_dir)
                    else:
                        print("Program not run.")
                elif debug_attempts >= max_debug_attempts:
                    print(colored(f"\nReached maximum number of debug attempts ({max_debug_attempts}).", "red"))
                    print(colored("The code still has errors. You may need to manually fix the issues.", "red"))
                else:
                    print(colored("\nBuild process was not successful.", "red"))
        except Exception as e:
            print(colored(f"An unexpected error occurred: {e}", "red"))
            self.explain_error(str(e))


    def clean_files(self):
        """Clean up generated project directories."""
        if "project_dirs" not in self.config:
            print("No project directories to clean.")
            return

        deleted_dirs = 0
        for project_dir in self.config["project_dirs"]:
            if os.path.exists(project_dir) and os.path.isdir(project_dir):
                try:
                    # Use shutil.rmtree to remove non-empty directories
                    import shutil
                    shutil.rmtree(project_dir)
                    deleted_dirs += 1
                except OSError as e:
                    print(colored(f"Error deleting {project_dir}: {e}", "red"))
                    self.explain_error(str(e)) # Explain deletion error
            else:
                print(colored(f"Directory not found: {project_dir}", "yellow"))

        print(colored(f"Deleted {deleted_dirs} project directories.", "green"))

        self.config["project_dirs"] = []
        self.save_config()

    def explain_error(self, error_message):
        """Explain the error using the AI."""

        prompt = f"""You are an expert programmer. Explain the following error message in simple terms,
        suggest possible causes, and provide potential solutions. The explanation should be concise and easy to understand for someone
        who may not be deeply familiar with the programming language.
        The error should be attempted to be kept within 2-3 sentences.
        Do not give the explanation in markdown, it should be given in plaintext only.
        Start with this sentence always 'Let's break down this error message.'
        There is no need to specify the name of the file as main.go or anything else in the explanation.:

        ERROR MESSAGE:
        {error_message}
        """
        try:
            if self.provider == "hf":
                response = self.send_to_hf(prompt)
            else:
                response = self.send_to_or(prompt)

            print(colored("\nError Explanation:", "cyan"))
            print(colored(response, "yellow"))

        except Exception as e:
            print(colored(f"Error explaining error: {e}", "red"))
            print(colored("\nOriginal Error Message:", "cyan"))
            print(colored(error_message, "yellow"))


def main():
    interpreter = AILanguageInterpreter()
    cwd = os.getcwd()

    while True:
        try:
            command = input(f"The AI Lang Interpreter 0.0.4 at {cwd} -> \n").strip()

            if command.lower() == 'exit':
                break

            elif command.lower().startswith('make '):
                file_path = command[5:].strip()
                interpreter.process_file(file_path)

            elif command.lower() == 'interactive':
                ail_file = input("Enter the location of the .ail file you want to base this interaction off of: ").strip()
                interpreter.interactive_session(ail_file)

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
                print("interactive      - Enter interactive mode")
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
            interpreter.explain_error(str(e))

if __name__ == "__main__":
    main()
