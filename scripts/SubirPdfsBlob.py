from main import *
from pathlib import Path

base_dir = Path(__file__).parent
ruta_pdf = base_dir/'pdf_ejemplo'

ruta = 'D:/Maestria/IAAI/proyecto/datos'
pdfs = [f for f in os.listdir(ruta) if f.lower().endswith(".pdf")]

pipeline = AnalizadorAguaPipeline()

for pdf in pdfs:
    pipeline.subir_pdf(ruta + f'/{pdf}')
