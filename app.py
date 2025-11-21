import streamlit as st
from docxtpl import DocxTemplate
from docx2python import docx2python
import io
import pathlib
import re

# --- Función auxiliar: extraer campos en el orden en que aparecen ---
def extract_fields_in_order(path_docx: pathlib.Path):
    text = docx2python(str(path_docx)).text
    campos = re.findall(r"{{\s*([A-Za-z0-9_]+)\s*}}", text)

    vistos = set()
    ordenados = []
    for c in campos:
        if c not in vistos:
            vistos.add(c)
            ordenados.append(c)
    return ordenados


# --- Diccionario para mostrar etiquetas más legibles ---
labels_amigables = {
    "anio": "Año",
    "nombre_cliente": "Nombre del cliente",
    "fecha": "Fecha",
    "destino": "Destino",
    "precio_total": "Precio total",
    "anio_vuelo": "Año del vuelo",
    "dia_vuelo": "Día del vuelo",
    "mes_vuelo": "Mes del vuelo",
    "precio_billetes": "Precio de los billetes",
    "SEGURO": "Seguro",
    "proveedores_servicios": "Proveedores de los servicios",
    "mayoristas_agencias": "Mayoristas de las agencias",
    "cod_postal": "Código postal",
}


# --- Carpeta donde buscar plantillas ---
BASE_DIR = pathlib.Path(__file__).parent
plantillas = list(BASE_DIR.glob("*.docx"))

if not plantillas:
    st.error("No se han encontrado archivos .docx junto a app.py.")
    st.stop()


label_to_path = {
    p.stem.replace("_", " ").title(): p
    for p in plantillas
}
etiquetas = sorted(label_to_path.keys())


# ---------------------- INTERFAZ ----------------------
st.title("🖨 Generador de Documentos - Ubadat Viajes")


# Selector de plantilla
choice_label = st.selectbox("Elige tu plantilla", etiquetas)
ruta_plantilla = label_to_path[choice_label]


# Cargar plantilla y extraer campos normales
tpl = DocxTemplate(str(ruta_plantilla))
campos = extract_fields_in_order(ruta_plantilla)


# ---------------------- FORMULARIO CAMPOS SIMPLES ----------------------
st.markdown("### Rellena los campos:")

context = {}
for c in campos:
    etiqueta = labels_amigables.get(c, c)
    context[c] = st.text_input(etiqueta)


# ---------------------- VIAJEROS DINÁMICOS ----------------------
st.markdown("## 👥 Viajeros adicionales")

num_viajeros = st.number_input(
    "Número de viajeros (sin incluir al cliente)", min_value=0, max_value=20, step=1
)

viajeros = []
for i in range(int(num_viajeros)):
    st.markdown(f"### Viajero {i+1}")
    nombre = st.text_input(f"Nombre Viajero {i+1}")
    apellido = st.text_input(f"Apellido Viajero {i+1}")
    viajeros.append({"nombre": nombre, "apellido": apellido})

context["viajeros"] = viajeros


# ---------------------- ALOJAMIENTOS DINÁMICOS ----------------------
st.markdown("## 🏨 Alojamientos")

num_aloj = st.number_input(
    "Número de alojamientos", min_value=0, max_value=20, step=1
)

alojamientos = []
for i in range(int(num_aloj)):
    st.markdown(f"### Alojamiento {i+1}")
    nombre = st.text_input(f"Nombre alojamiento {i+1}")
    direccion = st.text_input(f"Dirección alojamiento {i+1}")
    categoria = st.text_input(f"Categoría alojamiento {i+1}")
    regimen = st.text_input(f"Régimen de estancia {i+1}")
    tipo_hab = st.text_input(f"Tipo de habitación {i+1}")
    llegada = st.text_input(f"Fecha llegada {i+1}")
    salida = st.text_input(f"Fecha salida {i+1}")

    alojamientos.append({
        "nombre": nombre,
        "direccion": direccion,
        "categoria": categoria,
        "regimen": regimen,
        "tipo_habitacion": tipo_hab,
        "fecha_llegada": llegada,
        "fecha_salida": salida
    })

context["alojamientos"] = alojamientos


# ---------------------- GENERAR DOCUMENTO ----------------------
if st.button("🖨 Generar Documento"):
    tpl.render(context)
    buf = io.BytesIO()
    tpl.save(buf)
    buf.seek(0)

    st.download_button(
        "⬇ Descargar .docx",
        data=buf,
        file_name=f"{ruta_plantilla.stem}_rellenado.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )




