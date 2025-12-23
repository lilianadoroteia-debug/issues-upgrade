from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    versao = request.form.get("versao", "")
    cliente = request.form.get("cliente", "")

    # EXEMPLO de dados (depois ligas ao Jira / DB / API)
    issues = [
        {
            "key": "ABC-123",
            "resumo": "Erro na validação",
            "impacto_cliente": "Sim",
            "prioridade_teste": "Alta",
            "origem": "Bug",
            "testes": "Manual"
        },
        {
            "key": "ABC-456",
            "resumo": "Ajuste visual",
            "impacto_cliente": "Não",
            "prioridade_teste": "--",
            "origem": "Melhoria",
            "testes": "Automático"
        }
    ]

    return render_template(
        "index.html",
        issues=issues,
        versao_thom=versao,
        cliente_thom=cliente,
        
        projeto="PROJ",
        issue_upgrade="UPG-1"
    )

if __name__ == "__main__":
    app.run()
