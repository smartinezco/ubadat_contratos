import streamlit as st
from docxtpl import DocxTemplate
from docx2python import docx2python
import io
import pathlib
import re

# --- Función auxiliar: extraer campos en orden ---
def extract_fields_in_order(path_docx):
    text = docx2python(path_docx).text
    # Busca {{ campo }} en orden de aparición
    campos = re.findall(r"{{\s*(\w+)\s*}}", text)

    # Eliminar duplicados pero mantener el orden
    campos_unicos = []
    for c in campos:
        if c not in campos_unicos:
            campos_unicos.append(c)
    return campos_unicos

# --- Carpeta de plantillas ---
TEMPLATES_DIR = pathlib.Path(__file__).parent / "templates_word"
plantillas     = list(TEMPLATES_DIR.glob("*.docx"))

if not plantillas:
    st.error("La carpeta `templates_word/` está vacía. Añade ahí tus .docx y recarga.")
    st.stop()

# --- Diccionario etiqueta -> ruta ---
label_to_path = {
    p.stem.replace("_", " ").title(): p
    for p in plantillas
}
etiquetas = list(label_to_path.keys())

st.title("🖨 Generador de Documentos - Ubadat Viajes")

# --- Selector de plantilla ---
choice_label   = st.selectbox("Elige tu plantilla", etiquetas)
ruta_plantilla = label_to_path[choice_label]

# --- Cargar plantilla y extraer campos ---
tpl    = DocxTemplate(str(ruta_plantilla))
campos = extract_fields_in_order(ruta_plantilla)

if not campos:
    st.error("No se han encontrado marcadores {{ campo }} en la plantilla.")
    st.stop()

# --- Formulario dinámico ---
st.markdown("### Rellena los campos:")
context = {}
for c in campos:
    context[c] = st.text_input(c)

# --- Generar y descargar ---
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
