import json
import logging
from pathlib import Path
from datetime import datetime

from core.settings_loader import load_settings
from ingestion.helpers.make_metadata import make_metadata

settings = load_settings()
logger = logging.getLogger("ingestion")


def chunk_news_categories():
    """
    Chunk news category definitions.
    Each category becomes a single chunk with definition text.
    """
    # Xây dựng đường dẫn file
    processed_dir = settings['data']['processed_dir']
    if isinstance(processed_dir, str):
        processed_dir = Path(processed_dir)
    file_path = processed_dir / 'newsCategories.json'

    if not file_path.exists():
        logger.error(f'File not found: {file_path}')
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            news_categories = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f'Invalid JSON format: {e}')
        return []
    except Exception as e:
        logger.error(f'Error reading file: {e}')
        return []

    # Chuẩn hóa dữ liệu
    if isinstance(news_categories, dict):
        news_categories = [news_categories]

    if not isinstance(news_categories, list):
        logger.error('News categories data is not a list')
        return []

    if not news_categories:
        logger.warning('No news categories found in the file')
        return []

    chunks = []

    for idx, category in enumerate(news_categories):
        if not isinstance(category, dict):
            logger.warning(f'Category at index {idx} is not a dict')
            continue

        # Trích xuất dữ liệu
        category_id = category.get('id')
        category_name = category.get('name', '')
        category_slug = category.get('slug', '')

        if not category_name:
            logger.warning(f'News category at index {idx} has invalid or missing name')
            continue

        # Base metadata
        base_metadata = {
            'type': 'news_category',
            'source': 'newsCategories.json',
            'news_category_id': category_id,
            'news_category_name': category_name,
            'news_category_slug': category_slug,
            'created_at': datetime.utcnow().isoformat(),
            'language': 'vi',
        }

        # Text với đầy đủ thông tin
        text = (
            f'Tên danh mục tin tức: {category_name}\n'
            f'Danh mục tin tức này được sử dụng để phân loại các bài viết liên quan đến {category_name}.'
        )

        chunks.append({
            'text': text,
            'metadata': make_metadata(
                base_metadata,
                chunk_type='definition',
                priority=3
            )
        })

    logger.info(f'Created {len(chunks)} chunks from news categories')
    return chunks


if __name__ == '__main__':
    chunks = chunk_news_categories()
    print(f'Total chunks: {len(chunks)}')
    for chunk in chunks:
        print(f'- {chunk["text"][:80]}...')
