# DmAssistant Project Setup and Execution Guide

This guide will help you set up and run the DmAssistant project on Windows using Conda.

## Prerequisites

- [Anaconda](https://www.anaconda.com/products/distribution) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed on your system.

## Setting Up the Environment

1. Clone the repository:
   ```
   git clone https://github.com/YourUsername/DmAssistant.git
   cd DmAssistant
   ```

2. Create a new Conda environment:
   ```
   conda create --name dnd_manager_env python=3.x
   ```
   Replace `3.x` with the specific Python version you're using for this project.

3. Activate the Conda environment:
   ```
   conda activate dnd_manager_env
   ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

To run the DmAssistant, follow these steps:

1. Navigate to the project directory:
   ```
   cd C:\Users\Koena\Documents\GitHub\DmAssistant
   ```

2. Activate the Conda environment:
   ```
   conda activate dnd_manager_env
   ```

3. Run the main Python script:
   ```
   python main.py
   ```

## Requirements

The `requirements.txt` file contains all the necessary Python packages for this project. You don't need to add Conda to the `requirements.txt` file, as Conda is the environment management system, not a Python package.

Here's a reminder of what your `requirements.txt` should look like:

```
tkinter
tkhtmlview
markdown
openai
faiss-cpu
numpy
tiktoken
python-dotenv
Pillow
```

## Updating Python or Conda

To update Python within your Conda environment:

```
conda update python
```

To update Conda itself:

```
conda update conda
```

## Troubleshooting

If you encounter any issues:

- Ensure Conda is properly installed and added to your system's PATH.
- If a specific package fails to install, try installing it with Conda:
  ```
  conda install package_name
  ```
- For packages not available in Conda, use pip inside the activated Conda environment.

## Additional Notes

- Always ensure you're in the correct Conda environment (`dnd_manager_env`) when working on this project.
- If you need to add new dependencies, remember to update the `requirements.txt` file:
  ```
  pip freeze > requirements.txt
  ```

If you need any further assistance, please open an issue in this repository.
