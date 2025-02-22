from run import app
from src.commons.payload.response_handler import ResponseHandler

@app.errorhandler(Exception)
def handle_generic_exception(error):
    return ResponseHandler.error_from_exception(error, error.status_code)
