import sys

def generar(nombre, cant_clientes):
    
    with open(nombre, "w") as archivo:
        archivo.write("name: tp0\n")
        archivo.write("services:\n")

        # server
        archivo.write("\tserver:\n")
        archivo.write("\t\tcontainer_name: server\n")
        archivo.write("\t\timage: server:latest\n")
        archivo.write("\t\tentrypoint: python3 /main.py\n")
        archivo.write("\t\tenvironment:\n")
        archivo.write("\t\t\t- PYTHONUNBUFFERED=1\n")
        archivo.write("\t\t\t- LOGGING_LEVEL=DEBUG\n")
        archivo.write("\t\tnetworks:\n")
        archivo.write("\t\t\t- testing_net\n")

        archivo.write("\n")

        # clientes
        for i in range(cant_clientes):
            nombre_cliente = "client" + str(i + 1)
            archivo.write("\t" + nombre_cliente + ":\n")
            archivo.write("\t\tcontainer_name: " + nombre_cliente + "\n")
            archivo.write("\t\timage: client:latest\n")
            archivo.write("\t\tentrypoint: /client\n")
            archivo.write("\t\tenvironment:\n")
            archivo.write("\t\t\t- CLI_ID=1\n")
            archivo.write("\t\t\t- CLI_LOG_LEVEL=DEBUG\n")
            archivo.write("\t\tnetworks:\n")
            archivo.write("\t\t\t- testing_net\n")
            archivo.write("\t\tdepends_on:\n")
            archivo.write("\t\t\t- server\n")
            archivo.write("\n")
            
        # network
        archivo.write("networks:\n")
        archivo.write("\ttesting_net:\n")
        archivo.write("\t\tipam:\n")
        archivo.write("\t\t\tdriver: default\n")
        archivo.write("\t\t\tconfig:\n")
        archivo.write("\t\t\t\t- subnet: 172.25.125.0/24\n")

    return



generar(sys.argv[1], int(sys.argv[2]))
