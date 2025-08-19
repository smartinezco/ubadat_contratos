import streamlit as st
from docxtpl import DocxTemplate
from docx2python import docx2python
import io
import pathlib
import re

# --- Función auxiliar: extraer campos en el orden en que aparecen ---
def extract_fields_in_order(path_docx: pathlib.Path):
    text = docx2python(str(path_docx)).text
    # Busca {{ campo }} en orden de aparición
    campos = re.findall(r"{{\s*([A-Za-z0-9_]+)\s*}}", text)

    # Elimina duplicados manteniendo el orden
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
    # añade aquí todos los que necesites
}

# --- Carpeta donde buscar plantillas: la misma que app.py ---
BASE_DIR = pathlib.Path(__file__).parent
plantillas = list(BASE_DIR.glob("*.docx"))

if not plantillas:
    st.error("No se han encontrado archivos .docx junto a este app.py. "
             "Sube tus plantillas .docx a la raíz del repositorio y recarga.")
    st.stop()

# Mapea etiqueta legible -> ruta del archivo
label_to_path = {
    p.stem.replace("_", " ").title(): p
    for p in plantillas
}
etiquetas = sorted(label_to_path.keys())

st.title("🖨 Generador de Documentos - Ubadat Viajes")

# Selector de plantilla
choice_label = st.selectbox("Elige tu plantilla", etiquetas)
ruta_plantilla = label_to_path[choice_label]

# Carga la plantilla y extrae campos en orden
tpl = DocxTemplate(str(ruta_plantilla))
campos = extract_fields_in_order(ruta_plantilla)

if not campos:
    st.error("No se han encontrado marcadores {{ campo }} en la plantilla seleccionada.")
    st.stop()

# Formulario dinámico en el orden de aparición
st.markdown("### Rellena los campos:")
context = {}
for c in campos:
    etiqueta = labels_amigables.get(c, c)  # Usa traducción si existe
    context[c] = st.text_input(etiqueta)

# Generar y descargar
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

