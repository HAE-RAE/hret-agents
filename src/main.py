# src/main.py

import argparse
import logging
from src.agent import HretAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="hret-agent: haerae-evaluation-toolkit 개선 에이전트")
    parser.add_argument("--dataset", required=True, help="Hugging Face dataset name")
    parser.add_argument("--subset", default=None, help="Dataset subset name (선택 사항)")
    parser.add_argument("--split", default="train", help="Dataset split (기본값: train)")
    parser.add_argument("--push", action="store_true", help="번역된 dataset을 HF Hub에 업로드")
    args = parser.parse_args()

    agent = HretAgent(args.dataset, args.subset, args.split, args.push)
    agent.run()

if __name__ == "__main__":
    main()
