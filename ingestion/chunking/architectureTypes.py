import json
import logging
from pathlib import Path
from datetime import datetime

from core.settings_loader import load_settings
from ingestion.helpers.make_metadata import make_metadata

settings = load_settings()
logger = logging.getLogger("ingestion")


def chunk_architecture_types():
    """
    Chunk architecture type definitions.
    Each type becomes a single chunk with name and description.
    """
    # Xây dựng đường dẫn file
    processed_dir = settings['data']['processed_dir']
    if isinstance(processed_dir, str):
        processed_dir = Path(processed_dir)
    file_path = processed_dir / 'architectureTypes.json'

    if not file_path.exists():
        logger.error(f'File not found: {file_path}')
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            architecture_types = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f'Invalid JSON format: {e}')
        return []
    except Exception as e:
        logger.error(f'Error reading file: {e}')
        return []

    # Chuẩn hóa dữ liệu
    if isinstance(architecture_types, dict):
        architecture_types = [architecture_types]

    if not isinstance(architecture_types, list):
        logger.error('Architecture types data is not a list')
        return []

    if not architecture_types:
        logger.warning('No architecture types found in the data')
        return []

    chunks = []

    for idx, architecture_type in enumerate(architecture_types):
        if not isinstance(architecture_type, dict):
            logger.warning(f'Invalid architecture type at index {idx}')
            continue

        # Trích xuất dữ liệu
        architecture_id = architecture_type.get('id')
        architecture_slug = architecture_type.get('slug', '')
        architecture_name = architecture_type.get('name', '')
        architecture_description = architecture_type.get('description', '')

        if not architecture_name:
            logger.warning(f'Architecture type at index {idx} has invalid or missing name')
            continue

        # Base metadata
        base_metadata = {
            'type': 'architecture_type',
            'source': 'architectureTypes.json',
            'architecture_type_id': architecture_id,
            'architecture_type_name': architecture_name,
            'architecture_type_slug': architecture_slug,
            'created_at': datetime.utcnow().isoformat(),
            'language': 'vi'
        }

        # Text với đầy đủ thông tin
        text_parts = [
            f'Tên phong cách kiến trúc: {architecture_name}',
        ]
        if architecture_description:
            text_parts.append(f'Mô tả: {architecture_description}')

        chunks.append({
            'text': '\n'.join(text_parts),
            'metadata': make_metadata(
                base_metadata,
                chunk_type='definition',
                priority=3
            )
        })

    logger.info(f'Created {len(chunks)} chunks from architecture types')
    return chunks


if __name__ == '__main__':
    chunks = chunk_architecture_types()
    print(f'Total chunks: {len(chunks)}')
    for chunk in chunks:
        print(f'- {chunk["text"][:80]}...')
