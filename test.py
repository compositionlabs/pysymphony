import logging
import os

from pysymphony import SymphonyClient
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

client = SymphonyClient(
    api_key=os.getenv("SYMPHONY_API_KEY"),
    base_url="http://127.0.0.1:8000/inference"
)

task = "A workflow to find an artist's background and their works based on an input artist."
parameters = {
    "max_steps": 3
}
tools = ["pplx_online"]

workflow = client.generate_workflow(task, parameters, tools)
print(workflow)

run = workflow.run_workflow("Michealangelo")
print(run)
print(run.output)