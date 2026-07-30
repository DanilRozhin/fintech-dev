from fastapi import Request

from app.clients.provider_client import ProviderClient


def get_provider_client(request: Request) -> ProviderClient:
    return request.app.state.provider_client
