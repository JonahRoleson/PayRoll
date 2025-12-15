from django.views.debug import SafeExceptionReporterFilter

class SafeExceptionReporterFilter(SafeExceptionReporterFilter):
    """
    Redacts sensitive settings/headers from error reports.
    Keeps errors useful without leaking secrets.
    """
    def get_post_parameters(self, request):
        data = super().get_post_parameters(request).copy()
        for k in list(data.keys()):
            if "password" in k.lower() or "token" in k.lower() or "secret" in k.lower():
                data[k] = "********"
        return data
