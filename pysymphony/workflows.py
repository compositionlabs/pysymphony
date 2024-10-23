import logging
from typing import Any, Dict, List

import requests

from pysymphony.runs import Run
from pysymphony.settings import settings
from pysymphony.utils import get_mermaid_image_url


def resolve_parameters(parameters: Dict[str, Any]):
    """
    Resolve the parameters.
    """
    for key in parameters.keys():
        if key not in ["llmmodel", "max_steps", "optimize", "max_optimization_steps"]:
            raise ValueError(f"Parameter {key} is not supported")
    return parameters

class Workflow:
    def __init__(
        self, 
        task_description: str = None,
        id: str = None, 
        nodes: List[Dict[str, Any]] = [],
        runs: List[Run] = [],
        parameters: Dict[str, Any] = {},
        session: requests.Session = settings.session,
        tools: List[str] = [],
        base_url: str = settings.base_url,
    ):
        self.id = id
        
        self.task_description = task_description
        self.nodes = nodes
        self.runs = runs
        self.parameters = parameters
        self.session = session or requests.Session()
        self.tools = tools
        self.base_url = base_url

    def __str__(self):
        return f"Workflow(id={self.id}, task_description={self.task_description})"
    
    def run_workflow(self, input: str):
        """
        Run the workflow.
        """
        raise NotImplementedError("`run_workflow` is not implemented yet, use `init_run` and `run_step` instead")
        # if not self.id:
        #     raise ValueError("Workflow is not generated yet")
        # self.runs.append(Run(
        #     id=self.id,
        #     workflow_id=self.id,
        #     input=input,
        #     session=self.session,
        #     base_url=self.base_url,
        # ))
        # _ = self.runs[-1].run()
        # return self.runs[-1]
    
    async def arun_workflow(self, input: str):
        """
        Run the workflow.
        """
        raise NotImplementedError("`run_workflow` is not implemented yet, use `init_run` and `run_step` instead")
    
    def init_run(self, input: str):
        """
        Initialize a run.
        """
        try:
            response = self.session.post(
                f"{self.base_url}/runner/initrun",
                json={
                    "workflow_id": self.id,
                    "text_input": input,
                },
            )
            if response.status_code == 200:
                logging.info(f"POST {self.base_url}/runner/initrun: SUCCESS")
                res = response.json()
                return Run(
                    id=res["run_id"],
                    workflow_id=self.id,
                    input=input,
                    session=self.session,
                    base_url=self.base_url,
                )
            else:
                logging.error(f"POST {self.base_url}/runner/initrun: ERROR {response.status_code} {response.text}")
                raise Exception(f"POST {self.base_url}/runner/initrun: ERROR {response.status_code} {response.text}")
        except Exception as e:
            logging.error(f"POST {self.base_url}/runner/initrun: ERROR {e}")
            raise e
    
    def run_step(self, input: str):
        """
        Run a step.
        """
        pass

    def generate_workflow(
        self
    ):
        """
        Generate a workflow.
        """
        try:
            response = self.session.post(
                f"{self.base_url}/planner/generateworkflow",
                json={
                    "belongs_to": "",
                    "task_description": self.task_description,
                    "tools": self.tools,
                    "parameters": resolve_parameters(self.parameters),
                },
            )
            if response.status_code == 200:
                logging.info(f"POST {self.base_url}/planner/generateworkflow: SUCCESS")
                res = response.json()
                self.id = res["id"]
                self.nodes = res["nodes"]
                self.parameters = res["parameters"]
            else:
                logging.error(f"POST {self.base_url}/planner/generateworkflow: ERROR {response.status_code} {response.text}")
                raise Exception(f"POST {self.base_url}/planner/generateworkflow: ERROR {response.status_code} {response.text}")
        except Exception as e:
            logging.error(f"POST {self.base_url}/planner/generateworkflow: ERROR {e}")
            raise e

    async def agenerate_workflow(
        self
    ):
        """
        Generate a workflow.
        """
        raise NotImplementedError("`generate_workflow` is not implemented yet")
    
    def get_mermaid_image_url(self):
        """
        Get the mermaid image url.
        """
        return get_mermaid_image_url(self.get_mermaid_graph())
    
    def get_mermaid_graph(self):
        """
        Get the mermaid graph.
        """
        mm_str = f"graph TD\nclassDef bg-rounded fill:#f9f,stroke:#333,stroke-width:2px,rx:10px,ry:10px;\n"
        mm_str += f"INPUT\n"
        mm_str += "OUTPUT[Output]\n"
        for node in self.nodes:
            content = node["job"]
            if len(content) > 100:
                content = content[:100] + "..."
            # for tool in node["tools"]:
            #     content += f"\n<br>**{tool['name']}**"
            mm_str += f"Step_{str(node['step_index'])}[{content}]\n"
        for node in self.nodes:
            if len(node["tools"]) > 0:
                tool_content = ""
                for tool in node["tools"]:
                    tool_content += f"\n<br><span class='bg-rounded'>**{tool['name']}**</span>"
                mm_str += f"Step_{str(node['step_index'])} -.-> tools_{str(node['step_index'])}[{tool_content}]\n"
                mm_str += f"tools_{str(node['step_index'])} --> Step_{str(node['step_index'])}\n"
            dependencies = node["dependencies"]
            for dependency in dependencies:
                mm_str += f"Step_{str(dependency)} --> Step_{str(node['step_index'])}\n"
            if len(dependencies) == 0:
                mm_str += f"INPUT --> Step_{str(node['step_index'])}\n"
        for node in self.nodes:
            if node["step_index"] == len(self.nodes):
                mm_str += f"Step_{str(node['step_index'])} --> OUTPUT\n"
        return mm_str
