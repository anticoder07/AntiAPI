from src.payloads.responses.response_handler import ResponseHandler


def handle_generic_exception(error):
    return ResponseHandler.error_from_exception(error, getattr(error, 'status_code', 500))
