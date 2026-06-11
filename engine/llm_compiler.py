import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Literal
from django.conf import settings
from .models import DynamicAPI, APIField, compile_virtual_model, execute_runtime_migration
from django.db import transaction

class FieldSchema(BaseModel):
    field_name: str = Field(description="The exact database column name (e.g., 'first_name', 'employee_age'). Must be lowercase and use underscores.")
    data_type: Literal['char', 'text', 'int', 'float', 'bool', 'date', 'json'] = Field(description="The data type for this field.")
    is_required: bool = Field(description="Whether this field must be provided when creating a record.")
    max_length: int = Field(default=255, description="Only relevant if data_type is 'char'. Defaults to 255.")

class APISchema(BaseModel):
    api_name: str = Field(description="Human readable name for the API (e.g., 'Employee tracker')")
    api_slug: str = Field(description="URL friendly slug for the API.")
    description: str = Field(description="A brief description of what this API is for.")
    fields: List[FieldSchema] = Field(description="List of database fields required for this API.")

def generate_schema_from_prompt(prompt: str) -> APISchema:
    """Sends the prompt to Gemini and forces it to return valid APISchema JSON."""
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=APISchema,
            system_instruction="You are a database architect. Analyze the user's prompt and generate a relational database schema for an API. Do not include ID fields, those are handled automatically."
        )
    )
    
    # Parse the returned JSON text safely into our Pydantic model
    return APISchema.model_validate_json(response.text)

def create_api_from_schema(schema: APISchema, owner, prompt: str):
    with transaction.atomic():
        api_record = DynamicAPI.objects.create(
            owner=owner,
            name=schema.api_name,
            slug=schema.api_slug,
            description=schema.description,
            original_prompt=prompt,
            llm_raw_response=schema.model_dump_json()
        )

        for field in schema.fields:
            APIField.objects.create(
                api=api_record,
                field_name=field.field_name,
                data_type=field.data_type,
                is_required=field.is_required,
                max_length=field.max_length if field.data_type == 'char' else None
            )
        
        RuntimeModel = compile_virtual_model(api_record)
        execute_runtime_migration(RuntimeModel)

        return api_record