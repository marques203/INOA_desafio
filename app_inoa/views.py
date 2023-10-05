from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from .models import Email, Ativo
import requests
from decouple import config
import os
import smtplib
from email.message import EmailMessage
import concurrent.futures
import schedule
import time
import win32com.client as win32
import pythoncom
import threading
import matplotlib.pyplot as plt
from io import BytesIO
import base64

key = config('chave_api2')
EMAIL_ADDRESS = config('email')
EMAIL_PASSWORD = config('senha')

cancelar_schedule = None
email_thread = []
ativos_criados = []

def home(request):
    global cancelar_schedule
    cancelar_schedule = True
    Ativo.objects.all().delete()
    Email.objects.all().delete()
    return render(request, "usuario/home.html")


    
def send_email(ativo):
    pythoncom.CoInitialize()
    outlook = win32.Dispatch('outlook.application')
    email_obj = Email.objects.latest('id')
    novo_email = email_obj.email
    print(f"{novo_email}")
    email = outlook.CreateItem(0)
    email.To = novo_email
    email.Subject = "Monitoramento de ativos!!"
    dados_da_api = api_request(ativo)
    email.HTMLBody = "Resultados dos ativos:\n\n"
    ativo.precos.append(dados_da_api['results'][0]['regularMarketPrice'])
    
    print(dados_da_api['results'][0]['symbol'], dados_da_api['results'][0]['regularMarketPrice'])
    
    if dados_da_api['results'][0]['regularMarketPrice']> ativo.tunel_max:
        email.HTMLBody += f"Venda a ação {dados_da_api['results'][0]['symbol']}, está valendo: {dados_da_api['results'][0]['regularMarketPrice']}<br>"
    elif dados_da_api['results'][0]['regularMarketPrice']< ativo.tunel_min:
        email.HTMLBody += f"Compre a ação {dados_da_api['results'][0]['symbol']}, está valendo: {dados_da_api['results'][0]['regularMarketPrice']}<br>"
    else:  
        email.HTMLBody += "Mantenha os ativos<br>"
    email.Send()



def schedule_send_email(ativo, ):
    global cancelar_schedule

    
    while not cancelar_schedule:
    
     time.sleep(ativo.periodo * 60)
     print(cancelar_schedule)
     send_email(ativo)

def registro_email(request):
    Ativo.objects.all().delete()
    global cancelar_schedule
    cancelar_schedule = True
    novo_email = Email()
    novo_email.email=request.POST.get('email')
    if  novo_email.email is not None and novo_email.email.strip() != "":
        novo_email.save()
    return render(request, "usuario/registro_ativos.html")




def registro_ativos(request):
   global ativos_criados
   ativos_criados.clear()
   global cancelar_schedule
   cancelar_schedule = True
   if request.method == 'POST':
        # Receber os dados do formulário
        nome_ativo = request.POST.getlist('nome_ativo')
        tunel_max = request.POST.getlist('tunel_sup')
        tunel_min = request.POST.getlist('tunel_inf')
        periodo = request.POST.getlist('periodo')
        #global ativos_criados
        ativos_criados.clear()
        
        print(len(nome_ativo))
        # Validar e salvar os dados no banco de dados
        for i in range(len(nome_ativo)):
            try:
                ativo = Ativo(
                    nome_ativo=nome_ativo[i],
                    tunel_max=int(tunel_max[i]),
                    tunel_min=int(tunel_min[i]),
                    periodo=int(periodo[i])
                )
                ativo.save()
                ativos_criados.append(ativo)
                
            except (ValueError, ValidationError):
                # Lida com erros de validação, se necessário
                pass
        
        dados_da_api = []
        
        cancelar_schedule = False
        
        for ativo in ativos_criados:
            email_thread = threading.Thread(target=schedule_send_email, args=(ativo,))
            email_thread.start()
            dados_da_api.append(api_request(ativo))
    
        return render(request, 'monitorar/monitorar.html', {'dados_da_api': dados_da_api})

   return render(request, "usuario/registro_ativos.html")

def api_request(ativo):
        response = requests.get(f"https://brapi.dev/api/quote/{ativo.nome_ativo}?token={key}")
        if response.status_code == 200:
            data = response.json()
        return data

def historico(request):
    
    global ativos_criados
    ativos = ativos_criados
    graficos = []
    
    for ativo in ativos:
        # Simule dados de preços para o exemplo
        # Substitua isso pela lógica real para obter o histórico de preços do banco de dados

        precos = ativo.precos
        print(precos)
        plt.figure(figsize=(8, 4))
        plt.plot(precos, label=ativo.nome_ativo)
        plt.title(f"Histórico de Preços para {ativo.nome_ativo}")
        plt.xlabel("Tempo")
        plt.ylabel("Preço")
        plt.legend()
        
        # Salve o gráfico em formato de imagem
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        grafico_base64 = base64.b64encode(buffer.read()).decode()
        buffer.close()

        graficos.append((ativo.nome_ativo, grafico_base64))

    return render(request, 'historico/historico.html', {'graficos': graficos})




