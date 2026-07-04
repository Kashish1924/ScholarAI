from flask import jsonify


def success_response(message: str, data=None, status_code: int = 200):
    """Return a consistent success JSON payload."""
    payload = {
        "status": "success",
        "message": message,
        "data": data,
    }
    return jsonify(payload), status_code


def error_response(message: str, errors=None, status_code: int = 400):
    """Return a consistent error JSON payload."""
    payload = {
        "status": "error",
        "message": message,
        "errors": errors or {},
    }
    return jsonify(payload), status_code
