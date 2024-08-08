from flask import Blueprint, request, session, redirect


home_controller = Blueprint("home", __name__, url_prefix="/")


@home_controller.get("/")
def home():
    return "<h1>Sistema de integração do Sigma + WhatsApp + IA</h1>"
