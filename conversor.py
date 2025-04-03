import streamlit as st
import os
import shutil
import zipfile
import time
from pdf2image import convert_from_bytes
from PIL import Image
import pytesseract
from io import BytesIO
from pathlib import Path

st.set_page_config(page_title="OCR de PDFs", layout="centered")
st.title("🧠 Conversor OCR de PDFs e Imagens")

# Upload dos arquivos
uploaded_files = st.file_uploader(
    "📂 Envie os arquivos PDF ou imagem para conversão (você pode selecionar múltiplos):",
    type=["pdf", "jpg", "jpeg", "png", "tiff"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("🚀 Iniciar conversão com OCR"):
        output_dir = "arquivos_convertidos"
        shutil.rmtree(output_dir, ignore_errors=True)
        os.makedirs(output_dir, exist_ok=True)

        total_files = len(uploaded_files)
        progress_bar = st.progress(0)
        status_text = st.empty()
        start_time = time.time()

        for i, uploaded_file in enumerate(uploaded_files):
            file_bytes = uploaded_file.read()
            file_name = uploaded_file.name

            try:
                # Converte o arquivo
                if file_name.lower().endswith(".pdf"):
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
                st.error(f"❌ Erro ao processar {file_name}: {e}")

            # Progresso e tempo estimado
            elapsed_time = time.time() - start_time
            progress = (i + 1) / total_files
            avg_time = elapsed_time / (i + 1)
            remaining_time = avg_time * (total_files - (i + 1))

            progress_bar.progress(progress)
            status_text.text(
                f"⏳ Progresso: {int(progress * 100)}% | Tempo estimado restante: {int(remaining_time)} segundos"
            )

        # Verificar se os arquivos foram realmente gerados
        st.subheader("📂 Arquivos convertidos gerados:")
        converted_files = os.listdir(output_dir)
        if not converted_files:
            st.error("❌ Nenhum arquivo convertido foi encontrado. Verifique se a conversão foi feita corretamente.")
            st.stop()

        for file in converted_files:
            st.code(file)

        # Compacta os arquivos convertidos
        zip_path = "arquivos_convertidos.zip"
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file in converted_files:
                full_path = os.path.join(output_dir, file)
                zipf.write(full_path, arcname=file)

        # Garante leitura correta do zip
        if os.path.exists(zip_path):
            with open(zip_path, "rb") as f:
                zip_bytes = f.read()
                st.success("✅ Conversão finalizada!")
                st.download_button(
                    label="📦 Baixar arquivos convertidos (ZIP)",
                    data=zip_bytes,
                    file_name="arquivos_convertidos.zip",
                    mime="application/zip"
                )
        else:
            st.error("❌ O arquivo ZIP não foi encontrado.")
