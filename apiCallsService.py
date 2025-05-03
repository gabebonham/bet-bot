from selenium import webdriver
import json
import json


username = "Multiempreendedor@gmail.com"
password = "a9e7666"
loginUrl = "https://api.thtips.com.br/api/login/"
baseUrl = "https://thtips.com.br"

def getData():
   
    driver = webdriver.Chrome()
    driver.get(baseUrl)
    api_base_url = "https://api.thtips.com.br/api/futebolvirtual?liga={liga}&futuro=false&Horas=Horas12&tipoOdd=&dadosAlteracao=&filtros=ftc,fte,ftv,ftc,fte&confrontos=false&hrsConfrontos=240"

    def getToken():
        getTokenFun = f"""
            return fetch("{loginUrl}", {{
                method: "POST",
                 headers: {{
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                    }},
                body: JSON.stringify({{
                    "username": "{username}",
                    "password": "{password}"
                }})
            }})
        .then(response => response.json())
        .then(data => JSON.stringify(data))
        .catch(error => JSON.stringify({{ "error": error.toString() }}));
        """
        response_json = driver.execute_script(getTokenFun)
    
        try:
            data = json.loads(response_json)
            token = data["Payload"]["accessToken"]
            print("Access token retrieved successfully.")
            return token
        except (KeyError, json.JSONDecodeError) as e:
            print("Error parsing token:", e)
            print("Full response was:", response_json)
            raise
    
    token = getToken()

    def fetchData(liga):
        api_url = api_base_url.format(liga=liga)
        
        jsFun = f"""
            return fetch("{api_url}", {{
                method: "GET",
                headers: {{
                    "Authorization": "Bearer {token}",
                    "Accept": "application/json"
                }}
            }})
            .then(response => response.json())
            .then(data => JSON.stringify(data))
            .catch(error => JSON.stringify({{"error": error.toString()}}));
        """

        
        response_json = driver.execute_script(jsFun)

        
        return json.loads(response_json)

 
    all_data = {}
    for liga in range(6):  
        print(f"Fetching data for liga={liga}...")
        data = fetchData(liga)
        all_data[f"liga_{liga}"] = data

    driver.quit()
    return all_data

