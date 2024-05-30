import streamlit as st
import requests
import time
import pandas as pd
import altair as alt
from PIL import Image

url = "https://mojarras-server.vercel.app/api/traffic/last"

# Lista para almacenar los datos históricos
historical_data = []

def obtener_datos_trafico(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data_json = response.json()
        print(data_json)
        return data_json
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as err:
        print(f'Other error occurred: {err}')
    except ValueError as json_err:
        print(f'JSON parse error: {json_err}')
    return None

def mostrar_informacion_trafico():
    datos = obtener_datos_trafico(url)
    if datos:
        cars = datos.get("cars", [])
        
        # Crear índice incremental basado en el número de iteraciones
        timer = len(historical_data) + 1
        
        st.write("### Timer ⏲️:")
        st.write(f"{timer} segundos")
        
        # Resto del código sin cambios
        
        st.write("### Total de carros en todos los semáforos 🚗:")
        total_cars = sum(cars)
        st.write(f"{total_cars} carros")

        # Agregar datos al historial
        historical_data.append({'timer': timer, 'total_cars': total_cars})

        # Convertir el historial a un DataFrame
        df_total = pd.DataFrame(historical_data)

        # Crear gráfica lineal
        line_chart = alt.Chart(df_total).mark_line().encode(
            x='timer',
            y='total_cars',
            tooltip=['timer', 'total_cars']
        ).properties(
            title="Total de carros a lo largo del tiempo"
        )
        
        st.altair_chart(line_chart, use_container_width=True)

        time.sleep(0.2)
        st.rerun()
    else:
        st.warning("No se pudo obtener datos del servidor.")

def abrir_imagen_con_transparencia(path, size):
    try:
        imagen = Image.open(path)
        if imagen.mode != 'RGBA':
            imagen = imagen.convert('RGBA')
        imagen = imagen.resize(size, Image.LANCZOS)
        return imagen
    except FileNotFoundError:
        st.error(f"No se pudo encontrar el archivo: {path}")
        return None

def mostrar_control_semaforos():
    base_image_path = "calle.jpeg"
    semaforo_verde_path = "verde3.png"
    semaforo_rojo_path = "rojo4.png"

    semaforo_size = (50, 50)  

    base_image = abrir_imagen_con_transparencia(base_image_path, (1000, 800))
    semaforo_verde = abrir_imagen_con_transparencia(semaforo_verde_path, semaforo_size)
    semaforo_rojo = abrir_imagen_con_transparencia(semaforo_rojo_path, semaforo_size)

    if base_image is None or semaforo_verde is None or semaforo_rojo is None:
        return

    semaforo_positions = [(380, 400), (490, 600), (600, 380), (480, 200)]

    while True:
        datos = obtener_datos_trafico(url)
        if datos:
            traffic_light = datos.get("traffic_light", 0)
            semaforos = ["Semáforo 1", "Semáforo 2", "Semáforo 3", "Semáforo 4"]

            image_with_semaforos = base_image.copy()

            for i, pos in enumerate(semaforo_positions, start=1):
                if i == traffic_light:
                    image_with_semaforos.paste(semaforo_verde, pos, semaforo_verde)
                else:
                    image_with_semaforos.paste(semaforo_rojo, pos, semaforo_rojo)

            st.image(image_with_semaforos, use_column_width=True)
            time.sleep(0.2)
            st.rerun()
        else:
            st.warning("No se pudo obtener datos del servidor.")
            time.sleep(0.2)
            st.rerun()

pagina = st.sidebar.radio("Selecciona una página", ["Información de Tráfico", "Control de Semáforos"])

if pagina == "Información de Tráfico":
    st.header("Información de Tráfico")
    mostrar_informacion_trafico()
elif pagina == "Control de Semáforos":
    st.header("Control de Semáforos")
    mostrar_control_semaforos()
