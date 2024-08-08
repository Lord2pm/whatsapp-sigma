import google.generativeai as genai
import requests


genai.configure(api_key="AIzaSyCY1UkJpYb3IZzR2_I2n2N69f6Bwr8JIH4")
model = genai.GenerativeModel("gemini-1.5-flash")


def create_prompt(context: str, data):
    response = model.generate_content(f"{context}\n{data}")
    return response.text


def get_data_from(url: str):
    response = requests.get(url)
    return response.json()["data"]


def validar_cod_desc_maquina(data):
    maquinas = get_data_from(
        "http://demo.universosigma.com.br/api/maquinas?fields=MAQ_CODIGO,MAQ_DESCRI&w=MAQ_ATIVA:S"
    )
    return create_prompt(
        f"Diga unica e exclusivamente não caso {data} não conste nesta lista {maquinas} e se constar diga o código e a descrição da máquina encontrada no seguinte formato: Foi encontrada uma máquina com o código x, e com a descrição x",
        "",
    )


def validar_cod_desc_tag(data):
    tags = get_data_from(
        "http://demo.universosigma.com.br/api/tags?fields=TAG_CODIGO,TAG_DESCRI"
    )
    return create_prompt(
        f"Diga unica e exclusivamente não caso {data} não conste nesta lista {tags}, e se constar diga o código e a descrição da TAG encontrada no seguinte formato: Foi encontrada um TAG com o código x, e com a descrição x. Verifique atenciosamente a lista completa",
        "",
    )


def validar_ss(cod_maquina, tag, ss_desc):
    return create_prompt(
        f"Resuma em poucas palavras uma solicitação de serviço com os seguintes dados: Código ou descrição da máquina: {cod_maquina}, Códio ou descrição da TAG: {tag}, Descrição da silicitação de serviço: {ss_desc}",
        "",
    )
