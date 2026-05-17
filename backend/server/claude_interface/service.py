import os
from pathlib import Path
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from .models import SynthesisInput, SynthesisOutput

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_MAX_TOKENS = 1024
DEFAULT_PROMPT_PATH = Path(__file__).parent / "prompts" / "prompt.txt"
SERVER_ENV_PATH = Path(__file__).resolve().parents[1] / ".env" 


class ClaudeConfigurationError(RuntimeError):
    """Raised when the Claude API is called without valid configuration."""


class ClaudeService:
    """
    Isolated Claude API adapter for backend modules.

    The service can be constructed without an API key so local development and tests
    can start normally. It raises a config error only when a call is made.
    """
    
    # Initialise the service
    def __init__(
        self,
        api_key: str | None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        system_prompt_path: Path = DEFAULT_PROMPT_PATH,
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.system_prompt_path = system_prompt_path
        self._client = AsyncAnthropic(api_key=api_key) if api_key else None 

    # Loads the service from the environment
    @classmethod
    def from_env(cls) -> "ClaudeService":
        load_dotenv(SERVER_ENV_PATH)

        max_tokens = os.getenv("CLAUDE_MAX_TOKENS", str(DEFAULT_MAX_TOKENS))

        try:
            parsed_max_tokens = int(max_tokens)
        except ValueError as exc:
            raise ClaudeConfigurationError(
                "CLAUDE_MAX_TOKENS must be an integer"
            ) from exc
        if parsed_max_tokens <= 0:
            raise ClaudeConfigurationError(
                "CLAUDE_MAX_TOKENS must be greater than zero"
            )

        return cls(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            model=os.getenv("CLAUDE_MODEL", DEFAULT_MODEL),
            max_tokens=parsed_max_tokens,
            system_prompt_path=Path(
                os.getenv("CLAUDE_SYSTEM_PROMPT_PATH", str(DEFAULT_PROMPT_PATH))
            ),
        )

    # Checks if the client is configured
    @property
    def is_configured(self) -> bool:
        return self._client is not None

    # Generate synthesis
    async def generate_synthesis(
        self, activity_data: SynthesisInput
    ) -> SynthesisOutput:
        if self._client is None:
            raise ClaudeConfigurationError("ANTHROPIC_API_KEY is not configured")

        # Calls the Claude API
        response = await self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self._load_system_prompt(),
            messages=[
                {
                    "role": "user",
                    "content": activity_data.activity_data,
                }
            ],
        )

        # Parses text responses into SynthesisOutput
        text_parts = []
        for content in response.content:
            text = getattr(content, "text", None)
            if text is not None:
                text_parts.append(text)

        return SynthesisOutput(text="\n".join(text_parts))

    # Loads system prompt from prompt.txt
    def _load_system_prompt(self) -> str:
        if not self.system_prompt_path.exists():
            raise ClaudeConfigurationError(
                f"Claude system prompt not found: {self.system_prompt_path}"
            )

        return self.system_prompt_path.read_text(encoding="utf-8").strip()
