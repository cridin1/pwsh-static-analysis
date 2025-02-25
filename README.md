# pwsh-static-analyzer
![syntax-analysis](https://github.com/cridin1/pwsh-syntax-analysis/blob/main/static-analysis.png)

Static code analysis for PowerShell code. 
Make sure you have installed [PSScript Analyzer](https://github.com/PowerShell/PSScriptAnalyzer).

```bash
$>python .\analyzer.py --help
                                                                                            

 █▀▄ █   █ ▄▀▀ █▄█    ▄▀▀ ▀█▀ ▄▀▄ ▀█▀ █ ▄▀▀    ▄▀▄ █▄ █ ▄▀▄ █   ▀▄▀ ▄▀▀ █ ▄▀▀
 █▀  ▀▄▀▄▀ ▄██ █ █ ▀▀ ▄██  █  █▀█  █  █ ▀▄▄ ▀▀ █▀█ █ ▀█ █▀█ █▄▄  █  ▄██ █ ▄██



usage: analyzer.py [-h] [--SCRIPT_MODE] [--FROM_ESCAPE] [-v [V]]
                   [OUT_FILE] PS_PATH [GROUND_TRUTH]

Python NLP wrapper for powershell syntax analysis through PSScript Analyzer

positional arguments:
  OUT_FILE       Output csv file
  PS_PATH        CODE file path from the model
  GROUND_TRUTH   Ground truth text file path

options:
  -h, --help     show this help message and exit
  --SCRIPT_MODE  Multiple Scripts mode
  --FROM_ESCAPE  Output files from ESCAPE
  -v [V]         Verbose
```

In `utils\analysis_classes.py`, the analysis is extended to different error types.
