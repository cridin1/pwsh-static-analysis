import pandas as pd
import os,ast,subprocess,argparse
import logging as lg
from  math import pow
from tqdm import tqdm
import tempfile

lg.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', filename="app.log")
tmp_csv_code = tempfile.NamedTemporaryFile(delete=False, dir=os.getcwd(), suffix=".csv")
tmp_csv_truth = tempfile.NamedTemporaryFile(delete=False, dir=os.getcwd(), suffix=".csv")
tmp_csv_code.close()
tmp_csv_truth.close()

def extract_dataframe(PS_PATH, GROUND_TRUTH="") -> pd.DataFrame:
    
    list_scripts, scripts_name = [], []
    for root, dirs, files in os.walk(PS_PATH):
        for file in files:
            if(".ps" in file):
                with open(os.path.join(root,file), 'r') as f:
                    list_scripts.append(f.read())
                f.close()
                scripts_name.append(file)
        lg.debug(f"Extracted scripts: " + str(len(list_scripts)))

    list_target_powershell = list_scripts
    df_code = parse_analysis(PS_PATH, tmp_csv_code.name)

    if(GROUND_TRUTH != ""):
        list_scripts =  []
        for root, dirs, files in os.walk(GROUND_TRUTH):
            for file in files:
                if(".ps" in file):
                    with open(os.path.join(root,file), 'r') as f:
                        list_scripts.append(f.read())
                    f.close()
            lg.debug(f"Extracted truth: " + str(len(list_scripts)))

        list_truth = list_scripts
        df_truth = parse_analysis(GROUND_TRUTH, tmp_csv_truth.name)

        df = pd.DataFrame(data={"ScriptName": scripts_name,"CODE" : list_target_powershell, 'Ground Truth': list_truth})

        df = df.merge(df_code, on="ScriptName", how="left")
        df = df.rename(columns={"RuleName": "CODE Rulename", "Message": "CODE Message", "Severity": "CODE Severity"})
        df = df.merge(df_truth, on="ScriptName", how="left")
        df = df.rename(columns={"RuleName": "TRUTH Rulename", "Message": "TRUTH Message", "Severity": "TRUTH Severity"})
        

    else:
        df = pd.DataFrame(data={"ScriptName": scripts_name, "CODE" : list_target_powershell})
        df = df.merge(df_code, on="ScriptName", how="left")
        df = df.rename(columns={"RuleName": "CODE Rulename", "Message": "CODE Message", "Severity": "CODE Severity"})

    #replace nan with empty string
    df = df.fillna('')
    lg.debug("Created dataframe")
    return df

def parse_analysis(PS_PATH, PATH_CSV):
    current_dir = os.getcwd()

    #pwsh o powershell
    result = subprocess.call(f'pwsh {os.path.join(current_dir,"parser.ps1")} {PS_PATH} {PATH_CSV}', shell=True)
    df = pd.read_csv(PATH_CSV)
    df = df.groupby('ScriptName').agg(lambda x: x.tolist()).reset_index()
    df = df.drop(columns=["Line","Column","Extent","ScriptPath",
                          "RuleSuppressionID","SuggestedCorrections","IsSuppressed"])

    lg.debug(df.columns)
    return df

def str_to_list(s):
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        return s

def calculate_syntax_metric_single(df) -> float:
    l = df.shape[0]
    count = 0
    skip_error_rule = ['RedirectionNotSupported', "MissingFileSpecification"] #["The '<' operator is reserved for future use. "]
        

    for i,row in df.iterrows():
        if(row['CODE']== "No code found" or row["CODE Rulename"] == ""):
            continue
        
        lg.debug(f"{row['ScriptName']} {type(row['CODE Rulename'])} {list(row['CODE Rulename'])}")

        list_Rulename = [elem.replace("'","").replace(" ","") for elem in row['CODE Rulename']]
        list_severity = [elem.replace("'","").replace(" ","") for elem in row['CODE Severity']]
        
        if(list_Rulename == [] or list_Rulename == ['']):
            continue
        
        lg.debug(f"Answer single: {len(list_Rulename)} {len(list_severity)}")
        
        list_a = list(zip(list_Rulename,list_severity))
        
        list_a_filtered = []
        for elem_a in list_a:
            if(elem_a[1] == "ParseError" and  elem_a[0] not in skip_error_rule):
                list_a_filtered.append(elem_a)

        for j,elem in enumerate(list_a_filtered):
            if(elem[1] == 'ParseError'):
                count += 1
                break
    
    lg.debug(f"Count valid ParseErrors: {count}/{l}")
    return round((1-count/l)*100,2), count, l

def calculate_syntax_metric_double(df) -> float:
    l = df.shape[0]
    count= 0
    skip_error_rule = ['RedirectionNotSupported', "MissingFileSpecification"] #["The '<' operator is reserved for future use. "]
    
    for i,row in df.iterrows():
        if(row['CODE']== "No code found" or row["CODE Rulename"] == ""):
            continue
            
        list_Rulename = [elem.replace("'","").replace(" ","") for elem in row['CODE Rulename']]
        list_severity = [elem.replace("'","").replace(" ","") for elem in row['CODE Severity']]

        list_Rulename_t = [elem.replace("'","").replace(" ","") for elem in row['TRUTH Rulename']]
        list_severity_t = [elem.replace("'","").replace(" ","") for elem in row['TRUTH Severity']]

        lg.debug(f"{row['ScriptName']}  Answer double: {len(list_Rulename)} {list_severity} {len(list_Rulename_t)} {list_severity_t}")

        list_a = list(zip(list_Rulename, list_severity))
        list_b = list(zip(list_Rulename_t, list_severity_t))
        
        list_a_filtered = []
        for elem_a in list_a:
            if(elem_a[1] == "ParseError" and  elem_a[0] not in skip_error_rule):
                list_a_filtered.append(elem_a)
        
        list_b_filtered = []      
        for elem_b in list_b:
            if(elem_b[1] == "ParseError" and elem_b[0] not in skip_error_rule):
                list_b_filtered.append(elem_b)
        
        list_equals = list(set(list_a_filtered) & set(list_b_filtered))
        
        for j,elem in enumerate(list_a_filtered):
            if(elem[1] == 'ParseError' and elem not in list_equals):
                count += 1
                #lg.debug(f"Answer: {elem} {i}")
                break
    
    return round((1-count/l)*100,2), count, l

def check_if_psscriptanalyzer_installed():
    result = subprocess.call("pwsh -command 'Get-Module -ListAvailable PSScriptAnalyzer'", shell=True, stdout=subprocess.DEVNULL)
    if(result == 0):
        return True
    else:
        return False


if __name__ == '__main__':
 
    print("""        


 █▀▄ █   █ ▄▀▀ █▄█    ▄▀▀ ▀█▀ ▄▀▄ ▀█▀ █ ▄▀▀    ▄▀▄ █▄ █ ▄▀▄ █   ▀▄▀ ▄▀▀ █ ▄▀▀
 █▀  ▀▄▀▄▀ ▄██ █ █ ▀▀ ▄██  █  █▀█  █  █ ▀▄▄ ▀▀ █▀█ █ ▀█ █▀█ █▄▄  █  ▄██ █ ▄██

                                                                                            
    """)
    parser = argparse.ArgumentParser(description="Python NLP wrapper for powershell syntax analysis through PSScript Analyzer")
    #parser.add_argument("DESCRIPTION_PATH", help="Description text file path from the model")
    parser.add_argument("OUT_FILE", help="Output csv/txt file", nargs='?',const="output.csv")
    parser.add_argument("PS_PATH", help="Scripts generated from the model", type=str)
    parser.add_argument("GROUND_TRUTH", help="Ground truth text file path",nargs='?',  default="")
    parser.add_argument("-v", help="Verbose", nargs='?', type=int, const=1, default=0)
    
    args = parser.parse_args()
    
    #DESCRIPTION_PATH = args.DESCRIPTION_PATH
    PS_PATH = args.PS_PATH
    GROUND_TRUTH = args.GROUND_TRUTH
    OUT_FILE = args.OUT_FILE
    VERBOSE = args.v
    N = 0
    
    if(VERBOSE):
        lg.getLogger().setLevel(lg.DEBUG)
        lg.debug(vars(args))
    else:
        lg.getLogger().setLevel(lg.INFO)

    if(not check_if_psscriptanalyzer_installed()):
        lg.error("PSScriptAnalyzer not installed. Please install it with 'Install-Module -Name PSScriptAnalyzer'")
        exit(1)

    if(GROUND_TRUTH != ""):
        if((os.path.exists(OUT_FILE))):
            df = pd.read_csv(OUT_FILE,  converters={"CODE Rulename": str_to_list, "CODE Severity": str_to_list, "TRUTH Rulename": str_to_list, "TRUTH Severity": str_to_list})
        else:
            df = extract_dataframe(PS_PATH,GROUND_TRUTH)
            df.to_csv(OUT_FILE)
        
        lg.debug(df.columns)
        single_metric, count1, l1 = calculate_syntax_metric_single(df)
        double_metric, count2, l2 = calculate_syntax_metric_double(df)

        lg.info(f"Count valid ParseErrors: {count1}/{l1}")
        lg.info(f"Syntax metric single: {single_metric}")
        lg.info(f"Count valid ParseErrors: {count2}/{l2}")
        lg.info(f"Syntax metric double: {double_metric}")

        #write the print on file
        with open(OUT_FILE.replace(".csv",".txt"), 'w') as f:
            f.write(f"Count valid ParseErrors: {count1}/{l1}")
            f.write(f" Syntax metric single: {single_metric}\n")
            f.write(f"Count valid ParseErrors: {count2}/{l2}")
            f.write(f" Syntax metric double: {double_metric}\n")
        f.close()
    
    else:
        if((os.path.exists(OUT_FILE))):
            df = pd.read_csv(OUT_FILE, delimiter=",")
        else:
            df = extract_dataframe(PS_PATH)
            df.to_csv(OUT_FILE, index=False)
            
        single_metric, count, l = calculate_syntax_metric_single(df)

        lg.info(f"Count valid ParseErrors: {count}/{l}")
        lg.info(f"Syntax metric single: {single_metric}")

        with open(OUT_FILE.replace(".csv",".txt"), 'w') as f:
            f.write(f"Count valid ParseErrors: {count}/{l}")
            f.write(f" Syntax metric single: {single_metric}\n")
        f.close()

    os.remove(tmp_csv_code.name)
    os.remove(tmp_csv_truth.name)
    lg.info("Done!")