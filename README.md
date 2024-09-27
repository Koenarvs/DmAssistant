DmAssistant Project Setup and Execution Guide
This guide will help you set up and run the DmAssistant project on Windows using Conda.
Prerequisites

Anaconda or Miniconda installed on your system.

Setting Up the Environment

Clone the repository:
Copygit clone https://github.com/YourUsername/DmAssistant.git
cd DmAssistant

Create a new Conda environment:
Copyconda create --name dnd_manager_env python=3.x
Replace 3.x with the specific Python version you're using for this project.
Activate the Conda environment:
Copyconda activate dnd_manager_env

Install the required packages:
Copypip install -r requirements.txt


Running the Application
To run the DmAssistant, follow these steps:

Navigate to the project directory:
Copycd C:\Users\Koena\Documents\GitHub\DmAssistant

Activate the Conda environment:
Copyconda activate dnd_manager_env

Run the main Python script:
Copypython main.py


Requirements
The requirements.txt file contains all the necessary Python packages for this project. You don't need to add Conda to the requirements.txt file, as Conda is the environment management system, not a Python package.
Here's a reminder of what your requirements.txt should look like:
Copytkinter
tkhtmlview
markdown
openai
faiss-cpu
numpy
tiktoken
python-dotenv
Pillow
Updating Python or Conda
To update Python within your Conda environment:
Copyconda update python
To update Conda itself:
Copyconda update conda
Troubleshooting
If you encounter any issues:

Ensure Conda is properly installed and added to your system's PATH.
If a specific package fails to install, try installing it with Conda:
Copyconda install package_name

For packages not available in Conda, use pip inside the activated Conda environment.

Additional Notes

Always ensure you're in the correct Conda environment (dnd_manager_env) when working on this project.
If you need to add new dependencies, remember to update the requirements.txt file:
Copypip freeze > requirements.txt


If you need any further assistance, please open an issue in this repository.
