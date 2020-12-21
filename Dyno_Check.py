import os
import telebot
from time import sleep, ctime
from threading import Thread as th
from dotenv import load_dotenv
from time import ctime

#Comando Para Iniciar O App: heroku ps:scale worker=0 -a APP
#Comando Para Parar O App: heroku ps:scale worker=1 -a APP

#Lê o arquivo contendo as informações sobre os dynos e checa apenas a primeira linha ( que é onde fica armazenada a informação sobre dynos restants), retornando uma lista com o tempo restante dividido em horas e minutos e a porcentagem de tempo restante. 
def check_dynos():
	o = open("Dynos.log", "r")
	linhas  = o.readlines()
	dynos = (linhas)[0]
	o.close()
	if "No dynos" in linhas[5]:#Checa se o bot tá ativo, se não estiver esse if é True
#		o.close()
		return False
#	o.close()
	dynos = (dynos.split(" "))[-3:]
	final = []
	for i in dynos:
		final.append(i.strip())
	return(final)#Retorna o tempo final e a porcentagem em formato de lista

#Usa a cli do Heroku para criar um log com as informações de Dyno
def get_dynos():
	os.system("heroku ps -a ultimatespelltome > Dynos.log")
	os.system(f"echo '\n\n\t{ctime()}' >> Dynos.log")

#Checa se a porcentagem de dynos está dentro do valor limite para mandar o alerta
def valuate_dynos(lista_dos_dynos):
	porcentagem = (lista_dos_dynos[-1])[1:-2]
	if int(porcentagem) <=20:#Valor para que o telegram avise que os dynos estão acabando
		return True
	else:
		return False

#Manda a mensagem sobre o tempo de dyno restante
def message_me():
	meu_id = 592950370	#meu id no telegram
	while True:
		get_dynos()
		dynos_left = (check_dynos())
		if dynos_left == False:
			if int((ctime()).split(' ')[3]) < 10:#Checa se é dia 1, independente do mês, e se for True o bot principal é ativado e o secundário desativado
				os.system("heroku ps:scale worker=0 -a ustbackup")##Desliga o bot secundário
				os.system("heroku ps:scale worker=1 -a ultimatespelltome")#Liga o bot principal
				bot.send_message(meu_id, (f"O bot de backup foi desativado e o principal reativado."))#Manda alerta no telegram sobre a troca
			sleep(43200)
			continue
		dynos_time = " ".join(dynos_left)
		if valuate_dynos(dynos_left) == True:
			bot.send_message(meu_id, (f"Você tem {dynos_time} restantes"))#Manda alerta no telegram sobre os dynos restantes
			os.system("heroku ps:scale worker=0 -a ultimatespelltome")#Desliga o bot principal
			os.system("heroku ps:scale worker=1 -a ustbackup")#Liga o bot secundário
			bot.send_message(meu_id, (f"O bot principal foi desaivado e o de backup foi ativado"))
		else:
			pass
		sleep(43200)

#pega o token no .env
load_dotenv()
token = os.getenv("Tele_Token")

#Conecta o bot ao telegram
bot = telebot.TeleBot(token, parse_mode=None)

#inicia a função. Como é uma função pode ser usado com threading no futuro
message_me()
