from flask import Flask, render_template, request, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# Configurações do JIRA
JIRA_DOMINIO = "https://ciberbit.atlassian.net/" 
JIRA_EMAIL = "liliana.coelho@ciberbit.pt"
JIRA_TOKEN = "ATATT3xFfGF0AQzJZ8TYkphxlmceW52aCSWj4xxZzGWhYdy0-dR1InJ-C03eNIdG2uqmaJLgiGDiR5ND6JhXxt9bufcyqTTa3BmJ1W0Ugmnx2JZ7drbCAdrolFVkVnD11fP0UxZNILpHb2WMqZwEG0DqIIFwoaPua0vVIUYYUNkqE1OH11wLEKE=F14AE058"

@app.route("/", methods=["GET", "POST"])
def formulario():
    issues = []
    versao = request.form.get('versao')
    cliente = request.form.get('cliente')

    if request.method == "POST":
        versao = request.form["versao"]
        cliente = request.form["cliente"]

        url = f"{JIRA_DOMINIO}/rest/api/3/search/jql?fields=key&maxResults=150&fields=Key, summary, customfield_10312, customfield_10382"
        jql = f'"fixVersion" = "{versao}" AND "Excluir[Dropdown]" is EMPTY ORDER BY created DESC'
        #jql = f'"Key" = THOM-53698 ORDER BY created DESC'
        headers = {"Accept": "application/json"}
        params = {"jql": jql, "maxResults": 100}

        response = requests.get(
            url,
            headers=headers,
            params=params,
            auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
        )

        if response.status_code == 200:
            data = response.json()
            issues = [
                {
                    "key": issue["key"],
                    "resumo": issue["fields"]["summary"],
                    "origem": [item['value'] for item in issue["fields"].get("customfield_10312", [])] if issue["fields"].get("customfield_10312") else [],
                    "testes": [item['value'] for item in issue["fields"].get("customfield_10382", [])] if issue["fields"].get("customfield_10382") else [],
                    "impacto_cliente": "Sim" if cliente in [item['value'] for item in issue["fields"].get("customfield_10312", [])]else "Não",
                    "prioridade_teste": (lambda prioridade_lista:
                        "Highest" if cliente + " - " + "N1" in prioridade_lista else
                        "High" if cliente + " - " + "N2" in prioridade_lista else
                        "Medium" if cliente + " - " + "N3" in prioridade_lista else
                        "Low" if cliente + " - " + "N4" in prioridade_lista else
                        "--"
                    )([item['value'] for item in issue["fields"].get("customfield_10382", [])] if issue["fields"].get("customfield_10382") else [])
                }
                for issue in data.get("issues", [])
            ]
        else:
            issues = [{"key": "Erro", "summary": response.text}]

    projeto_jira = get_project_code(cliente)
    issueKey = buscar_issue_jira(projeto_jira) if projeto_jira != "Desconhecido" else "Desconhecido"
    
    return render_template("index.html", issues=issues, versao_thom=versao, cliente_thom=cliente, issue_upgrade=issueKey, projeto=projeto_jira)

def buscar_issue_jira(projeto):
    issue_key = "JC-101"

    url = f"{JIRA_DOMINIO}/rest/api/3/search/jql?fields=key&maxResults=50&fields=Key, summary, customfield_10312, customfield_10382"
    #jql = f'"fixVersion" = "{versao}" AND "Excluir[Dropdown]" is EMPTY ORDER BY created DESC'
    jql = f'summary ~ "Atualização Versões*" and project = "{projeto}" and statusCategory in ("In Progress") ORDER BY created DESC'
    headers = {"Accept": "application/json"}
    params = {"jql": jql, "maxResults": 1}
        
    response = requests.get(
        url,
        headers=headers,
        params=params,
        auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
        )

    if response.status_code == 200:    
        issues = response.json().get("issues", [])
        if not issues:
            return "Desconhecido"
        issue = issues[0]
        if not issue:
            return "Desconhecido"
        else:
            return issue.get("key")
    else:
        print(f"Erro ao buscar issue: {response.status_code} - {response.text}")
        return "Erro"

def get_project_code(projeto):
    switcher = {
        "JCS": "JC",
        "CUF": "CT",
        "TSH": "GT",
        "Jenner": "IJP"
        # adicione outros códigos conforme necessidade
    }
    return switcher.get(projeto, "Desconhecido")

if __name__ == "__main__":
    app.run(debug=True)
