import os
import subprocess
from iptables.serializers.main import IPTablesRuleSerializer
from rest_framework import permissions

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSetMixin

from drf_spectacular.utils import extend_schema


class IPTablesView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(responses=IPTablesRuleSerializer(many=True))
    @action(methods=["get"], detail=False)
    def get_rules(self, request):
        result = subprocess.run(["ufw", "status"], capture_output=True, text=True)
        output = result.stdout
        if "inactive" in output:
            area = []
        else:
            lines = output.splitlines()
            first = lines[2].find("To")
            second = lines[2].find("Action")
            third = lines[2].find("From")
            area = []
            for index, line in enumerate(lines[4:]):
                if not line:
                    continue
                To = line[first:second]
                Action = line[second:third]
                From = line[third:]
                data = {
                    "id": index + 1,
                    "to": To.strip(),
                    "action": Action.strip(),
                    "from_src": From.strip(),
                }
                area.append(data)
        return Response(
            {
                "pagination": {
                    "total_pages": 1,
                    "total": len(area),
                    "page": 1,
                    "per_page": len(area),
                },
                "results": area,
            }
        )
