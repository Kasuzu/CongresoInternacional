# database.py
import pandas as pd
import os

# Ruta al archivo CSV unificado
data_csv = os.path.join(os.path.dirname(__file__), 'datos_evento.csv')

# Función para crear el archivo CSV si no existe
def create_csv_file():
    if not os.path.exists(data_csv):
        df = pd.DataFrame(columns=['id', 'nombres', 'apellidos', 'identificacion', 'correo', 'celular',
                                   'institucion', 'profesion', 'fecha_nacimiento',
                                   'sesion1', 'sesion2', 'sesion3', 'sesion4'])
        df.to_csv(data_csv, index=False)

def registrar_asistente(data):
    df = pd.read_csv(data_csv, dtype={'identificacion': str})
    identificacion = str(data[2]).strip()
    if identificacion in df['identificacion'].values:
        return False, "Ya existe un asistente con esa identificación."
    if len(df) == 0:
        new_id = 1
    else:
        new_id = df['id'].max() + 1
    new_row = {'id': new_id, 'nombres': data[0], 'apellidos': data[1], 'identificacion': identificacion, 'correo': data[3],
               'celular': data[4], 'institucion': data[5], 'profesion': data[6], 'fecha_nacimiento': data[7],
               'sesion1': 'No asistió', 'sesion2': 'No asistió', 'sesion3': 'No asistió', 'sesion4': 'No asistió'}
    new_df = pd.DataFrame([new_row])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(data_csv, index=False)
    return True, "Asistente registrado exitosamente"

def buscar_asistente(search_input, search_by='identificacion'):
    df = pd.read_csv(data_csv, dtype={'identificacion': str})
    search_input = str(search_input).strip()
    if search_by == 'identificacion':
        df['identificacion'] = df['identificacion'].astype(str).str.strip()
        asistentes = df[df['identificacion'] == search_input]
    elif search_by == 'nombre':
        asistentes = df[df['nombres'].str.contains(search_input, case=False, na=False) | df['apellidos'].str.contains(search_input, case=False, na=False)]
    return asistentes

def registrar_asistencia(asistente_id, updated_attendance):
    df = pd.read_csv(data_csv)
    if asistente_id in df['id'].values:
        # Actualizar las columnas de asistencia con "Asistió" o "No asistió"
        df.loc[df['id'] == asistente_id, ['sesion1', 'sesion2', 'sesion3', 'sesion4']] = updated_attendance
        df.to_csv(data_csv, index=False)
        return True, "Asistencia registrada y actualizada en el archivo CSV"
    else:
        return False, "Asistente no encontrado"

def obtener_asistencia(asistente_id):
    df = pd.read_csv(data_csv)
    asistencia = df[df['id'] == asistente_id]
    if asistencia.empty:
        return None
    else:
        return asistencia.iloc[0][['sesion1', 'sesion2', 'sesion3', 'sesion4']]

def obtener_datos_completos():
    df = pd.read_csv(data_csv)
    return df
