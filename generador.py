import sys

def generar(nombre, cant_clientes):
    
	with open(nombre, "w") as archivo:
		path_server = "./server/config.ini"
		path_cliente = "./client/config.yaml"
		contenido = "name: tp0\n"
		contenido += "services:\n"

		# server
		contenido += "  server:\n"
		contenido += "    container_name: server\n"
		contenido += "    image: server:latest\n"
		contenido += "    entrypoint: python3 /main.py\n"
		contenido += "    environment:\n"
		contenido += "      - PYTHONUNBUFFERED=1\n"
		contenido += "      - LOGGING_LEVEL=DEBUG\n"
		contenido += "    networks:\n"
		contenido += "      - testing_net\n"
		contenido += "    volumes:\n"
		contenido += "      - type: bind\n"
		contenido += "        source: " + path_server + "\n"
		contenido += "        target: /config.ini\n"

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
			contenido += "      - CLI_LOG_LEVEL=DEBUG\n"
			contenido += "    networks:\n"
			contenido += "      - testing_net\n"
			contenido += "    depends_on:\n"
			contenido += "      - server\n"
			contenido += "    volumes:\n"
			contenido += "      - type: bind\n"
			contenido += "        source: " + path_cliente + "\n"
			contenido += "        target: /config.yaml\n"
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
