
# ðŸŒ  LookBack Apriori Algorithm
This is a flask app developed in order to manage data and through LookBack Apriori Algorithm creates a set of rules to match a user query.


## Project description
The application is based on LAL, this algorithm is an extension with time of classic Apriori Algorithm.
It's a data mining techniques to analyze big datasets.
We simulate that the data (Data/) coming from fitbit.

### ðŸš€ Future implementation
This project represents the server and in the future it will connected through API with Database and mobile Application.

### ðŸ Technologies used
To develop application i used VisualStudio code and powershell integrated.
The language to handle data and creates algorithm is Python.

I used a Flask because it's a Python module that lets me develop web application easily.

Web App pages are based on Bootstrap a front-end framework used to create modern websites and web apps.
It's open-source and free to use, yet features numerous HTML and CSS templates for UI interface elements.

## âš ï¸ Installation and Run the Project
### Configuration
- Clone the project
```
 git clone https://github.com/DataScienceUNIVR/Temporal_Apriori_Algorithm
  ```
- Create a virtual enviroment
- Put the project in venv
- Create folder 'Data' in venv and put in it fitbit data named pm1,pm2,pm3,pm4
- Activate venv:
   
   ```
   .\Scripts\activate
   ```
- Install all library necessary:  
   ```
   pip install -r requirements.txt
    ```

### Run
0- Make sure you have activate venv

1- You need to add enviroment variable.
- Win10 powershell:  ```$FLASK_APP="app"```
- Linux and MacOs: ```export FLASK_APP=app```

2- Launch app.
- ```flask run```

3- Open http://127.0.0.1:5000/

### âš¡ Usage
#### Use case diagram
![](images/UseCase.jpg)
- Settings page: compile form with setting in order to generate rules
![](images/form1.jpg)
- Rules generated
![](images/form2.jpg)
- MatchQuery: insert a query for matching
![](images/form3.jpg)
- Result of matching
![](images/form4.jpg)


## Authors

- ðŸ‡®ðŸ‡¹ [@MarcoCastelli](https://github.com/MarcoCastelli4)
- [![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://it.linkedin.com/in/marco-castelli-65643b203)

