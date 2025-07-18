from typing import Dict

from fastapi import APIRouter, Depends, Query

from feast.api.registry.rest.rest_utils import (
    create_grpc_pagination_params,
    create_grpc_sorting_params,
    get_pagination_params,
    get_sorting_params,
    grpc_call,
    parse_tags,
)
from feast.registry_server import RegistryServer_pb2


def get_feature_view_router(grpc_handler) -> APIRouter:
    router = APIRouter()

    @router.get("/feature_views/{name}")
    def get_any_feature_view(
        name: str,
        project: str = Query(...),
        allow_cache: bool = Query(True),
    ):
        req = RegistryServer_pb2.GetAnyFeatureViewRequest(
            name=name,
            project=project,
            allow_cache=allow_cache,
        )
        response = grpc_call(grpc_handler.GetAnyFeatureView, req)
        any_feature_view = response.get("anyFeatureView", {})
        feature_view = (
            any_feature_view.get("featureView")
            or any_feature_view.get("onDemandFeatureView")
            or any_feature_view.get("streamFeatureView")
            or {}
        )
        return {"featureView": feature_view}

    @router.get("/feature_views")
    def list_all_feature_views(
        project: str = Query(...),
        allow_cache: bool = Query(default=True),
        tags: Dict[str, str] = Depends(parse_tags),
        pagination_params: dict = Depends(get_pagination_params),
        sorting_params: dict = Depends(get_sorting_params),
    ):
        req = RegistryServer_pb2.ListAllFeatureViewsRequest(
            project=project,
            allow_cache=allow_cache,
            tags=tags,
            pagination=create_grpc_pagination_params(pagination_params),
            sorting=create_grpc_sorting_params(sorting_params),
        )
        return grpc_call(grpc_handler.ListAllFeatureViews, req)

    return router
