API Key Management for models

Command Prompt
--------------
To set an API KEY:
    set API_KEY=your_api_key_here
To access it in Python:
    import os; api_key = os.getenv("API_KEY")
To view it:
    echo %API_KEY%


PowerShell
----------
To set an API KEY:
    $env:API_KEY = "your_api_key_here"
To access it in Python:
    import os; api_key = os.getenv("API_KEY")
To view it:
    echo $env:API_KEY


Linux/MacOS (Terminal)
----------------------
To set an API KEY:
    export API_KEY=your_api_key_here
To access it in Python:
    import os; api_key = os.getenv("API_KEY")
To view it:
    echo $API_KEY
