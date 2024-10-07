import logging
import os
from typing import Dict, List

import requests
from dotenv import load_dotenv

from pysymphony.constants import ToolType
from pysymphony.tooling import LocalTool

load_dotenv()

class Settings:
    def __init__(
        self,
        session: requests.Session = None,
        local_tools: List[LocalTool] = [],
    ):
        assert os.getenv("SYMPHONY_API_KEY"), "SYMPHONY_API_KEY is not set"

        self.api_key = os.getenv("SYMPHONY_API_KEY")
        self.base_url = os.getenv("SYMPHONY_BASE_URL", "https://inference.composition-labs.com/inference")

        self.local_tools = local_tools

        self.session = session or requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}"
        })

        self._tools = None

    @property
    def tools(self) -> List[str]:
        if not self._tools:
            res = self.get_tools()
            self._tools = []
            for tool in res:
                self._tools.append({
                    "id": tool["unique_id"],
                    "name": tool["name"],
                    "description": tool["description"],
                    "type": ToolType.SYMPHONY if tool["tool_type"] == "in_house" else ToolType.CLIENT
                })
            for tool in self.local_tools:
                self.add_client_tool(
                    unique_id=tool.id,
                    name=tool.name,
                    description=tool.description,
                    schema=tool.schema,
                )
        return self._tools
    
    @tools.setter
    def tools(self, tools: List[str]):
        self._tools = tools

    def add_local_tool(
        self,
        fn: callable,
    ):
        """
        Add a local tool.
        """
        tool = LocalTool(fn=fn)
        self.local_tools.append(tool)
        self.add_client_tool(
            unique_id=tool.id,
            name=tool.name,
            description=tool.description,
            schema=tool.schema,
        )

    def add_client_tool(
        self, 
        unique_id: str,
        name: str,
        description: str,
        schema: Dict,
    ):
        """
        Add a client tool.
        """
        tools = self.tools
        if unique_id in [tool["id"] for tool in tools]:
            return
        try:
            response = self.session.post(
                f"{self.base_url}/tools/add",
                json={
                    "unique_id": unique_id,
                    "name": name,
                    "description": description,
                    "schema": schema,
                },
            )
            if response.status_code == 200:
                logging.info(f"POST {self.base_url}/tools/add: SUCCESS")
                self.tools.append({
                    "id": unique_id,
                    "name": name,
                    "description": description,
                    "type": ToolType.CLIENT,
                })
                return
            else:
                logging.error(f"POST {self.base_url}/tools/add: ERROR {response.status_code} {response.text}")
                raise Exception(f"POST {self.base_url}/tools/add: ERROR {response.status_code} {response.text}")
        except Exception as e:
            logging.error(f"POST {self.base_url}/tools/add: ERROR {e}")
            raise e
        
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

settings = Settings()