import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from openai import OpenAI
from azure.cosmos import CosmosClient

load_dotenv()

print("\n" + "="*60)
print("🔍 VERIFICANDO CREDENCIALES")
print("="*60 + "\n")

# 1. Blob Storage
try:
    blob_service = BlobServiceClient.from_connection_string(
        os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    )
    containers = list(blob_service.list_containers())
    print(f"✅ Blob Storage OK - {len(containers)} contenedores")
except Exception as e:
    print(f"❌ Blob Storage ERROR: {e}")

# 2. Document Intelligence
try:
    doc_client = DocumentAnalysisClient(
        endpoint=os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT"),
        credential=AzureKeyCredential(os.getenv("DOCUMENT_INTELLIGENCE_KEY"))
    )
    print("✅ Document Intelligence OK")
except Exception as e:
    print(f"❌ Document Intelligence ERROR: {e}")

# 3. OpenAI
try:
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "di hola"}],
        max_tokens=5
    )
    print("✅ OpenAI OK")
except Exception as e:
    print(f"❌ OpenAI ERROR: {e}")

# 4. Cosmos DB
try:
    cosmos_client = CosmosClient(
        os.getenv("COSMOS_ENDPOINT"),
        os.getenv("COSMOS_KEY")
    )
    databases = list(cosmos_client.list_databases())
    print(f"✅ Cosmos DB OK - {len(databases)} databases")
except Exception as e:
    print(f"❌ Cosmos DB ERROR: {e}")

print("\n" + "="*60)
print("✅ Si todo está OK, estás listo para procesar PDFs!")
print("="*60 + "\n")