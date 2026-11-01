"""Conexión kRPC compartida por las herramientas de solo lectura."""
import sys

import krpc


def conectar(nombre):
    try:
        return krpc.connect(name=nombre, address='127.0.0.1')
    except ConnectionRefusedError:
        sys.exit('Sin servidor kRPC en 127.0.0.1:50000. Abre KSP 1, entra en vuelo y pulsa '
                 '"Start server" en la ventana kRPC.')
