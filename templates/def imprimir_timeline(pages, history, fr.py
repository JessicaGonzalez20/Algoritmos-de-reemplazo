def imprimir_timeline(pages, history, frames_count):
    print("\nSecuencia de referencias:")
    print(" ".join(str(p) for p in pages))

    print("\nEstado de marcos en cada paso:")
    for i in range(frames_count):
        fila = []
        for estado, _, _ in history:
            val = estado[i] if i < len(estado) else None
            fila.append(str(val) if val is not None else " ")
        print(f"Marco {i+1}: {' '.join(fila)}")

    print("\nFaltas de página:")
    linea_fallos = []
    num_fallos = 0
    for _, fallo, _ in history:
        linea_fallos.append("*" if fallo else " ")
        num_fallos += 1 if fallo else 0
    print("            " + " ".join(linea_fallos))
    print(f"\nTotal de fallos de página: {num_fallos}")

def segunda_oportunidad(paginas, num_marcos):
    marcos = [None] * num_marcos
    bits = [0] * num_marcos
    puntero = 0
    fault = 0
    history = []

    for pagina in paginas:

        if pagina in marcos:
            fault = False  # No hay falta de página
            indice = marcos.index(pagina)
            bits = [0] * num_marcos
            bits[indice] = 1
        else:
            while True:

                if bits[puntero] == 0:
                    #print(f"Reemplazando la página {marcos[puntero]} por {pagina} en el marco {puntero}.")
                    marcos[puntero] = pagina
                    bits = [0] * num_marcos  # Reiniciar todos los bits
                    bits[puntero] = 1        # El marco nuevo entra con bit en 1
                    fault += 1
                    puntero = (puntero + 1) % num_marcos
                    break
                else:
                    #print(f"Inspeccionando marco {puntero}: valor={marcos[puntero]}, bit={bits[puntero]} -> Segunda oportunidad")
                    bits[puntero] = 0  # Le damos la segunda oportunidad
                    puntero = (puntero + 1) % num_marcos
        
        # Guardar estado actual
        estado_actual = marcos.copy()
        while len(estado_actual) < num_marcos:
            estado_actual.append(None)
        history.append((estado_actual, fault, None))


    return history, fault

pages = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0]
frames_count = 3
history, faults = segunda_oportunidad(pages, frames_count)

imprimir_timeline(pages, history, frames_count)

