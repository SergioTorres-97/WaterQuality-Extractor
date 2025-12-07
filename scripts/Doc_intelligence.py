from main import *

ruta = r'D:\Maestria\IAAI\proyecto\datos'
pdfs = [f for f in os.listdir(ruta) if f.lower().endswith(".pdf")]

pipeline = AnalizadorAguaPipeline()

for pdf in pdfs:
    blob_name = pdf
    contenido = pipeline.extraer_datos_pdf(blob_name)
    datos = pipeline.procesar_con_ia(contenido)
    pipeline.guardar_en_cosmos(datos, blob_name)