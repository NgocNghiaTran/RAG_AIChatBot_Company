import json
import logging
from pathlib import Path
from datetime import datetime

from core.settings_loader import load_settings
from ingestion.helpers.make_metadata import make_metadata

settings = load_settings()
logger = logging.getLogger("ingestion")


def chunk_projects():
    """
    Chunk project information into multiple parts:
    1. overview_title - Project title
    2. overview_description - Project description
    3. overview_location_investor - Location and investor info
    4. overview_specs - Area and completion date
    5. overview_architecture_interior - Architecture and interior type
    """
    # Xây dựng đường dẫn file
    processed_dir = settings['data']['processed_dir']
    if isinstance(processed_dir, str):
        processed_dir = Path(processed_dir)
    file_path = processed_dir / 'projects.json'

    if not file_path.exists():
        logger.error(f'File not found: {file_path}')
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            projects = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f'Invalid JSON format: {e}')
        return []
    except Exception as e:
        logger.error(f'Error reading file: {e}')
        return []

    # Chuẩn hóa dữ liệu
    if isinstance(projects, dict):
        projects = [projects]

    if not isinstance(projects, list):
        logger.error('Projects data is not a list')
        return []

    if not projects:
        logger.warning('No projects found in the file')
        return []

    chunks = []

    for idx, project in enumerate(projects):
        if not isinstance(project, dict):
            logger.warning(f'Project at index {idx} is not a dict')
            continue

        # Trích xuất dữ liệu
        project_id = project.get('id')
        project_title = project.get('title', '').strip()
        project_slug = project.get('slug', '')
        project_investor = project.get('investor', '')
        project_location = project.get('location', '')
        project_description = project.get('description', '')
        project_thumbnail_url = project.get('thumbnailUrl', '')
        project_area = project.get('area', '')
        project_complete_date = project.get('completedDate', '')
        project_category = project.get('category', {})
        project_interior = project.get('interiorStyle', {})
        project_architecture_type = project.get('architectureType', {})

        # Base metadata
        base_metadata = {
            'type': 'project',
            'source': 'projects.json',
            'project_id': project_id,
            'project_title': project_title,
            'project_slug': project_slug,
            'created_at': datetime.utcnow().isoformat(),
            'language': 'vi',
        }

        # Priority cho các loại chunk
        chunk_priority = {
            'overview_title': 1,
            'overview_description': 2,
            'overview_architecture_interior': 3,
            'overview_location_investor': 4,
            'overview_specs': 5,
        }

        # Chunk 1: Title
        if project_title:
            chunks.append({
                'text': f'Tên dự án: {project_title}',
                'metadata': make_metadata(
                    base_metadata,
                    chunk_type='overview_title',
                    priority=chunk_priority['overview_title']
                )
            })

        # Chunk 2: Description
        if project_description:
            chunks.append({
                'text': f'Mô tả dự án {project_title}: {project_description}',
                'metadata': make_metadata(
                    base_metadata,
                    chunk_type='overview_description',
                    priority=chunk_priority['overview_description']
                )
            })

        # Chunk 3: Location + Investor
        if project_location or project_investor:
            spec_parts = []
            if project_location:
                spec_parts.append(f'Địa điểm: {project_location}')
            if project_investor:
                spec_parts.append(f'Chủ đầu tư: {project_investor}')

            chunks.append({
                'text': '\n'.join(spec_parts),
                'metadata': make_metadata(
                    base_metadata,
                    chunk_type='overview_location_investor',
                    priority=chunk_priority['overview_location_investor']
                )
            })

        # Chunk 4: Specs (area, completion date)
        if project_area or project_complete_date:
            spec_parts = []
            if project_area:
                spec_parts.append(f'Diện tích: {project_area}')
            if project_complete_date:
                spec_parts.append(f'Ngày hoàn thành: {project_complete_date}')

            chunks.append({
                'text': '\n'.join(spec_parts),
                'metadata': make_metadata(
                    base_metadata,
                    chunk_type='overview_specs',
                    priority=chunk_priority['overview_specs']
                )
            })

        # Chunk 5: Architecture + Interior type
        if project_architecture_type or project_interior:
            type_parts = []
            if project_architecture_type:
                arch_type_name = project_architecture_type.get('name', '')
                if arch_type_name:
                    type_parts.append(f'Loại kiến trúc: {arch_type_name}')
            if project_interior:
                inter_type_name = project_interior.get('name', '')
                if inter_type_name:
                    type_parts.append(f'Phong cách nội thất: {inter_type_name}')

            if type_parts:
                chunks.append({
                    'text': '\n'.join(type_parts),
                    'metadata': make_metadata(
                        base_metadata,
                        chunk_type='overview_architecture_interior',
                        priority=chunk_priority['overview_architecture_interior']
                    )
                })

    logger.info(f'Created {len(chunks)} chunks from {len(projects)} projects')
    return chunks


if __name__ == '__main__':
    chunks = chunk_projects()
    print(f'Total chunks: {len(chunks)}')
    for i, chunk in enumerate(chunks[:3]):
        print(f'\n--- Chunk {i+1} ---')
        print(f"Type: {chunk['metadata'].get('chunk_type')}")
        print(f"Priority: {chunk['metadata'].get('priority')}")
        print(f"Text: {chunk['text'][:100]}...")
