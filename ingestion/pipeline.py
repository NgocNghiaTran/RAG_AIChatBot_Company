import logging

from ingestion.chunking.architectureTypes import chunk_architecture_types
from ingestion.chunking.companyInfo import chunk_company_info
from ingestion.chunking.heroSlides import chunk_hero_slides
from ingestion.chunking.InteriorStyles import chunk_interior_styles
from ingestion.chunking.newCategories import chunk_news_categories
from ingestion.chunking.news import chunk_news
from ingestion.chunking.projectCategories import chunk_project_categories
from ingestion.chunking.projects import chunk_projects
from core.logging_setup import setup_logging

from vectorstore.upsert import upsert_chunks

setup_logging()
logger = logging.getLogger("ingestion")

def _safe_extend(chunks_list: list, new_chunks):
    """Safely extend chunks list, handling None returns"""
    if new_chunks:
        chunks_list.extend(new_chunks)

def run_ingestion_pipeline():
    """
    Run the complete ingestion pipeline:
    1. Chunk all data sources
    2. Fit sparse embedder
    3. Build hybrid points (dense + sparse)
    4. Upsert to Qdrant
    """
    all_chunks = []
    
    # Chunk all data sources
    _safe_extend(all_chunks, chunk_architecture_types())
    _safe_extend(all_chunks, chunk_company_info())
    _safe_extend(all_chunks, chunk_interior_styles())
    _safe_extend(all_chunks, chunk_news_categories())
    _safe_extend(all_chunks, chunk_news())
    _safe_extend(all_chunks, chunk_project_categories())
    _safe_extend(all_chunks, chunk_projects())
    _safe_extend(all_chunks, chunk_hero_slides())
    
    if not all_chunks:
        logger.error("No chunks generated. Check data files and chunking functions.")
        return
    
    logger.info(f"Total chunks generated: {len(all_chunks)}")
    
    # Upsert to vector store
    upsert_chunks(all_chunks)
    logger.info(f"Successfully upserted {len(all_chunks)} chunks into the vector store.")
    
if __name__ == "__main__":
    run_ingestion_pipeline()