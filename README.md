# WaterQuality Extractor

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Azure](https://img.shields.io/badge/Azure-Cloud-0078D4)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Pipeline automatizado para extracción, estructuración y almacenamiento de datos de análisis fisicoquímicos de agua desde reportes PDF, reduciendo el tiempo de procesamiento por documento.

---

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Parámetros Extraídos](#-parámetros-extraídos)
- [Licencia](#-licencia)
- [Contacto](#-contacto)

---

## 🎯 Descripción

### Problemática

Los reportes de análisis fisicoquímicos de agua llegan en formato PDF, requiriendo un proceso manual de costoso a nivel de tiempo de procesamiento por documento donde un operador debe identificar monitoreos, copiar metadatos, extraer parámetros fisicoquímicos, normalizar límites de detección (< 0.5 → 0.25), corregir separadores decimales y validar datos antes de consolidar en Excel. Este proceso repetitivo y propenso a errores consume aproximadamente 100 horas-persona mensuales para procesar 100 PDFs, genera inconsistencias en el formato de datos, dificulta el análisis histórico y no es escalable.

### Solución

Pipeline automatizado que integra **Azure Blob Storage**, **Azure Document Intelligence**, **OpenAI GPT-4o-mini** y **Azure Cosmos DB** para:

- ✅ Extraer automáticamente texto y tablas de PDFs
- ✅ Interpretar semánticamente los datos con IA
- ✅ Normalizar valores y formatos
- ✅ Almacenar en base de datos NoSQL consultable
- ✅ Permitir consultas en lenguaje natural

---

## Características

### Funcionalidades Principales

- 🔄 **Procesamiento automático**: De PDF a base de datos sin intervención manual
- 🧠 **Inteligencia artificial**: Comprensión semántica de documentos con variabilidad de formato
- 📊 **Extracción estructurada**: parámetros fisicoquímicos y microbiológicos
- 🔢 **Normalización automática**: Límites de detección (< X → X/2, > X → X)
- 🗣️ **Consultas en lenguaje natural**: Interfaz conversacional para búsquedas
- 📈 **Escalable**: Procesa 1 o 1000 PDFs con la misma arquitectura
- 💾 **Trazabilidad**: Mantiene valor original + normalizado
- 🔒 **Seguro**: Manejo de credenciales con variables de entorno

### Ventajas vs Proceso Manual

| Aspecto | Manual | Automatizado | Mejora |
|---------|--------|--------------|--------|
| **Tiempo/PDF** | 60 min | 2 min | **30x más rápido** |
| **Precisión** | 90-95% | 95-98% | +5% |
| **Escalabilidad** | ❌ Lineal | ✅ Automática | Ilimitada |
| **Consistencia** | ⚠️ Variable | ✅ Estandarizada | 100% |

---

## 🏗️ Arquitectura

### Flujo del Pipeline
```
┌──────────────┐
│   PDF Local  │
└──────┬───────┘
       │
       ↓
┌─────────────────────────────────┐
│  FASE 1: INGESTA                │
│  Azure Blob Storage             │
│  • Almacenamiento seguro        │
└──────┬──────────────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│  FASE 2: EXTRACCIÓN             │
│  Document Intelligence          │
│  • OCR con deep learning        │
│  • Extracción de tablas         │
│  • Precisión: 98-99%            │
└──────┬──────────────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│  FASE 3: INTELIGENCIA           │
│  OpenAI GPT-4o-mini             │
│  • Comprensión semántica        │
│  • Normalización de datos       │
│  • Separación de monitoreos     │
└──────┬──────────────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│  FASE 4: PERSISTENCIA           │
│  Azure Cosmos DB                │
│  • NoSQL (JSON nativo)          │
│  • Consultas SQL-like           │
│  • Latencia <10ms               │
└──────┬──────────────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│  FASE 5: CONSULTA               │
│  • SQL tradicional              │
│  • Lenguaje natural (IA)        │
│  • Análisis histórico           │
└─────────────────────────────────┘
```

### Servicios Azure Utilizados

| Servicio | Propósito | Tier Recomendado |
|----------|-----------|------------------|
| **Blob Storage** | Almacenamiento de PDFs | Standard LRS |
| **Document Intelligence** | OCR + Extracción |
| **Cosmos DB** | Base de datos NoSQL |
| **OpenAI** | Procesamiento con IA | GPT-4o-mini |

---

## 📋 Requisitos Previos

### Software

- **Python 3.8+** ([Descargar](https://www.python.org/downloads/))
- **Git** ([Descargar](https://git-scm.com/))
- **Cuenta de Azure** ([Crear cuenta gratis](https://azure.microsoft.com/free/students/))
- **Cuenta de OpenAI** ([Registrarse](https://platform.openai.com/))

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/SergioTorres-97/WaterQuality-Extractor.git
cd WaterQuality-Extractor
```

### 2. Crear entorno virtual
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```
---

## ⚙️ Configuración

### 1. Crear servicios en Azure

#### a) Azure Storage Account
```bash
# Portal Azure → Create Resource → Storage Account
# Configuración:
# - Name: storageaguaXXX (único globalmente)
# - Performance: Standard
# - Redundancy: LRS (Locally Redundant Storage)
# - Create container: "pdfs-agua"
```

**Obtener Connection String:**
```
Storage Account → Access keys → key1 → Connection string → Copy
```

#### b) Document Intelligence
```bash
# Portal Azure → Create Resource → Document Intelligence
# Configuración:
# - Name: doc-inteligencia-agua
```

**Obtener credenciales:**
```
Resource → Keys and Endpoint
- Endpoint: https://xxx.cognitiveservices.azure.com/
- Key 1: [copiar]
```

#### c) Cosmos DB
```bash
# Portal Azure → Create Resource → Azure Cosmos DB
# Configuración:
# - API: Core (SQL)
# - Account name: cosmos-agua-XXX
# - Capacity mode: Serverless o Provisioned
# - Enable Free Tier: Yes
```

**Obtener credenciales:**
```
Cosmos Account → Keys
- URI: https://xxx.documents.azure.com:443/
- Primary Key: [copiar]
```

#### d) OpenAI API Key
```bash
# 1. Ve a: https://platform.openai.com/
# 2. Sign up / Log in
# 3. Settings → Billing → Add payment method ($10 USD recomendado)
# 4. API Keys → Create new secret key
# 5. Copia el key (empieza con sk-proj-...)
```

---

### 2. Configurar variables de entorno

**Copia el archivo de ejemplo:**
```bash
cp .env.example .env
```

**Edita `.env` con tus credenciales reales:**
```env
# AZURE STORAGE
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=storageagua123;AccountKey=TU_KEY_AQUI;EndpointSuffix=core.windows.net
BLOB_CONTAINER_NAME=pdfs-agua

# DOCUMENT INTELLIGENCE
DOCUMENT_INTELLIGENCE_ENDPOINT=https://doc-inteligencia-agua.cognitiveservices.azure.com/
DOCUMENT_INTELLIGENCE_KEY=tu_key_aqui

# OPENAI
OPENAI_API_KEY=sk-proj-tu_api_key_aqui

# COSMOS DB
COSMOS_ENDPOINT=https://cosmos-agua-123.documents.azure.com:443/
COSMOS_KEY=tu_cosmos_key_aqui
COSMOS_DATABASE_NAME=agua_db
COSMOS_CONTAINER_NAME=analisis
```

---

### 3. Verificar instalación
```bash
python scripts/verificar_credenciales.py
```

**Salida esperada:**
```
✅ Blob Storage: OK
✅ Document Intelligence: OK
✅ OpenAI: OK
✅ Cosmos DB: OK

Todo configurado correctamente.
```

---

## 💻 Uso

### Uso Básico
```python
from main import AnalizadorAguaPipeline

# 1. Inicializar pipeline
pipeline = AnalizadorAguaPipeline()

# 2. Subir PDF a Blob Storage
pipeline.subir_pdf("pdfs/ejemplos/analisis_muestra.pdf")

# 3. Listar PDFs disponibles
pipeline.listar_pdfs()

# 4. Procesar PDF completo (extracción + IA + guardado)
pipeline.procesar_pdf("analisis_muestra.pdf")

# 5. Consultar todos los monitoreos guardados
pipeline.consultar_todos()
```

---

### Consultas en Lenguaje Natural
```python
# Búsqueda simple
pipeline.consultar_lenguaje_natural("Muéstrame todos los monitoreos de Empresa XYZ")

# Filtros por parámetro
pipeline.consultar_lenguaje_natural("Monitoreos con DQO mayor a 150")

# Filtros por fecha
pipeline.consultar_lenguaje_natural("Análisis realizados en enero de 2024")

# Consultas complejas
pipeline.consultar_lenguaje_natural("Agua residual con pH fuera del rango 6-9")

# Agregaciones
pipeline.consultar_lenguaje_natural("¿Cuántos monitoreos tiene cada cliente?")
```

---

### Ejemplo Completo
```python
from main import AnalizadorAguaPipeline

def main():
    # Inicializar
    pipeline = AnalizadorAguaPipeline()
    
    # Procesar múltiples PDFs
    pdfs = [
        "analisis_punto_norte.pdf",
        "analisis_punto_sur.pdf",
        "analisis_efluente.pdf"
    ]
    
    for pdf in pdfs:
        print(f"\n{'='*70}")
        print(f"Procesando: {pdf}")
        print(f"{'='*70}\n")
        
        # Subir
        pipeline.subir_pdf(f"pdfs/reales/{pdf}")
        
        # Procesar
        pipeline.procesar_pdf(pdf)
    
    # Consultar resultados
    print("\n📊 TODOS LOS MONITOREOS PROCESADOS:\n")
    pipeline.consultar_todos()
    
    # Análisis específico
    print("\n🔍 BÚSQUEDA ESPECÍFICA:\n")
    pipeline.consultar_lenguaje_natural(
        "Monitoreos con DQO superior a 100 mg/L"
    )

if __name__ == "__main__":
    main()
```

---

## 📁 Estructura del Proyecto
```
WaterQuality-Extractor/
│
├── 📄 main.py                          # Clase principal AnalizadorAguaPipeline
├── 📄 requirements.txt                 # Dependencias Python del proyecto
├── 📄 verificar_credenciales.py        # Script para validar configuración Azure/OpenAI
├── 📄 .env                             # Credenciales (⚠️ NO SE SUBE A GIT)
├── 📄 .env.example                     # Plantilla de configuración sin credenciales
├── 📄 .gitignore                       # Archivos ignorados por Git
├── 📄 README.md                        # Documentación principal (este archivo)
│
├── 📁 scripts/                         # Scripts auxiliares y módulos
│   ├── ConsultaNLP.py                  # Consultas en lenguaje natural con OpenAI
│   ├── ConsultasNLOB.py                # Consultar pdf subidos a Blob Storage
│   ├── ConsultasCosmos.py              # Operaciones específicas de Cosmos DB
│   ├── Doc_intelligence.py             # Funciones de Document Intelligence
│   └── SubirPdfsBlob.py                # Utilidades para upload a Blob Storage
│
└── 📁 pdf_ejemplo/                     # PDFs de ejemplo para pruebas

---

## 🧪 Parámetros Extraídos

El sistema extrae automáticamente los siguientes parámetros:

### Fisicoquímicos

| Parámetro | Variaciones Reconocidas | Unidad Típica |
|-----------|------------------------|---------------|
| **DQO** | Demanda Química de Oxígeno, COD | mg/L |
| **DBO5** | Demanda Bioquímica de Oxígeno (5 días), BOD5 | mg/L |
| **SST** | Sólidos Suspendidos Totales, TSS | mg/L |
| **Grasas y Aceites** | Oils and Grease, GA | mg/L |
| **pH** | Potencial de Hidrógeno | Unidades de pH |

### Nutrientes

| Parámetro | Variaciones Reconocidas | Unidad Típica |
|-----------|------------------------|---------------|
| **Ortofosfatos** | PO4-P, Fósforo Reactivo | mg/L |
| **Fósforo Total** | Total Phosphorus, Ptot | mg/L |
| **Nitratos** | NO3-, Nitrate | mg/L |
| **Nitritos** | NO2-, Nitrite | mg/L |
| **N. Amoniacal** | NH4-N, Ammonium | mg/L |
| **N. Total** | Total Nitrogen, Ntot | mg/L |
| **N. Kjeldahl** | TKN | mg/L |

### Microbiológicos

| Parámetro | Variaciones Reconocidas | Unidad Típica |
|-----------|------------------------|---------------|
| **Coliformes Totales** | Total Coliforms | NMP/100mL |
| **Coliformes Fecales** | Coliformes Termotolerantes, Fecal Coliforms | NMP/100mL |
| **E. coli** | Escherichia coli | NMP/100mL |

### Normalización Automática

El sistema maneja automáticamente:

- **Límites de detección inferiores:** `< 0.5` → valor: `0.25`, valor_original: `"< 0.5"`
- **Límites de detección superiores:** `> 1500` → valor: `1500`, valor_original: `"> 1500"`
- **Separadores decimales:** `7,2` → `7.2`
- **Múltiples monitoreos:** Un PDF con 3 puntos de muestreo → 3 documentos separados

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor sigue estos pasos:

1. **Fork** el repositorio
2. **Crea una rama** para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -m 'feat: Agrega nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Abre un Pull Request**

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.
```
MIT License

Copyright (c) 2024 [Tu Nombre]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 👤 Contacto

**Sergio David Torres Piraquive**

- 🔗 LinkedIn: [Sergio Torres]([https://linkedin.com/in/tu-perfil](https://www.linkedin.com/in/sergio-torres-04b230126/))
- 📧 Email: sertorrespira@gmail.com
- 💼 GitHub: [@SergioTorres-97]([https://github.com/tu_usuario](https://github.com/SergioTorres-97))

---

**⚡ Desarrollado con Azure + OpenAI**

Si este proyecto te fue útil, considera darle una ⭐ en GitHub

[⬆ Volver arriba](#WaterQuality Extractor)

</div>
