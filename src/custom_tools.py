from smolagents import tool
from datasets import load_dataset
import requests
import pandas as pd
from prompts import translation_prompt
from litellm import batch_completion
from src import parse_litellm_response
import os
from datasets import Dataset
from dotenv import load_dotenv

load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
access_token = os.getenv('HF_ACCESS_TOKEN')

@tool
def check_hf_dataset_subset(dataset_name: str) -> list:
    """
    This is a tool that checks if a dataset from the huggingface_hub has subsets.
    It returns the list of subsets in the dataset.

    Args:
        dataset_name: The name of the dataset to check.
    """
    
    API_TOKEN = "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"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    API_URL = f"https://datasets-server.huggingface.co/splits?dataset={dataset_name}"

    def query():
        response = requests.get(API_URL, headers=headers)
        return response.json()
    
    data = query()
    subsets = [item['config'] for item in data['splits']]
    return subsets
         
@tool
def dataset_download_tool(dataset_name: str, subset_name: str) -> pd.DataFrame:
    """
    This is a tool that downloads a dataset from the HuggingFace Hub.
    It downloads the test set only and returns a pandas dataframe.

    Args:
        dataset_name: The name of the dataset to download.
        subset_name: The name of the subset to download.
    """
    ds = load_dataset(dataset_name, subset_name)['train']
    df = pd.DataFrame(ds).head()
    return df

@tool
def push_to_hub_tool(dataframe:pd.DataFrame, dataset_name: str) -> str:
    """
    This is a tool that push a dataframe to the Huggingface Hub.
    It receives the dataset and the dataset name. 

    Args:
        dataframe: The dataframe to push to huggingface_hub.
        dataset_name: The name of the dataset.
    """
    ds = Dataset.from_pandas(dataframe)
    dataset_name = dataset_name.replace('/','_')
    ds.push_to_hub(f"HAERAE-HUB/hret_agent_{dataset_name}_translated", token=access_token)
    return "Successfully pushed to path"
    
@tool
def translate_column(dataframe: pd.DataFrame, src_col_name: str, tgt_col_name:str) -> pd.DataFrame:
    """
    This is a tool that translates a fixed column from a pandas dataframe.
    It returns a dataframe with the translated column added.

    Args:
        dataframe: The dataframe with the column that needs to be translated.
        src_col_name: The name of the column that should be translated.
        tgt_col_name: The name of the column that the translated items will be added. It should be fixed to 'question', unless stated.
    """
    source = dataframe[src_col_name]
    qrys = []
    for src in source:
        qrys.append(
            [{'content':translation_prompt.format(source=src), "role":"user"}]
        )
    responses = batch_completion(
        model="gpt-4o-mini",
        messages = qrys,
    )
    responses,translation = parse_litellm_response(responses)
    dataframe['log'] = responses
    dataframe[tgt_col_name] = translation
    return dataframe