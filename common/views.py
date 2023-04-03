import os
import pathlib
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.response import Response
from django.conf import settings


@csrf_exempt
def index(request):
    request_host = request.headers.get('host')
    cors_allowed_origins = settings.CORS_ALLOWED_ORIGINS
    host = f"{request.scheme}://{request_host}"
    if host not in cors_allowed_origins:
        return HttpResponse(pathlib.Path("./common/html/404.html").open(), status=404)

    static_index = pathlib.Path('./static/common/index.html')
    template_index = pathlib.Path('./common/templates/common/index.html')

    if template_index.exists():
        return render(request, 'common/index.html')

    if static_index.exists():
        os.system(
            f'ln -s {static_index.absolute()}  {template_index.absolute()}')
        return render(request, 'common/index.html')
    else:
        return HttpResponse("Frontend static files not found.", status=404)
