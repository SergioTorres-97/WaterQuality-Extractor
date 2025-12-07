import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from openai import OpenAI
from azure.cosmos import CosmosClient, PartitionKey
import json
import uuid
from datetime import datetime, timedelta

load_dotenv()

class AnalizadorAguaPipeline:
    def __init__(self):
        print("🔧 Inicializando servicios Azure...")

        self.blob_service = BlobServiceClient.from_connection_string(
            os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        )
        self.container_name = os.getenv("BLOB_CONTAINER_NAME")

        self.doc_intelligence_client = DocumentAnalysisClient(
            endpoint=os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT"),
            credential=AzureKeyCredential(os.getenv("DOCUMENT_INTELLIGENCE_KEY"))
        )

        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        self.cosmos_client = CosmosClient(
            os.getenv("COSMOS_ENDPOINT"),
            os.getenv("COSMOS_KEY")
        )

        self._setup_cosmos()
        print("Servicios listos\n")

    #función para iniciar BD en cosmos
    def _setup_cosmos(self):
        database_name = os.getenv("COSMOS_DATABASE_NAME")
        container_name = os.getenv("COSMOS_CONTAINER_NAME")

        database = self.cosmos_client.create_database_if_not_exists(id=database_name)
        self.container = database.create_container_if_not_exists(
            id=container_name,
            partition_key=PartitionKey(path="/cliente"),
            offer_throughput=400
        )

    #función para subir pdf a blob
    def subir_pdf(self, archivo_local_path):
        blob_name = os.path.basename(archivo_local_path)

        print(f"Subiendo: {blob_name}")

        blob_client = self.blob_service.get_blob_client(
            container=self.container_name,
            blob=blob_name
        )

        with open(archivo_local_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        print(f"pdf subido correctamente")
        return blob_name

    #funcion para listar pdf en blob
    def listar_pdfs(self):
        """Listar todos los PDFs en Blob Storage"""
        container_client = self.blob_service.get_container_client(self.container_name)
        blob_list = container_client.list_blobs()

        pdfs = []
        for idx, blob in enumerate(blob_list, 1):
            print(f"{idx}. {blob.name} ({blob.size / 1024:.2f} KB)")
            pdfs.append(blob.name)
        return pdfs

    #función para extraer datos del pdf
    def extraer_datos_pdf(self, blob_name):
        """Extraer información del PDF con Document Intelligence"""
        print(f"Analizando: {blob_name}")

        # Generar SAS token
        blob_client = self.blob_service.get_blob_client(
            container=self.container_name,
            blob=blob_name
        )

        sas_token = generate_blob_sas(
            account_name=blob_client.account_name,
            container_name=self.container_name,
            blob_name=blob_name,
            account_key=self.blob_service.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )

        blob_url_con_sas = f"{blob_client.url}?{sas_token}"

        # Analizar documento
        poller = self.doc_intelligence_client.begin_analyze_document_from_url(
            "prebuilt-layout",
            blob_url_con_sas
        )
        result = poller.result()

        contenido = {"texto": "", "tablas": []}

        # Extraer texto
        for page in result.pages:
            for line in page.lines:
                contenido["texto"] += line.content + "\n"

        # Extraer tablas
        for table_idx, table in enumerate(result.tables):
            tabla_data = {
                "numero_tabla": table_idx + 1,
                "filas": table.row_count,
                "columnas": table.column_count,
                "celdas": []
            }

            for cell in table.cells:
                tabla_data["celdas"].append({
                    "fila": cell.row_index,
                    "columna": cell.column_index,
                    "contenido": cell.content
                })

            contenido["tablas"].append(tabla_data)

        print(f"Extraídas {len(result.pages)} páginas, {len(result.tables)} tablas\n")
        return contenido

    #función para procesar datos con IA
    def procesar_con_ia(self, contenido_extraido):
        """Usar OpenAI para estructurar los datos"""
        print(f"Procesando con IA...")

        parametros_buscar = {
            "DQO": ["DQO", "Demanda Química de Oxígeno", "COD"],
            "DBO5": ["DBO5", "Demanda Bioquímica de Oxígeno (5 días)", "BOD5", "DBO"],
            "SST": ["Sólidos Suspendidos Totales", "SST", "Total Suspended Solids", "TSS"],
            "Grasas_Aceites": ["Grasas y Aceites", "Oils and Grease", "GA", "Grasas", "Aceites"],
            "Ortofosfatos": ["Ortofosfatos", "PO4-P", "Fósforo Reactivo"],
            "Fosforo_Total": ["Fósforo Total", "Total Phosphorus", "Ptot", "P Total"],
            "Nitratos": ["Nitratos", "NO3-", "Nitrate", "NO3"],
            "Nitritos": ["Nitritos", "NO2-", "Nitrite", "NO2"],
            "N_Amoniacal": ["Nitrógeno Amoniacal", "NH4-N", "Ammonium", "NH4"],
            "N_Total": ["Nitrógeno Total", "Total Nitrogen", "Ntot", "N Total"],
            "N_Kjeldahl": ["Nitrógeno Kjeldahl", "TKN", "Total Kjeldahl Nitrogen"],
            "pH": ["pH", "Potencial de Hidrógeno"],
            "Coliformes_Totales": ["Coliformes Totales", "Total Coliforms"],
            "Coliformes_Fecales": ["Coliformes Fecales", "Coliformes Termotolerantes", "Fecal Coliforms"],
            "E_coli": ["Escherichia coli", "E. coli", "E coli"]
        }

        prompt = f"""
Eres un experto en análisis fisicoquímicos y microbiológicos de agua. Analiza el contenido extraído 
de un PDF de caracterización de agua y extrae la información en JSON.

IMPORTANTE: Un PDF puede tener MÚLTIPLES MONITOREOS. Separa cada uno.

EXTRAER:
- cliente: Nombre del solicitante
- tipo_agua: Tipo (residual, superficial, potable, etc.)
- tipo_muestreo: Tipo de muestreo
- fecha_muestreo: Fecha más antigua (YYYY-MM-DD)
- coordenadas: Coordenadas (mantener formato original)
- punto_muestreo: Identificador del punto

PARÁMETROS:
{json.dumps(parametros_buscar, ensure_ascii=False, indent=2)}

REGLAS VALORES:
- "< X" → valor: X/2, valor_original: "< X"
- "> X" → valor: X, valor_original: "> X"
- "25.5" → valor: 25.5, valor_original: "25.5"

CONTENIDO:
{json.dumps(contenido_extraido, ensure_ascii=False, indent=2)[:20000]}

JSON (sin markdown, sin backticks):
{{
  "monitoreos": [
    {{
      "cliente": "...",
      "tipo_agua": "...",
      "tipo_muestreo": "...",
      "fecha_muestreo": "YYYY-MM-DD",
      "coordenadas": "...",
      "punto_muestreo": "...",
      "parametros": [
        {{
          "parametro": "DQO",
          "valor": 125.5,
          "valor_original": "125.5",
          "unidad": "mg/L",
          "metodo": "...",
          "limite": "..."
        }}
      ],
      "observaciones": "..."
    }}
  ]
}}
"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Experto en análisis de agua. Responde solo JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=4000
        )

        resultado_texto = response.choices[0].message.content.strip()
        resultado_texto = resultado_texto.replace("```json", "").replace("```", "").strip()

        datos = json.loads(resultado_texto)
        print(f"{len(datos.get('monitoreos', []))} monitoreos encontrados\n")
        return datos

    #función para guardar en cosmos
    def guardar_en_cosmos(self, datos, pdf_nombre):
        """Guardar datos en Cosmos DB"""
        print(f"Guardando en Cosmos BD")

        monitoreos = datos.get('monitoreos', [])
        ids_guardados = []

        for idx, monitoreo in enumerate(monitoreos, 1):
            documento = {
                "id": str(uuid.uuid4()),
                "cliente": monitoreo.get('cliente', 'No especificado'),
                "tipo_agua": monitoreo.get('tipo_agua'),
                "tipo_muestreo": monitoreo.get('tipo_muestreo'),
                "fecha_muestreo": monitoreo.get('fecha_muestreo'),
                "coordenadas": monitoreo.get('coordenadas'),
                "punto_muestreo": monitoreo.get('punto_muestreo'),
                "parametros": monitoreo.get('parametros', []),
                "observaciones": monitoreo.get('observaciones'),
                "pdf_origen": pdf_nombre,
                "fecha_procesamiento": datetime.utcnow().isoformat(),
                "num_parametros": len(monitoreo.get('parametros', []))
            }

            self.container.create_item(body=documento)
            ids_guardados.append(documento['id'])
            print(f"Monitoreo {idx}: {documento['cliente']} - {documento['num_parametros']} parámetros")

        return ids_guardados

    #función para consultar en la BD cosmos
    def consultar_todos(self):
        """Ver todos los documentos en Cosmos DB"""
        query = "SELECT * FROM c ORDER BY c.fecha_procesamiento DESC"
        items = list(self.container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))

        print(f"Total: {len(items)} monitoreos\n")

        for idx, item in enumerate(items, 1):
            print(f"{'─' * 70}")
            print(f"📄 Monitoreo {idx}")
            print(f"ID: {item.get('id')}")
            print(f"Cliente: {item.get('cliente')}")
            print(f"Fecha: {item.get('fecha_muestreo')}")
            print(f"Tipo agua: {item.get('tipo_agua')}")
            print(f"Punto: {item.get('punto_muestreo')}")
            print(f"Coordenadas: {item.get('coordenadas')}")
            print(f"PDF: {item.get('pdf_origen')}")
            print(f"\nParámetros ({item.get('num_parametros')}):")
            for param in item.get('parametros', []):
                print(f"  • {param.get('parametro')}: {param.get('valor')} {param.get('unidad')}")
                if param.get('valor_original') != str(param.get('valor')):
                    print(f"    (original: {param.get('valor_original')})")

        return items

    #Función para consultar en lenguaje natural
    def consultar_lenguaje_natural(self, pregunta_usuario):

        print(f"CONSULTA: {pregunta_usuario}")

        ejemplo_documento = """
        {
          "id": "uuid",
          "cliente": "Nombre de la empresa",
          "tipo_agua": "residual/superficial/potable",
          "tipo_muestreo": "simple/compuesto",
          "fecha_muestreo": "YYYY-MM-DD",
          "coordenadas": "lat,lon o texto",
          "punto_muestreo": "identificador",
          "parametros": [
            {
              "parametro": "DQO/pH/SST/etc",
              "valor": número,
              "valor_original": "texto con símbolos",
              "unidad": "mg/L/unidades/etc",
              "metodo": "método usado",
              "limite": "límite normativo"
            }
          ],
          "observaciones": "texto",
          "pdf_origen": "nombre.pdf",
          "fecha_procesamiento": "timestamp",
          "num_parametros": número
        }
        """

        prompt_sql = f"""
    Eres un experto en Cosmos DB con API SQL. Genera una query SQL válida para Cosmos DB basada en la pregunta del usuario.

    ESTRUCTURA DE DOCUMENTOS EN COSMOS DB:
    {ejemplo_documento}

    REGLAS IMPORTANTES:
    1. La colección se llama "c" (FROM c)
    2. Para buscar en arrays usa JOIN:
       SELECT * FROM c JOIN p IN c.parametros WHERE p.parametro = "DQO"
    3. Para verificar existencia en array usa EXISTS:
       WHERE EXISTS(SELECT VALUE p FROM p IN c.parametros WHERE p.valor > 100)
    4. Los campos de texto son case-sensitive
    5. Usa CONTAINS() para búsquedas parciales: CONTAINS(c.cliente, "Empresa")
    6. Para fechas usa comparación de strings: c.fecha_muestreo > "2024-01-01"

    PREGUNTA DEL USUARIO:
    {pregunta_usuario}

    Responde SOLO con el SQL query, sin explicaciones, sin markdown, sin ```sql.
    Si la pregunta es ambigua, genera el query más razonable.
    """
        print("Generando query SQL...")

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages= [
                    {"role": "system",
                     "content": "Eres un experto en generar queries SQL para Cosmos DB. Respondes solo con SQL válido."},
                    {"role": "user", "content": prompt_sql}
                ],
                temperature=0.1,
                max_tokens=500
            )

            sql_query = response.choices[0].message.content.strip()

            # Limpiar posible markdown
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

            print(f"Query generado:\n{sql_query}\n")

        except Exception as e:
            print(f"Error generando query: {e}")
            return None

        print("Ejecutando en Cosmos DB...")

        try:
            items = list(self.container.query_items(
                query=sql_query,
                enable_cross_partition_query=True
            ))

            print(f"Encontrados {len(items)} resultados\n")

        except Exception as e:
            print(f"Error ejecutando query: {e}")
            print(f"   Query que falló: {sql_query}")
            return None

        # Paso 5: Si no hay resultados
        if len(items) == 0:
            print("ℹNo se encontraron resultados para esta consulta\n")
            return []

        # Paso 6: Formatear resultados con OpenAI
        print("📊 Formateando resultados...\n")

        # Preparar resumen de resultados (no enviar todo si son muchos)
        if len(items) <= 10:
            resultados_texto = json.dumps(items, ensure_ascii=False, indent=2)
        else:
            # Solo primeros 10 + resumen
            resultados_texto = json.dumps(items[:10], ensure_ascii=False, indent=2)
            resultados_texto += f"\n\n... y {len(items) - 10} resultados más"

        prompt_formato = f"""
    La pregunta del usuario fue: "{pregunta_usuario}"

    Los resultados de la base de datos son:
    {resultados_texto}

    Genera un resumen claro y conciso de los resultados en lenguaje natural.
    Incluye:
    - Cuántos resultados se encontraron
    - Información relevante de cada resultado
    - Si hay patrones o datos destacables

    Responde en tono profesional pero conversacional.
    """

        try:
            response_formato = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system",
                     "content": "Eres un asistente que explica resultados de bases de datos de forma clara."},
                    {"role": "user", "content": prompt_formato}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            respuesta_formateada = response_formato.choices[0].message.content

            print(f"{'─' * 70}")
            print(respuesta_formateada)
            print(f"{'─' * 70}\n")

        except Exception as e:
            print(f"No se pudo formatear respuesta: {e}")
            print("Mostrando resultados crudos:\n")
            for idx, item in enumerate(items[:5], 1):
                print(f"{idx}. Cliente: {item.get('cliente')}")
                print(f"   Fecha: {item.get('fecha_muestreo')}")
                print(f"   Parámetros: {item.get('num_parametros')}")
                print()

        return items