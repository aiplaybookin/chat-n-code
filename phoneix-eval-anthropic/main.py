# Reference : https://github.com/Arize-ai/phoenix/blob/main/tutorials/tracing/anthropic_tracing_tutorial.ipynb
# pip install anthropic arize-phoenix jsonschema openinference-instrumentation-anthropic

import os
from getpass import getpass
from typing import Any, Dict
import pandas as pd
import phoenix as px
import anthropic

from openinference.instrumentation.anthropic import AnthropicInstrumentor
from phoenix.otel import register

pd.set_option("display.max_colwidth", None)

# Configure Anthropic API Key and Instantiate Your Anthropic Client
if not (anthropic_api_key := os.getenv("ANTHROPIC_API_KEY")):
    anthropic_api_key = getpass("🔑 Enter your Anthropic API key: ")

client = anthropic.Anthropic(api_key=anthropic_api_key)

# Instrument Your Anthropic Client
tracer_provider = register(project_name="anthropic-tools")
AnthropicInstrumentor().instrument(tracer_provider=tracer_provider)

(session := px.launch_app()).view()

# Extract Structured Data from user query
travel_requests = [
    "Can you recommend a luxury hotel in Tokyo with a view of Mount Fuji for a romantic honeymoon?",
    "I'm looking for a mid-range hotel in London with easy access to public transportation for a solo backpacking trip. Any suggestions?",
    "I need a budget-friendly hotel in San Francisco close to the Golden Gate Bridge for a family vacation. What do you recommend?",
    "Can you help me find a boutique hotel in New York City with a rooftop bar for a cultural exploration trip?",
    "I'm planning a business trip to Tokyo and I need a hotel near the financial district. What options are available?",
    "I'm traveling to London for a solo vacation and I want to stay in a trendy neighborhood with great shopping and dining options. Any recommendations for hotels?",
    "I'm searching for a luxury beachfront resort in San Francisco for a relaxing family vacation. Can you suggest any options?",
    "I need a mid-range hotel in New York City with a fitness center and conference facilities for a business trip. Any suggestions?",
    "I'm looking for a budget-friendly hotel in Tokyo with easy access to public transportation for a backpacking trip. What do you recommend?",
    "I'm planning a honeymoon in London and I want a luxurious hotel with a spa and romantic atmosphere. Can you suggest some options?",
]

# tools to extract/ function calling
tool_schema = {
    "name": "record_travel_request_attributes",
    "description": "Records the attributes of a travel request",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": 'The desired destination location. Use city, state, and country format when possible. If no destination is provided, return "not_stated".',
            },
            "budget_level": {
                "type": "string",
                "enum": ["low", "medium", "high", "not_stated"],
                "description": 'The desired budget level. If no budget level is provided, return "not_stated".',
            },
            "purpose": {
                "type": "string",
                "enum": ["business", "pleasure", "other", "not_stated"],
                "description": 'The purpose of the trip. If no purpose is provided, return "not_stated".',
            },
        },
        "required": ["location", "budget_level", "purpose"],
    },
}


system_message = (
    "You are an assistant that parses and records the attributes of a user's travel request."
)

def extract_raw_travel_request_attributes_string(
    travel_request: str,
    tool_schema: Dict[str, Any],
    system_message: str,
    client: client,
    model: str = "claude-3-5-sonnet-20240620",
) -> str:
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[
            {"role": "user", "content": travel_request},
        ],
        system=system_message,
        tools=[tool_schema],
        # By default, the LLM will choose whether or not to call a function given the conversation context.
        # The line below forces the LLM to call the function so that the output conforms to the schema.
        tool_choice={"type": "tool", "name": "record_travel_request_attributes"},
    )
    return response.content[0].input

# Run the extractions
raw_travel_attributes_column = []

for travel_request in travel_requests:
    print("Travel request:")
    print("==============")
    print(travel_request)
    print()
    raw_travel_attributes = extract_raw_travel_request_attributes_string(
        travel_request, tool_schema, system_message, client
    )
    raw_travel_attributes_column.append(raw_travel_attributes)
    print("Raw Travel Attributes:")
    print("=====================")
    print(raw_travel_attributes)
    print()
    print()

print(f"🔥🐦 Open the Phoenix UI if you haven't already: {session.url}")

# Export and Evaluate Your Trace Data
trace_ds = px.Client().get_trace_dataset(project_name="anthropic-tools")
trace_ds.get_spans_dataframe().head()