from fastapi import APIRouter, Request, HTTPException
import httpx

router = APIRouter()

# Backend service URL - configure via environment variable in production
BACKEND_SERVICE = "http://localhost:9000"

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request, path: str):
   """
   Proxy endpoint that forwards requests to the backend service.
   
   Forwards all HTTP methods and preserves headers, query parameters,
   and request body to the target backend service.
   
   Args:
       request: Incoming FastAPI request
       path: Dynamic path to forward to backend
       
   Returns:
       Backend service response
       
   Raises:
       HTTPException: When backend service is unreachable or returns error
   """
   try:
       async with httpx.AsyncClient(timeout=30.0) as client:
           response = await client.request(
               method=request.method,
               url=f"{BACKEND_SERVICE}/{path}",
               params=request.query_params,
               headers=dict(request.headers),
               content=await request.body()
           )
           
           # Handle different response types
           if response.headers.get("content-type", "").startswith("application/json"):
               return response.json()
           else:
               return response.text
               
   except httpx.RequestError as e:
       raise HTTPException(
           status_code=503,
           detail=f"Backend service unavailable: {str(e)}"
       )
   except httpx.HTTPStatusError as e:
       raise HTTPException(
           status_code=e.response.status_code,
           detail=f"Backend service error: {e.response.text}"
       )