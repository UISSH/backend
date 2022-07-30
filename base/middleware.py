import time


class PerformanceStatistics:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        request.performance_statistics_start_time = time.time()
        response = self.get_response(request)
        total = time.time() - request.performance_statistics_start_time

        # Add the header.
        response["PS-running-time"] = f"{int(total * 1000)} ms"
        response["PS-request-ip"] = self.get_client_ip(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_list = x_forwarded_for.split(',')
            if len(ip_list) == 1:
                ip = ip_list[0]
            else:
                ip = ip_list
        else:
            ip = request.META.get('REMOTE_ADDR', None)
        return ip
