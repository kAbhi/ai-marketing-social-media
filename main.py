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
# Task 1: Design Input Parameters
# - Define key variables: brand_voice, target_audience, campaign_type, key_message, platform, etc.
# - Create input validation and processing logic.
# - Structure data for optimal prompt generation.
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
    """
    Validates input variables and structures them into a clean dictionary
    for downstream dynamic prompt construction.
    """
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

    # Input validation: Ensure required parameters are non-empty strings
    for field, value in inputs.items():
        if isinstance(value, str) and not value.strip():
            raise ValueError(f"Input validation error: '{field}' cannot be empty.")

    return inputs


# ============================================================================
# Task 2: Implement Dynamic Prompt Generation
# - Create prompts incorporating validated user inputs.
# - Include explicit context regarding brand voice and audience.
# - Specify concrete output format, constraints, and platform style requirements.
# ============================================================================

def generate_dynamic_prompt(params: Dict[str, str]) -> str:
    """
    Builds a structured dynamic prompt incorporating all brand guidelines,
    audience details, campaign goals, and output requirements.
    """
    prompt = f"""You are an expert social media strategist and copywriter. Generate a high-performing social media post based on the following brand parameters and campaign objectives:

<campaign_parameters>
- Brand Name: {params['brand_name']}
- Brand Voice / Tone: {params['brand_voice']}
- Target Audience: {params['target_audience']}
- Campaign Type: {params['campaign_type']}
- Key Message: {params['key_message']}
- Destination Platform: {params['platform']}
- Call to Action (CTA): {params['call_to_action']}
- Hashtag Requirement: {params['hashtags_required']}
</campaign_parameters>

<instructions>
1. Match the exact tone and style of the specified brand voice.
2. Tailor language, hooks, and pacing directly to the target audience.
3. Optimize formatting (line breaks, hook, CTA placement) specifically for {params['platform']}.
4. Present the output strictly in the following format:

[HOOK / HEADLINE]
<attention-grabbing opening line>

[BODY]
<engaging core post content reinforcing the key message>

[CALL TO ACTION]
<clear CTA directive>

[HASHTAGS]
<comma-separated hashtags if required, otherwise omit>
</instructions>

Provide only the formatted post content without extra conversational filler.
"""
    return prompt.strip()


# ============================================================================
# Task 3: Build Response Processing
# - Implement API call with the dynamic prompt.
# - Process Claude's response for consistency.
# - Format output cleanly for social media deployment/review.
# ============================================================================

def generate_social_post(params: Dict[str, str], model: str = "claude-opus-5") -> Dict[str, str]:
    """
    Executes the Anthropic Messages API call using the generated dynamic prompt,
    parses the response, and formats the output for client review.
    """
    prompt = generate_dynamic_prompt(params)

    # API Integration
    response = client.messages.create(
        model=model,
        max_tokens=600,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    raw_text = response.content[0].text.strip()

    # Response processing and structure verification
    return {
        "platform": params["platform"],
        "brand": params["brand_name"],
        "campaign_type": params["campaign_type"],
        "generated_post": raw_text,
        "input_summary": f"Voice: '{params['brand_voice']}' | Audience: '{params['target_audience']}'"
    }


def display_post(result: Dict[str, str]) -> None:
    """Utility to print processed social media post cleanly."""
    separator = "=" * 60
    print(f"\n{separator}")
    print(f"BRAND: {result['brand']} | PLATFORM: {result['platform']}")
    print(f"CONFIG: {result['input_summary']}")
    print(separator)
    print(result["generated_post"])
    print(f"{separator}\n")


# ============================================================================
# Execution & Example Outputs Demonstrating Different Brand Voices
# ============================================================================

if __name__ == "__main__":
    # Example 1: B2B Enterprise / Thought Leadership Voice
    tech_b2b_campaign = validate_and_structure_input(
        brand_name="CloudScale Systems",
        brand_voice="Authoritative, analytical, visionary, and professional",
        target_audience="CTOs, VP of Engineering, and Cloud Architects",
        campaign_type="Product Launch / Thought Leadership",
        key_message="Our new distributed data mesh reduces cross-region query latency by 45%.",
        platform="LinkedIn",
        call_to_action="Read the technical whitepaper and benchmarks",
        hashtags_required=True
    )

    # Example 2: D2C Lifestyle / Casual & Energetic Voice
    d2c_lifestyle_campaign = validate_and_structure_input(
        brand_name="BrewRoots Coffee Co.",
        brand_voice="Playful, energetic, relatable, and community-driven",
        target_audience="Young professionals and remote workers who need a morning boost",
        campaign_type="Limited Edition Seasonal Drop",
        key_message="Cold brew concentrate infused with organic Madagascar vanilla is back in stock.",
        platform="Instagram",
        call_to_action="Tap the link in bio to grab your bottle before it sells out!",
        hashtags_required=True
    )

    print("Generating Campaign 1: B2B Enterprise...")
    result_1 = generate_social_post(tech_b2b_campaign)
    display_post(result_1)

    print("Generating Campaign 2: D2C Lifestyle...")
    result_2 = generate_social_post(d2c_lifestyle_campaign)
    display_post(result_2)