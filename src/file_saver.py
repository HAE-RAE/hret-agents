import os
import logging
from smolagents import tool

logger = logging.getLogger(__name__)

@tool
def save_module_to_file(module_code: str, dataset_name: str, output_dir: str = "output") -> None:
    """
    생성된 모듈 코드를 output 디렉토리에 저장
    파일명은 [원본데이터셋이름]_translated.py 
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        safe_dataset_name = dataset_name.replace("/", "_")
        file_path = os.path.join(output_dir, f"{safe_dataset_name}_translated.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(module_code)
        logger.info(f"Module code saved to {file_path}")
    except Exception as e:
        logger.error(f"Failed to save file for {dataset_name}: {e}")
        raise
