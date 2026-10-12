
import os
import json
import time
import random
import requests

from collections import deque
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-3.5-flash-lite"

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    f"models/{GEMINI_MODEL}:generateContent"
)

# Rate limit: at most 3 story requests per rolling 60 seconds.
MAX_STORIES_PER_MINUTE = 3
RATE_LIMIT_WINDOW_SECONDS = 60

# Retry settings for Gemini rate-limit errors.
MAX_RETRIES = 5
INITIAL_RETRY_DELAY = 5
MAX_RETRY_DELAY = 60


class StoryRateLimiter:
    """Limits story request starts to 3 per rolling minute."""

    def __init__(self):
        self.request_times = deque()

    def wait_for_slot(self):
        while True:
            now = time.monotonic()

            # Remove requests outside the rolling 60-second window.
            while (
                self.request_times
                and now - self.request_times[0]
                >= RATE_LIMIT_WINDOW_SECONDS
            ):
                self.request_times.popleft()

            if len(self.request_times) < MAX_STORIES_PER_MINUTE:
                self.request_times.append(now)
                return

            wait_seconds = (
                RATE_LIMIT_WINDOW_SECONDS
                - (now - self.request_times[0])
            )

            print(
                f"Rate limit reached. "
                f"Waiting {wait_seconds:.1f} seconds..."
            )

            time.sleep(max(wait_seconds, 0.1))


def read_test_case_prompt(prompt_file_path):
    with open(
        prompt_file_path,
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()


def build_test_case_prompt(
    base_prompt,
    user_story,
    application_context,
    story_mapping
):
    return f"""
{base_prompt}

==================================================
CURRENT USER STORY
==================================================

{json.dumps(
    user_story,
    indent=2,
    ensure_ascii=False
)}

==================================================
COMPLETE APPLICATION CONTEXT
==================================================

Use the complete discovered application context.
Do not assume that the mapping contains every relevant
state, element, action, navigation path or dependency.

{json.dumps(
    application_context,
    indent=2,
    ensure_ascii=False
)}

==================================================
MAPPING FOR CURRENT USER STORY
==================================================

Use this mapping as guidance, not as a restriction
on relevant evidence available in the complete context.

{json.dumps(
    story_mapping,
    indent=2,
    ensure_ascii=False
)}

==================================================
TEST GENERATION REQUIREMENTS
==================================================

1. Generate test cases for the CURRENT USER STORY ONLY.

2. Analyze every acceptance criterion individually.

3. Generate MULTIPLE meaningful test cases wherever
   different scenarios are required. Do not produce
   only one test case for the entire story.

4. Cover applicable positive, negative, boundary,
   validation, navigation and state-transition scenarios.

5. Do not create redundant test cases merely to increase
   the count. Each test case must verify a meaningful
   scenario.

6. Include accurate steps and expected results grounded
   in the BRD and discovered application context.

7. Use the complete application context to resolve
   dependencies omitted by the mapping.

8. Never invent application functionality, UI elements,
   actions, application states or state IDs.

9. Preserve the output schema specified in the base prompt.

10. Return every generated test case in the "test_cases"
    array. Return valid JSON only.

Return this structure, preserving any required fields
specified by the base prompt:

{{
    "test_cases": [
        ...
    ]
}}
"""


def generate_test_cases_for_story(
    base_prompt,
    user_story,
    application_context,
    story_mapping,
    session=None
):
    prompt = build_test_case_prompt(
        base_prompt=base_prompt,
        user_story=user_story,
        application_context=application_context,
        story_mapping=story_mapping
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }

    http = session or requests

    for attempt in range(MAX_RETRIES + 1):
        response = http.post(
            GEMINI_URL,
            headers={
                "Content-Type": "application/json"
            },
            params={
                "key": GEMINI_API_KEY
            },
            json=payload,
            timeout=180
        )

        if response.status_code == 429:
            if attempt == MAX_RETRIES:
                raise RuntimeError(
                    f"Gemini rate limit persisted after "
                    f"{MAX_RETRIES} retries for story "
                    f"{user_story.get('ID', 'UNKNOWN')}: "
                    f"{response.text}"
                )

            retry_after = response.headers.get("Retry-After")

            if retry_after:
                try:
                    delay = float(retry_after)
                except ValueError:
                    delay = min(
                        INITIAL_RETRY_DELAY * (2 ** attempt),
                        MAX_RETRY_DELAY
                    )
            else:
                delay = min(
                    INITIAL_RETRY_DELAY * (2 ** attempt),
                    MAX_RETRY_DELAY
                )
                delay += random.uniform(0, 1)

            print(
                f"Gemini returned 429 for story "
                f"{user_story.get('ID', 'UNKNOWN')}. "
                f"Retrying in {delay:.1f} seconds "
                f"(attempt {attempt + 1}/{MAX_RETRIES})."
            )

            time.sleep(delay)
            continue

        if response.status_code != 200:
            raise RuntimeError(
                f"Gemini API error {response.status_code}: "
                f"{response.text}"
            )

        response_data = response.json()

        try:
            generated_text = (
                response_data["candidates"][0]
                ["content"]["parts"][0]["text"]
            )
        except (KeyError, IndexError, TypeError) as error:
            raise RuntimeError(
                f"Unexpected Gemini response for story "
                f"{user_story.get('ID', 'UNKNOWN')}: "
                f"{response.text}"
            ) from error

        try:
            result = json.loads(generated_text)
        except json.JSONDecodeError as error:
            raise RuntimeError(
                f"Gemini returned invalid JSON for story "
                f"{user_story.get('ID', 'UNKNOWN')}: "
                f"{error}"
            ) from error

        if not isinstance(result, dict):
            raise RuntimeError(
                f"Expected a JSON object for story "
                f"{user_story.get('ID', 'UNKNOWN')}"
            )

        if not isinstance(result.get("test_cases"), list):
            raise RuntimeError(
                f"Missing or invalid 'test_cases' array for "
                f"story {user_story.get('ID', 'UNKNOWN')}"
            )

        return result

    raise RuntimeError("Unexpected retry loop termination")


def generate_test_cases(
    brd,
    application_context,
    mapping,
    prompt_file_path
):
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not configured"
        )

    base_prompt = read_test_case_prompt(
        prompt_file_path
    )

    user_stories = brd.get("User Stories", [])

    if not user_stories:
        raise ValueError("No user stories found in BRD")

    mappings = mapping.get("mappings", [])

    mapping_by_story_id = {
        str(item.get("story_id")): item
        for item in mappings
        if item.get("story_id") is not None
    }

    # Keep one limiter for the entire generation run.
    rate_limiter = StoryRateLimiter()

    all_test_cases = []
    story_results = []
    processed_story_count = 0

    with requests.Session() as session:
        for user_story in user_stories:
            story_id = user_story.get("ID")

            if story_id is None or not str(story_id).strip():
                print("Skipping story with missing ID.")
                continue

            story_id_key = str(story_id)

            story_mapping = mapping_by_story_id.get(
                story_id_key
            )

            if story_mapping is None:
                story_mapping = {
                    "story_id": story_id,
                    "mapping_status": "unmapped",
                    "mapped_application_states": [],
                    "mapped_ui_elements": [],
                    "mapped_actions": [],
                    "evidence": [],
                    "confidence": 0
                }

            print(
                f"\nPreparing story {story_id} "
                f"({processed_story_count + 1})"
            )

            # A slot is reserved immediately before each
            # story request, including a request that retries.
            rate_limiter.wait_for_slot()

            print(
                f"Generating multiple test cases "
                f"for story {story_id}..."
            )

            result = generate_test_cases_for_story(
                base_prompt=base_prompt,
                user_story=user_story,
                application_context=application_context,
                story_mapping=story_mapping,
                session=session
            )

            story_test_cases = result["test_cases"]

            all_test_cases.extend(story_test_cases)
            processed_story_count += 1

            story_results.append({
                "story_id": story_id,
                "test_case_count": len(story_test_cases)
            })

            print(
                f"Generated {len(story_test_cases)} "
                f"test cases for story {story_id}"
            )

    return {
        "test_cases": all_test_cases,
        "metadata": {
            "user_story_count": len(user_stories),
            "processed_story_count": processed_story_count,
            "test_case_count": len(all_test_cases),
            "stories_per_minute_limit": MAX_STORIES_PER_MINUTE,
            "story_results": story_results
        }
    }
