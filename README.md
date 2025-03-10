<h1 align="center">AI Lang - The future of programming languages</h1>

<p align="center">
  <img src="logo.PNG"/>
</p>

This project is a programming language designed to integrate AI into a programming language & translate natural language descriptions/roadmaps into functional Go code. It leverages the HuggingFace & OpenRouter API to convert English text into Go source code, streamlining the development process. The tool supports custom HuggingFace models, saves generated code, and provides build and run capabilities.

## Features

*   Converts english descriptions/roadmaps into Golang code.
*   Saves generated Golang code to `.go` files and also converts the same into a `.exe` file.
*   Generates GoLang code on the roadmap in the file used & converts it to an executable.
*   The user can use any model on HuggingFace or OpenRouter.

## Prerequisites

*   Python 3.x (Only if you are using the application via the Python script).
*   HuggingFace/OpenRouter API key (depending on the provider you use) (obtainable from [here](https://huggingface.co/settings/tokens)).
*   Go (for building and running the generated code).

## Installation

### Using the installer

*   Go to the [Latest Release](https://github.com/zephyr-programming/AI-Lang/releases/latest) and install the file 'AILInstaller.exe'.
*   Open the downloaded installer program.
*   Install the program by following the steps in the installer.
*   Restart your computer, in order to effectively use resources added the PATH by the installer.

### Using the Python file

*   Clone the repository using the command: `git clone https://github.com/zephyr-programming/AI-Lang.git`
*   Enter the directory in which the repository has been cloned.
*   Install the required python libraries using the command: `pip install -r requirements.txt`

## Usage

*  Run the `main.py` script or type `ail` in your terminal with respect to your installation method.
*  Enter your HuggingFace API key when prompted.
*  Use the `make <file.ail>` command to process a `.ail` file.  For example: `make your-file.ail`
*  Enter a project name when prompted.
*  The program will convert the English text in the `.ail` file to Golang code, save it to a `.go` file, and attempt to build it.
*  If the build is successful, you will be prompted to run the program.

## License

This project is licensed under the Creative Commons Zero v1.0 Universal license. You may view the license [here](https://github.com/zephyr-programming/AI-Lang/blob/main/LICENSE).
