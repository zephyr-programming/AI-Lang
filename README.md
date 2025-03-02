# AI Lang - The future of programming languages

AI Lang or AIL, is the future of programming languages.<br>
It functions by integrating programming and AI together.<br>
This makes it easy for anyone to do programming.<br>
No learning is required and thus makes AIL a plain english programming language.

## Features

*   Converts English descriptions to Golang code.
*   Saves generated Golang code to `.go` files.
*   Builds and optionally runs the generated Golang code.
*   Allows the user to specify a custom Hugging Face model.
*   Saves and loads the Hugging Face API key from a configuration file.

## Prerequisites

*   Python 3.x
*   Hugging Face API key (obtainable from [https://huggingface.co/](https://huggingface.co/))
*   Go (for building and running the generated code)

## Installation

### Using the installer

*   Go to the [Latest Release](https://github.com/zephyr-programming/AI-Lang/releases/tag/Installer) and install the file 'AILInstaller.exe'.
*   Open the downloaded installer program.
*   Install the program by following the steps in the installer.
*   Restart your computer, in order to effectively use resources added the PATH by the installer.

### Using the Python file

*   Clone the repository using the command:
    ```bash
    git clone https://github.com/zephyr-programming/AI-Lang.git
    ```
*   Enter the directory in which the repository has been cloned.
*   Install the required python libraries using the command:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

*  Run the `main.py` script or type `ail` in your terminal with respect to your installation method.
*  Enter your HuggingFace API key when prompted.
*  Use the `make <file.ail>` command to process a `.ail` file.  For example:

    ```
    make your-file.ail
    ```

*  Enter a project name when prompted.
*  The program will convert the English text in the `.ail` file to Golang code, save it to a `.go` file, and attempt to build it.
*  If the build is successful, you will be prompted to run the program.

## Commands

*   `make <file.ail>`: Processes a `.ail` file.
*   `clean`: Removes all generated `.go` and `.exe` files.
*   `config <key>`: Sets the Hugging Face API key.
*   `help`: Displays the help menu.
*   `exit`: Exits the program.

## License

This project is licensed under the Creative Commons Zero v1.0 Universal license. You may view the license at [this link.](https://github.com/zephyr-programming/AI-Lang/blob/main/LICENSE).
