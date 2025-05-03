import json
import csv
import os
from datetime import datetime
from apiCallsService import getData


response = getData()
matches = {}

def getLeague(leagueKey):
    return {
        'liga_0': "Express",
        'liga_1': "Euro",
        'liga_2': "Copa",
        'liga_3': "Premier",
        'liga_4': "Super",
        'liga_5': "Euro"
    }.get(leagueKey, "Unknown liga")

def parse_odd(raw_odd):
    try:
        
        return f"{float(raw_odd):.2f}" if raw_odd and float(raw_odd) > 0 else "N/A"
    except (ValueError, TypeError):
        return "N/A"

def parse_odds_string(odds_string):
    odds_dict = {
        'casa_vence': "N/A", 
        'empate': "N/A", 
        'visitante_vence': "N/A" 
    }
    
    if not odds_string:
        return odds_dict 
    
    for odd in odds_string.split(';'):
        if odd:
            try:
                key, value = odd.split('@')
                
                if key == 'ftc':
                    odds_dict['casa_vence'] = parse_odd(value)
                elif key == 'fte':
                    odds_dict['empate'] = parse_odd(value)
                elif key == 'ftv':
                    odds_dict['visitante_vence'] = parse_odd(value)
            except ValueError:
                continue  
    return odds_dict


for liga_key, liga_data in response.items():
    if isinstance(liga_data, dict) and "error" in liga_data:
        print(f" Erro ao buscar dados para {liga_key}: {liga_data['error']}")
        continue

    if isinstance(liga_data, list):
        print(f" Aviso: Dados de {liga_key} estão em formato de lista, ignorando...")
        continue

    data_atualizacao = liga_data.get("DataAtualizacao", "Unknown")
    if data_atualizacao == "Unknown":
        odds_time = "Unknown Time"
        date_str = "Unknown"
    else:
        date_str = data_atualizacao.split("T")[0]
        try:
            odds_time = datetime.strptime(data_atualizacao, "%Y-%m-%dT%H:%M:%S.%f").strftime("%d-%m-%Y %H:%M")
        except:
            odds_time = data_atualizacao

    for linha in liga_data.get("Linhas", []):
        for coluna in linha.get("Colunas", []):
            match_id = coluna.get("Id")
            if not match_id:
                print(" Aviso: Match ID ausente, ignorando.")
                continue

            horario_raw = coluna.get("Horario", "").replace(".", ":")
            home_team = coluna.get("TimeA", "Unknown")
            away_team = coluna.get("TimeB", "Unknown")
            resultado = coluna.get("Resultado", "0-0")

            if "+" in resultado or "-" not in resultado:
                print(f" Formato de resultado inválido ({resultado}) para o jogo {match_id}, ignorando.")
                continue

            try:
                home_goals, away_goals = map(int, resultado.split("-"))
            except:
                print(f" Erro ao analisar resultado '{resultado}' para o jogo {match_id}, ignorando.")
                continue

            total_goals = home_goals + away_goals
            over_25 = total_goals > 2.5
            under_25 = total_goals <= 2.5
            over_35 = total_goals > 3.5
            under_35 = total_goals <= 3.5

            
            odds_dict = parse_odds_string(coluna.get("Odds", ""))

          
            exact_score_odd = parse_odd(coluna.get("Resultado_FT_Odd", coluna.get("Resultado_HT_Odd", "N/A")))

            match_data = [
                match_id,
                getLeague(liga_key),
                date_str,
                horario_raw,
                home_team,
                away_team,
                home_goals,
                away_goals,
                total_goals,
               
                odds_dict.get('casa_vence' if over_25 else 'empate' if over_25 else 'visitante_vence', "N/A"),
              
                odds_dict.get('casa_vence' if under_25 else 'empate' if under_25 else 'visitante_vence', "N/A"),
                
                odds_dict.get('casa_vence' if over_35 else 'empate' if over_35 else 'visitante_vence', "N/A"),
                
                odds_dict.get('casa_vence' if under_35 else 'empate' if under_35 else 'visitante_vence', "N/A"),
                odds_dict.get('casa_vence', "N/A"), 
                odds_dict.get('empate', "N/A"), 
                odds_dict.get('visitante_vence', "N/A"),  
                resultado,  
                exact_score_odd, 
                odds_time
            ]

            matches[match_id] = match_data


csv_file = "tabela.csv"
if os.path.exists(csv_file):
    os.remove(csv_file)
    print(f" Arquivo anterior '{csv_file}' deletado.")
else:
    print(f" Nenhum arquivo '{csv_file}' anterior encontrado.")


with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([ 
        "Id da partida", "Campeonato", "Data", "Tempo", "Time da casa", "Time contra",
        "Gols time casa", "Gols time contra", "Gols totais",
        "Odd Over 2.5", "Odd Under 2.5", "Odd Over 3.5", "Odd Under 3.5",
        "Odd Casa Vence", "Odd Empate", "Odd Visitante Vence", "Placar Exato", "Odd Placar Exato", "Data das odds"
    ])
    writer.writerows(matches.values()) 

print(f"CSV '{csv_file}' gerado com sucesso.")
