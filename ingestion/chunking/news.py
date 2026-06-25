import json
import logging
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

from core.settings_loader import load_settings
from ingestion.helpers.make_metadata import make_metadata
from ingestion.helpers.split_paragraphs import split_paragraphs

settings = load_settings()
logger = logging.getLogger("ingestion")


def html_to_text(html: str) -> str:
    """Chuyển đổi HTML thành text thuần túy"""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def chunk_news():
    """
    Chunk news/articles into multiple parts:
    1. overview - Title, excerpt, thumbnail
    2. full_content - Content split into paragraphs
    3. category - News category
    """
    # Xây dựng đường dẫn file
    processed_dir = settings['data']['processed_dir']
    if isinstance(processed_dir, str):
        processed_dir = Path(processed_dir)
    file_path = processed_dir / 'news.json'

    if not file_path.exists():
        logger.error(f'File not found: {file_path}')
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            news = json.load(file)
    except json.JSONDecodeError as e:
        logger.error(f'Invalid JSON format: {e}')
        return []
    except Exception as e:
        logger.error(f'Error reading file: {e}')
        return []

    # Chuẩn hóa dữ liệu
    if isinstance(news, dict):
        news = [news]

    if not isinstance(news, list):
        logger.error('News data is not a list')
        return []

    if not news:
        logger.warning('No news found in the file')
        return []

    chunks = []

    for idx, news_item in enumerate(news):
        if not isinstance(news_item, dict):
            logger.warning(f'News item at index {idx} is not a dictionary')
            continue

        # Trích xuất dữ liệu
        news_id = news_item.get('id')
        news_title = news_item.get('title', '')
        news_slug = news_item.get('slug', '')
        news_excerpt = news_item.get('excerpt', '')
        news_content = news_item.get('content', '')
        news_thumbnail = news_item.get('thumbnailUrl', '')
        news_category = news_item.get('category', {})

        # Chuyển HTML thành text
        news_content_text = html_to_text(news_content)
        news_content_parts = split_paragraphs(news_content_text)

        # Base metadata
        base_metadata = {
            'type': 'news',
            'source': 'news.json',
            'news_id': news_id,
            'news_title': news_title,
            'news_slug': news_slug,
            'created_at': datetime.utcnow().isoformat(),
            'language': 'vi',
        }

        # Priority cho các loại chunk
        chunk_priority = {
            'overview': 1,
            'full_content': 2,
            'category': 3,
        }

        # Chunk 1: Overview (title + excerpt + thumbnail)
        if news_title:
            overview_parts = [f'Tựa đề tin tức: {news_title}']
            if news_excerpt:
                overview_parts.append(f'Tóm tắt: {news_excerpt}')
            if news_thumbnail:
                overview_parts.append(f'Hình ảnh đại diện: {news_thumbnail}')

            chunks.append({
                'text': '\n'.join(overview_parts),
                'metadata': make_metadata(
                    base_metadata,
                    chunk_type='overview',
                    priority=chunk_priority['overview']
                )
            })

        # Chunk 2: Full content (split into paragraphs)
        for i, part in enumerate(news_content_parts):
            chunks.append({
                'text': f'Nội dung tin tức "{news_title}": {part}',
                'metadata': make_metadata(
                    base_metadata,
                    chunk_type='full_content',
                    priority=chunk_priority['full_content'],
                    part_index=i
                )
            })

        # Chunk 3: Category
        if news_category:
            category_name = news_category.get('name', '')
            if category_name:
                chunks.append({
                    'text': f'Danh mục tin tức: {category_name}',
                    'metadata': make_metadata(
                        base_metadata,
                        chunk_type='category',
                        priority=chunk_priority['category']
                    )
                })

    logger.info(f'Created {len(chunks)} chunks from {len(news)} news items')
    return chunks


if __name__ == '__main__':
    chunks = chunk_news()
    print(f'Total chunks: {len(chunks)}')
    for i, chunk in enumerate(chunks[:3]):
        print(f'\n--- Chunk {i+1} ---')
        print(f"Type: {chunk['metadata'].get('chunk_type')}")
        print(f"Text: {chunk['text'][:100]}...")
