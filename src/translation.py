import time
import logging
from litellm import batch_completion
from config.config import Config

logger = logging.getLogger(__name__)

translation_prompt = "Translate the following text to Korean: {source}, Translation:"

def parse_litellm_response(response):
    """
    Parses a litellm batch_completion response into usable texts.

    Args:
        response (List[dict]): litellm's batch_completion response.

    Returns:
        tuple:
            - The raw response object
            - A list of extracted translation strings.
    """
    translations = []

    for res in response:
        # 확인 필요요
        try:
            content = res['choices'][0]['message']['content'].strip()
        except (KeyError, IndexError, TypeError) as e:
            translations.append("")  # Append empty string if error occurs
            continue
        translations.append(content.strip())

    return response, translations


def batch_translate(texts: list, model: str = None, max_retries: int = None, sleep_time: float = None) -> list:
    """
    litellm의 batch_completion을 사용해 텍스트 리스트를 배치 번역
    실패 시 최대 max_retries회 재시도
    """
    model = model or Config.MODEL_TRANSLATION
    max_retries = max_retries or Config.TRANSLATION_MAX_RETRIES
    sleep_time = sleep_time or Config.TRANSLATION_SLEEP_TIME

    queries = [[{'content': translation_prompt.format(source=text), "role": "user"}] for text in texts]

    for attempt in range(1, max_retries + 1):
        try:
            responses = batch_completion(model=model, messages=queries)
            _, translations = parse_litellm_response(responses)
            return translations
        except Exception as e:
            logger.warning(f"Batch translation attempt {attempt} failed: {e}")
            time.sleep(sleep_time)
    logger.error("Max retries reached for batch translation.")
    return texts  
