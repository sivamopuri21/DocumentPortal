from pathlib import Path
import sys
from src.multi_document_chat.data_ingestion import DocumentIngestor
from src.multi_document_chat.retrieval import ConversationalRAG
def test_documeny_ingestion_and_rag():
    try:
        test_files =[
            "data\\multi_doc_chat\\Dec-2021.pdf",
            "data\\multi_doc_chat\\GenAI Interview Question.docx",
            "data\\multi_doc_chat\\Info_About_Project.txt",
            "data\\multi_doc_chat\\NIPS-2017-attention-is-all-you-need-Paper.pdf"
        ]

        uploaded_files = []
        for file_path in test_files:
            if Path(file_path).exists():
                uploaded_files.append(open(file_path, "rb"))
            else:
                print(f"File not found: {file_path}")
        
        if not uploaded_files:
            print("No files uploaded.")
            sys.exit(1)

        ingestor = DocumentIngestor()
        retriever = ingestor.ingest_documents(uploaded_files)
        for f in uploaded_files:
            f.close()

        session_id ="test_multi_doc_chat"
        rag = ConversationalRAG(session_id, retriever)
        question = "Whose payslip is this ??"
        answer = rag.invoke(question)
        print("\nQuestion: ",question)
        print("Answer",answer)
        

    except Exception as e:
        print(e)
        return False
    
if __name__ == "__main__":
    test_documeny_ingestion_and_rag()