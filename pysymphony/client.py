import logging
from typing import Any, Dict, List

import requests

def resolve_parameters(parameters: Dict[str, Any]):
    """
    Resolve the parameters.
    """
    for key in parameters.keys():
        if key not in ["llmmodel", "max_steps", "optimize", "max_optimization_steps"]:
            raise ValueError(f"Parameter {key} is not supported")
    return parameters

class Run:
    def __init__(
        self, 
        id: str, 
        workflow_id: str, 
        input: str, 
        session: requests.Session = None,
        base_url: str = "https://inference.composition-labs.com/inference",
    ):
        self.id = id
        self.workflow_id = workflow_id
        self.input = input
        self.base_url = base_url
        self.session = session or requests.Session()

        self.output = None

    def __str__(self):
        return f"Run(id={self.id}, workflow_id={self.workflow_id}, input={self.input})"
    
    def run(
        self,
    ):
        """
        Run a workflow.
        """
        try:
            logging.info(f"POST {self.base_url}/runner/runworkflow: RUNNING")
            response = self.session.post(
                f"{self.base_url}/runner/runworkflow",
                json={
                    "workflow_id": self.workflow_id,
                    "text_input": self.input,
                },
            )
            if response.status_code == 200:
                logging.info(f"POST {self.base_url}/runner/runworkflow: SUCCESS")
                self.output = response.json()
                return self.output
            else:
                logging.error(f"POST {self.base_url}/runner/runworkflow: ERROR {response.status_code} {response.text}")
                raise Exception(f"POST {self.base_url}/runner/runworkflow: ERROR {response.status_code} {response.text}")
        except Exception as e:
            logging.error(f"POST {self.base_url}/runner/runworkflow: ERROR {e}")
            raise e

    async def arun(self, workflow_id: str):
        """
        Run a workflow.
        """
        pass

class Workflow:
    def __init__(
        self, 
        task_description: str, 
        id: str = None, 
        nodes: List[Dict[str, Any]] = [],
        runs: List[Run] = [],
        parameters: Dict[str, Any] = {},
        session: requests.Session = None,
        tools: List[str] = [],
        base_url: str = "https://inference.composition-labs.com/inference",
    ):
        self.task_description = task_description
        self.id = id
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
        if not self.id:
            raise ValueError("Workflow is not generated yet")
        self.runs.append(Run(
            id=self.id,
            workflow_id=self.id,
            input=input,
            session=self.session,
            base_url=self.base_url,
        ))
        _ = self.runs[-1].run()
        return self.runs[-1]
    
    async def arun_workflow(self, input: str):
        """
        Run the workflow.
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
        pass


class SymphonyClient:
    """
    SymphonyClient is a client for the Symphony API.
    """
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://inference.composition-labs.com/inference",
        session: requests.Session = None,
    ):
        """
        Initialize the SymphonyClient.
        """
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = base_url
        self.session = session or requests.Session()

        self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

        self._tools = []
        self._workflows = []
    
    @property
    def tools(self) -> List[str]:
        if not self._tools:
            res = self.get_tools()
            self._tools = []
            for tool in res["tools"]:
                self._tools.append({
                    "id": tool["id"],
                    "name": tool["name"],
                    "description": tool["description"],
                })
        return self._tools
    
    @tools.setter
    def tools(self, tools: List[str]):
        self._tools = tools

    @property
    def workflows(self) -> List[str]:
        if not self._workflows:
            res = self.get_workflows()
            self._workflows = []
            for workflow in res:
                self._workflows.append(Workflow(
                    id=workflow["id"],
                    task_description=workflow["task_description"],
                    nodes=workflow["nodes"],
                    parameters=workflow["parameters"],
                    session=self.session,
                    base_url=self.base_url,
                ))
        return self._workflows
    
    @workflows.setter
    def workflows(self, workflows: List[str]):
        self._workflows = workflows

    def get_tools(self):
        """
        Get the tools.
        """
        try:
            response = self.session.get(f"{self.base_url}/tools/list")
            logging.info(f"GET {self.base_url}/tools/list: RUNNING")
            if response.status_code == 200:
                logging.info(f"GET {self.base_url}/tools/list: SUCCESS")
                return response.json()
            else:
                logging.error(f"GET {self.base_url}/tools/list: ERROR {response.status_code} {response.text}")
                raise Exception(f"GET {self.base_url}/tools/list: ERROR {response.status_code} {response.text}")
        except Exception as e:
            logging.error(f"GET {self.base_url}/tools/list: ERROR {e}")
            raise e

    async def aget_tools(self):
        """
        Get the tools.
        """
        pass

    def get_workflows(self):
        """
        Get the workflows.
        """
        try:
            response = self.session.get(f"{self.base_url}/planner/getworkflows")
            logging.info(f"GET {self.base_url}/planner/getworkflows: RUNNING")
            if response.status_code == 200:
                logging.info(f"GET {self.base_url}/planner/getworkflows: SUCCESS")
                return response.json()
            else:
                logging.error(f"GET {self.base_url}/planner/getworkflows: ERROR {response.status_code} {response.text}")
                raise Exception(f"GET {self.base_url}/planner/getworkflows: ERROR {response.status_code} {response.text}")
        except Exception as e:
            logging.error(f"GET {self.base_url}/planner/getworkflows: ERROR {e}")
            raise e

    async def aget_workflows(self):
        """
        Get the workflows.
        """
        pass

    def generate_workflow(
        self,
        task_description: str,
        parameters: Dict[str, Any],
        tools: List[str] = [],
    ):
        """
        Generate a workflow.
        """
        workflow = Workflow(task_description=task_description, parameters=parameters, tools=tools, session=self.session, base_url=self.base_url)
        workflow.generate_workflow()
        self.workflows.append(workflow)
        return workflow
    
    async def agenerate_workflow(
        self,
        task_description: str,
        parameters: Dict[str, Any],
        tools: List[str] = [],
    ):
        """
        Generate a workflow.
        """
        pass