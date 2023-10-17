#!/usr/bin/env python3
import sys
from scapy.all import *
from time import *
import matplotlib.pyplot as plt
import math
#Esto es solo para obtener la ip del host
import socket
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

responses = {}
tandas = int(sys.argv[2])
for i in range(tandas):    
    print("Tanda de mensajes " + str(i+1))
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
        rtt_promedios.append((ip_most_replys,promedio,ttl))
print(rtt_promedios )

#Finalmente en rtt_salto guardamos el rtt estimado entre salto y salto
#Para calcularlo, vamos de ttl mayor a menor, y como dice el enunciado ignoramos los casos donde nos darían saltos con tiempo negativo
#rtt_salto va a tener los saltos en orden, cada salto contiene (IP ORIGEN DEL SALTO, IP DESTINO DEL SALTO, RTT DEL SALTO, NUMERO TTL QUE ALCANZO A DESTINO)
rtt_salto=[]
i = len(rtt_promedios)-1
j = len(rtt_promedios)-2
print("Calculando tiempos de salto")
while i > 0:    
    while j > 0 and rtt_promedios[i][1] <= rtt_promedios[j][1] :
        j = j-1
    delta = rtt_promedios[i][1] - rtt_promedios[j][1]
    rtt_salto.insert(0,(rtt_promedios[j][0],rtt_promedios[i][0],delta,rtt_promedios[i][2]))    
    i = j
    j = j-1 
rtt_salto.insert(0,(ip_address,rtt_promedios[i][0],rtt_promedios[i][1],rtt_promedios[i][2]))    
print(rtt_salto)
#Parte opcional

#Thompson empieza con n = 3, vamos a usar maximo hasta  n = 24
modifiedThompson=[1.1511,1.4250,1.5712,1.6563,1.7110,1.7491,1.7770,1.7984,1.8153,1.8290,1.8403,1.8498,1.8579,1.8649,1.8710,1.8764,1.8811,1.8853,1.8891,1.8926,1.8957,1.8985]

outliersThompson = []
quedanOutliers = True
rtt_sin_outliers = rtt_salto[:]
desviacionesSobreVarianza = {}
#Obtenemos outliers con el metodo de thompson
while quedanOutliers:
    #Promedio de tiempos
    total_tiempos = 0
    for salto in rtt_sin_outliers:
        total_tiempos+=salto[2]
    promedio_tiempos = total_tiempos/len(rtt_sin_outliers)   

    #Desviacion y varianza de salto
    rtt_salto_desviacion = []
    desviacionStandard =0
    salto_mayor_desviacion = None
    maxima_desviacion = None
    for salto in rtt_sin_outliers:
        desviacion = abs(salto[2] - promedio_tiempos)        
        if salto_mayor_desviacion == None:
            salto_mayor_desviacion = salto
            maxima_desviacion = desviacion
        elif maxima_desviacion < desviacion:
            salto_mayor_desviacion = salto
            maxima_desviacion = desviacion
        desviacionStandard += (desviacion**2)/(len(rtt_sin_outliers)-1)
        rtt_salto_deviacion = salto + (desviacion,)
    desviacionStandard = math.sqrt(desviacionStandard)
    #Actualizamos las desviaciones sobre varianza de cada salto para graficar luego
    for salto in rtt_sin_outliers:
        desviacionesSobreVarianza[salto] = (abs(salto[2] - promedio_tiempos)/desviacionStandard)    

    #Vemos si es outlier el salto con mayor desviacion
    limite = desviacionStandard * modifiedThompson[len(rtt_sin_outliers)-3]

    quedanOutliers = maxima_desviacion > limite
    if quedanOutliers:
        outliersThompson.append(salto_mayor_desviacion)
        rtt_sin_outliers.remove(salto_mayor_desviacion)

print("Outliers")
print(outliersThompson)

desviacionesSobreVarianzaLista = []
esOutlierThompson = []
for salto in rtt_salto:
    esOutlierThompson.append(salto in outliersThompson)  
    desviacionesSobreVarianzaLista.append(desviacionesSobreVarianza[salto]) 

#Graficamos el tiempo da cada salto, rojo es outlier de Thompson 
colores = ['red' if cond else 'blue' for cond in esOutlierThompson]
ip_llegada_saltos = [salto[1] for salto in rtt_salto]
tiempo_saltos = [salto[2] for salto in rtt_salto]

plt.scatter(ip_llegada_saltos,tiempo_saltos,c = colores)
plt.axhline(y=sum(tiempo_saltos)/len(tiempo_saltos), color='cyan', linestyle='--', label='Promedio del tiempo de todos los saltos')
plt.xticks(rotation=340) 
plt.xlabel('IP destino de cada salto')
plt.ylabel('RTT del salto (ms)')
plt.legend()
plt.show()    

#Grafico del valor (x - promedio)/S de cada salto, mantenemos rojo si fue outliers de Thompson
plt.scatter(ip_llegada_saltos,desviacionesSobreVarianzaLista,c = colores)
plt.xticks(rotation=340) 
plt.xlabel('IP destino de cada salto')
plt.ylabel('Valor (xi - X)/S')
plt.legend()
plt.show()   