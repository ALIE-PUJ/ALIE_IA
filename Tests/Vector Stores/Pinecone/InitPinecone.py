import os
from pinecone import Pinecone, ServerlessSpec
from langchain_core.embeddings import FakeEmbeddings
import json

# Initialize Pinecone with API key
pc = Pinecone(
    api_key=os.environ.get("PINECONE_API_KEY")  # Set your Pinecone API key here
)

# Define index name
index_name = 'syllabus-index'

# Check if the index exists, if not, create it
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1024,  # Set dimension to 1024 to match embeddings size
        metric='cosine',  # Use cosine similarity
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'  # Set your preferred cloud region
        )
    )

# Connect to the index
index = pc.Index(index_name)

# Initialize fake embeddings generator with size 1024
embeddings = FakeEmbeddings(size=1024)

# Syllabus data
syllabus_data = {
    "version": "1.0",
    "last_updated": "2024-08-20",
    "title": "18_EstructurasDeDatos_4196",
    "description": "Syllabus de la materia 'EstructurasDeDatos' con código '4196'",
    "access_control": "privado",
    "content": {
        "Nombre Corto de la Asignatura": "Estructuras de Datos",
        "Nombre Largo de la Asignatura": "Estructuras de Datos",
        "Código de la asignatura": "4196",
        "Grado": "Pregrado",
        "Descripción": ("En la mayoría de los ambientes reales de desarrollo de software se procesan grandes "
                        "cantidades de información, que está representada en datos que tienen sentido, secuencia y "
                        "magnitud. Entonces, los correctos diseños e implementaciones de estructuras de datos y algoritmos "
                        "son vitales para el funcionamiento adecuado de los sistemas de cómputo y almacenamiento en la vida real."),
        "Número de Créditos": "3",
        "Condiciones Académicas de Inscripción (Pre-requisitos)": "Requisitos de inscripción: Programación avanzada /y/ (Lógica y Matemáticas Discretas /o/\nMatemáticas Discretas Sistemas /o/ Fundamentos de matemáticas II /o/ Matemáticas II /o/\n001297 Cálculo Integral)",
        "Período Académico de Vigencia": "2430",
        "Objetivos de Formación": ("1. Presentar los principios básicos de la complejidad algorítmica como criterio de calidad de algoritmos.\n"
                                   "2. Brindar al estudiante las herramientas básicas para el diseño de tipos abstractos de datos, particularmente en el diseño de estructuras contenedoras.\n"
                                   "3. Mostrar estrategias de implementación de estructuras de datos y algoritmos asociados a ellas en un lenguaje de programación (C++).\n"
                                   "4. Exponer al estudiante a ambientes de desarrollo de software donde se cubran las primeras etapas de dicha actividad: concepción, diseño, implementación y pruebas."),
        # Other fields omitted for brevity...
    }
}

# Generate embedding for the syllabus title
syllabus_embedding = embeddings.embed_documents([syllabus_data["content"]["Nombre Corto de la Asignatura"]])[0]

# Convert embedding to list of Python floats
syllabus_embedding = [float(value) for value in syllabus_embedding]

# Prepare metadata with "text" key and other necessary fields
metadata = {
    "version": syllabus_data["version"],
    "last_updated": syllabus_data["last_updated"],
    "title": syllabus_data["title"],
    "description": syllabus_data["description"],
    "access_control": syllabus_data["access_control"],
    # Store the text content of the syllabus under the "text" key
    "text": json.dumps(syllabus_data["content"])  # Convert the content to a JSON string
}

# Prepare the vector for upsertion with metadata containing the "text" key
to_upsert = [
    (
        syllabus_data["title"],  # The syllabus ID or title
        syllabus_embedding,      # The generated embedding
        metadata                 # The metadata with the "text" key
    )
]

# Upsert the syllabus data into the index
index.upsert(vectors=to_upsert)

print("Syllabus upserted successfully.")
