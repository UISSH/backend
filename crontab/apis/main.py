from rest_framework import permissions
from rest_framework.decorators import action

from base.demo.serializers.main import MainSerializer
from base.viewset import BaseReadOnlyModelViewSet
from common.models import User
