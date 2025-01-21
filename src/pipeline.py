import os
from dotenv import load_dotenv
from custom_tools import dataset_download_tool, translate_column, push_to_hub_tool
from translated_dataset import TranslatedDataset  # 미구현현
from pr_manager import create_pull_request

load_dotenv()

def main():
    dataset_name = "your_dataset_name_here"  # 실제 데이터셋 이름으로 교체
    subset_name = "your_subset_name_here"    # 실제 subset 이름으로 교체
    
    df = dataset_download_tool(dataset_name, subset_name)
    
    translated_df = translate_column(df, src_col_name='text', tgt_col_name='translation')

    push_message = push_to_hub_tool(translated_df, dataset_name)
    print(push_message)
    
    translated_dataset = TranslatedDataset(
        dataset_name=f"HAERAE-HUB/hret_agent_{dataset_name.replace('/','_')}_translated",
        subset=subset_name,
        split="test" 
    )
    data = translated_dataset.load()
    print(f"Loaded {len(data)} samples from the translated dataset.")
    
    # PR 생성
    pr_status = create_pull_request(
        branch_name="translation-update", 
        title="Update translated dataset and add TranslatedDataset class", 
        description="This PR contains the latest translated dataset upload and adds the TranslatedDataset class for evaluation."
    )
    print(pr_status)

if __name__ == "__main__":
    main()
