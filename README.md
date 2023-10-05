# pwsh-gen
Python NLP wrapper for powershell syntax analysis through PSScript Analyzer

```bash
PS > python .\script.py -h
usage: script.py [-h] [-v [VERBOSE]] DESCRIPTION_PATH ANSWER_PATH GROUND_TRUTH OUT_FILE

Python NLP wrapper for powershell syntax analysis through PSScript Analyzer

positional arguments:
  DESCRIPTION_PATH      Description text file path from the model
  ANSWER_PATH           Answers text file path from the model
  GROUND_TRUTH          Ground truth text file path
  OUT_FILE              Output csv file

options:
  -h, --help            show this help message and exit
  -v [VERBOSE], --verbose [VERBOSE]
                        Verbose
```