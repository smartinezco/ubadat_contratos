import streamlit as st
from docxtpl import DocxTemplate
import io
import pathlib

# Carpeta de plantillas
TEMPLATES_DIR = pathlib.Path(__file__).parent / "templates_word"
plantillas     = list(TEMPLATES_DIR.glob("*.docx"))

# Si no hay plantillas, mostramos error y detenemos
if not plantillas:
    st.error("La carpeta `templates_word/` está vacía. Añade ahí tus .docx y recarga.")
    st.stop()

# Mapea 'Contrato Viaje Combinado' -> Path('templates/contrato_viaje_combinado.docx')
label_to_path = {
    p.stem.replace("_", " ").title(): p
    for p in plantillas
}
etiquetas = list(label_to_path.keys())

st.title("🖨 Generador de Documentos - Ubadat Viajes")

# Desplegable con las etiquetas
choice_label = st.selectbox("Elige tu plantilla", etiquetas)

# Ruta real de la plantilla elegida
ruta_plantilla = label_to_path[choice_label]

# Carga y detecta marcadores {{ campo }}
tpl    = DocxTemplate(str(ruta_plantilla))
campos = tpl.get_undeclared_template_variables()
if not campos:
    st.error("No se han encontrado marcadores {{ campo }} en la plantilla.")
    st.stop()

# Formulario dinámico
st.markdown("Rellena los campos:")
context = {}
for c in sorted(campos):
    context[c] = st.text_input(c)

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
