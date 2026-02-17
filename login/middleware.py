from django.http import HttpResponsePermanentRedirect


class StripTrailingSpacesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if path.endswith(' '):
            cleaned_path = path.rstrip(' ')
            new_url = cleaned_path
            if request.META.get('QUERY_STRING'):
                new_url = f"{cleaned_path}?{request.META['QUERY_STRING']}"
            return HttpResponsePermanentRedirect(new_url)

        return self.get_response(request)
