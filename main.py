# Entry point for the RAG application

from modules.rag_pipeline import RAGPipeline

def main():
    rag = RAGPipeline()
    rag.run()

if __name__ == "__main__":
    main()
