from pydantic import BaseModel, Field


class ApiCallRequest(BaseModel):
    api_name: str = Field(description="Name of the Aladdin API (e.g. 'TrainJourneyAPI')")
    endpoint: str = Field(description="API endpoint swagger path (e.g. '/trainJourneys:filter')")
    http_method: str = Field(
        default="GET",
        description="HTTP method: GET, POST, PUT, DELETE, PATCH",
    )
    request_body: dict | None = Field(
        default=None,
        description="Request body for POST/PUT/PATCH calls",
    )
    query_params: dict = Field(
        default_factory=dict,
        description="Query parameters for the API call",
    )


class AdcQueryRequest(BaseModel):
    sql: str = Field(description="SQL query to execute against Aladdin Data Cloud")


class ApiListResponse(BaseModel):
    apis: list[str] = Field(description="List of available API names")


class ApiEndpointsResponse(BaseModel):
    api_name: str
    base_url: str
    endpoints: list[dict[str, str]] = Field(description="List of endpoint details")


class ApiEndpointSchemaResponse(BaseModel):
    api_name: str
    endpoint: str
    method: str
    schema: dict | None = Field(description="Endpoint schema from swagger")
