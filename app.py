import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import sys
from flask import Flask, request, jsonify, render_template

sys.stdout = sys.__stdout__

app = Flask(__name__)

def fifo(pages, frames_count):
    frames = [None] * frames_count
    pointer = 0
    page_faults = 0
    history = []

    for page in pages:
        fault = False
        if page not in frames:
            # Solo si hay fallo se reemplaza y se mueve el puntero
            frames[pointer] = page
            pointer = (pointer + 1) % frames_count
            page_faults += 1
            fault = True
        # Guardamos el estado actual de los marcos
        history.append((frames.copy(), fault, pointer))

    return history, page_faults




def print_table(pages, history, frames_count):
    print("\nReferencia de páginas:")
    print(" ".join(str(p) for p in pages))
    print("\nTabla de marcos:")

    for frame_index in range(frames_count):
        row = ""
        for state, _ in history:
            val = state[frame_index]
            row += f"{val if val is not None else ' '} "
        print(row.strip())

    # Línea de fallos
    faults_line = ""
    for _, fault in history:
        faults_line += "* " if fault else "  "
    print("\nFaltas de página:")
    print(faults_line.strip())


#Algoritmo Optimo
def optimo(pages, frames_count):
    frames = []
    page_faults = 0
    history = []

    for i in range(len(pages)):
        current = pages[i]
        fault = False

        if current not in frames:
            fault = True
            page_faults += 1

            if len(frames) < frames_count:
                # Si hay espacio, simplemente agrega la página
                frames.append(current)
            else:
                # Buscar la página con uso más lejano en el futuro
                future = pages[i+1:]
                indices = []

                for f in frames:
                    if f in future:
                        idx = future.index(f)
                    else:
                        idx = float('inf')  # No se volverá a usar
                    indices.append(idx)

                to_replace = indices.index(max(indices))
                frames[to_replace] = current

        # Guardar una copia del estado de marcos
        estado_actual = frames.copy()
        while len(estado_actual) < frames_count:
            estado_actual.append(None)  # Para alinear con filas vacías
        history.append((estado_actual, fault, None))

    return history, page_faults

#Algoritmo LRU
def lru(pages, frames_count):
    frames = []
    recently_used = []
    page_faults = 0
    history = []

    for page in pages:
        fault = False

        if page in frames:
            # Página ya está: moverla al final (más reciente)
            recently_used.remove(page)
            recently_used.append(page)
        else:
            fault = True
            page_faults += 1

            if len(frames) < frames_count:
                # Espacio disponible
                frames.append(page)
                recently_used.append(page)
            else:
                # Reemplazar la menos usada recientemente
                lru_page = recently_used.pop(0)  # Primera es la más antigua
                idx = frames.index(lru_page)
                frames[idx] = page
                recently_used.append(page)

        # Guardar estado actual
        estado_actual = frames.copy()
        while len(estado_actual) < frames_count:
            estado_actual.append(None)
        history.append((estado_actual, fault, None))

    return history, page_faults


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

#pages = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0]
#frames_count = 3
#history, faults = segunda_oportunidad(pages, frames_count)

import matplotlib.pyplot as plt
import os

import matplotlib.pyplot as plt
import os

def plot_matrix_timeline(pages, history, frames_count):
    print("Generando gráfico de tabla")
    print("Referencia de paginas:")
    print(" ".join(str(p) for p in pages))
    print("Tabla de marcos:")
    
    num_steps = len(pages)
    table_data = []

    # Fila 0: referencias
    table_data.append([str(p) for p in pages])

    print("iniciando tabla")
    # Filas de marcos
    for frame_index in range(frames_count):
        row = []
        for memory, fault, pointer in history:
            val = memory[frame_index] if frame_index < len(memory) else None
            row.append("" if val is None else str(val))
        table_data.append(row)

    # Fila de fallos
    fallo_row = []
    for _, fault, _ in history:
        fallo_row.append("*" if fault else "")
    table_data.append(fallo_row)

    row_labels = ["Referencia"] + [f"Marco {i+1}" for i in range(frames_count)] + ["Fallos"]

    fig, ax = plt.subplots(figsize=(1.2 * num_steps, 0.6 * (frames_count + 2)))
    ax.axis("off")
    table = ax.table(cellText=table_data,
                     rowLabels=row_labels,
                     cellLoc="center",
                     loc="center")
    table.scale(1, 2)

    os.makedirs("static", exist_ok=True)
    image_path = "static/grafico.png"
    if os.path.exists(image_path):
        os.remove(image_path)

    plt.savefig(image_path, bbox_inches="tight")
    plt.close(fig)
    print("Tabla guardada como imagen")
    return "/" + image_path



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/simular", methods=["POST"])
def simular():
    try:
        print("iniciando simulacion")
        data = request.json
        sequence = data["sequence"]
        frames = int(data["frames"])
        algorithm = data["algoritmo"].strip().upper()

        if algorithm == "FIFO":
            print("Iniciando FIFO")
            timeline, faults = fifo(sequence, frames)
        elif algorithm == "OPTIMO":
            timeline, faults = optimo(sequence, frames)
        elif algorithm == "LRU":
            timeline, faults = lru(sequence, frames)
        elif algorithm in ["SEGUNDA_OPORTUNIDAD", "SEGUNDA OPORTUNIDAD"]:
            print("Iniciando Segunda Oportunidad")
            timeline, faults = segunda_oportunidad(sequence, frames)
        else:
            return jsonify({"error": f"Algoritmo no soportado: {algorithm}"}), 400

        print("llamando a plot_timeline")
        image_path = plot_matrix_timeline(sequence, timeline, frames)
        print("llamado sin errores")

        return jsonify({
            "image_path": "/static/grafico.png",
            "fallos": faults,
            "timeline": [
                {
                    "page": sequence[i],
                    "memory": memory,
                    "fault": fault,
                }
                for i, (memory, fault, num_fallos)  in enumerate(timeline)
            ],

            "referencias": sequence
        })

    except Exception as e:
        print("Errorr:", e)
        sys.stdout.flush()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)



'''
def main():
    references = input("Ingresa la secuencia de referencias (separadas por espacio): ")
    pages = list(map(int, references.strip().split()))
    frames_count = int(input("Número de marcos de página: "))
    algorithm = input("Elige el algoritmo (FIFO / OPTIMO / LRU / SEGUNDA OPORTUNIDAD): ").strip().upper()

    if algorithm == "SEGUNDA_OPORTUNIDAD":
        history, faults = segunda_oportunidad(pages, frames_count)
    elif algorithm == "FIFO":
        history, faults = fifo(pages, frames_count)
    elif algorithm == "OPTIMO":
        history, faults = optimo(pages, frames_count)
    elif algorithm == "LRU":
        history, faults = lru(pages, frames_count)
    else:
        print("Algoritmo no reconocido.")
        return
    
    print("\nReferencia de páginas:")
    print(" ".join(str(p) for p in pages))

    print("\nTabla de marcos:")
    for i in range(frames_count):
        row = ""
        for state, _ in history:
            val = state[i]
            row += f"{val if val is not None else ' '} "
        print(row.strip())

    print("\nFaltas de página:")
    print(" ".join("*" if f else " " for _, f in history))
    print(f"\nTotal de fallos de página: {faults}")


if __name__ == "__main__":
    main() '''

