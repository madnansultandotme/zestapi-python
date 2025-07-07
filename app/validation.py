
from pydantic import BaseModel, ValidationError
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException

def validate(model: BaseModel):
    def decorator(func):
        async def wrapper(request, *args, **kwargs):
            try:
                if request.method in ["POST", "PUT", "PATCH"]:
                    data = await request.json()
                    request.state.validated_data = model(**data)
                elif request.method == "GET":
                    request.state.validated_data = model(**request.query_params)
                # For path parameters, Pydantic handles it implicitly via type hints in the route function
            except ValidationError as e:
                raise HTTPException(status_code=400, detail={"code": 4003, "message": "Validation failed", "errors": e.errors()})
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


