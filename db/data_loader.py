from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    Settings,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from pathlib import Path
import re, os
from dotenv import load_dotenv
load_dotenv()

PERSIST_DIR = "./storage/promotion"
document_path = Path("./data_pdf")

def normalize_vietnamese_text(text: str) -> str:
    text = text.replace("\n", ". ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

if os.path.exists(PERSIST_DIR):
    storage_context = StorageContext.from_defaults(
        persist_dir=PERSIST_DIR
    )
    vector_db = load_index_from_storage(storage_context)

else:
    documents = SimpleDirectoryReader(
        input_dir=document_path
    ).load_data()

    for doc in documents:
        doc.text_resource.text = normalize_vietnamese_text(
            doc.text_resource.text
        )

    parser = SentenceSplitter(
        chunk_size=500,
        chunk_overlap=80
    )
    nodes = parser.get_nodes_from_documents(documents)

    vector_db = VectorStoreIndex(nodes)
    vector_db.storage_context.persist(PERSIST_DIR)


# retriever = vector_db.as_retriever(similarity_top_k=5)
# nodes = retriever.retrieve("buffet Yatai 399k co nhung mon an nao")
# document_list = [node.text for node in nodes]

# print(document_list)