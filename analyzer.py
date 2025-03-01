import pandas as pd
import os,ast,subprocess,argparse
import logging as lg
from  math import pow
from tqdm import tqdm
import tempfile

lg.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
tmp_csv_code = tempfile.NamedTemporaryFile(delete=True, delete_on_close=False, dir=os.getcwd(), suffix=".csv")
tmp_csv_truth = tempfile.NamedTemporaryFile(delete=True, delete_on_close=False, dir=os.getcwd(), suffix=".csv")

def extract_dataframe(PS_PATH, GROUND_TRUTH="", FROM_ESCAPE=False, SCRIPT_MODE=False) -> pd.DataFrame:
    if(SCRIPT_MODE == False):
        if(FROM_ESCAPE == True):
            with open(PS_PATH, 'r') as f:
                list_powershell = [elem.split("\t")[1].strip() for elem in f.readlines()]
            f.close()
            lg.debug("Extracted CODE: " + str(len(list_powershell)))
        else:
            with open(PS_PATH, 'r') as f:
                list_powershell = [elem.strip() for elem in f.readlines()]
            f.close()
            lg.debug("Extracted CODE: " + str(len(list_powershell)))
    else:
        list_scripts = []
        for root, dirs, files in os.walk(PS_PATH):
            for file in files:
                if(".ps" in file):
                    with open(os.path.join(root,file), 'r') as f:
                        list_scripts.append(f.read())
                    f.close()
            lg.debug(f"Extracted scripts: " + str(len(list_scripts)))

        list_target_powershell = list_scripts
        parse_analysis(PS_PATH, tmp_csv_code.name)


    if(GROUND_TRUTH != ""):
        if(SCRIPT_MODE == False):
            if(FROM_ESCAPE == True):
                with open(GROUND_TRUTH, 'r') as f:
                    list_truth = [elem.split("\t")[1].strip() for elem in f.readlines()]
                f.close()
                lg.debug("Extracted truth: "+ str(len(list_truth)))
            else:
                with open(GROUND_TRUTH, 'r') as f:
                    list_truth = [elem.strip() for elem in f.readlines()]
                f.close()
                lg.debug("Extracted truth: "+ str(len(list_truth)))
        
        else:
            list_scripts = []
            for root, dirs, files in os.walk(GROUND_TRUTH):
                for file in files:
                    if(".ps" in file):
                        with open(os.path.join(root,file), 'r') as f:
                            list_scripts.append(f.read())
                        f.close()
                lg.debug(f"Extracted truth: " + str(len(list_scripts)))

            list_truth = list_scripts
            parse_analysis(PS_PATH, tmp_csv_code.name)

        df = pd.DataFrame(data={"CODE" : list_target_powershell, 'Ground Truth': list_truth})

        lg.debug("Created dataframe: ")
        return df
    else:
        df = pd.DataFrame(data={"CODE" : list_target_powershell})
        lg.debug("Created dataframe: ")
        return df

def parse_analysis(PS_PATH, GROUND_TRUTH, PATH_CSV):
    current_dir = os.getcwd()

    #pwsh o powershell
    result = subprocess.call(f'pwsh {os.path.join(current_dir,"parser.ps1")} {} {PATH_CSV}', stdout=subprocess.PIPE, text=True)
    df = pd.read_csv(PATH_CSV)
    df = df.groupby('ScriptName').agg(lambda x: x.tolist()).reset_index()

    lg.debug(df.columns)
    return df

def add_results_compare(df, df_partial,FILE_CSV) -> pd.DataFrame:
    l = df.shape[0]
    N = df_partial.shape[0]

    answer_df = parse_analysis(PS_PATH, tmp_csv_code.name)
    truth_df = parse_analysis(tmp_csv_truth.name) 


    for i,row in tqdm(df.iterrows(),total=l, colour='blue'):
        if(i>=N):
            answer,truth = row['CODE'], row['Ground Truth']

            if(answer_out == ['']):
                answer_out = ['','','']

            if(truth_out == ['']):
                truth_out = ['','','']

            lg.debug(f"It: {i+1}/{l} Len_ans_out: {len(answer_out)} Len_truth_out: {len(truth_out)}")
            
            try:
                df_partial.loc[len(df_partial.index)] = answer_out+truth_out
            finally:
                df_partial.to_csv(FILE_CSV, index=False)
        
        
    df_out = pd.concat([df,df_partial], axis = 1)
    lg.debug(df_out.columns)

    return df_out

def add_results_single(df,df_partial,FILE_CSV) -> pd.DataFrame:
    l = df.shape[0]
    N = df_partial.shape[0]
    for i,row in tqdm(df.iterrows(), total=l, colour='blue'):
        if(i>=N):
            answer = row['CODE']
            answer_out = parse_output(answer)

            if(answer_out == ['']):
                answer_out = ['','','']

            lg.debug(f"It: {i+1}/{l} Len_ans_out: {len(answer_out)}")
            
            try:
                df_partial.loc[len(df_partial.index)] = answer_out
            finally:
                df_partial.to_csv(FILE_CSV, index=False)

    df_out = pd.concat([df,df_partial], axis = 1)

    return df_out

def str2list(string):
    if(string == [''] or string == '' or string == ['']):
        return []
    else:
        return string[1:-1].split(",")

def calculate_syntax_metric_single(df) -> float:
    l = df.shape[0]
    count = 0
    skip_error_rule = ['RedirectionNotSupported', "MissingFileSpecification"] #["The '<' operator is reserved for future use. "]
    
    for i,row in df.iterrows():
        
        if(type(row['CODE Rulename']) == str):
            list_rulename = [elem.replace("'","").replace(" ","") for elem in str2list(row['CODE Rulename'])]
            list_severity = [elem.replace("'","").replace(" ","") for elem in str2list(row['CODE Severity'])]
        else:
            list_rulename = [elem.replace("'","").replace(" ","") for elem in row['CODE Rulename']]
            list_severity = [elem.replace("'","").replace(" ","") for elem in row['CODE Severity']]
        
        if(list_rulename == [] or list_rulename == ['']):
            continue
        
        list_a = list(zip(list_rulename,list_severity))
        
        list_a_filtered = []
        for elem_a in list_a:
            if(elem_a[1] == "ParseError" and  elem_a[0] not in skip_error_rule):
                list_a_filtered.append(elem_a)
        
        for j,elem in enumerate(list_a_filtered):
            if(elem[1] == 'ParseError'):
                count += 1
                lg.debug(f"Answer: {row} {i}")
                break
        
    return round((1-count/l)*100,2), count, l

def calculate_syntax_metric_double(df) -> float:
    l = df.shape[0]
    count= 0
    skip_error_rule = ['RedirectionNotSupported', "MissingFileSpecification"] #["The '<' operator is reserved for future use. "]
    
    for i,row in df.iterrows():
        
        if(type(row['CODE Rulename']) == str):
            list_rulename = [elem.replace("'","").replace(" ","") for elem in str2list(row['CODE Rulename'])]
            list_severity = [elem.replace("'","").replace(" ","") for elem in str2list(row['CODE Severity'])]
            list_rulename_t = [elem.replace("'","").replace(" ","") for elem in str2list(row['TRUTH Rulename'])]
            list_severity_t = [elem.replace("'","").replace(" ","") for elem in str2list(row['TRUTH Severity'])]
        else:
            list_rulename = [elem.replace("'","").replace(" ","") for elem in row['CODE Rulename']]
            list_severity = [elem.replace("'","").replace(" ","") for elem in row['CODE Severity']]
            list_rulename_t = [elem.replace("'","").replace(" ","") for elem in row['TRUTH Rulename']]
            list_severity_t = [elem.replace("'","").replace(" ","") for elem in row['TRUTH Severity']]
        
        list_a = list(zip(list_rulename, list_severity))
        list_b = list(zip(list_rulename_t, list_severity_t))
        
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
                lg.debug(f"Answer: {elem} {i}")
                break
    
    return round((1-count/l)*100,2), count, l


if __name__ == '__main__':
 
    print("""        


 █▀▄ █   █ ▄▀▀ █▄█    ▄▀▀ ▀█▀ ▄▀▄ ▀█▀ █ ▄▀▀    ▄▀▄ █▄ █ ▄▀▄ █   ▀▄▀ ▄▀▀ █ ▄▀▀
 █▀  ▀▄▀▄▀ ▄██ █ █ ▀▀ ▄██  █  █▀█  █  █ ▀▄▄ ▀▀ █▀█ █ ▀█ █▀█ █▄▄  █  ▄██ █ ▄██

                                                                                            
    """)
    parser = argparse.ArgumentParser(description="Python NLP wrapper for powershell syntax analysis through PSScript Analyzer")
    #parser.add_argument("DESCRIPTION_PATH", help="Description text file path from the model")
    parser.add_argument("OUT_FILE", help="Output csv file", nargs='?',const="output.csv")
    parser.add_argument("PS_PATH", help="CODE file path from the model", type=str)
    parser.add_argument("GROUND_TRUTH", help="Ground truth text file path",nargs='?',  default="")
    parser.add_argument("--SCRIPT_MODE", help="Multiple Scripts mode", action="store_true", default=False)
    parser.add_argument("--FROM_ESCAPE", help="Output files from ESCAPE", action="store_true", default=False)
    parser.add_argument("-v", help="Verbose", nargs='?', type=int, const=1, default=0)
    
    args = parser.parse_args()
    
    #DESCRIPTION_PATH = args.DESCRIPTION_PATH
    PS_PATH = args.PS_PATH
    GROUND_TRUTH = args.GROUND_TRUTH
    FROM_ESCAPE= args.FROM_ESCAPE
    SCRIPT_MODE = args.SCRIPT_MODE
    OUT_FILE = args.OUT_FILE
    VERBOSE = args.v
    N = 0
    
    if(VERBOSE):
        lg.getLogger().setLevel(lg.DEBUG)
        lg.debug(vars(args))
    else:
        lg.getLogger().setLevel(lg.INFO)

    if(GROUND_TRUTH != ""):
        if((os.path.exists(OUT_FILE))):
            df_partial = pd.read_csv(OUT_FILE)
        else:
            df_partial = pd.DataFrame(columns=["CODE Rulename",'CODE Message','CODE Severity',
                                    "TRUTH Rulename",'TRUTH Message','TRUTH Severity'])
            
        df = extract_dataframe(PS_PATH,GROUND_TRUTH,FROM_ESCAPE, SCRIPT_MODE)
        df_out = add_results_compare(df, df_partial, OUT_FILE)
        
        single_metric, count1, l1 = calculate_syntax_metric_single(df_out)
        double_metric, count2, l2 = calculate_syntax_metric_double(df_out)

        lg.info(f"Count valid ParseErrors: {count1}/{l1}")
        lg.info("Syntax metric single: ",single_metric)
        lg.info(f"Count valid ParseErrors: {count2}/{l2}")
        lg.info("Syntax metric double: ",double_metric)

        #write the print on file
        with open(OUT_FILE.replace(".csv",".txt"), 'w') as f:
            f.write(f"Count valid ParseErrors: {count1}/{l1}")
            f.write(f"Syntax metric single: {single_metric}\n")
            f.write(f"Count valid ParseErrors: {count2}/{l2}")
            f.write(f"Syntax metric double: {double_metric}\n")
        f.close()

        
    else:
        if((os.path.exists(OUT_FILE))):
            df_partial = pd.read_csv(OUT_FILE)
        else:
            df_partial = pd.DataFrame(columns=["CODE Rulename",'CODE Message','CODE Severity'])
            
        df = extract_dataframe(PS_PATH, FROM_ESCAPE=FROM_ESCAPE, SCRIPT_MODE=SCRIPT_MODE)
        df_out = add_results_single(df,df_partial,OUT_FILE)

        single_metric, count, l = calculate_syntax_metric_single(df_out)

        lg.info(f"Count valid ParseErrors: {count}/{l}")
        lg.info("Syntax metric single: ", single_metric)

        with open(OUT_FILE.replace(".csv",".txt"), 'w') as f:
            f.write(f"Count valid ParseErrors: {count}/{l}")
            f.write(f"Syntax metric single: {single_metric}\n")
        f.close()
        
    df_out.to_csv(OUT_FILE, index=False)