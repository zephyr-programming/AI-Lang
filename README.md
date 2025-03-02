# AI Lang - The future of programming languages

This project provides a command-line tool that interprets English text and converts it into Golang code using the Hugging Face API.

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
*   

## Usage

1.  Run the `main.py` script:

    ```bash
    python main.py
    ```

2.  Enter your Hugging Face API key when prompted (or use the `config` command).
3.  Use the `make <file.ail>` command to process a `.ail` file.  For example:

    ```
    make AIL-Files/test.ail
    ```

4.  Enter a project name when prompted.
5.  The program will convert the English text in the `.ail` file to Golang code, save it to a `.go` file, and attempt to build it.
6.  If the build is successful, you will be prompted to run the program.

## Commands

*   `make <file.ail>`: Processes a `.ail` file.
*   `clean`: Removes all generated `.go` and `.exe` files.
*   `config <key>`: Sets the Hugging Face API key.
*   `help`: Displays the help menu.
*   `exit`: Exits the program.

## Example .ail file (AIL-Files/test.ail)

```
Write a simple "Hello, World!" program in Go.
```

## License

[Insert License Here - e.g., MIT, Apache 2.0]
