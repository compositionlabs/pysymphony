import json
import logging

import requests
from pydantic import BaseModel

from pysymphony.constants import Status
from pysymphony.settings import settings


class ToolCallInfo(BaseModel):
    name: str
    input: str
    output: str | None = None

class ToolCalls(BaseModel):
    calls: dict[str, ToolCallInfo]

class Run:
    def __init__(
        self, 
        id: str, 
        workflow_id: str, 
        input: str, 
        session: requests.Session = settings.session,
        base_url: str = settings.base_url,
        status: Status = Status.IDLE,
    ):
        self.id = id
        self.workflow_id = workflow_id
        self.input = input
        self.base_url = base_url
        self.session = session or requests.Session()

        self.status = status

        self.response = None
        self.ios = None
        self.tool_calls = None

    def __str__(self):
        return f"Run(id={self.id}, workflow_id={self.workflow_id}, input={self.input})"
    
    def update_status(self, status: Status):
        self.status = status

    def run_step(self):
        """
        Run a step.
        """
        try:
            self.update_status(Status.RUNNING)
            json_input = {
                "run_id": self.id
            }
            if self.tool_calls is not None:
                json_input["tool_calls"] = {
                    key: str(t.output) for key, t in self.tool_calls.calls.items()
                }
                self.tool_calls = None
            response = self.session.post(
                f"{self.base_url}/runner/runstep",
                json=json_input
            )
            if response.status_code == 200:
                logging.info(f"POST {self.base_url}/runner/runstep: SUCCESS")
                res = response.json()

                if res["tool_calls"]:
                    self.tool_calls = ToolCalls(calls=res["tool_calls"])
                    self.update_status(Status.WAITING_FOR_CLIENT_TOOL)
                    self.handle_tool_calls()
                    self.update_status(Status.RUNNING)
                if res["status"] == "completed":
                    self.update_status(Status.SUCCESS)
                self.ios = res["ios"]
            else:
                logging.error(f"POST {self.base_url}/runner/runstep: ERROR {response.status_code} {response.text}")
                raise Exception(f"POST {self.base_url}/runner/runstep: ERROR {response.status_code} {response.text}")
        except Exception as e:
            logging.error(f"POST {self.base_url}/runner/runstep: ERROR {e}")
            self.update_status(Status.ERROR)
            raise e

    async def arun_step(self, input: str):
        """
        Run a step.
        """
        raise NotImplementedError("`arun_step` is not implemented yet")
    
    def run(
        self,
    ):
        """
        Run a workflow.
        """
        raise NotImplementedError("`run` is not implemented yet, use `run_step` instead")
        # try:
        #     logging.info(f"POST {self.base_url}/runner/runworkflow: RUNNING")
        #     response = self.session.post(
        #         f"{self.base_url}/runner/runworkflow",
        #         json={
        #             "workflow_id": self.workflow_id,
        #             "text_input": self.input,
        #         },
        #     )
        #     if response.status_code == 200:
        #         logging.info(f"POST {self.base_url}/runner/runworkflow: SUCCESS")
        #         self.output = response.json()
        #         return self.output
        #     else:
        #         logging.error(f"POST {self.base_url}/runner/runworkflow: ERROR {response.status_code} {response.text}")
        #         raise Exception(f"POST {self.base_url}/runner/runworkflow: ERROR {response.status_code} {response.text}")
        # except Exception as e:
        #     logging.error(f"POST {self.base_url}/runner/runworkflow: ERROR {e}")
        #     raise e

    async def arun(self, workflow_id: str):
        """
        Run a workflow.
        """
        raise NotImplementedError("`run` is not implemented yet, use `run_step` instead")

    def handle_tool_call(self, tool_call: ToolCallInfo):
        """
        Handle a tool call.
        """
        local_tool = [tool for tool in settings.local_tools if tool_call.name == tool.id][0]
        res = local_tool.fn(**json.loads(tool_call.input))
        tool_call.output = res
    
    def handle_tool_calls(self):
        """
        Handle tool calls.
        """
        for tool_call in self.tool_calls.calls.values():
            self.handle_tool_call(tool_call)