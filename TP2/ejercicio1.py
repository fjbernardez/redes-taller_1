#!/usr/bin/env python3
import sys
from scapy.all import *
from time import *

responses = {}
tandas = 30
for i in range(tandas):    
    print("Tanda de mensajes " + str(i))
    for ttl in range(1,25):
        print("Enviando con TTL " + str(ttl))
        probe = IP(dst=sys.argv[1], ttl=ttl) / ICMP()
        t_i = time()
        ans = sr1(probe, verbose=False, timeout=0.8)
        t_f = time()
        rtt = (t_f - t_i)*1000
        if ans is not None:
            
            
            if ttl not in responses:                
                responses[ttl] = {}
                
            if ans.src not in responses[ttl]:
                responses[ttl][ans.src] = []

            responses[ttl][ans.src].append(rtt)    
                 
            #Enunciado pide calcular RTT solo de saltos de TTL Time excceeded, si llego a destino termino
            if ans.type == 0:
                break
            #if ttl in responses:
                #print(ttl, responses[ttl])

print("Calculando promedios")

#Obtenemos el promedio de rtt por ttl
rtt_promedios = []
for ttl in range(1,25):
    if ttl in responses:
        responses_sorted = sorted(responses[ttl].items(), key=lambda x:len(x[1]))         
        rttl_ip_with_most_replys = responses_sorted[0]        
        promedio = sum(rttl_ip_with_most_replys[1]) / (len(rttl_ip_with_most_replys[1]))
        ip_most_replys = rttl_ip_with_most_replys[0]
        rtt_promedios.append((ip_most_replys,promedio))
print(rtt_promedios )

#Finalmente en rtt_salto guardamos el rtt estimado entre salto y salto
#Para calcularlo, vamos de ttl mayor a menor, y como dice el enunciado ignoramos los casos donde nos darían saltos con tiempo negativo
rtt_salto=[]
i = len(rtt_promedios)-1
j = len(rtt_promedios)-2
print("Calculando tiempos de salto")
while i > 0:    
    while j > 0 and rtt_promedios[i][1] <= rtt_promedios[j][1] :
        j = j-1
    delta = rtt_promedios[i][1] - rtt_promedios[j][1]
    rtt_salto.insert(0,(rtt_promedios[i][0],delta))    
    i = j
    j = j-1 
rtt_salto.insert(0,(rtt_promedios[i][0],rtt_promedios[i][1]))    
print(rtt_salto)
