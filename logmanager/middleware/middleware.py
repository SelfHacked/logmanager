"""Middleware to log requests."""

import logging

logger = logging.getLogger('app.request')


def get_client_ip(request, default='') -> str:
    """
    Get User's IP Address.

    This functions extract user's ip address according to following spec.
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For

    Warning: This IP address might not be user's real IP address,
      since the user can send false headers to the server.
      It is advised to use a middleware that logs HTTP_X_FORWARDED_FOR and
      REMOTE_ADDR for traceability.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR') or ''
    if x_forwarded_for.strip():
        ip_address = str(x_forwarded_for.split(',')[0])
    else:
        ip_address = str(request.META.get('REMOTE_ADDR', default))

    return ip_address.strip()


class LogRequestMiddleware:
    """Log requests middleware."""

    NO_VALUE_MARKER = '-'

    def __init__(self, get_response):
        """Initializer."""
        self.get_response = get_response

    def __call__(self, request):
        """Log request information and response code."""
        response = None

        try:
            response = self.get_response(request)
        finally:
            self._log_request(request, response)

        return response

    def _log_request(self, request, response):
        client_ip = get_client_ip(request, self.NO_VALUE_MARKER)
        remote_addr = self._get_value(request, 'REMOTE_ADDR')
        x_forwarded_for = self._get_value(request, 'HTTP_X_FORWARDED_FOR')
        user_agent = self._get_value(request, 'HTTP_USER_AGENT')
        method = self._get_value(request, 'REQUEST_METHOD')
        path = self._get_value(request, 'PATH_INFO')
        status_code = response.status_code if response else 500
        user_id = self._get_user_id(request)

        logger.info(' '.join([
            client_ip,
            f'{remote_addr},{x_forwarded_for}',
            f'"{method} {path}"',
            str(user_id),
            str(status_code),
            f'"{user_agent}"',
        ]))

    def _get_user_id(self, request) -> str:
        user_id = None
        if request.user:
            user_id = request.user.id

        return user_id or self.NO_VALUE_MARKER

    def _get_value(self, request, key):
        return request.META.get(key, self.NO_VALUE_MARKER)
