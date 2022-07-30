import os
import pathlib
import traceback

from django.db import transaction
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from base.utils.logger import plog
from base.viewset import BaseModelViewSet
from common.models import User
from website.applications.core.dataclass import BaseSSLCertificate
from website.models import Website
from website.serializers.website import WebsiteModelSerializer


class WebsiteView(BaseModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Website.objects.select_related('user').all()
    serializer_class = WebsiteModelSerializer

    def get_queryset(self):
        user: User = self.request.user
        if user.is_superuser:
            return self.queryset.all()
        else:
            return self.queryset.filter(user=user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(WebsiteView, self).create(request, *args, **kwargs)

    # @extend_schema(responses= todo add schema)
    @action(methods=['get'], detail=True)
    def get_ssl_info(self, request, *args, **kwargs):
        instance = self.get_object()
        valid = False

        certificate_path = instance.ssl_config['path']['certificate']
        if certificate_path != '' and pathlib.Path(certificate_path).exists():
            try:
                cert = BaseSSLCertificate.get_certificate(certificate_path)
                return Response(cert.__dict__)

            except Exception:
                e = traceback.format_exc()
                return Response(e, status=500)

        else:
            return Response('Not found', status=404)

    def update(self, request, *args, **kwargs):
        domain = request.data.get('domain', None)
        instance = self.get_object()
        if domain and domain != instance.domain:
            plog.debug("Due to the change of the primary domain name, delete the original configuration.")
            os.system(f"rm -rf  /etc/nginx/sites-enabled/{instance.domain}.conf")
        return super(WebsiteView, self).update(request, args, kwargs)

    def partial_update(self, request, *args, **kwargs):

        kwargs['partial'] = True
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
