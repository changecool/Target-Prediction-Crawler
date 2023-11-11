### IMPORT LIBRARIES ###
# make sure libraries are installed on your PC
# install libraries via 'pip install xxx'
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoSuchElementException
import argparse
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from bioservices import UniProt

### DEFINE FUNCTIONs ###
## Crawl data from SwissTargetPrediction
def SwissCrawler (smiles, CpdName):
    SwissUrl = 'http://www.swisstargetprediction.ch/index.php'
    platform = 'SwissTargetPrediction' 
    driver.get(SwissUrl) 
    SearchField = driver.find_element(By.NAME, 'smiles') 
    SearchField.send_keys(smiles) 
    SearchField.submit() 
    dfs = []  
    max_retries = 3  
    retries = 0  
    all_pages_processed = False
    while retries < max_retries and not all_pages_processed:
        try:
            WebDriverWait(driver, 200).until(EC.presence_of_element_located((By.XPATH, '//*[@id="resultTable"]/tbody')))
            CurrUrl = driver.current_url 
            df = pd.read_html(CurrUrl) 
            df = df[0] 
            cols = [col for col in df.columns if col in ['Uniprot ID', 'Probability*']]
            df = df[cols]          
            df.insert(0, 'compound', CpdName)   
            df.insert(1, 'platform', platform)  
            df = df.rename(columns={"Uniprot ID": "uniprotID", "Probability*": "prob"}) 
            dfs.append(df)  
            ## Determine whether the current page is the last page. If it is not the last page, click the "Next" button to load the next page.
            try:
                next_button = driver.find_element(By.XPATH, '//*[@id="resultTable_next"]')
                if (df['prob'] == 0).any():  
                    all_pages_processed = True
                elif next_button.get_attribute("class") == "paginate_button next disabled":
                    all_pages_processed = True  
            except NoSuchElementException:
                all_pages_processed = True  
            ## If the current page is not the last page, click the "Next" button to load the next page.
            if not all_pages_processed:
                next_button.click()
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="resultTable"]/tbody')))
            else:
                break
        ## Handling exceptional situations: page loading timeout, pop-up warning boxes, and other exceptions.
        except TimeoutException:
            retries += 1
            if retries >= max_retries:
                all_pages_processed = True
                CurrUrl = driver.current_url
                dfs = pd.DataFrame(columns=['compound', 'platform', 'uniprotID', 'prob'])
                dfs = pd.concat([dfs, pd.DataFrame({'compound': [CpdName],
                                                'platform': [platform],
                                                'uniprotID': ['result page reached timeout'],
                                                'prob': [CurrUrl]})], ignore_index=True)
                return dfs
        except UnexpectedAlertPresentException:
            retries += 1
            if retries >= max_retries:
                all_pages_processed = True
                alert = driver.switch_to.alert
                dfs = pd.DataFrame(columns=['compound', 'platform', 'uniprotID', 'prob'])
                dfs = pd.concat([dfs, pd.DataFrame({'compound': [CpdName],
                                                'platform': [platform],
                                                'uniprotID': ['error message'],
                                                'prob': [alert.text]})], ignore_index=True)
                alert.accept()
                return dfs
        except Exception as e:
            print(f"Error occurred: {e}")
            all_pages_processed = True
            break
    ## If the page is loaded normally, the data of all pages is merged into one dataframe.        
    df = pd.concat(dfs, ignore_index=True)
    ## Retain target data from SwissTargetPrediction database with "Probability*" greater than or equal to 0.6.
    df = df[df['prob'] >= 0.6]
    ## Retrieve the entry name corresponding to the UniProt ID from the UniProt database.      
    def get_uniprot_name(entry):
        u = UniProt(verbose=False)
        res = u.search(f"{entry}+AND+organism_id:9606", frmt="tsv", columns="id", limit=1)        
        if len(res.split('\n')) < 2:
            Entr = 'no_entry_found_in_uniprot'
        else:
            Entr = res.split('\n')[1].split('\t')[0]        
        return Entr
    def get_uniprot_names(df):
        def process_entry(entry):
            ## If there is only one value in the Uniprot ID, return the entry name directly.
            if entry.count(' ') == 0:
                return get_uniprot_name(entry)
            ## If there are multiple values in the uniprotID, return multiple entry names separated by '|' symbol.
            else:
                new_lst = entry.split(' ')
                new_Entr = []
                for i in new_lst:
                    Entr = get_uniprot_name(i)
                    new_Entr.append(Entr)
                new = '|'.join(new_Entr)
                return new
        ## By adjusting the value of max_workers, the number of concurrent threads can be adjusted according to hardware resources.
        with ThreadPoolExecutor(max_workers=100) as executor:
            newCol = list(executor.map(process_entry, df.uniprotID.values))
        df['UniProt_name'] = newCol
        df = df.drop('uniprotID', axis=1)
        return df
    df = get_uniprot_names(df)
    return df    

## Crawl data from SEA       
def SEACrawler (smiles, CpdName):
    SEAUrl = 'http://sea.bkslab.org/' 
    platform = 'SEA'
    driver.get(SEAUrl)
    SearchField = driver.find_element(By.NAME, 'query_custom_targets_paste') 
    SearchField.send_keys(smiles) 
    SearchField.submit() 
    max_retries = 3  
    retries = 0  
    while retries < max_retries:
        try:
            WebDriverWait(driver, 200).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/table/tbody'))) 
            CurrUrl = driver.current_url 
            df = pd.read_html(CurrUrl) 
            df = df[0] 
            cols = [col for col in df.columns if col in ['Target Key','P-Value']]
            df = df[cols]
            ## Remove the first line and check the content elements of the table on the website. The first row is a graphic introduction of ingredients, so it should be deleted. If not removed, an error "TypeError: 'float' object is not subscriptable" will occur when executing line 122. 
            df = df.iloc[1:, :]                
            df.insert(0,'compound',CpdName) 
            df.insert(1,'platform',platform)
            df = df.rename(columns={"Target Key": "targetkey", "P-Value": "prob"}) 
            TargetKeys = df.targetkey.values 
            genes = []
            for key in TargetKeys: 
                gene = key 
                genes.append(gene) 
            df = df.drop('targetkey', axis=1)
            df['UniProt_name'] = genes 
            break
        ## Handling exceptional situations: page loading timeout, pop-up warning boxes, and other exceptions.
        except TimeoutException:
            retries += 1
            if retries >= max_retries:
                CurrUrl = driver.current_url
                df = pd.DataFrame(columns=['compound','platform','UniProt_name','prob'])
                df = df.append({'compound':CpdName, 
                    'platform':platform,
                    'UniProt_name':'result page reached timeout',
                    'prob':CurrUrl,},
                    ignore_index=True)
                return df
        except UnexpectedAlertPresentException:
            retries += 1
            if retries >= max_retries:
                alert = driver.switch_to.alert
                df = pd.DataFrame(columns=['compound','platform','UniProt_name','prob'])
                df = df.append({'compound':CpdName, 
                    'platform':platform,
                    'UniProt_name':'error message',
                    'prob':alert.text},
                    ignore_index=True)
                alert.accept()
                return df
        except Exception as e:
            print(f"Error occurred: {e}")
            break
    ## Retain target data from SEA database with "P-value" less than 0.05.
    df = df[df['prob'] < 0.05] 
    return df

## Crawl data from SuperPred
def SuperPredCrawler (smiles, CpdName):  
    platform = 'SuperPred'
    SPUrl = 'https://prediction.charite.de/subpages/target_prediction.php'
    driver.get(SPUrl) 
    SearchField = driver.find_element(By.XPATH, '//*[@id="smiles_string"]') 
    SearchField.send_keys(smiles) 
    search_button = driver.find_elements(By.XPATH, '/html/body/div[2]/div/div/form/div[2]/div/div/button')[0] 
    search_button.click() 
    startcalculation_button = driver.find_element(By.XPATH, '/html/body/div[2]/center/form/table/tbody/tr/td/button') 
    startcalculation_button.click() 
    dfsp = [] 
    max_retries = 3  
    retries = 0 
    all_pages_processed = False
    while retries < max_retries and not all_pages_processed:
        try:
            WebDriverWait(driver, 200).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'table')))
            table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="targets"]')))
            table_html = table.get_attribute('outerHTML')
            df = pd.read_html(table_html, header=0)[0]
            cols = [col for col in df.columns if col in ['UniProt ID', 'Probability']]
            df = df[cols]
            df.insert(0, 'compound', CpdName)
            df.insert(1, 'platform', platform)
            df = df.rename(columns={"UniProt ID": "uniprotID", "Probability": "prob"}) 
            dfsp.append(df)  
            ## Check if the "Next" button is available
            try:
                next_button = driver.find_element(By.XPATH, '//*[@id="targets_next"]')
                if next_button.get_attribute("class") == "paginate_button next disabled":
                    all_pages_processed = True  
            except NoSuchElementException:
                all_pages_processed = True 
            ## If the "Next" button is available, click the "Next" button to go to the next page
            if not all_pages_processed:
                next_button.click()
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="targets"]/tbody')))
            else:
                break  
        ## Handling exceptional situations: page loading timeout, pop-up warning boxes, and other exceptions.
        except TimeoutException:
            retries += 1            
            if retries >= max_retries:
                all_pages_processed = True
                CurrUrl = driver.current_url
                dfsp = pd.DataFrame(columns=['compound', 'platform', 'uniprotID', 'prob'])
                dfsp = pd.concat([dfsp, pd.DataFrame({'compound': [CpdName],
                                                'platform': [platform],
                                                'uniprotID': ['result page reached timeout'],
                                                'prob': [CurrUrl]})], ignore_index=True)
                return dfsp
        except UnexpectedAlertPresentException:
            retries += 1            
            if retries >= max_retries:
                all_pages_processed = True
                alert = driver.switch_to.alert
                dfsp = pd.DataFrame(columns=['compound', 'platform', 'uniprotID', 'prob'])
                dfsp = pd.concat([dfsp, pd.DataFrame({'compound': [CpdName],
                                                'platform': [platform],
                                                'uniprotID': ['error message'],
                                                'prob': [alert.text]})], ignore_index=True)
                alert.accept()
                return dfsp
        except Exception as e:
            print(f"Error occurred: {e}")
            all_pages_processed = True
            break        
    ## If the page is loaded normally, the data of all pages is merged into one dataframe.
    df = pd.concat(dfsp, ignore_index=True)
    ## Retain target data in the SuperPred database with a "Probability" greater than or equal to 60%.
    df['prob'] = df['prob'].str.rstrip('%').astype('float') / 100
    df = df[df['prob'] >= 0.6]
    ## Retrieve the entry name corresponding to the UniProt ID from the UniProt database. 
    def get_uniprot_name(entry):
        u = UniProt(verbose=False)
        res = u.search(f"{entry}+AND+organism_id:9606", frmt="tsv", columns="id", limit=1)        
        if len(res.split('\n')) < 2:
            Entr = 'no_entry_found_in_uniprot'
        else:
            Entr = res.split('\n')[1].split('\t')[0]        
        return Entr
    def get_uniprot_names(df):
        def process_entry(entry):
            ## If there is only one value in the Uniprot ID, return the entry name directly.
            if entry.count(' ') == 0:
                return get_uniprot_name(entry)
            ## If there are multiple values in the uniprotID, return multiple entry names separated by '|' symbol.
            else:
                new_lst = entry.split(' ')
                new_Entr = []
                for i in new_lst:
                    Entr = get_uniprot_name(i)
                    new_Entr.append(Entr)
                new = '|'.join(new_Entr)
                return new
        ## By adjusting the value of max_workers, the number of concurrent threads can be adjusted according to hardware resources.
        with ThreadPoolExecutor(max_workers=100) as executor:
            newCol = list(executor.map(process_entry, df.uniprotID.values))
        df['UniProt_name'] = newCol
        df = df.drop('uniprotID', axis=1)
        return df
    df = get_uniprot_names(df)
    return df


### INITIALIZE SCRIPT ###
## The following code is used to initialize the script, including processing input parameters, reading input files, and writing output files.
if __name__ == '__main__': 
    print('\n\n') 
    print('TarPredCrawler initialized...')
    print('\n\n')
 
    ### PROCESS INPUT ###
    ## The following code is used to process input parameters and read input files.    
    parser = argparse.ArgumentParser(description='Crawl throug 4 Target Prediction Servers')     
    parser.add_argument('-in',
        '--input',
        type=str,
        metavar='',
        required=True,
        help='csv-table in the format "name ; smiles-code" of n compounds')    
    parser.add_argument('-out',
        '--output',
        type=str,
        metavar='',
        required=True,
        help='csv-table populated with processed results')    
    args = parser.parse_args()
 
    ### READ IN INPUT ###
    ## The following code is used to read input files.
    with open (args.input, 'r') as fin:
        data = pd.read_csv(fin, sep=',', names=['name','smiles'])
    rowcount = data['name'].count()
    print('     Found {} molecules in "{}"\n'.format(rowcount, args.input))
    print('     Start screening:')

    ### START CRAWLING ###
    ## The following code is used to start crawling.
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)

    # driver = webdriver.Chrome('C:\\Windows\\chromedriver.exe', options=options)
    cols = ['compound','platform','prob','UniProt_name'] 
    results = pd.DataFrame(columns=cols)
    results.to_csv(args.output,sep=',')     
    ## The following code is used to crawl through the 3 target prediction servers.
    data['smiles'] = data['smiles'].astype(str)
    for index, row in data.iterrows():
        CpdName = row['name']
        smiles = row['smiles']
        SwissResult = SwissCrawler(smiles, CpdName)
        SEAResult = SEACrawler(smiles, CpdName)
        SuperPredResult = SuperPredCrawler(smiles, CpdName)        
        with open (args.output,'a',newline='') as f:
            SwissResult.to_csv(f,sep=',',header=False)
            SEAResult.to_csv(f,sep=',',header=False)
            SuperPredResult.to_csv(f,sep=',',header=False)           
        print('         screened {} of {} molecules ({})'.format(index+1, rowcount, CpdName))
    ## The following code is used to close the browser.
    driver.quit() 
    print('') 
    print('     Finished Analysis')
    print('     Results are now available in "{}"'.format(args.output))
