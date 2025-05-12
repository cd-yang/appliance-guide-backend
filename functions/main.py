# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from typing import Any

import llm_service
from firebase_admin import auth, initialize_app
from firebase_functions import https_fn, options, params

initialize_app()

options.set_global_options(
    region=options.SupportedRegion.US_EAST1,
    # memory=options.MemoryOption.MB_128,
    # min_instances=params.IntParam("MIN", default=3),
)


# test api
@https_fn.on_request(
    # cors=options.CorsOptions(
    #     cors_origins="*",
    #     cors_methods=["get", "post", "options"])
)
def on_request_example_auth(req: https_fn.Request) -> https_fn.Response:
    # Check for Authorization header
    if 'Authorization' not in req.headers:
        return https_fn.Response('Unauthorized - No auth token provided', status=401)

    auth_header = req.headers['Authorization']
    # Bearer token format: "Bearer <token>"
    if not auth_header.startswith('Bearer '):
        return https_fn.Response('Unauthorized - Invalid auth header format', status=401)

    id_token = auth_header.split('Bearer ')[1]

    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        # Continue with the function logic for authenticated users
        return https_fn.Response(f"Hello authenticated user {uid}!")
    except Exception as e:
        return https_fn.Response(f'Unauthorized - Invalid token: {str(e)}', status=401)


# test api
@https_fn.on_request(
    # cors=options.CorsOptions(
    #     cors_origins="*",
    #     cors_methods=["get", "post", "options"])
)
def on_request_example_no_auth(req: https_fn.Request) -> https_fn.Response:
    return https_fn.Response("<h1>Hello world!</h1>")


# test api
@https_fn.on_call(
    cors=options.CorsOptions(
        cors_origins="*",
        cors_methods=["get", "post", "options"])
)
def addNumbers(req: https_fn.CallableRequest) -> Any:
    """Adds two numbers to each other."""
    # [START v2addHttpsError]
    # Checking that attributes are present and are numbers.
    try:
        # [START v2readAddData]
        # Numbers passed from the client.
        first_number_param = req.data["firstNumber"]
        second_number_param = req.data["secondNumber"]
        # [END v2readAddData]
        first_number = int(first_number_param)
        second_number = int(second_number_param)
    except (ValueError, KeyError):
        # Throwing an HttpsError so that the client gets the error details.
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
            message=('The function must be called with two arguments, "firstNumber"'
                     ' and "secondNumber", which must both be numbers.'))
    # [END v2addHttpsError]

    # [START v2returnAddData]
    return {
        "firstNumber": first_number,
        "secondNumber": second_number,
        "operator": "+",
        "operationResult": first_number + second_number
    }
    # [END v2returnAddData]
# [END v2allAdd]


@https_fn.on_call(
    cors=options.CorsOptions(
        cors_origins="*",
        cors_methods=["post"])
)
def applianceAssistant(req: https_fn.CallableRequest) -> Any:
    """LLM chat assistant for appliance."""
    try:
        messages = req.data["messages"]
        stream = req.data.get("stream", False)
    except (ValueError, KeyError):
        # Throwing an HttpsError so that the client gets the error details.
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
            message=('The function must be called with "messages" field.'))

    if stream:
        return llm_service.process_chat_request(messages)
        # TODO: should return SSE stream, but onCall python does not support SSE stream yet
        # yield llm_service.process_streaming_chat_request(messages)
    else:
        return llm_service.process_chat_request(messages)
