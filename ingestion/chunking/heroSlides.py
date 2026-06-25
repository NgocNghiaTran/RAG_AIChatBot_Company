import logging
import json
from pathlib import Path
from datetime import datetime

from core.settings_loader import load_settings
from ingestion.helpers.make_metadata import make_metadata

settings = load_settings()
logger = logging.getLogger('ingestion')


def chunk_hero_slides():
    """
    Chunk hero slide content.
    Each slide becomes a single chunk with title, subtitle, description.
    """
    # Xây dựng đường dẫn file
    processed_dir = settings['data']['processed_dir']
    if isinstance(processed_dir, str):
        processed_dir = Path(processed_dir)
    file_path = processed_dir / 'heroSlides.json'

    if not file_path.exists():
        logger.error(f'File not found: {file_path}')
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            hero_slides = json.load(file)
            logger.info(f'Successfully loaded {len(hero_slides) if isinstance(hero_slides, list) else 0} hero slides from {file_path}')
    except json.JSONDecodeError as e:
        logger.error(f'Invalid JSON format: {e}')
        return []
    except Exception as e:
        logger.error(f'Error reading file {file_path}: {e}')
        return []

    # Chuẩn hóa dữ liệu
    if isinstance(hero_slides, dict):
        hero_slides = [hero_slides]

    if not isinstance(hero_slides, list):
        logger.error(f'Hero slides is not a list: {file_path}')
        return []

    if not hero_slides:
        logger.warning('No hero slides found in the data')
        return []

    chunks = []

    for idx, slide in enumerate(hero_slides):
        if not isinstance(slide, dict):
            logger.warning(f'Invalid slide at index {idx}')
            continue

        # Trích xuất dữ liệu
        slide_title = slide.get('title', '')
        slide_subtitle = slide.get('subtitle', '')
        slide_description = slide.get('description', '')
        slide_image_url = slide.get('imageUrl', '')

        # Validate required fields
        if not slide_title or not isinstance(slide_title, str):
            logger.warning(f'Skipping slide at index {idx} due to missing or invalid title')
            continue

        if not slide_subtitle or not isinstance(slide_subtitle, str):
            logger.warning(f'Skipping slide at index {idx} due to missing or invalid subtitle')
            continue

        if not slide_description or not isinstance(slide_description, str):
            logger.warning(f'Skipping slide at index {idx} due to missing or invalid description')
            continue

        # Base metadata
        base_metadata = {
            'type': 'hero_slide',
            'source': 'heroSlides.json',
            'slide_index': idx,
            'created_at': datetime.utcnow().isoformat(),
            'language': 'vi'
        }

        # Text với đầy đủ thông tin
        text_parts = [
            f'Tiêu đề hero slide: {slide_title}',
            f'Phụ đề: {slide_subtitle}',
            f'Mô tả: {slide_description}'
        ]
        if slide_image_url:
            text_parts.append(f'URL hình ảnh: {slide_image_url}')

        chunks.append({
            'text': '\n'.join(text_parts),
            'metadata': make_metadata(
                base_metadata,
                chunk_type='definition',
                priority=5
            )
        })

    logger.info(f'Created {len(chunks)} chunks from hero slides')
    return chunks


if __name__ == '__main__':
    chunks = chunk_hero_slides()
    print(f'Total chunks: {len(chunks)}')
    for chunk in chunks:
        print(f'- {chunk["text"][:80]}...')
