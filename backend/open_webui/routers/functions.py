import os
import re
import time

import logging
import aiohttp
from pathlib import Path
from typing import Optional

from open_webui.models.functions import (
    FunctionForm,
    FunctionModel,
    FunctionResponse,
    Functions,
)
from open_webui.utils.plugin import (
    load_function_module_by_id,
    replace_imports,
    get_function_module_from_cache,
)
from open_webui.config import CACHE_DIR
from open_webui.constants import ERROR_MESSAGES
from fastapi import APIRouter, Depends, HTTPException, Request, status
from open_webui.utils.auth import get_admin_user, get_verified_user
from open_webui.env import SRC_LOG_LEVELS
from open_webui.utils.url_security import get_function_url_validator
from pydantic import BaseModel, HttpUrl


log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MAIN"])


router = APIRouter()

# Get URL validator for function loading
url_validator = get_function_url_validator()

def is_url_allowed(url: str) -> bool:
    """
    Validate if the URL is allowed using the common URL security validator.
    This prevents SSRF attacks by only permitting connections to approved domains.
    
    Args:
        url: The URL to validate
        
    Returns:
        bool: True if the URL is allowed, False otherwise
    """
    return url_validator.is_url_allowed(url)


############################
# GetFunctions
############################


@router.get("/", response_model=list[FunctionResponse])
async def get_functions(user=Depends(get_verified_user)):
    return Functions.get_functions()


############################
# ExportFunctions
############################


@router.get("/export", response_model=list[FunctionModel])
async def get_functions(user=Depends(get_admin_user)):
    return Functions.get_functions()


############################
# LoadFunctionFromLink
############################


class LoadUrlForm(BaseModel):
    url: HttpUrl


def github_url_to_raw_url(url: str) -> str:
    # Handle 'tree' (folder) URLs (add main.py at the end)
    m1 = re.match(r"https://github\.com/([^/]+)/([^/]+)/tree/([^/]+)/(.*)", url)
    if m1:
        org, repo, branch, path = m1.groups()
        return f"https://raw.githubusercontent.com/{org}/{repo}/refs/heads/{branch}/{path.rstrip('/')}/main.py"

    # Handle 'blob' (file) URLs
    m2 = re.match(r"https://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.*)", url)
    if m2:
        org, repo, branch, path = m2.groups()
        return (
            f"https://raw.githubusercontent.com/{org}/{repo}/refs/heads/{branch}/{path}"
        )

    # No match; return as-is
    return url


@router.post("/load/url", response_model=Optional[dict])
async def load_function_from_url(
    request: Request, form_data: LoadUrlForm, user=Depends(get_admin_user)
):
    # Log the request for security auditing
    log.info(f"Function load request from user {user.id} for URL: {form_data.url}")
    
    # Rate limiting: Check if user has made too many requests recently
    # This is a simple in-memory rate limiter - in production, consider using Redis
    user_id = str(user.id)
    current_time = time.time()
    
    # Simple rate limiting: max 10 requests per hour per user
    if not hasattr(request.app.state, 'function_load_requests'):
        request.app.state.function_load_requests = {}
    
    if user_id in request.app.state.function_load_requests:
        user_requests = request.app.state.function_load_requests[user_id]
        # Clean old requests (older than 1 hour)
        user_requests = [req_time for req_time in user_requests if current_time - req_time < 3600]
        
        if len(user_requests) >= 10:  # 10 requests per hour limit
            log.warning(f"Rate limit exceeded for user {user_id}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Maximum 10 function load requests per hour."
            )
        
        user_requests.append(current_time)
        request.app.state.function_load_requests[user_id] = user_requests
    else:
        request.app.state.function_load_requests[user_id] = [current_time]
    # NOTE: This endpoint is admin-only (see get_admin_user), meant for *trusted* internal use,
    # and does NOT accept untrusted user input. Access is enforced by authentication.
    # However, we still implement strict URL validation to prevent SSRF attacks.

    url = str(form_data.url)
    if not url:
        raise HTTPException(status_code=400, detail="Please enter a valid URL")

    # Validate URL against allow-list to prevent SSRF attacks
    if not is_url_allowed(url):
        raise HTTPException(
            status_code=400, 
            detail="URL not allowed. Only approved domains are permitted for security reasons."
        )

    url = github_url_to_raw_url(url)
    
    # Re-validate the transformed URL to ensure it's still allowed
    if not is_url_allowed(url):
        raise HTTPException(
            status_code=400, 
            detail="Transformed URL not allowed. Only approved domains are permitted for security reasons."
        )
    
    url_parts = url.rstrip("/").split("/")

    file_name = url_parts[-1]
    function_name = (
        file_name[:-3]
        if (
            file_name.endswith(".py")
            and (not file_name.startswith(("main.py", "index.py", "__init__.py")))
        )
        else url_parts[-2] if len(url_parts) > 1 else "function"
    )

    try:
        # Set strict timeout and size limits to prevent abuse
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        connector = aiohttp.TCPConnector(limit=1, limit_per_host=1)
        
        async with aiohttp.ClientSession(
            timeout=timeout, 
            connector=connector,
            headers={
                "User-Agent": "GovGPT-Function-Loader/1.0",
                "Accept": "text/plain,text/x-python,application/x-python",
                "Accept-Encoding": "gzip, deflate"
            }
        ) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise HTTPException(
                        status_code=resp.status, detail="Failed to fetch the function"
                    )
                
                # Check content length to prevent large file downloads
                content_length = resp.headers.get('content-length')
                if content_length and int(content_length) > 1024 * 1024:  # 1MB limit
                    raise HTTPException(
                        status_code=400, 
                        detail="File too large. Maximum size allowed is 1MB."
                    )
                
                data = await resp.text()
                if not data:
                    raise HTTPException(
                        status_code=400, detail="No data received from the URL"
                    )
                
                # Additional size check for the actual content
                if len(data) > 1024 * 1024:  # 1MB limit
                    raise HTTPException(
                        status_code=400, 
                        detail="Content too large. Maximum size allowed is 1MB."
                    )
                
                # Validate content type - ensure it's Python code
                content_type = resp.headers.get('content-type', '').lower()
                if not any(py_type in content_type for py_type in ['text/plain', 'text/x-python', 'application/x-python']):
                    # Check if the content looks like Python code
                    if not data.strip().startswith(('#', '"""', "'''", 'import ', 'from ', 'def ', 'class ')):
                        log.warning(f"Content from {url} doesn't appear to be Python code")
                        # Don't block, but log for monitoring
                
                # Log successful function load
                log.info(f"Successfully loaded function '{function_name}' from {url} (size: {len(data)} bytes)")
                    
        return {
            "name": function_name,
            "content": data,
        }
    except aiohttp.ClientError as e:
        log.warning(f"Network error when loading function from {url}: {e}")
        raise HTTPException(
            status_code=400, 
            detail="Network error when fetching the function. Please check the URL and try again."
        )
    except Exception as e:
        log.error(f"Error importing function from {url}: {e}")
        raise HTTPException(status_code=500, detail=f"Error importing function: {e}")


############################
# SyncFunctions
############################


class SyncFunctionsForm(FunctionForm):
    functions: list[FunctionModel] = []


@router.post("/sync", response_model=Optional[FunctionModel])
async def sync_functions(
    request: Request, form_data: SyncFunctionsForm, user=Depends(get_admin_user)
):
    return Functions.sync_functions(user.id, form_data.functions)


############################
# CreateNewFunction
############################


@router.post("/create", response_model=Optional[FunctionResponse])
async def create_new_function(
    request: Request, form_data: FunctionForm, user=Depends(get_admin_user)
):
    if not form_data.id.isidentifier():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only alphanumeric characters and underscores are allowed in the id",
        )

    form_data.id = form_data.id.lower()

    function = Functions.get_function_by_id(form_data.id)
    if function is None:
        try:
            form_data.content = replace_imports(form_data.content)
            function_module, function_type, frontmatter = load_function_module_by_id(
                form_data.id,
                content=form_data.content,
            )
            form_data.meta.manifest = frontmatter

            FUNCTIONS = request.app.state.FUNCTIONS
            FUNCTIONS[form_data.id] = function_module

            function = Functions.insert_new_function(user.id, function_type, form_data)

            function_cache_dir = CACHE_DIR / "functions" / form_data.id
            function_cache_dir.mkdir(parents=True, exist_ok=True)

            if function:
                return function
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ERROR_MESSAGES.DEFAULT("Error creating function"),
                )
        except Exception as e:
            log.exception(f"Failed to create a new function: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT(e),
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ID_TAKEN,
        )


############################
# GetFunctionById
############################


@router.get("/id/{id}", response_model=Optional[FunctionModel])
async def get_function_by_id(id: str, user=Depends(get_admin_user)):
    function = Functions.get_function_by_id(id)

    if function:
        return function
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# ToggleFunctionById
############################


@router.post("/id/{id}/toggle", response_model=Optional[FunctionModel])
async def toggle_function_by_id(id: str, user=Depends(get_admin_user)):
    function = Functions.get_function_by_id(id)
    if function:
        function = Functions.update_function_by_id(
            id, {"is_active": not function.is_active}
        )

        if function:
            return function
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT("Error updating function"),
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# ToggleGlobalById
############################


@router.post("/id/{id}/toggle/global", response_model=Optional[FunctionModel])
async def toggle_global_by_id(id: str, user=Depends(get_admin_user)):
    function = Functions.get_function_by_id(id)
    if function:
        function = Functions.update_function_by_id(
            id, {"is_global": not function.is_global}
        )

        if function:
            return function
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT("Error updating function"),
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# UpdateFunctionById
############################


@router.post("/id/{id}/update", response_model=Optional[FunctionModel])
async def update_function_by_id(
    request: Request, id: str, form_data: FunctionForm, user=Depends(get_admin_user)
):
    try:
        form_data.content = replace_imports(form_data.content)
        function_module, function_type, frontmatter = load_function_module_by_id(
            id, content=form_data.content
        )
        form_data.meta.manifest = frontmatter

        FUNCTIONS = request.app.state.FUNCTIONS
        FUNCTIONS[id] = function_module

        updated = {**form_data.model_dump(exclude={"id"}), "type": function_type}
        log.debug(updated)

        function = Functions.update_function_by_id(id, updated)

        if function:
            return function
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT("Error updating function"),
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(e),
        )


############################
# DeleteFunctionById
############################


@router.delete("/id/{id}/delete", response_model=bool)
async def delete_function_by_id(
    request: Request, id: str, user=Depends(get_admin_user)
):
    result = Functions.delete_function_by_id(id)

    if result:
        FUNCTIONS = request.app.state.FUNCTIONS
        if id in FUNCTIONS:
            del FUNCTIONS[id]

    return result


############################
# GetFunctionValves
############################


@router.get("/id/{id}/valves", response_model=Optional[dict])
async def get_function_valves_by_id(id: str, user=Depends(get_admin_user)):
    function = Functions.get_function_by_id(id)
    if function:
        try:
            valves = Functions.get_function_valves_by_id(id)
            return valves
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT(e),
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# GetFunctionValvesSpec
############################


@router.get("/id/{id}/valves/spec", response_model=Optional[dict])
async def get_function_valves_spec_by_id(
    request: Request, id: str, user=Depends(get_admin_user)
):
    function = Functions.get_function_by_id(id)
    if function:
        function_module, function_type, frontmatter = get_function_module_from_cache(
            request, id
        )

        if hasattr(function_module, "Valves"):
            Valves = function_module.Valves
            return Valves.schema()
        return None
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# UpdateFunctionValves
############################


@router.post("/id/{id}/valves/update", response_model=Optional[dict])
async def update_function_valves_by_id(
    request: Request, id: str, form_data: dict, user=Depends(get_admin_user)
):
    function = Functions.get_function_by_id(id)
    if function:
        function_module, function_type, frontmatter = get_function_module_from_cache(
            request, id
        )

        if hasattr(function_module, "Valves"):
            Valves = function_module.Valves

            try:
                form_data = {k: v for k, v in form_data.items() if v is not None}
                valves = Valves(**form_data)
                Functions.update_function_valves_by_id(id, valves.model_dump())
                return valves.model_dump()
            except Exception as e:
                log.exception(f"Error updating function values by id {id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ERROR_MESSAGES.DEFAULT(e),
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.NOT_FOUND,
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# FunctionUserValves
############################


@router.get("/id/{id}/valves/user", response_model=Optional[dict])
async def get_function_user_valves_by_id(id: str, user=Depends(get_verified_user)):
    function = Functions.get_function_by_id(id)
    if function:
        try:
            user_valves = Functions.get_user_valves_by_id_and_user_id(id, user.id)
            return user_valves
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT(e),
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


@router.get("/id/{id}/valves/user/spec", response_model=Optional[dict])
async def get_function_user_valves_spec_by_id(
    request: Request, id: str, user=Depends(get_verified_user)
):
    function = Functions.get_function_by_id(id)
    if function:
        function_module, function_type, frontmatter = get_function_module_from_cache(
            request, id
        )

        if hasattr(function_module, "UserValves"):
            UserValves = function_module.UserValves
            return UserValves.schema()
        return None
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


@router.post("/id/{id}/valves/user/update", response_model=Optional[dict])
async def update_function_user_valves_by_id(
    request: Request, id: str, form_data: dict, user=Depends(get_verified_user)
):
    function = Functions.get_function_by_id(id)

    if function:
        function_module, function_type, frontmatter = get_function_module_from_cache(
            request, id
        )

        if hasattr(function_module, "UserValves"):
            UserValves = function_module.UserValves

            try:
                form_data = {k: v for k, v in form_data.items() if v is not None}
                user_valves = UserValves(**form_data)
                Functions.update_user_valves_by_id_and_user_id(
                    id, user.id, user_valves.model_dump()
                )
                return user_valves.model_dump()
            except Exception as e:
                log.exception(f"Error updating function user valves by id {id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ERROR_MESSAGES.DEFAULT(e),
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.NOT_FOUND,
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )
