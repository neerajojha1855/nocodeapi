from django.shortcuts import render
from .models import DynamicAPI, compile_virtual_model
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import NotFound

def dynamic_api_gateway_router(request, api_slug, pk=None):
    try:
        api_meta = DynamicAPI.objects.prefetch_related('fields').get(slug=api_slug, active=True)
    except DynamicAPI.DoesNotExist:
        raise NotFound("Requested dynamic endpoint is inactive or missing.")
    
    RuntimeModel = compile_virtual_model(api_meta)

    class RuntimeSerializer(ModelSerializer):
        class Meta:
            model = RuntimeModel
            fields = '__all__'
        
    class RuntimeViewSet(ModelViewSet):
        queryset = RuntimeModel.objects.all()
        serializer_class = RuntimeSerializer
    
    action_map = {
        'GET': 'list' if not pk else 'retrieve',
        'POST': 'create',
        'PUT': 'update',
        'PATCH': 'partial_update',
        "DELETE": 'destroy'
    }

    target_action = action_map.get(request.method)
    executable_view = RuntimeViewSet.as_view({
        'get': target_action,
        'post': target_action,
        'put': target_action,
        'patch': target_action,
        'delete': target_action
    })

    return executable_view(request, pk=pk)