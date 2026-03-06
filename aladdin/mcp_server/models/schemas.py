from pydantic import BaseModel, Field


class ApiCallRequest(BaseModel):
    api_name: str = Field(description="Name of the Aladdin API (e.g. 'TrainJourneyAPI')")
    endpoint: str = Field(description="API endpoint method name or swagger path")
    http_method: str = Field(
        default="get",
        description="HTTP method: get, post, put, delete, patch",
    )
    request_body: dict | None = Field(
        default=None,
        description="Request body for POST/PUT/PATCH calls",
    )
    params: dict = Field(
        default_factory=dict,
        description="Query parameters for the API call",
    )


class AdcQueryRequest(BaseModel):
    sql: str = Field(description="SQL query to execute against Aladdin Data Cloud")


class ApiListResponse(BaseModel):
    apis: list[str] = Field(description="List of available API names")


class ApiEndpointsResponse(BaseModel):
    api_name: str
    endpoints: list[str] = Field(description="List of endpoint method names")


class ApiEndpointSignatureResponse(BaseModel):
    api_name: str
    endpoint: str
    signature: str = Field(description="Method signature of the endpoint")
