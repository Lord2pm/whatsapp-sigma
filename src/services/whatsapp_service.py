import requests
from requests.auth import HTTPBasicAuth
from pprint import pprint


def fazer_login(email, senha, db_id):
    url = f"http://demo.universosigma.com.br/api/login?dbid={db_id}"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, auth=HTTPBasicAuth(email, senha), headers=headers)
    try:
        response_data = response.json()
        return response_data.get("success")
    except Exception as e:
        print(e)
        return False


def consultar_ss(codigo_ss: int, email: str, senha: str, db_id: int):
    url = f"http://demo.universosigma.com.br/api/ss?w=SS_CODIGO:=:{codigo_ss}&dbid={db_id}&fields=SS_CODIGO,SS_DESCRIC,AFETA_PROD,DHATU,SOLICITANT,MAQ_CODIGO,TAG_CODIGO,DATA,SS_HORAEMI"
    response = requests.get(url, auth=HTTPBasicAuth(email, senha)).json()
    try:
        response_data = response["data"][0]
        return f"""Dados da Solicitação de serviço {codigo_ss}

Código: {codigo_ss}
Código da Máquina: {response_data.get('MAQ_CODIGO') if response_data.get('MAQ_CODIGO', False) else "Não disponível"}
Afeta a produção: {["Não", "Sim"][int(response_data.get('AFETA_PROD')[0])] if response_data.get('AFETA_PROD', False) else "Não disponível"}
Tag: {response_data.get('TAG_CODIGO') if response_data.get('TAG_CODIGO', False) else "Não disponível"}
Solicitante: {response_data.get('SOLICITANT') if response_data.get('SOLICITANT', False) else "Não disponível"}
Descrição: {response_data.get('SS_DESCRIC') if response_data.get('SS_DESCRIC', False) else "Não disponível"}
Data de emissão: {response_data.get('DATA').replace(" ", " | ") if response_data.get('DATA', False) else "Não disponível"} | {response_data.get('SS_HORAEMI').replace(" ", " | ") if response_data.get('SS_HORAEMI', False) else "Não disponível"}

Informe novamente um código para consultar outra Solicitação de serviço
"""
    except Exception as e:
        print(f"Erro: {e}")
        return False


def consultar_os(codigo_os: int, email: str, senha: str, db_id: int):
    url = f"http://demo.universosigma.com.br/api/os?w=OS_CODIGO:=:{codigo_os}&dbid={db_id}"
    response = requests.get(url, auth=HTTPBasicAuth(email, senha)).json()
    try:
        response_data = response["data"][0]
        pprint(response_data)
        return f"""Dados da Ordem de serviço {codigo_os}

Código: {codigo_os}
Código da Máquina: {response_data.get('MAQ_CODIGO') if response_data.get('MAQ_CODIGO', False) else "Não disponível"}
Afeta a produção: {["Não", "Sim"][int(response_data.get('OS_AFETAPR'))] if response_data.get('OS_AFETAPR', False) else "Não disponível"}
Tag: {response_data.get('TAG_CODIGO') if response_data.get('TAG_CODIGO', False) else "Não disponível"}
Solicitante: {response_data.get('OS_SOLICIT') if response_data.get('OS_SOLICIT', False) else "Não disponível"}
Descrição: {response_data.get('OS_DESCRIC') if response_data.get('OS_DESCRIC') else "Não disponível"}
Data de emissão: {response_data.get('OS_DATAEMI').replace(" ", " | ") if response_data.get('OS_DATAEMI', False) else "Não disponível"} | {response_data.get('OS_HORAEMI').replace(" ", " | ") if response_data.get('OS_HORAEMI', False) else "Não disponível"}

Informe novamente um código para consultar outra Ordem de serviço
"""
    except Exception as e:
        print(f"Erro: {e}")
        return False


def criar_ss(email: str, senha: str, ss_desc, maq_cod, tag_cod, db_id: int):
    url = f"http://demo.universosigma.com.br/api/ss/forms/cadastro?dbid={db_id}"
    data = {"SS_DESCRIC": ss_desc, "MAQ_CODIGO": maq_cod, "TAG_CODIGO": tag_cod}
    response = requests.post(url, auth=HTTPBasicAuth(email, senha), data=data)
    data = response.json()

    try:
        if data["success"]:
            return f"Solicitação de serviço com Código {data['id']} salva com sucesso"
    except Exception as e:
        print(e)
        return False


def criar_os(
    email: str,
    senha: str,
    os_desc: str,
    maq_cod,
    tag_cod,
    os_afeta_producao: int,
    db_id: int,
):
    url = f"http://demo.universosigma.com.br/api/os/forms/cadastro?dbid={db_id}"
    data = {
        "OS_AFETAPR": os_afeta_producao,
        "PRIORIDADE": 1,
        "AREA_CODIG": 1,
        "TIP_OS_COD": "Corretiva",
        "OS_DESCRIC": os_desc,
        "MAQ_CODIGO": maq_cod,
        "TAG_CODIGO": tag_cod,
        "SINT_CODIG": 1,
    }

    try:
        response = requests.post(url, auth=HTTPBasicAuth(email, senha), data=data)
        data = response.json()
        print(data)
        if data["success"]:
            return f"Ordem de serviço com Código {data['id']} salva com sucesso"
    except Exception as e:
        print(e.with_traceback())

    return False


def consultar_todas_ss(email: str, senha: str, db_id: int, status: str):
    url = f"http://demo.universosigma.com.br/api/ss?fields=SS_CODIGO,SS_DESCRIC,AFETA_PROD,DATA,SOLICITANT,MAQ_CODIGO,TAG_CODIGO&q=&limit=5&dbid={db_id}&w=SS.APROVADO:{status}"
    response = requests.get(url, auth=HTTPBasicAuth(email, senha)).json()
    response_data = response["data"]
    string = ""

    for ss in response_data:
        string += f"""Dados da Solicitação de serviço {ss['SS_CODIGO']}

Código: {ss['SS_CODIGO']}
Código da Máquina: {ss.get('MAQ_CODIGO') if ss.get('MAQ_CODIGO', False) else "Não disponível"}
Afeta a produção: {["Não", "Sim"][int(ss.get('AFETA_PROD')[0])] if ss.get('AFETA_PROD', False) else "Não disponível"}
Tag: {ss.get('TAG_CODIGO') if ss.get('TAG_CODIGO', False) else "Não disponível"}
Solicitante: {ss.get('SOLICITANT') if ss.get('SOLICITANT', False) else "Não disponível"}
Descrição: {ss.get('SS_DESCRIC') if ss.get('SS_DESCRIC', False) else "Não disponível"}
Data de emissão: {ss.get('DATA').replace(" ", " | ") if ss.get('DATA', False) else "Não disponível"} | {ss.get('SS_HORAEMI').replace(" ", " | ") if ss.get('SS_HORAEMI', False) else "Não disponível"}"

===========================================

"""

    print(string)
    return string


def buscar_todos_bancos_de_dados(subdominio: str) -> dict:
    url = f"http://{subdominio}/api/dbs"
    try:
        response = requests.get(url)
        response_data = response.json()["data"]
        db_dict = {}

        for db in response_data:
            db_dict.__setitem__(db["id"], db["label"])

        return db_dict
    except:
        ...


if __name__ == "__main__":
    db_dict = buscar_todos_bancos_de_dados("demo.universosigma.com.br")
    if len(db_dict.keys()) > 1:
        string = ""
        for db_id, db_label in db_dict.items():
            string += f"ID: {db_id} => {db_label}\n"
        print(f"{string}\n\nEscolha o banco de dados pelo seu ID. Exemplo: 30")
    elif len(db_dict.keys()) == 1:
        for db_id, db_label in db_dict.items():
            print(
                f"ID: {db_id} => {db_label}\n\nFoi encontrado apenas um banco de dados.\n\nSim -> Para continuar"
            )
