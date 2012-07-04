# -*- coding: utf-8 -*-
import socket, sys, time
from datetime import datetime
from threading import Thread

### - Verificacao dos parametros - ###
if len(sys.argv) < 3:
    print 'Parametros nao informados corretamente\nVerifique e tente novamente.'
    print 'Ex: "python PingClient.py (ip server) (porta server)"'
    sys.exit()

#Recupera o ip do servidor
ip_server = sys.argv[1]

try:
    #Recupera a porta em que o servidor está rodando
    porta_server = int(sys.argv[2])
except ValueError:
    print 'O segundo parametro "porta do servidor" deve ser um numero e nao ('+sys.argv[1]+')'
    sys.exit()

### - Fim da verificacao dos parametros - ###
    
#Ip do cliente    
UDP_IP="127.0.0.1"
#Porta do cliente, sempre uma a mais que a do servidor
UDP_PORT= porta_server+1

#Define o tipo de conexao, neste caso UDP
sock = socket.socket( socket.AF_INET, # Internet
                      socket.SOCK_DGRAM ) # UDP
                      
#Dicionario de pacotes enviados
pacotes = {}
#Dicionario de pacotes recebidos
recebidos = {}

#dadoa a enviar caso o pacotes a enviar
dados = {1:'abc',2:'def',3:'ghi',4:'jkl',5:'mno',6:'pqr',7:'stu',8:'vwx',9:'yz'}


#controle da sequencia
sequencia = 0
         
def escuta():
    '''
    Função que fica recebendo os pacotes enviados pelo servidor
    '''
    #reserva a porta para escuta
    try:
        sock.bind( (UDP_IP,UDP_PORT) )
        while 1:
            data, addr = sock.recvfrom( 1024 ) # buffer size is 1024 bytes
            #Verifica se o pacote veio do servidor
            if addr[0] == ip_server and addr[1] == porta_server:
                try:
                    #Extrai a sequencia da mensagem
                    key = int(data.split()[1])
                    data_recebida = " ".join(data.split()[2:4])
                    time = datetime.strptime(data_recebida, '%Y-%m-%d %H:%M:%S.%f')
                    
                    tempo = (datetime.today() - time).microseconds/1000 + (datetime.today() - time).seconds*1000
                    if  tempo > 1000:
                        print 'sequencia '+str(key)+' time_out com '+str(tempo)+' milisegundos'
                    else:
                        #print 'sequencia '+str(key)+' aceita com '+str(tempo)+' milisegundos'
                        
                        #Verifica se está trafegando dados, e valida os mesmos
                        if len(sys.argv) == 4 and sys.argv[3] == '-d':
                            #Verifica se os dados são os mesmos...
                            if dados[key] == data.split()[4]:
                                #Valida os dados
                                recebidos[key] = tempo
                                del dados[key]
                            else:
                                #Reprova os dados....
                                print 'sequencia %s com valor incompativel (%s) != (%s)'%(str(key),dados[key],data.split()[4])
                        else:
                            #Valida os dados...
                            recebidos[key] = tempo
                            del pacotes[key]
                except ValueError:
                    print 'Sequencia nao encontrada na mensagem'
                except SyntaxError:
                    print 'O pacote esta fora dos padroes'
                
    except socket.error, msg:
        print 'Opss!!! Ocorreu um erro na escuta.\n'+str(msg)
    
#Abre um thread para escuta
th=Thread( target=escuta, args = () )
th.start()    
# Se for para transferencia de dados...
if len(sys.argv) == 4 and sys.argv[3] == '-d':
    #enquanto existir pacotes para enviar...
    while (dados):
        #Envia os pacotes que ainda não foram enviados
        for i in dados.keys():
            #Pega a hora atual
            hora = datetime.today()
            #Monta a mensagem
            mensagem = 'PING '+str(i)+' '+str(hora)+' '+dados[i]+'\n'
            #Envia a mensagem para o servidor
            try:
                sock.sendto( mensagem, (ip_server, porta_server) )
            except socket.error, msg:
                print 'O servidor especificado nao esta disponivel para receber pacotes'
                
            #Grava para controle de perdas o pacote enviado
            pacotes[i]=hora
            
            #Proxima sequencia
            sequencia += 1
            
            #Dorme 1 segundo
            time.sleep(1)
    

#Se for para estatistica de ping...
else:
    #Envia uma sequencia de 10 pocotes para o servidor em um intervalo de 1seg.
    for i in range(10):
        #Pega a hora atual
        hora = datetime.today()
        #Monta a mensagem
        mensagem = 'PING '+str(sequencia)+' '+str(hora)+'\n'
        #Envia a mensagem para o servidor
        try:
            sock.sendto( mensagem, (ip_server, porta_server) )
        except socket.error, msg:
            print 'O servidor especificado nao esta disponivel para receber pacotes'
            
        #Grava para controle de perdas o pacote enviado
        pacotes[sequencia]=hora
        
        #Proxima sequencia
        sequencia += 1
        
        #Dorme 1 segundo
        time.sleep(1)
        
#Para a thread de escuta
th._Thread__stop() 

### - Analize dos dados - ####

# Se for para transferencia de dados...
if len(sys.argv) == 4 and sys.argv[3] == '-d':
    print 'foram enviados %d pacotes'%(sequencia)
else:
    if len(pacotes):
        print '\n\nA Conexao nao foi integra\n'
        for key in sorted(pacotes.iterkeys()):
            print 'Sequencia %d perdida'%(key)
    else:
        print '\n\nNenhum pacote perdido durante a transmissao'
    
#Se recebeu algum pacote
if len(recebidos):
    print "\n#### - Dados finais - ####"
    
    #Exibe os pacotes recebido pela sequencia de envio
    for key in sorted(recebidos.iterkeys()):
        print 'Sequencia %d com %d milisegundos'%(key,recebidos[key])
    
    #Ordena os pacotes recebidos pelo tempo de resposta    
    resultado = sorted(recebidos.items(), key=lambda x: x[1])
    
    print '\nMaior tempo:'
    print 'Sequencia %d com %d milisegundos'%(resultado[-1]) #Maior tempo de resposta
    print '\nMenor tempo:'
    print 'Sequencia %d com %d milisegundos'%(resultado[0]) #Menor tempo de resposta
    print '\nMedia de tempo:'
    #Soma os tempos de todos resultados e divide pela quantidade de pacotes
    print 'Media em milisegundos ~',(round(sum([r2 for k,r2 in resultado],0.0)/len(resultado),2)),'\n\n' 
    
else:
    print '\nNenhum pacote recebido'
    

