import pandas as pd
import os,ast,subprocess,argparse
import logging as lg
lg.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

def extract_dataframe(des_path,answer_path, ground_truth) -> pd.DataFrame:
    with open(des_path, 'r') as f:
        list_des = [elem.strip() for elem in f.readlines()]
    f.close()
    lg.debug("Extracted descriptions: " + str(len(list_des)))

    with open(answer_path, 'r') as f:
        list_answer = ast.literal_eval(f.read())
    f.close()
    lg.debug("Extracted answers: " + str(len(list_answer)))

    with open(ground_truth, 'r') as f:
        list_truth = [elem.strip() for elem in f.readlines()]
    f.close()
    lg.debug("Extracted truth: "+ str(len(list_truth)))

    df = pd.DataFrame(data={"Description": list_des,"Answer" : list_answer, 'Ground Truth': list_truth})
    lg.debug("Created dataframe: ")
    return df

def parse_output(answer) -> []:
    lg.debug(answer)

    with open("buffer.ps1", 'w') as f:
        f.write(answer)
    f.close()

    result = subprocess.run(f'pwsh .\parser.ps1 buffer.ps1', stdout=subprocess.PIPE, text=True)
    result = result.stdout.strip().split("--")
    result = [elem.strip("|").strip().strip("|") for elem in result]

    try: 
        result = [elem.split("|") for elem in result]
    except:
        pass
    
    lg.debug(result)
    return result

def add_results(df,FILE_CSV) -> pd.DataFrame:
    l = df.shape[0]
    for i,row in df.iterrows():
        if(i>=N):
            answer,truth = row['Answer'], row['Ground Truth']
            answer_out = parse_output(answer)
            truth_out = parse_output(truth) 

            if(answer_out == ['']):
                answer_out = ['','','']

            if(truth_out == ['']):
                truth_out = ['','','']

            lg.info(f"It: {i+1}/{l} Len_ans_out: {len(answer_out)} Len_truth_out: {len(truth_out)}")
            
            try:
                df_partial.loc[len(df_partial.index)] = answer_out+truth_out
            finally:
                df_partial.to_csv(FILE_CSV, index=False)

    df_out = pd.concat([df,df_partial], axis = 1)
    os.remove("buffer.ps1")

    return df_out

if __name__ == '__main__':
 
    parser = argparse.ArgumentParser(description="Python NLP wrapper for powershell syntax analysis through PSScript Analyzer")
    parser.add_argument("DESCRIPTION_PATH", help="Description text file path from the model")
    parser.add_argument("ANSWER_PATH", help="Answers text file path from the model")
    parser.add_argument("GROUND_TRUTH", help="Ground truth text file path")
    parser.add_argument("OUT_FILE", help="Output csv file")
    parser.add_argument("-v","--verbose", help="Verbose", nargs='?', type=int, const=1, default=0)

    args = parser.parse_args()
    
    DESCRIPTION_PATH = args.DESCRIPTION_PATH
    ANSWER_PATH = args.ANSWER_PATH
    GROUND_TRUTH = args.GROUND_TRUTH
    FILE_CSV = "output_partial.csv"
    OUT_FILE = args.OUT_FILE
    VERBOSE = args.verbose

    if(VERBOSE):
        lg.getLogger().setLevel(lg.DEBUG)
        lg.debug(vars(args))
    else:
        lg.getLogger().setLevel(lg.INFO)

    N = 0
    if((os.path.exists(FILE_CSV))):
        df_partial = pd.read_csv(FILE_CSV)
        N = df_partial.shape[0]
    else:
        df_partial = pd.DataFrame(columns=["ANSWER Rulename",'ANSWER Message','ANSWER Severity',
                                "TRUTH Rulename",'TRUTH Message','TRUTH Severity'])
    
    df = extract_dataframe(DESCRIPTION_PATH,ANSWER_PATH,GROUND_TRUTH)
    df_out = add_results(df,FILE_CSV)

    df_out.to_csv(OUT_FILE, index=False)
    
