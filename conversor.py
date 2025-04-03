import streamlit as st
import os
import shutil
import zipfile
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from io import BytesIO

st.set_page_config(page_title="OCR em Lote", layout="centered")
st.title("🧠 OCR em Arquivos - Conversão em Lote para PDF com Texto")

input_path = st.text_input("📂 Digite o caminho da pasta com os arquivos (em ambiente Docker):", value="./input")

if input_path and os.path.isdir(input_path):
    files = list(Path(input_path).glob("*"))
    st.success(f"✅ {len(files)} arquivos encontrados.")

    if st.button("🚀 Iniciar conversão com OCR"):
        output_dir = Path("arquivos_convertidos")
        shutil.rmtree(output_dir, ignore_errors=True)
        output_dir.mkdir(exist_ok=True)

        for i, file in enumerate(files):
            if file.suffix.lower() not in [".pdf", ".jpg", ".jpeg", ".png", ".tiff"]:
                continue

            try:
                if file.suffix.lower() == ".pdf":
                    images = convert_from_path(str(file))
                else:
                    images = [Image.open(file)]

                pdf_pages = []
                for img in images:
                    pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
                    pdf_pages.append(BytesIO(pdf_bytes))

                output_path = output_dir / f"{file.stem}_ocr.pdf"
                with open(output_path, "wb") as f_out:
                    for page in pdf_pages:
                        f_out.write(page.getbuffer())

                st.write(f"✔️ {file.name} convertido com sucesso.")

            except Exception as e:
                st.error(f"Erro ao processar {file.name}: {e}")

        zip_path = "arquivos_convertidos.zip"
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file in output_dir.glob("*.pdf"):
                zipf.write(file, arcname=file.name)

        with open(zip_path, "rb") as f:
            st.success("✅ Conversão concluída!")
            st.download_button("📦 Baixar arquivos convertidos (ZIP)", data=f, file_name="arquivos_convertidos.zip", mime="application/zip")

else:
    if input_path:
        st.error("❌ Caminho inválido.")
