# pwsh-syntax-analyzer
Python NLP wrapper for powershell syntax analysis through PSScript Analyzer. Make sure you have installed [PSScript Analyzer](https://github.com/PowerShell/PSScriptAnalyzer).

```bash
PS > python analyzer.py -h                                                                 

     __        __           __           ___                                     __  ___  __
    |__) |  | /__` |__| __ /__` \ / |\ |  |   /\  \_/ __  /\  |\ |  /\  |    \ /  / |__  |__)
    |    |/\| .__/ |  |    .__/  |  | \|  |  /~~\ / \    /~~\ | \| /~~\ |___  |  /_ |___ |  \


usage: analyzer.py [-h] [-v [V]] ANSWER_PATH [GROUND_TRUTH] [OUT_FILE] [FROM_ESCAPE]

Python NLP wrapper for powershell syntax analysis through PSScript Analyzer

positional arguments:
  ANSWER_PATH   Answers text file path from the model
  GROUND_TRUTH  Ground truth text file path
  OUT_FILE      Output csv file
  FROM_ESCAPE   Output files from ESCAPE

options:
  -h, --help    show this help message and exit
  -v [V]        Verbose
```
