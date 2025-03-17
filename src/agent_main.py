import argparse
import logging
from src.agent import AutonomousHretAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="hret-agent: Autonomous haerae-evaluation-toolkit agent")
    parser.add_argument("--dataset", required=True, help="Hugging Face dataset name (e.g., HAERAE-HUB/QARV)")
    parser.add_argument("--subset", default=None, help="Dataset subset name (optional)")
    parser.add_argument("--split", default="train", help="Dataset split (default: train)")
    parser.add_argument("--push", action="store_true", help="Upload translated dataset to HF Hub")
    args = parser.parse_args()

    agent = AutonomousHretAgent(args.dataset, args.subset, args.split, args.push)
    agent.run()

if __name__ == "__main__":
    main()
