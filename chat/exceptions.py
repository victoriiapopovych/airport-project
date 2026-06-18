class GeminiServiceError(Exception):
    default_message = "Internal AI assistant error. Please try again later."

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)


class GeminiServerUnavailableError(GeminiServiceError):
    default_message = "Gemini API is currently overloaded. Please try again later."


class GeminiRateLimitError(GeminiServiceError):
    default_message = "Gemini API rate limit exceeded. Please try again later."


class GeminiClientUnavailableError(GeminiServiceError):
    default_message = "Gemini API is temporarily unavailable. Please try again later."