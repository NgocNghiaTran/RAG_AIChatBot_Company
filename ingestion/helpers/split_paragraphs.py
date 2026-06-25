import logging

logger = logging.getLogger("ingestion")

def split_paragraphs(text: str, max_len: int = 400):
    if not text:
        logger.warning(f'Empty text provided to split paragraph')
        return []

    sentences = text.split('. ')
    out = [] # List cac chunk
    buff = '' #buffer ghep cac doan nho

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            logger.warning(f'Empty sentence after stripping')
            continue

        while len(sentence) > max_len:
            cut_dot = sentence.rfind('. ',0,max_len)# tim dau cham
            if cut_dot == -1:
                cut_dot = max_len

            chunk = sentence[:cut_dot].strip() #Xóa khoảng trắng cuar chunk
            if chunk:
                out.append(chunk)

            sentence = sentence[cut_dot:].strip()

        if len(buff) + len(sentence) + 2 <= max_len: # +2 la vi de tinh dau '. '
            buff += sentence + '. '
        else:
            out.append(buff.strip())
            buff = sentence + '. '
    if buff:# check sau khi tao ra cac chunk xong van can buff thi cho vo out coi nhu 1 chunk cuoi luon
        out.append(buff.strip())
    return  out