# Urban-Mobility-Optimization
____________________________________________________________________________________________________________________________________________________________________________________
## Introduction
The challenges of urban mobility, such as traffic jams, road accidents, and the inefficiency of public transportation, are major concerns in modern urban areas. With the increasing access to open data from platforms such as Open Data Soft, Data.gov, and the European Data Portal, it is becoming possible to leverage this information to optimize traffic flows and improve transportation systems.

## Problem Statement
This project aims to provide real-time predictive traffic conditions and intelligent recommendations based on customized scenarios to improve urban mobility. By using advanced predictive models, such as Recurrent Neural Networks (RNN) and hybrid models combining statistical approaches (like ARIMA) with deep learning, the solution seeks to help traffic managers and citizens make informed decisions ahead of time, mitigating congestion and optimizing transportation networks. Additionally, personalized recommendations for private drivers, public transportation, and urban managers will improve decision-making, reduce traffic jams, and facilitate efficient resource allocation.
____________________________________________________________________________________________________________________________________________________________________________________
## Data sources
- APIs :
  - [PRIM - Prochains passages - Requpête globale](https://prim.iledefrance-mobilites.fr/fr/apis/idfm-ivtr-requete_globale)
  - [PRIM - Prochains passages - Requpête unitaire](https://prim.iledefrance-mobilites.fr/fr/apis/idfm-ivtr-requete_unitaire)
- Datasets :
  - [Référentiels des arrêts](https://data.iledefrance-mobilites.fr/explore/dataset/arrets/export/?ref=prim.iledefrance-mobilites.fr)
- Other sources :
____________________________________________________________________________________________________________________________________________________________________________________
## Best Practices (First : English as a programming language)
- Follow naming conventions :
  - Use lowercase letters and underscores to separate words in file names and variables
  - Use meaningful names for files, variables, and functions
  - Use verbs for function names and nouns for arguments
- Add comments and docstrings :
  - Use docstrings to explain what your functions do and what they return
  - Always use comments to explain your code
- Use the main function to run your code
- For clean code :
  - Use a virtual environment for your project : `python -m venv venv`
  - Use a `.gitignore` file to avoid uploading unnecessary files to the repository
  - Use the `requirements.txt` file to list all the packages needed to run your code : `pip freeze > requirements.txt`
  - Upload the README.md file if necessary
  - Use the isort and black libraries to format your code : `isort black <filename>.py` and `black <filename>.py`
  - Use the flake8 library to check your code for PEP 8 compliance : `flake8 <filename>.py` and correct the errors
  - Use logging to log information, warnings, and errors and print them to the console

## Git
- Create a new branch for each feature you are working on
- Commit your changes with a meaningful message
- Push your changes to develop branch and create a pull request
- Review the code with your teammate
- Name the pull request with the name of the feature you are working on and add a description
- Merge the pull request if everything is correct and delete the branch

## Installation
- Clone the repository : `git clone
- Install the required packages : `pip install -r requirements.txt`
- Run the .exe file
- A navigation window will open to the streamlit interface
____________________________________________________________________________________________________________________________________________________________________________________
## Contributors
- [Aghiles SAGHIR](https://www.linkedin.com/in/aghiles-s)
- [Amayas MAHMOUDI](https://www.linkedin.com/in/amayas-mhd)
