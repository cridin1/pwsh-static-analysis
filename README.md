# pwsh-syntax-analyzer
Python NLP wrapper for powershell syntax analysis through PSScript Analyzer. Make sure you have installed [PSScript Analyzer](https://github.com/PowerShell/PSScriptAnalyzer).

```bash
PS > python script.py -h                                                                 

                          _                                _                                            _
                         | |                              | |                                          | |
    _ __ __      __ ___  | |__  ______  ___  _   _  _ __  | |_  __ _ __  __ ______  __ _  _ __    __ _ | | _   _  ____ ___  _ __  
    | '_ \ \ /\ / // __|| '_ \|______|/ __|| | | || '_ \ | __|/ _` |\ \/ /|______|/ _` || '_ \  / _` || || | | ||_  // _ \| '__|  
    | |_) |\ V  V / \__ \| | | |       \__ \| |_| || | | || |_| (_| | >  <        | (_| || | | || (_| || || |_| | / /|  __/| |    
    | .__/  \_/\_/  |___/|_| |_|       |___/ \__, ||_| |_| \__|\__,_|/_/\_\        \__,_||_| |_| \__,_||_| \__, |/___|\___||_|    
    | |                                       __/ |                                                         __/ |
    |_|                                      |___/                                                         |___/


usage: script.py [-h] [-v [V]] ANSWER_PATH [GROUND_TRUTH] [OUT_FILE] [FROM_ESCAPE]

Python NLP wrapper for powershell syntax analysis through PSScript Analyzer       

positional arguments:
  ANSWER_PATH   Answers text file path from the model
  GROUND_TRUTH  Ground truth text file path
  OUT_FILE      Output csv file
  FROM_ESCAPE   Output files from escape

options:
  -h, --help    show this help message and exit
  -v [V]        Verbose
```
