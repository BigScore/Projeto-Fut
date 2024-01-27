from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm.auto import tqdm
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")
chrome_options = Options()
chrome_options.add_argument("--headless")

s=Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s)
driver.maximize_window()
ligas = [
       'brazil/serie-a','brazil/serie-b','brazil/serie-c','mexico/liga-mx',
       'norway/eliteserien','suecia/allsvenskan','japao/liga-j1',
       'alemanha/2-bundesliga','alemanha/bundesliga','arabia-saudita/primeira-liga',
       'inglaterra/campeonato-ingles','franca/ligue-1','italia/serie-a',
       'italia/serie-b','espanha/laliga','espanha/laliga2','portugal/liga-portugal',
       'portugal/liga-portugal-2','belgica/liga-jupiler','inglaterra/2-divisao',
       'australia/liga-a','alemanha/3-liga','colombia/primera-a','inglaterra/liga-2',
       'inglaterra/liga-1','eua/mls','holanda/eredivisie','escocia/primeira-liga',
       'austria/bundesliga','turquia/super-lig','grecia/superliga','noruega/obos-ligaen',
       'franca/ligue-2','austria/2-liga','argentina/liga-profissional','dinamarca/superliga',
       'holanda/eerste-divisie','bulgaria/parva-liga',
]



df = pd.DataFrame()
for liga in tqdm(ligas):
    url = f'https://www.flashscore.com.br/futebol/{liga}/calendario/'
    driver.get(url)

    try:
        WebDriverWait(driver, 8).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'button#onetrust-accept-btn-handler')))
        button_cookies = driver.find_element(By.CSS_SELECTOR,'button#onetrust-accept-btn-handler')
        button_cookies.click()
    except:
        print("cookies already closed")
        
    sleep(3)    
        
    jogos = driver.find_elements(By.CSS_SELECTOR,'div.event__match')

    sleep(3)
    jogos_data = []
    id_jogos =[]

    for i in jogos:
        id_jogos.append(i.get_attribute("id")[4:])  
        id_jogos = id_jogos[:10] 
        
    season = driver.find_element(By.CSS_SELECTOR,'div.heading__info').text 
    print(driver.title)

    for id_jogo in tqdm(id_jogos):

        try:
            jogo = {}
            jogo['Season'] = season
            driver.get(f'https://www.flashscore.com.br/jogo/{id_jogo}/#/resumo-de-jogo/resumo-de-jogo')
            jogo['Id'] = id_jogo
                ### Pais
            country = driver.find_element(By.CSS_SELECTOR,'span.tournamentHeader__country').text.split(':')[0]
                ### Data e Hora
            date = driver.find_element(By.CSS_SELECTOR,'div.duelParticipant__startTime').text.split(' ')[0]
            jogo['Date'] = date.replace('.','/')
            time = driver.find_element(By.CSS_SELECTOR,'div.duelParticipant__startTime').text.split(' ')[1]
            jogo['Time'] = time
            league = driver.find_element(By.CSS_SELECTOR,'span.tournamentHeader__country > a').text.split(' -')[0]
            jogo['League'] = f'{country} - {league}'
            ### Home e Away
            home = driver.find_element(By.CSS_SELECTOR,'div.duelParticipant__home').find_element(By.CSS_SELECTOR,'div.participant__participantName').text
            jogo['Home'] = home
            away = driver.find_element(By.CSS_SELECTOR,'div.duelParticipant__away').find_element(By.CSS_SELECTOR,'div.participant__participantName').text
            jogo['Away'] = away
            try:
                rodada = driver.find_element(By.CSS_SELECTOR,'span.tournamentHeader__country > a').text.split('- ')[1]
                jogo['Round_number'] = rodada
            except:
                jogo['Round_number'] = '-'
                
               
            posicao_home, posicao_away = None, None
            try:
                driver.get(f'https://www.flashscore.com.br/jogo/{id_jogo}/#/classificacao/table/overall')
                sleep(2)

                linhas = driver.find_elements(By.CSS_SELECTOR, 'div.ui-table__row')
                classificacoes = {}

                for linha in linhas:
                    try:
                        classificacao = linha.find_element(By.CSS_SELECTOR, 'div.table__cell--rank').text
                        nome_equipe = linha.find_element(By.CSS_SELECTOR, 'a.tableCellParticipant__name').text

                        classificacao = classificacao.replace('.', '')
                        classificacoes[nome_equipe] = classificacao
                    except Exception as e:
                        print(f"Erro ao processar a linha da tabela: {str(e)}")
                    
                posicao_home = classificacoes.get(home, None)
                posicao_away = classificacoes.get(away, None)
                jogo['posicao_home'] =  posicao_home   
                jogo['posicao_away'] =  posicao_away                   
            except Exception as e:
                print(e)    
                

                
            url_ml_full_time = f'https://www.flashscore.com.br/jogo/{id_jogo}/#/comparacao-de-odds/1x2-odds/tempo-regulamentar'
            driver.get(url_ml_full_time)
            sleep(1)        
            if driver.current_url == url_ml_full_time:
                    WebDriverWait(driver, 8).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'div.ui-table')))
                    table_odds = driver.find_element(By.CSS_SELECTOR,'div.ui-table')
                    linha_ml_ft = table_odds.find_element(By.CSS_SELECTOR,'div.ui-table__row')
                    jogo['FT_Odd_ML_Bookie'] = linha_ml_ft.find_element(By.CSS_SELECTOR,'img.prematchLogo').get_attribute('title')
                    jogo['FT_Odd_ML_H'] = float(linha_ml_ft.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
                    jogo['FT_Odd_ML_D'] = float(linha_ml_ft.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
                    jogo['FT_Odd_ML_A'] = float(linha_ml_ft.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[2].text)
                    
            url_ou_first_half = f'https://www.flashscore.com.br/jogo/{id_jogo}/#/comparacao-de-odds/acima-abaixo/1-tempo'
            driver.get(url_ou_first_half)
            sleep(1)
            if driver.current_url == url_ou_first_half:
                WebDriverWait(driver, 8).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'div.ui-table')))
                linhas = driver.find_elements(By.CSS_SELECTOR,'div.ui-table__body')
                for linha in linhas:
                    if (len(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')) > 1):
                        bookie = linha.find_element(By.CSS_SELECTOR,'img.prematchLogo').get_attribute('title')
                        total_gols = linha.find_element(By.CSS_SELECTOR,'span.oddsCell__noOddsCell').text.replace('.','')
                        if total_gols == '05':
                            over = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
                            under = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
                            jogo[f'HT_Odd_OU_{total_gols}_Bookie'] = bookie
                            jogo[f'HT_Odd_Over{total_gols}'] = over
                            jogo[f'HT_Odd_Under{total_gols}'] = under
                            del total_gols,over,under            
                    
            url_ou_full_time = f'https://www.flashscore.com.br/jogo/{id_jogo}/#/comparacao-de-odds/acima-abaixo/tempo-regulamentar'
            driver.get(url_ou_full_time)
            sleep(1)
            if driver.current_url == url_ou_full_time:
                WebDriverWait(driver, 8).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'div.ui-table')))
                linhas = driver.find_elements(By.CSS_SELECTOR,'div.ui-table__body')
                for linha in linhas:
                    if (len(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')) > 1):
                        bookie = linha.find_element(By.CSS_SELECTOR,'img.prematchLogo').get_attribute('title')
                        total_gols = linha.find_element(By.CSS_SELECTOR,'span.oddsCell__noOddsCell').text.replace('.','')
                        if total_gols == '05':
                            over = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
                            under = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
                            jogo[f'FT_Odd_OU_{total_gols}_Bookie'] = bookie
                            jogo[f'FT_Odd_Over{total_gols}'] = over
                            jogo[f'FT_Odd_Under{total_gols}'] = under
                            del total_gols,over,under
                        elif total_gols == '15':
                            over = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
                            under = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
                            jogo[f'FT_Odd_OU_{total_gols}_Bookie'] = bookie
                            jogo[f'FT_Odd_Over{total_gols}'] = over
                            jogo[f'FT_Odd_Under{total_gols}'] = under
                            del total_gols,over,under
                        elif total_gols == '25':
                            over = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
                            under = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
                            jogo[f'FT_Odd_OU_{total_gols}_Bookie'] = bookie
                            jogo[f'FT_Odd_Over{total_gols}'] = over
                            jogo[f'FT_Odd_Under{total_gols}'] = under
                            del total_gols,over,under
                        elif total_gols == '35':
                            over = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
                            under = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
                            jogo[f'FT_Odd_OU_{total_gols}_Bookie'] = bookie
                            jogo[f'FT_Odd_Over{total_gols}'] = over
                            jogo[f'FT_Odd_Under{total_gols}'] = under
                            del total_gols,over,under
                        elif total_gols == '45':
                            over = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
                            under = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
                            jogo[f'FT_Odd_OU_{total_gols}_Bookie'] = bookie
                            jogo[f'FT_Odd_Over{total_gols}'] = over
                            jogo[f'FT_Odd_Under{total_gols}'] = under
                            del total_gols,over,under
                        
            url_btts_full_time = f'https://www.flashscore.com.br/jogo/{id_jogo}/#/comparacao-de-odds/ambos-marcam/tempo-regulamentar'
            driver.get(url_btts_full_time)
            sleep(1)
            if driver.current_url == url_btts_full_time:
                WebDriverWait(driver, 8).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'div.ui-table')))
                linha = driver.find_element(By.CSS_SELECTOR,'div.ui-table__row')
                bookie_btts = linha.find_element(By.CSS_SELECTOR,'img.prematchLogo').get_attribute('title')
                jogo['FT_Odd_BTTS_Bookie'] = bookie_btts
                jogo['FT_Odd_BTTS_Yes'] = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
                jogo['FT_Odd_BTTS_No'] = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
                
           
            jogos_data.append(jogo)               
            df_liga = pd.DataFrame(jogos_data)
            df = pd.concat([df, df_liga], ignore_index=True)
            df.sort_values(['Date','Time'], inplace=True)
            df.reset_index(inplace=True, drop=True)
            df.index = df.index.set_names(['Nº'])
            df = df.rename(index=lambda x: x + 1)
            #print(jogo)                
                                
                
        except:
            print(f'Erro ao coletar dados do jogo {id_jogo}')
            sleep(0.5) 
            
 
driver.quit()             
df = df[
    [
        "Id",
        "Date",
        "Time",
        "League",
        "Season",
        "Round_number",
        "Home",
        "Away",
        "posicao_home",
        "posicao_away",
        "FT_Odd_ML_H",
        "FT_Odd_ML_D",
        "FT_Odd_ML_A",
        "HT_Odd_Over05",
        "HT_Odd_Under05",
        "FT_Odd_Over05",
        "FT_Odd_Under05",
        "FT_Odd_Over15",
        "FT_Odd_Under15",
        "FT_Odd_Over25",
        "FT_Odd_Under25",
        "FT_Odd_Over35",
        "FT_Odd_Under35",
        "FT_Odd_Over45",
        "FT_Odd_Under45",
        "FT_Odd_BTTS_Yes",
        "FT_Odd_BTTS_No"

    ]
]
df.columns = [
    "Id",
    "Date",
    "Time",
    "League",
    "Season",
    "Round",
    "Home",
    "Away",
    "posicao_home",
    "posicao_away",
    "FT_Odd_H",
    "FT_Odd_D",
    "FT_Odd_A",
    "HT_Odd_Over05",
    "HT_Odd_Under05",
    "FT_Odd_Over05",
    "FT_Odd_Under05",
    "FT_Odd_Over15",
    "FT_Odd_Under15",
    "FT_Odd_Over25",
    "FT_Odd_Under25",
    "FT_Odd_Over35",
    "FT_Odd_Under35",
    "FT_Odd_Over45",
    "FT_Odd_Under45",
    "Odd_BTTS_Yes"
]


df.drop_duplicates(subset=['Id'], inplace=True)

diretorio = r"C:\Users\Alexandre\OneDrive\Área de Trabalho\Projeto Fut\base_excel"

if not os.path.exists(diretorio):
    os.makedirs(diretorio)

df.to_excel(os.path.join(diretorio, 'jogos_do_dia_trat.xlsx'), index=False)                  