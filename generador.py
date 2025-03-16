import sys

def generar(nombre, cant_clientes):
    
	with open(nombre, "w") as archivo:
		archivo.write("name: tp0\n")
		archivo.write("services:\n")

		# server
		archivo.write("  server:\n")
		archivo.write("    container_name: server\n")
		archivo.write("    image: server:latest\n")
		archivo.write("    entrypoint: python3 /main.py\n")
		archivo.write("    environment:\n")
		archivo.write("      - PYTHONUNBUFFERED=1\n")
		archivo.write("      - LOGGING_LEVEL=DEBUG\n")
		archivo.write("    networks:\n")
		archivo.write("      - testing_net\n")

		archivo.write("\n")

		# clientes
		for i in range(1, cant_clientes+1):
			num_string = str(i)
			nombre_cliente = "client" + num_string
			archivo.write("  " + nombre_cliente + ":\n")
			archivo.write("    container_name: " + nombre_cliente + "\n")
			archivo.write("    image: client:latest\n")
			archivo.write("    entrypoint: /client\n")
			archivo.write("    environment:\n")
			archivo.write("      - CLI_ID=" + num_string + "\n")
			archivo.write("      - CLI_LOG_LEVEL=DEBUG\n")
			archivo.write("    networks:\n")
			archivo.write("      - testing_net\n")
			archivo.write("    depends_on:\n")
			archivo.write("      - server\n")
			archivo.write("\n")
				
		# network
		archivo.write("networks:\n")
		archivo.write("  testing_net:\n")
		archivo.write("    ipam:\n")
		archivo.write("      driver: default\n")
		archivo.write("      config:\n")
		archivo.write("        - subnet: 172.25.125.0/24\n")

	return



generar(sys.argv[1], int(sys.argv[2]))
