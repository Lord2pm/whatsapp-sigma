from flask import session


def start_sessions():
    session["i"] = 0
    session["email"] = None
    session["senha"] = None
    session["servico_escolhido"] = None
    session["status_login"] = False
    session["db_id"] = 30
    session["i_servico"] = 0
    session["menu_visivel"] = False
    session["ss_data"] = {}
    session["os_data"] = {}
    session["db_list"] = []
