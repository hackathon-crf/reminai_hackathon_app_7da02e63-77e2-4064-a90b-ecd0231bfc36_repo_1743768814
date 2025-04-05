import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import backend.app.routes as appp_router
import argparse
from dotenv import set_key

from settings.config import settings


def create_app() -> FastAPI:
    """
    Creating a FastAPI instance and registering routes.
    """

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Registering routes
    app.include_router(appp_router.app_router)
    return app


app = create_app()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run FastAPI server with custom port")
    parser.add_argument("--port", type=int, default=8090, help="Port number to run the server on")
    parser.add_argument("--baseurl", type=str, default="http://localhost", help="Port number to run the server on")

    args = parser.parse_args()

    set_key(".client_env", "BACKEND_PORT", str(args.port))
    set_key(".client_env", "BASE_URL", str(args.baseurl))
    uvicorn.run("main_back:app", host="0.0.0.0", port=args.port, reload=False, log_level="debug")
