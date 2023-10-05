from celery import shared_task
import win32com.client as win32
import pythoncom
from .models import Email, Ativo
from celery.beat import periodic_task
from datetime import timedelta
import requests
from decouple import config
key = config('chave_api2')
EMAIL_ADDRESS = config('email')
EMAIL_PASSWORD = config('senha')


@shared_task
def send_email(ativos):
    pythoncom.CoInitialize()
    outlook = win32.Dispatch('outlook.application')
    email_obj = Email.objects.latest('email')
    novo_email = email_obj.email
    print(f"{novo_email}")
    email = outlook.CreateItem(0)
    email.To = novo_email
    email.Subject = "Monitoramento de ativos!!"
    print('1')
    ativos = Ativo.objects.all()
    dados_da_api = api_request(ativos)
    
    email.HTMLBody = "Resultados dos ativos:\n\n"
    print(dados_da_api[0]['results'][0]['regularMarketPrice'])
    for i in range(0, len(dados_da_api)):
        if dados_da_api[i]['results'][0]['regularMarketPrice']> ativos[i].tunel_max:
            email.HTMLBody += f"Venda a ação {dados_da_api[i]['results'][0]['symbol']}<br>"
        elif dados_da_api[i]['results'][0]['regularMarketPrice']< ativos[i].tunel_min:
            email.HTMLBody += f"Compre a ação {dados_da_api[i]['results'][0]['symbol']}<br>"
        else:  email.HTMLBody += "TA MASSA!!!!<br>"
    email.Send()

@periodic_task(run_every=timedelta(minutes=1))  # Define o intervalo de tempo
def agendar_envio_de_email():
    # Chama a função send_email em intervalos regulares
    send_email.delay() 

@shared_task
def api_request(ativos):
    data = []
    for ativo in ativos:
        response = requests.get(f"https://brapi.dev/api/quote/{ativo.nome_ativo}?token={key}")
        if response.status_code == 200:
            data.append(response.json())
    return data

    