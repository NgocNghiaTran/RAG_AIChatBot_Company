import logging
import json
from datetime import datetime
from pathlib import Path

from core.logging_setup import setup_logging
from core.settings_loader import load_settings
from ingestion.helpers.make_metadata import make_metadata

setup_logging()
settings = load_settings()
logger = logging.getLogger('ingestion')


def chunk_company_info():
    """
    Chunk company information into multiple parts:
    1. overview - Company name, slogan, description
    2. contact_detail - Hotlines, emails, address, working hours, website
    3. social_links - Social media links
    4. additional_info - Employee count, total projects
    """
    # Xây dựng đường dẫn file
    processed_dir = settings['data']['processed_dir']
    if isinstance(processed_dir, str):
        processed_dir = Path(processed_dir)
    file_path = processed_dir / 'companyInfo.json'

    if not file_path.exists():
        logger.error(f'File not found: {file_path}')
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            company_info = json.load(file)
            logger.info(f'Successfully loaded data from {file_path}')
    except json.JSONDecodeError as e:
        logger.error(f'Invalid JSON format: {e}')
        return []
    except Exception as e:
        logger.error(f'Error reading file {file_path}: {e}')
        return []

    # Chuẩn hóa dữ liệu: dict -> list
    if isinstance(company_info, dict):
        company_info = [company_info]
    
    # Kiểm tra kiểu dữ liệu
    if not isinstance(company_info, list):
        logger.error('Company info data is not a list')
        return []
    
    if not company_info:
        logger.warning('No company info found in the data')
        return []

    chunks = []

    for idx, info in enumerate(company_info):
        if not isinstance(info, dict):
            logger.warning(f'Invalid company info at index {idx}')
            continue

        # Trích xuất dữ liệu
        company_id = info.get('id')
        company_name = info.get('companyName', '')
        company_slogan = info.get('companySlogan', '')
        company_description = info.get('companyDescription', '')
        company_hotlines = info.get('hotlines', [])
        company_emails = info.get('emails', [])
        company_main_address = info.get('mainAddress', '')
        company_working_hours = info.get('workingHours', '')
        company_website = info.get('website', '')
        company_social_links = info.get('socialLinks', {})
        company_employees = info.get('totalEmployees')
        company_total_projects = info.get('totalProjects')

        # Chuyển đổi social links dict thành text
        social_text = ''
        if isinstance(company_social_links, dict):
            social_items = [f'{key}: {value}' for key, value in company_social_links.items() if value]
            social_text = ', '.join(social_items)

        # Base metadata
        base_metadata = {
            'type': 'company_info',
            'source': 'companyInfo.json',
            'company_id': company_id,
            'company_name': company_name,
            'created_at': datetime.utcnow().isoformat(),
            'language': 'vi'
        }

        # Priority cho các loại chunk
        chunk_priority = {
            'overview': 1,
            'contact_detail': 2,
            'social_links': 3,
            'additional_info': 4
        }

        # Chunk 1: Overview (name, slogan, description)
        if company_name and company_description:
            overview_text = f'Tên công ty: {company_name}'
            if company_slogan:
                overview_text += f'\nKhẩu hiệu công ty: {company_slogan}'
            overview_text += f'\nMô tả công ty: {company_description}'
            
            chunks.append({
                'text': overview_text,
                'metadata': make_metadata(
                    base_metadata,
                    chunk_type='overview',
                    priority=chunk_priority['overview']
                )
            })

        # Chunk 2: Contact detail
        contact_parts = []
        if company_hotlines:
            hotline_text = ', '.join(company_hotlines) if isinstance(company_hotlines, list) else str(company_hotlines)
            contact_parts.append(f'Hotline: {hotline_text}')
        if company_emails:
            email_text = ', '.join(company_emails) if isinstance(company_emails, list) else str(company_emails)
            contact_parts.append(f'Email: {email_text}')
        if company_main_address:
            contact_parts.append(f'Địa chỉ: {company_main_address}')
        if company_working_hours:
            contact_parts.append(f'Giờ làm việc: {company_working_hours}')
        if company_website:
            contact_parts.append(f'Website: {company_website}')

        if contact_parts:
            chunks.append({
                'text': '\n'.join(contact_parts),
                'metadata': make_metadata(
                    base_metadata,
                    chunk_type='contact_detail',
                    priority=chunk_priority['contact_detail']
                )
            })

        # Chunk 3: Social links
        if social_text or company_website:
            social_parts = []
            if social_text:
                social_parts.append(f'Mạng xã hội: {social_text}')
            if company_website:
                social_parts.append(f'Website: {company_website}')
            
            chunks.append({
                'text': '\n'.join(social_parts),
                'metadata': make_metadata(
                    base_metadata,
                    chunk_type='social_links',
                    priority=chunk_priority['social_links']
                )
            })

        # Chunk 4: Additional info
        additional_parts = []
        if company_employees:
            additional_parts.append(f'Số nhân viên: {company_employees}')
        if company_total_projects:
            additional_parts.append(f'Tổng số dự án đã thực hiện: {company_total_projects}')

        if additional_parts:
            chunks.append({
                'text': '\n'.join(additional_parts),
                'metadata': make_metadata(
                    base_metadata,
                    chunk_type='additional_info',
                    priority=chunk_priority['additional_info']
                )
            })

    logger.info(f'Created {len(chunks)} chunks from company info')
    return chunks


if __name__ == '__main__':
    chunks = chunk_company_info()
    print(f'Total chunks: {len(chunks)}')
    for i, chunk in enumerate(chunks[:2]):
        print(f'\n--- Chunk {i+1} ---')
        print(f"Type: {chunk['metadata'].get('chunk_type')}")
        print(f"Priority: {chunk['metadata'].get('priority')}")
        print(f"Text: {chunk['text'][:100]}...")
