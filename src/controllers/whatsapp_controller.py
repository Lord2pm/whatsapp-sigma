from flask import Blueprint, request, session
from twilio.twiml.messaging_response import MessagingResponse

from src.services.whatsapp_service import buscar_todos_bancos_de_dados, criar_ss, fazer_login, consultar_ss, consultar_os, criar_os, consultar_todas_ss
from src.utils.gemini import validar_cod_desc_maquina, validar_cod_desc_tag, validar_ss
from src.utils.start_sessions import start_sessions


whatsapp_controller = Blueprint("whatsapp", __name__, url_prefix="/")


@whatsapp_controller.before_request
def carregar_dados_do_usuario():
	if "i" not in session.keys():
		start_sessions()


@whatsapp_controller.route("/whatsapp", methods=["GET", "POST"])
def responder_mensagem():
	resp = MessagingResponse()
	msg = request.values.get("Body", "").strip()
	profile_name = request.form.get("ProfileName")

	# fim para limpar os dados da sessão
	if msg.lower() == "fim":
		resp.message("Sessão encerrada")
		session.clear()
		return str(resp)
	if msg.lower() == "v":
		if session["i"] == 4:
			if session["i_servico"] > 1:
				session["i_servico"] -= 2
			else:
				session["i_servico"] = 0
				session["servico_escolhido"] = None
				session["i"] = (
					session["i"] - 2 if session["menu_visivel"] else session["i"] - 1
				)
		else:
			if session["i"] > 2:
				session["i"] -= 2
			else:
				start_sessions()
	if msg.lower() == "0" and session["status_login"]:
		session["i"] = 3
		session["i_servico"] = 0
		session["servico_escolhido"] = None

	# Início do fluxo do programa
	if session["i"] == 0:
		resp.message(
			f"Olá, {profile_name}, eu sou a IAN (Inteligência Artificial Natural da Rede Industrial). Estou aqui para te ajudar. Mas para continuar, você deve me fornecer os teus dados de autenticação (e-mail e senha).\n\n"
			"Digite o seu e-mail"
		)
		session["i"] += 1
	# Pegar e-mail
	elif session["i"] == 1:
		session["email"] = msg if msg.lower() != "v" else session["email"]
		session["i"] += 1
		resp.message("Digite a sua senha")
	# Pegar a senha, fazer login e caso o usuário se logue, exibir os negócios
	elif session["i"] == 2:
		session["senha"] = msg if msg.lower() != "v" else session["senha"]
		session["status_login"] = fazer_login(
			session["email"], session["senha"], session["db_id"]
		)
		if session["status_login"]:
			db_dict = buscar_todos_bancos_de_dados("demo.universosigma.com.br")
			print(db_dict)
			session["db_list"] = db_dict
			string = ""
			if len(db_dict.keys()) > 1:
				for db_id, db_label in db_dict.items():
					string += f"ID: {db_id} => {db_label}\n"
				string = f"{string}\nEscolha o banco de dados pelo seu ID. Exemplo: 30"
			elif len(db_dict.keys()) == 1:
				for db_id, db_label in db_dict.items():
					string = f"ID: {db_id} => {db_label}\n\nFoi encontrado apenas um banco de dados.\n\nSim -> Para continuar"
			session["i"] += 1
			resp.message(string)
		else:
			resp.message("E-mail ou senha inválidos\n\nDigite novamente o e-mail")
			session["i"] = 1
	# Receber a escolha do negócio
	elif session["i"] == 3:
		db_id = msg if msg.lower() != "v" else str(session["db_id"])
		if session["db_list"].get(db_id):
			# session["db_id"] = int(db_id)
			resp.message(
				"1 - Emitir Solicitação de serviço\n2 - Emitir Ordem de serviço\n3 - Consultar Solicitação de serviço\n4 - Consultar Ordem de serviço\n5 - Ver SSs pendentes\n6 - Ver SSs concluidas\n7 - Ver todas SSs\n0 - Para voltar ao menu\nV - Para voltar ao ponto anterior\nFim - Para Terminar sessão\n\nEscolha uma opção:"
			)
			session["i"] += 1
			session["menu_visivel"] = True
		else:
			resp.message("ID inválido. Verifique a lista de banco de dados e tente novamente")
	# Entra na parte de serviços
	elif session["i"] == 4:
		if not session.get("servico_escolhido"):
			session["menu_visivel"] = False
			session["servico_escolhido"] = int(msg)

		# Emissão de SS
		if session["servico_escolhido"] == 1:
			if session["i_servico"] == 0:
				resp.message("Informe o código ou a descrição do activo")
				session["i_servico"] = 1
			elif session["i_servico"] == 1:
				session["ss_data"]["MAQ_COD"] = msg if msg.lower() != "v" else session["ss_data"]["MAQ_COD"]
				resposta = validar_cod_desc_maquina(msg) if msg.lower() != "v" else ""

				if "Não" in resposta or "não" in resposta:
					resp.message(
						"O código ou a descrição do activo são inválidos\n\n"
						"Informe novamente o código ou a descrição do activo"
					)
				else:
					resp.message(f"{resposta}\nInforme o código ou a descrição do TAG")
					session["i_servico"] = 2
			elif session["i_servico"] == 2:
				session["ss_data"]["TAG"] = msg if msg.lower() != "v" else session["ss_data"]["TAG"]
				resposta = validar_cod_desc_tag(msg) if msg.lower() != "v" else ""

				if "Não" in resposta or "não" in resposta:
					resp.message(
							"O código ou a descrição do TAG são inválidos\n\n"
							"Informe novamente o código ou a descrição do TAG"
						)
				else:
					resp.message(f"{resposta}\nInforme a descrição da Solicitação de serviço")
					session["i_servico"] = 3
			elif session["i_servico"] == 3:
				session["ss_data"]["SS_DESCR"] = msg
				resp.message(
						f"{validar_ss(session["ss_data"]["MAQ_COD"], session["ss_data"]["TAG"], msg,)}\n"
						"1 - Para Salvar\n0 - Para cancelar e voltar ao menu\nV - Para voltar ao ponto anterior\n\nEscolha uma opção"
					)
				session["i_servico"] = 4
			elif session["i_servico"] == 4:
				resp.message("Salvando Solicitação de serviço...")
				response = criar_ss(
						session["email"],
						session["senha"],
						session["ss_data"]["SS_DESCR"],
						session["ss_data"]["MAQ_COD"],
						session["ss_data"]["TAG"],
						session["db_id"]
					)
				if not response:
					resp.message("Erro ao salvar Solicitação de serviço")
				else:
					print(response)
					resp.message(f"response")
		# Emissão de OS
		elif session["servico_escolhido"] == 2:
			if session["i_servico"] == 0:
				resp.message("Informe o código ou a descrição do activo")
				session["i_servico"] = 1
			elif session["i_servico"] == 1:
				session["os_data"]["MAQ_COD"] = msg if msg.lower() != "v" else session["os_data"]["MAQ_COD"]
				resposta = validar_cod_desc_maquina(msg) if msg.lower() != "v" else ""

				if "Não" in resposta or "não" in resposta:
					resp.message(
						"O código ou a descrição do activo são inválidos\n\n"
						"Informe novamente o código ou a descrição do activo"
					)
				else:
					resp.message(f"{resposta}\nInforme o código ou a descrição do TAG")
					session["i_servico"] = 2
			elif session["i_servico"] == 2:
				session["os_data"]["TAG"] = msg if msg.lower() != "v" else session["os_data"]["TAG"]
				resposta = validar_cod_desc_tag(msg) if msg.lower() != "v" else ""

				if "Não" in resposta or "não" in resposta:
					resp.message(
							"O código ou a descrição do TAG são inválidos\n\n"
							"Informe novamente o código ou a descrição do TAG"
						)
				else:
					resp.message(f"{resposta}\nInforme se a Ordem de serviço afeta a produção\n1 - Sim\n2 - Não")
					session["i_servico"] = 3
			elif session["i_servico"] == 3:
				try:
					session["os_data"]["OS_AFETAPR"] = {1: 1, 2: 0}[int(msg)] if msg.lower() != "v" else session["os_data"]["OS_AFETAPR"]
					resp.message("Informe a descrição da Ordem de serviço")
					session["i_servico"] = 4
				except:
					resp.message(f"Valor inválido\n\nInforme novamente se a Ordem de serviço afeta a produção\n1 - Sim\n2 - Não")
			elif session["i_servico"] == 4:
				session["os_data"]["OS_DESCR"] = msg
				resp.message(
					f"{validar_ss(session["os_data"]["MAQ_COD"], session["os_data"]["TAG"], msg,).replace("Solicitação", "Ordem").replace("solicitação", "ordem")}\n"
					"1 - Para Salvar\n0 - Para cancelar e voltar ao menu\nV - Para voltar ao ponto anterior\n\nEscolha uma opção"
				)
				session["i_servico"] = 5
			elif session["i_servico"] == 5:
				response = criar_os(session["email"], session["senha"], session["os_data"]["OS_DESCR"], session["os_data"]["MAQ_COD"], session["os_data"]["TAG"], session["os_data"]["OS_AFETAPR"], session["db_id"])
				print(response)
				resp.message(f"{response}")
		# Consulta de SS
		elif session["servico_escolhido"] == 3:
			if session["i_servico"] == 0:
				resp.message("Informe o código da Solicitação de serviço")
				session["i_servico"] += 1
			elif session["i_servico"] == 1:
				codigo_ss = int(msg)
				ss = consultar_ss(
					codigo_ss, session["email"], session["senha"], session["db_id"]
				)
				if ss:
					resp.message(ss)
				else:
					resp.message(
						"Você não possui autorização para aceder esta informação ou código inválido"
						"\n\nInforme um código novamente"
					)
		# Consulta de OS
		elif session["servico_escolhido"] == 4:
			if session["i_servico"] == 0:
				resp.message("Informe o código da Ordem de serviço")
				session["i_servico"] += 1
			elif session["i_servico"] == 1:
				codigo_os = int(msg)
				os = consultar_os(
					codigo_os, session["email"], session["senha"], session["db_id"]
				)
				if os:
					resp.message(os)
				else:
					resp.message(
						"Você não possui autorização para aceder esta informação ou código inválido"
						"\n\nInforme um código novamente"
					)
		elif session["servico_escolhido"] == 5:
			lista_de_ss = consultar_todas_ss(session["email"], session["senha"], session["db_id"], "P")
			resp.message(f"Lista de SSs pendentes\n\n{lista_de_ss}")
		elif session["servico_escolhido"] == 6:
			lista_de_ss = consultar_todas_ss(session["email"], session["senha"], session["db_id"], "A")
			resp.message(f"Lista de SSs concluidas\n\n{lista_de_ss}")
		elif session["servico_escolhido"] == 7:
			lista_de_ss = consultar_todas_ss(session["email"], session["senha"], session["db_id"], "N")
			resp.message(f"Lista de SSs\n\n{lista_de_ss}")

	return str(resp)
