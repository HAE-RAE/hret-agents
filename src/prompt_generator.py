# src/prompt_generator.py
from smolagents import tool, OpenAIServerModel
import logging
import pandas as pd
from smolagents import tool
from config.config import Config

logger = logging.getLogger(__name__)

@tool
def generate_guide_prompt(markdown_table: str) -> str:
    """
    base.py와 __init__.py 코드, 그리고 번역된 데이터셋의 상위 5개 행(마크다운 테이블)을 포함한
    guide prompt를 생성합니다.
    """
    base_code = r'''### base.py

from typing import List, Dict, Any, Optional

class BaseDataset:
    """
    Abstract base class that all dataset classes should inherit from.
    
    Purpose:
      1) To provide a consistent interface expected by the evaluation pipeline.
      2) To allow easy customization of dataset-specific loading/preprocessing logic.
      
    Required Method:
      - load(): Loads the data and returns a list of dictionaries in the format [{"input":..., "reference":...}, ...].
    """

    def __init__(self, dataset_name: str, split: str = "test", subset: str = None, base_prompt_template : str = None, **kwargs):
        self.dataset_name = dataset_name
        self.split = split
        self.subset = subset
        self.base_prompt_template = base_prompt_template
        self.kwargs = kwargs

    def load(self) -> List[Dict[str, Any]]:
        raise NotImplementedError("Subclasses must implement load().")
'''

    init_code = r'''### __init__.py

from typing import Dict, Type
from .base import BaseDataset

DATASET_REGISTRY: Dict[str, Type[BaseDataset]] = {}

def register_dataset(name: str):
    def decorator(cls: Type[BaseDataset]):
        if name in DATASET_REGISTRY:
            raise ValueError(f"Dataset '{name}' already registered.")
        DATASET_REGISTRY[name] = cls
        return cls
    return decorator

def load_datasets(name: str, split: str = "test", **kwargs) -> BaseDataset:
    if name not in DATASET_REGISTRY:
        raise ValueError(f"Unknown dataset: {name}. Please register it in DATASET_REGISTRY.")
    dataset_class = DATASET_REGISTRY[name]
    return dataset_class(split=split, **kwargs)
'''

    prompt = f'''"""
아래는 haerae-evaluation-toolkit의 dataset 모듈을 개발하기 위한 가이드입니다.

상속해야 하는 base 클래스와 __init__.py의 내용은 아래와 같습니다.

{base_code}

{init_code}

번역된 데이터셋의 구조 및 상위 5개 행은 다음과 같습니다:

{markdown_table}

위의 정보를 참고하여, 완전히 동작하는 dataset 모듈 코드를 생성해 주세요.
생성된 모듈은 BaseDataset을 상속받아 모든 기능이 동작하도록 구현해야 합니다.
"""'''
    logger.info("Guide prompt generated.")
    return prompt


@tool
def generate_module_code(guide_prompt: str) -> str:
    """
    Uses smolagents' OpenAIServerModel to generate dataset module code from the provided guide prompt.
    The guide prompt should include necessary instructions (e.g., base class definitions, markdown table of the dataset).
    """
    # Create the model instance using configuration settings.
    model = OpenAIServerModel(
        model_id=Config.MODEL_MODULE,   # e.g., "gpt-4o"
        api_base="https://api.openai.com/v1",
        api_key=Config.OPENAI_API_KEY,
        temperature=0.2,
        max_tokens=2500,
    )
    
    # Prepare messages in the expected format.
    messages = [
        {
            "role": "user", 
            "content": [{"type": "text", "text": guide_prompt}]
        }
    ]
    
    try:
        response = model(messages)
        # Extract module code from the response.
        module_code = response["choices"][0]["message"]["content"].strip()
        logger.info("Module code generated successfully using OpenAIServerModel.")
        return module_code
    except Exception as e:
        logger.error(f"Failed to generate module code: {e}")
        raise
