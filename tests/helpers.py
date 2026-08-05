from fastapi import status
from httpx import Response


def assert_validation_error(response: Response, expected_error_loc: str):
    assert_error_response(response, status.HTTP_422_UNPROCESSABLE_CONTENT, "VALIDATION_ERROR")

    data = response.json()

    assert any(expected_error_loc in err["loc"] for err in data["invalid_params"])


def assert_error_response(response: Response, expected_status: int, expected_code: str) -> None:
    assert response.status_code == expected_status

    data = response.json()

    assert data["status"] == expected_status
    assert data["code"] == expected_code
