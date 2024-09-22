from symphony.client import SymphonyClient
import logging

logging.basicConfig(level=logging.INFO)

client = SymphonyClient(api_key="symphony-2DgJeCiFP7pTxLKLISuZb70xuYRZOAP96fXODNe_bElTIRRhsQ0kLx9BWNEOLlUu_wshv6ROrQ")

task = "Given a country name, return the capital city"
parameters = {
    "max_steps": 1
}
tools = ["pplx_online"]

workflow = client.generate_workflow(task, parameters, tools)
print(workflow)

run = workflow.run_workflow("Japan")
print(run)
print(run.output)
