# Firebase Cloud Functions - Appliance Assistant

This project implements a Firebase Cloud Function that provides an AI-powered chat assistant for appliance-related queries using Google's Gemini LLM.

## Overview

The service provides both authenticated and non-authenticated endpoints:
- A REST API for testing authentication
- A callable function for performing simple math operations
- A callable function for interacting with the Gemini LLM to provide appliance assistance

## Prerequisites

- Python 3.9+
- Firebase CLI
- Google Cloud Project with Firebase
- Google Gemini API key

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with:
   ```
   GOOGLE_API_KEY=your_gemini_api_key
   ```
4. Local dev with emulator:
    ```
    firebase emulators:start
    ```

5. Deploy to Firebase:
   ```
   firebase deploy --only functions
   ```

## Functions

### HTTP Endpoints

- `on_request_example_auth`: (for test) Authenticated endpoint (requires Firebase Auth token)
- `on_request_example_no_auth`: (for test) Non-authenticated endpoint for testing

### Callable Functions

- `addNumbers`: (for test) Simple function that adds two numbers
- `applianceAssistant`: Main function that processes messages with Gemini LLM to provide appliance-related assistance

## Usage

### Appliance Assistant

Call the function from your client application:

```javascript
const applianceResponse = await firebase.functions().httpsCallable('applianceAssistant')({
  messages: [
    { role: "user", content: "How do I reset my refrigerator?" }
  ],
  stream: false  // Set to true for streaming responses (not fully implemented yet)
});
```

## Development

The project consists of two main files:
- `main.py`: Defines the Firebase Cloud Functions
- `llm_service.py`: Handles interaction with the Gemini LLM

## Environment Variables

- `GOOGLE_API_KEY`: API key for Google Gemini

## License

Private
