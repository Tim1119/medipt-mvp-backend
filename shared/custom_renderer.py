from rest_framework.renderers import JSONRenderer

class SuccessJsonRenderer(JSONRenderer):
    """
    Custom renderer to wrap successful responses in a standard format
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response", None)

        # Wrap only if response is successful (no exception, 2xx codes)
        if response and not response.exception:
            wrapped_data = {
                "success": True,
                "data": data
            }
            return super().render(wrapped_data, accepted_media_type, renderer_context)

        return super().render(data, accepted_media_type, renderer_context)