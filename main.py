import os
from typing import Dict, List, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

# ============================================================================
# Environment Setup & Client Initialization
# ============================================================================
load_dotenv()
my_api_key = os.getenv("ANTHROPIC_API_KEY")

if not my_api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set. Please set it in your .env file.")

client = Anthropic(api_key=my_api_key)


# ============================================================================
# Parameter Validation & Setup
# ============================================================================
def validate_and_structure_input(
        brand_name: str,
        brand_voice: str,
        target_audience: str,
        campaign_type: str,
        key_message: str,
        platform: str = "LinkedIn",
        call_to_action: Optional[str] = None,
        hashtags_required: bool = True
) -> Dict[str, str]:
    """Validates inputs and structures brand guidelines."""
    inputs = {
        "brand_name": brand_name,
        "brand_voice": brand_voice,
        "target_audience": target_audience,
        "campaign_type": campaign_type,
        "key_message": key_message,
        "platform": platform,
        "call_to_action": call_to_action or "Learn more through the link below.",
        "hashtags_required": "Yes (3-5 relevant hashtags)" if hashtags_required else "No hashtags"
    }

    for field, value in inputs.items():
        if isinstance(value, str) and not value.strip():
            raise ValueError(f"Input validation error: '{field}' cannot be empty.")

    return inputs


# ============================================================================
# Multi-Turn Dialogue Manager
# ============================================================================
class SocialMediaDialogueSession:
    """
    Manages multi-turn conversation state, system prompt anchoring,
    and iterative refinement of social media copy.
    """
    def __init__(self, brand_params: Dict[str, str], model: str = "claude-opus-5", max_history_turns: int = 10):
        self.brand_params = brand_params
        self.model = model
        self.max_history_turns = max_history_turns
        self.messages: List[Dict[str, str]] = []

    def _build_system_prompt(self) -> str:
        """Anchors brand voice and format rules as immutable system context."""
        return f"""You are an expert social media copywriter and brand strategist working on a live revision session.

<brand_guidelines>
- Brand Name: {self.brand_params['brand_name']}
- Core Voice & Tone: {self.brand_params['brand_voice']}
- Target Audience: {self.brand_params['target_audience']}
- Campaign Objective: {self.brand_params['campaign_type']}
- Key Message: {self.brand_params['key_message']}
- Platform: {self.brand_params['platform']}
- Target CTA: {self.brand_params['call_to_action']}
- Hashtags: {self.brand_params['hashtags_required']}
</brand_guidelines>

<formatting_rules>
When drafting or revising posts, output the final post using these structural slots:
[HOOK / HEADLINE]
<opening hook>

[BODY]
<core copy reinforcing key message>

[CALL TO ACTION]
<clear directive>

[HASHTAGS]
<relevant hashtags or omit if requested>
</formatting_rules>

Adhere strictly to the brand voice across all revisions. If the user asks for iterative tweaks (e.g., tone shifts, shorter lengths, or alternate angles), adjust accordingly while keeping the core identity intact."""

    def _trim_history(self) -> None:
        """Sliding window: retains the most recent turns to maintain token efficiency."""
        # Keep the latest N message pairs (user + assistant)
        max_messages = self.max_history_turns * 2
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]

    def send_turn(self, user_instruction: str) -> str:
        """
        Processes a user turn, appends it to conversation history,
        calls the Anthropic API, and captures the assistant response.
        """
        self.messages.append({"role": "user", "content": user_instruction})
        self._trim_history()

        response = client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=self._build_system_prompt(),
            messages=self.messages
        )

        assistant_reply = response.content[1].text.strip()
        self.messages.append({"role": "assistant", "content": assistant_reply})
        return assistant_reply

    def start_campaign(self) -> str:
        """Initial turn: generates the initial baseline post."""
        initial_prompt = (
            f"Generate the initial social media post for {self.brand_params['platform']} "
            f"reinforcing our key message: '{self.brand_params['key_message']}'."
        )
        return self.send_turn(initial_prompt)


# ============================================================================
# Interactive Terminal Runner (CLI)
# ============================================================================
def run_interactive_session():
    # 1. Define initial campaign parameters from user input
    print("=" * 70)
    print(" Enter Initial Campaign Parameters:")
    print("=" * 70)

    brand_name = input("Enter Brand Name (e.g., CloudScale Systems): ").strip()
    brand_voice = input("Enter Brand Voice/Tone (e.g., Authoritative, analytical, visionary): ").strip()
    target_audience = input("Enter Target Audience (e.g., CTOs, VP of Engineering, Cloud Architects): ").strip()
    campaign_type = input("Enter Campaign Type (e.g., Product Launch / Thought Leadership): ").strip()
    key_message = input("Enter Key Message (e.g., Our new distributed data mesh reduces latency by 45%): ").strip()

    platform_input = input("Enter Platform [default: LinkedIn]: ").strip()
    platform = platform_input if platform_input else "LinkedIn"

    cta_input = input("Enter Call to Action [default: Learn more through the link below.]: ").strip()
    call_to_action = cta_input if cta_input else None

    hashtags_input = input("Include Hashtags? (yes/no) [default: yes]: ").strip().lower()
    hashtags_required = hashtags_input not in ("no", "n", "false")

    campaign_config = validate_and_structure_input(
        brand_name=brand_name,
        brand_voice=brand_voice,
        target_audience=target_audience,
        campaign_type=campaign_type,
        key_message=key_message,
        platform=platform,
        call_to_action=call_to_action,
        hashtags_required=hashtags_required
    )

    # 2. Initialize dialogue manager
    session = SocialMediaDialogueSession(brand_params=campaign_config)

    print("=" * 70)
    print(f" Starting session for: {campaign_config['brand_name']} ({campaign_config['platform']})")
    print(" Type your refinement commands (e.g., 'Make the hook punchier', 'Shorter').")
    print(" Type 'exit' or 'quit' to end the session.")
    print("=" * 70)

    # 3. Generate initial post (Turn 1)
    print("\n[Generating Initial Post...]\n")
    initial_post = session.start_campaign()
    print(f"Claude:\n{initial_post}\n")

    # 4. Multi-turn dialogue loop
    while True:
        try:
            user_input = input("You (revision / feedback) > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("\nEnding session. Happy publishing!")
                break

            print("\n[Revising with Claude...]\n")
            reply = session.send_turn(user_input)
            print(f"Claude:\n{reply}\n")

        except KeyboardInterrupt:
            print("\nSession interrupted. Exiting.")
            break


if __name__ == "__main__":
    run_interactive_session()