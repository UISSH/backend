import os
import pathlib

from django.shortcuts import render
from rest_framework.response import Response


def index(request):
    static_index = pathlib.Path('./static/common/index.html')
    template_index = pathlib.Path('./common/templates/common/index.html')

    if template_index.exists():
        return render(request, 'common/index.html')

    if static_index.exists():
        os.system(f'ln -s {static_index.absolute()}  {template_index.absolute()}')
        return render(request, 'common/index.html')
    else:
        return Response("Frontend static files not found.",404)


