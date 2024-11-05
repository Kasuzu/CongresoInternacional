import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import emoji
import base64
from datetime import date
import os

# Importar las funciones de database.py
from database import (
    create_csv_file,
    registrar_asistente,
    buscar_asistente,
    registrar_asistencia,
    obtener_asistencia,
    obtener_datos_completos,
    data_csv
)

# Función para agregar imagen de fondo desde un archivo local con manejo de error
def add_bg_from_local(image_file):
    try:
        with open(image_file, "rb") as image:
            encoded = base64.b64encode(image.read()).decode()
        css = f"""
        <style>
        .stApp {{
            background-image: url(data:image/jpg;base64,{encoded});
            background-size: cover;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("El archivo de fondo no se encontró. Por favor, verifica el nombre y la ubicación.")

# Función para generar la escarapela personalizada
def generar_escarapela(nombre, cedula):
    # Ruta de la imagen base de la escarapela
    base_path = 'escarapela.jpg'  # Cambia esta ruta si es necesario para la imagen base actualizada
    img = Image.open(base_path)

    # Crear un objeto de dibujo
    draw = ImageDraw.Draw(img)

    # Definir la fuente y el tamaño del texto
    font_path = "DejaVuSans-Bold.ttf"  # Cambia esta ruta si es necesario
    font = ImageFont.truetype(font_path, 30)  # Ajustar tamaño según la necesidad

    # Convertir el nombre y la cédula a mayúsculas y definir el color negro
    nombre_texto = nombre.upper()
    cedula_texto = f"C.C: {cedula}".upper()
    color_texto = (0, 0, 0)  # Negro

    # Ajustar las posiciones para alinear el texto en las líneas blancas
    nombre_pos = (180, 490)  # Ajusta esta posición para que el texto esté en la línea blanca de "Nombre y apellido"
    cedula_pos = (180, 680)  # Ajusta esta posición para que el texto esté en la línea blanca de "C.C."

    # Escribir el nombre y la cédula en la imagen
    draw.text(nombre_pos, nombre_texto, fill=color_texto, font=font)
    draw.text(cedula_pos, cedula_texto, fill=color_texto, font=font)

    # Retornar la imagen generada
    return img

# Mostrar la escarapela virtual en Streamlit
def mostrar_escarapela_virtual():
    st.subheader("Escarapela Virtual")
    identificacion = st.text_input("Ingrese su identificación para buscar")

    if st.button("Buscar"):
        # Buscar en el CSV usando la identificación
        asistentes = buscar_asistente(identificacion, 'identificacion')
        if not asistentes.empty:
            asistente = asistentes.iloc[0]
            nombre = f"{asistente['nombres']} {asistente['apellidos']}"
            cedula = asistente['identificacion']
            escarapela = generar_escarapela(nombre, cedula)

            # Mostrar la escarapela generada
            st.image(escarapela, caption="Escarapela generada")

            # Botón para descargar la escarapela como JPG
            escarapela_bytes = escarapela.convert("RGB")
            with open("escarapela_generada.jpg", "wb") as f:
                escarapela_bytes.save(f, format="JPEG")
            with open("escarapela_generada.jpg", "rb") as f:
                st.download_button(
                    label="Descargar Escarapela",
                    data=f,
                    file_name="escarapela.jpg",
                    mime="image/jpeg"
                )
        else:
            st.warning("Asistente no encontrado")

# Función para la autenticación
def autenticar(usuario_input, password_input):
    usuario_correcto = "CongresoIn2025"
    password_correcta = "Paz2025"
    return usuario_input == usuario_correcto and password_input == password_correcta

# Interfaz de Streamlit
def main():
    # Crear archivo CSV si no existe
    create_csv_file()

    add_bg_from_local('fondo.jpg')
    st.image('banner.jpg', use_column_width=True)

    st.title(emoji.emojize(":star: Sistema de Registro y Asistencia al Evento :star:"))
    menu = ["Registro del Asistente", "Ver Escarapela Virtual", "Asistencia al Evento", "Descargar Base de Datos"]
    choice = st.sidebar.selectbox("Seleccione una opción", menu)

    if choice == "Registro del Asistente":
        st.subheader("Registro del Asistente")
        with st.form(key='registro_form'):
            nombres = st.text_input("Nombres")
            apellidos = st.text_input("Apellidos")
            identificacion = st.text_input("Cédula o Documento de Identificación")
            correo = st.text_input("Correo Electrónico")
            celular = st.text_input("Número de Celular")
            institucion = st.text_input("Universidad, Institución o Ente")
            profesion = st.text_input("Profesión")
            fecha_nacimiento = st.date_input(
                "Fecha de Nacimiento",
                value=date(2000, 1, 1),
                min_value=date(1950, 1, 1),
                max_value=date(2024, 12, 31)
            )
            submit_button = st.form_submit_button(label='Registrar')

        if submit_button:
            data = (nombres, apellidos, identificacion, correo, celular, institucion, profesion, fecha_nacimiento.strftime("%Y-%m-%d"))
            success, message = registrar_asistente(data)
            if success:
                st.success(message)
            else:
                st.error(message)

    elif choice == "Ver Escarapela Virtual":
        mostrar_escarapela_virtual()

    elif choice == "Asistencia al Evento":
        st.subheader("Registro de Asistencia")

        if 'autenticado' not in st.session_state:
            st.session_state['autenticado'] = False

        if not st.session_state['autenticado']:
            usuario_input = st.text_input("Usuario")
            password_input = st.text_input("Contraseña", type='password')
            if st.button("Iniciar Sesión"):
                if autenticar(usuario_input, password_input):
                    st.session_state['autenticado'] = True
                    st.success("Autenticación exitosa")
                else:
                    st.error("Usuario o contraseña incorrectos")
        else:
            if 'asistente' not in st.session_state:
                search_option = st.selectbox('Buscar por', ['Identificación', 'Nombre'])
                search_input = st.text_input(f'Ingrese la {search_option.lower()} del asistente').strip()

                if st.button('Buscar Asistente'):
                    if search_option == 'Identificación':
                        asistentes = buscar_asistente(search_input, 'identificacion')
                    else:
                        asistentes = buscar_asistente(search_input, 'nombre')
                    if not asistentes.empty:
                        st.session_state['asistente'] = asistentes.iloc[0]
                        st.session_state['attendance_updated'] = False
                    else:
                        st.warning("Asistente no encontrado")

            if 'asistente' in st.session_state:
                asistente = st.session_state['asistente']
                st.write(f"**Asistente:** {asistente['nombres']} {asistente['apellidos']}")

                # Obtener asistencia actual
                asistencia = obtener_asistencia(asistente['id'])
                sessions = ['Sesión 6 de noviembre - mañana', 'Sesión 6 de noviembre - tarde', 'Sesión 7 de noviembre - mañana', 'Sesión 7 de noviembre - tarde']
                attendance = [asistencia['sesion1'], asistencia['sesion2'], asistencia['sesion3'], asistencia['sesion4']] if asistencia is not None else ['No asistió'] * 4

                # Crear formulario con selección de asistencia
                with st.form(key='asistencia_form'):
                    st.write("### Registro de Asistencia")
                    updated_attendance = []
                    for i, session in enumerate(sessions):
                        selected_status = st.selectbox(f"{session}", ["Asistió", "No asistió"], index=0 if attendance[i] == "Asistió" else 1)
                        updated_attendance.append(selected_status)
                    col1, col2 = st.columns(2)
                    submit_asistencia = col1.form_submit_button(label='Registrar Asistencia')
                    buscar_otro = col2.form_submit_button(label='Buscar otro asistente')

                if submit_asistencia:
                    success, message = registrar_asistencia(asistente['id'], updated_attendance)
                    if success:
                        st.session_state['attendance_updated'] = True
                        st.success("Asistencia actualizada y guardada en el CSV")
                    else:
                        st.error(message)

                # Botón para buscar otro asistente
                if buscar_otro:
                    st.session_state.pop('asistente', None)  # Limpiar asistente para volver a buscar
                    st.session_state['attendance_updated'] = False  # Reiniciar el indicador de actualización

                if st.session_state.get('attendance_updated', False):
                    st.session_state.pop('asistente')  # Limpiar asistente de la sesión para volver a buscar

    elif choice == "Descargar Base de Datos":
        st.subheader("Descargar Base de Datos de Asistentes y Asistencia")
        if 'autenticado_admin' not in st.session_state:
            st.session_state['autenticado_admin'] = False

        if not st.session_state['autenticado_admin']:
            usuario_input = st.text_input("Usuario")
            password_input = st.text_input("Contraseña", type='password')
            if st.button("Iniciar Sesión"):
                if autenticar(usuario_input, password_input):
                    st.session_state['autenticado_admin'] = True
                    st.success("Autenticación exitosa")
                else:
                    st.error("Usuario o contraseña incorrectos")
        else:
            df = obtener_datos_completos()
            columnas = ['id', 'nombres', 'apellidos', 'identificacion', 'correo', 'celular', 'institucion', 'profesion', 'fecha_nacimiento',
                        'sesion1', 'sesion2', 'sesion3', 'sesion4']
            df = df[columnas]
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar base de datos en CSV",
                data=csv,
                file_name='base_de_datos.csv',
                mime='text/csv',
            )
            st.success("Base de datos actualizada lista para descargar")

if __name__ == '__main__':
    main()
