# src/agent.py

import logging
from src.tools import (
    check_hf_dataset_subset,
    dataset_download_tool,
    translate_dataframe_tool,
    push_to_hub_tool,
)
from src.prompt_generator import generate_guide_prompt, generate_module_code
from src.file_saver import save_module_to_file

logger = logging.getLogger(__name__)

class HretAgent:
    """
    A simple pipeline that sequentially executes each step.
    """
    def __init__(self, dataset_name: str, subset: str = None, split: str = "train", push: bool = False):
        self.dataset_name = dataset_name
        self.subset = subset
        self.split = split
        self.push = push

    def run(self):
        if not self.subset:
            subsets = check_hf_dataset_subset(self.dataset_name)
            if subsets:
                self.subset = subsets[0]
                logger.info(f"Using default subset: {self.subset}")
            else:
                logger.info("No subsets found; proceeding without subset.")

        df = dataset_download_tool(self.dataset_name, self.subset, self.split)
        translated_df = translate_dataframe_tool(df)
        markdown_table = translated_df.head(5).to_markdown(index=False)
        guide_prompt = generate_guide_prompt(markdown_table)
        module_code = generate_module_code(guide_prompt)
        save_module_to_file(module_code, self.dataset_name)
        if self.push:
            push_msg = push_to_hub_tool(translated_df, self.dataset_name)
            logger.info(push_msg)

###############################################################################
# Autonomous agent that plans and executes all tasks using the available tools.
###############################################################################

class AutonomousHretAgent:
    """
    An autonomous agent that dynamically plans its workflow using the defined tools,
    and then executes each step in order.
    """
    def __init__(self, dataset_name: str, subset: str = None, split: str = "train", push: bool = False):
        self.dataset_name = dataset_name
        self.subset = subset
        self.split = split
        self.push = push
        self.results = {}
        self.plan_steps = []

    def plan(self):
        """
        Create a list of steps that form the execution plan. Each step is a dict containing:
          - name: A unique name for the step.
          - tool: The tool function to call.
          - params: Parameters to pass to the tool.
          - output: A key for storing the output (if applicable).
        """
        # If no subset is provided, plan to check available subsets.
        if not self.subset:
            self.plan_steps.append({
                'name': 'check_subset',
                'tool': check_hf_dataset_subset,
                'params': {'dataset_name': self.dataset_name},
                'output': 'subsets'
            })

        self.plan_steps.append({
            'name': 'download_dataset',
            'tool': dataset_download_tool,
            'params': {'dataset_name': self.dataset_name, 'subset_name': self.subset, 'split': self.split},
            'output': 'df'
        })
        self.plan_steps.append({
            'name': 'translate_dataset',
            'tool': translate_dataframe_tool,
            'params': {'dataframe': None},  # will fill after download
            'output': 'translated_df'
        })
        self.plan_steps.append({
            'name': 'generate_markdown',
            'tool': lambda df: df.head(5).to_markdown(index=False),
            'params': {'df': None},  # to be filled with translated_df
            'output': 'markdown_table'
        })
        self.plan_steps.append({
            'name': 'generate_guide_prompt',
            'tool': generate_guide_prompt,
            'params': {'markdown_table': None},  # will fill after markdown generation
            'output': 'guide_prompt'
        })
        self.plan_steps.append({
            'name': 'generate_module_code',
            'tool': generate_module_code,
            'params': {'guide_prompt': None},  # to be filled after guide prompt
            'output': 'module_code'
        })
        self.plan_steps.append({
            'name': 'save_module_to_file',
            'tool': save_module_to_file,
            'params': {'module_code': None, 'dataset_name': self.dataset_name},
            'output': None
        })
        if self.push:
            self.plan_steps.append({
                'name': 'push_to_hub',
                'tool': push_to_hub_tool,
                'params': {'dataframe': None, 'dataset_name': self.dataset_name},
                'output': 'push_result'
            })
        step_names = ", ".join([step['name'] for step in self.plan_steps])
        logger.info(f"Plan created with steps: {step_names}")

    def execute_plan(self):
        """
        Execute each planned step sequentially and store results.
        Parameters for subsequent steps are updated dynamically.
        """
        for step in self.plan_steps:
            step_name = step['name']
            tool_func = step['tool']
            params = step['params']
            logger.info(f"Executing step: {step_name}")

            if step_name == 'check_subset':
                result = tool_func(**params)
                self.results['subsets'] = result
                if result:
                    self.subset = result[0]
                    logger.info(f"Auto-selected subset: {self.subset}")
                    # Update dataset download step with the chosen subset.
                    for s in self.plan_steps:
                        if s['name'] == 'download_dataset':
                            s['params']['subset_name'] = self.subset

            elif step_name == 'download_dataset':
                result = tool_func(**params)
                self.results['df'] = result
                # Update translation and markdown steps.
                for s in self.plan_steps:
                    if s['name'] == 'translate_dataset':
                        s['params']['dataframe'] = result
                    if s['name'] == 'generate_markdown':
                        s['params']['df'] = result

            elif step_name == 'translate_dataset':
                result = tool_func(**params)
                self.results['translated_df'] = result
                # Update markdown and push steps.
                for s in self.plan_steps:
                    if s['name'] == 'generate_markdown':
                        s['params']['df'] = result
                    if s['name'] == 'push_to_hub':
                        s['params']['dataframe'] = result

            elif step_name == 'generate_markdown':
                result = tool_func(params['df'])
                self.results['markdown_table'] = result
                # Update guide prompt step.
                for s in self.plan_steps:
                    if s['name'] == 'generate_guide_prompt':
                        s['params']['markdown_table'] = result

            elif step_name == 'generate_guide_prompt':
                result = tool_func(**params)
                self.results['guide_prompt'] = result
                # Update module generation step.
                for s in self.plan_steps:
                    if s['name'] == 'generate_module_code':
                        s['params']['guide_prompt'] = result

            elif step_name == 'generate_module_code':
                result = tool_func(**params)
                self.results['module_code'] = result
                # Update file saver step.
                for s in self.plan_steps:
                    if s['name'] == 'save_module_to_file':
                        s['params']['module_code'] = result

            elif step_name == 'save_module_to_file':
                tool_func(**params)

            elif step_name == 'push_to_hub':
                result = tool_func(**params)
                self.results['push_result'] = result

            logger.info(f"Step '{step_name}' completed.")
        logger.info("Plan execution completed.")

    def run(self):
        self.plan()
        self.execute_plan()
