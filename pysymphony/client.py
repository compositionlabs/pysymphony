import logging
from typing import Any, Dict, List

import requests

from pysymphony.tooling import LocalTool
from pysymphony.workflows import Workflow
from pysymphony.settings import settings


class SymphonyClient:
    """
    SymphonyClient is a client for the Symphony API.
    """
    def __init__(
        self,
        api_key: str = settings.api_key,
        base_url: str = settings.base_url,
        session: requests.Session = settings.session,
        local_tools: List[LocalTool] = [],
    ):
        """
        Initialize the SymphonyClient.
        """
        if not settings.api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = base_url
        self.session = session or requests.Session()

        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}"
        })

        self.local_tools = local_tools
        self.tools = settings.tools
        
        self._workflows = []

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