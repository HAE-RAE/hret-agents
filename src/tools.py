import os
import logging
import requests
import pandas as pd
from datasets import load_dataset, Dataset
from smolagents import tool
from config.config import Config
from src.translation import batch_translate

logger = logging.getLogger(__name__)

@tool
def check_hf_dataset_subset(dataset_name: str) -> list:
    token = Config.HF_API_TOKEN
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    api_url = f"https://datasets-server.huggingface.co/splits?dataset={dataset_name}"
    try:
        response = requests.get(api_url, headers=headers)
        data = response.json()
        subsets = [item['config'] for item in data.get('splits', [])]
        return subsets
    except Exception as e:
        logger.error(f"Error checking subsets for {dataset_name}: {e}")
        return []

@tool
def dataset_download_tool(dataset_name: str, subset_name: str = None, split: str = "train") -> pd.DataFrame:
    try:
        if subset_name:
            ds = load_dataset(dataset_name, subset_name, split=split)
        else:
            ds = load_dataset(dataset_name, split=split)
        df = pd.DataFrame(ds)
        logger.info(f"Downloaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")
        return df
    except Exception as e:
        logger.error(f"Error downloading dataset {dataset_name}: {e}")
        raise

@tool
def translate_dataframe_tool(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dataframe.copy()

    original_columns = list(df.columns)
    translated_columns = batch_translate(original_columns)
    col_mapping = dict(zip(original_columns, translated_columns))
    df.rename(columns=col_mapping, inplace=True)

    batch_size = Config.BATCH_SIZE
    for col in df.columns:
        values = df[col].astype(str).tolist()
        translated_values = []
        for i in range(0, len(values), batch_size):
            batch_texts = values[i:i+batch_size]
            translated_batch = batch_translate(batch_texts)
            translated_values.extend(translated_batch)
        df[col] = translated_values
    logger.info("DataFrame translation complete.")
    return df

@tool
def push_to_hub_tool(dataframe: pd.DataFrame, dataset_name: str) -> str:
    try:
        ds = Dataset.from_pandas(dataframe)
        safe_dataset_name = dataset_name.replace('/', '_')
        repo_name = f"HAERAE-HUB/hret_agent_{safe_dataset_name}_translated"
        ds.push_to_hub(repo_name, token=Config.HF_ACCESS_TOKEN)
        logger.info(f"Dataset pushed to HF Hub: {repo_name}")
        return f"Successfully pushed to {repo_name}"
    except Exception as e:
        logger.error(f"Error pushing dataset {dataset_name} to hub: {e}")
        raise
