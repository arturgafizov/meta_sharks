from django.utils.deprecation import MiddlewareMixin

class UserTimeTrackingMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # print('process_request')
        user = request.user

    def process_response(self, request, response):
        # print('process_response')

        return response
