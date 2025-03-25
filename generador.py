import sys
import random

def generar(nombre, cant_clientes):

	lista_nombres = ["Antonella", "Jazmín", "Patricia", "Dibu", "Marc", "Oscar"]
	lista_apellidos = ["Pellegrini", "Martinez", "Marquez", "Piastri"]
	lista_dni = ["14328903", "47259862", "7592348", "28324758"]
	lista_nacimiento = ["2003-01-29", "1992-09-02", "1993-02-17", "2001-04-06"]
    
	with open(nombre, "w") as archivo:
		path_server = "./server/config.ini"
		path_cliente = "./client/config.yaml"
		path_data = ".data/agency-"
		contenido = "name: tp0\n"
		contenido += "services:\n"

		# server
		contenido += "  server:\n"
		contenido += "    container_name: server\n"
		contenido += "    image: server:latest\n"
		contenido += "    entrypoint: python3 /main.py\n"
		contenido += "    environment:\n"
		contenido += "      - PYTHONUNBUFFERED=1\n"
		contenido += "    networks:\n"
		contenido += "      - testing_net\n"
		contenido += "    volumes:\n"
		contenido += "      - " + path_server + ":/config.ini\n"

		contenido += "\n"

		# clientes
		for i in range(1, cant_clientes+1):
			num_string = str(i)
			nombre_cliente = "client" + num_string
			contenido += "  " + nombre_cliente + ":\n"
			contenido += "    container_name: " + nombre_cliente + "\n"
			contenido += "    image: client:latest\n"
			contenido += "    entrypoint: /client\n"
			contenido += "    environment:\n"
			contenido += "      - CLI_ID=" + num_string + "\n"

			contenido += "    networks:\n"
			contenido += "      - testing_net\n"
			contenido += "    depends_on:\n"
			contenido += "      - server\n"

			contenido += "    volumes:\n"
			contenido += "      - " + path_cliente + ":/config.yaml\n"
			contenido += "      - " + path_data + num_string + ".csv:/agencyFile.csv\n"
			contenido += "\n"
				
		# network
		contenido += "networks:\n"
		contenido += "  testing_net:\n"
		contenido += "    ipam:\n"
		contenido += "      driver: default\n"
		contenido += "      config:\n"
		contenido += "        - subnet: 172.25.125.0/24\n"


		archivo.write(contenido)

	return



generar(sys.argv[1], int(sys.argv[2]))
