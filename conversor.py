import streamlit as st
import os
import shutil
import zipfile
from pdf2image import convert_from_bytes
from PIL import Image
import pytesseract
from io import BytesIO

st.set_page_config(page_title="OCR de PDFs", layout="centered")
st.title("🧠 Conversão OCR de PDFs ou imagens")

uploaded_files = st.file_uploader("📂 Envie seus arquivos PDF ou imagem", type=["pdf", "jpg", "jpeg", "png", "tiff"], accept_multiple_files=True)

if uploaded_files:
    if st.button("🚀 Iniciar conversão com OCR"):
        output_dir = "arquivos_convertidos"
        shutil.rmtree(output_dir, ignore_errors=True)
        os.makedirs(output_dir, exist_ok=True)

        for uploaded_file in uploaded_files:
            file_bytes = uploaded_file.read()
            file_name = uploaded_file.name

            try:
                if file_name.endswith(".pdf"):
                    images = convert_from_bytes(file_bytes)
                else:
                    images = [Image.open(BytesIO(file_bytes))]

                pdf_pages = []
                for img in images:
                    pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
                    pdf_pages.append(BytesIO(pdf_bytes))

                output_path = os.path.join(output_dir, f"{Path(file_name).stem}_ocr.pdf")
                with open(output_path, "wb") as f_out:
                    for page in pdf_pages:
                        f_out.write(page.getbuffer())

                st.write(f"✔️ {file_name} convertido com sucesso.")

            except Exception as e:
                st.error(f"Erro ao processar {file_name}: {e}")

        # Compactar em ZIP
        zip_path = "arquivos_convertidos.zip"
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file in os.listdir(output_dir):
                zipf.write(os.path.join(output_dir, file), arcname=file)

        with open(zip_path, "rb") as f:
            st.success("✅ Conversão concluída!")
            st.download_button("📦 Baixar arquivos convertidos (ZIP)", data=f, file_name="arquivos_convertidos.zip", mime="application/zip")
