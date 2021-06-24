# Instructions to use the API



![File structure scheme](Documentation/structure_scheme.png)



Follow the next steps to execute the API. Section 1 is optional.

### 1. Create a virtual environment

1. Install *virtualenv* library:

   ```shell
   $ pip install virtualenv
   ```

   

2. Create an environment:

   ```shell
   $ virtualenv venv
   ```

   

3. Activate the environment:

   ```shell
   $ source ./venv/bin/activate
   ```

   or

   ```shell
   $ source ./venv/Scripts/activate
   ```

   depending on what the directories names are.




### 2. Install required packages

1. Install 'requirements.txt':

   ```shell
   $ pip install -r requirements.txt
   ```

   

2. Install Tkinter to be able to use the application (App.py). It must be installed apart as it does not exist on PyPi:

   ```shell
   $ sudo apt-get install python3-tk
   ```




### 3. Execution

1. Enter the directory *Code*:

   ```shell
   $ cd Code
   ```

   

2. Execute the desired files from console. You can either execute the app or create a class instance.

   - If you want to try *MatchClass.py* methods, you can use *__TestMatchClass.py*, where there are examples of executions relating to match information calculation. You can uncomment the lines you are interested in.
   - If you want to try *SeasonClass.py* methods, you can use *__TestSeasonClass.py*, where there are examples of executions relating to season information calculation. You can uncomment the lines you are interested in.
   - You can execute *App.py* to execute the UI designed to execute the API methods.