import os
import json
import requests

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from brd_injestion import read_excel_data
from application_discovery import discover_application


# ============================================================
# ENVIRONMENT CONFIGURATION
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = "gemini-3.5-flash-lite"

GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/{GEMINI_MODEL}:generateContent"
)


# ============================================================
# BRD + APPLICATION CONTEXT PROMPT
# ============================================================

def build_mapping_prompt(
    brd_data,
    application_context
):
    """
    Build the prompt used to map BRD requirements
    to the discovered application.

    The application discovery context is treated as
    the source of truth for what actually exists.
    """

    return f"""
You are an expert software requirements analyst and
application testing analyst.

Your task is to map BRD requirements and user stories
to the ACTUAL discovered application UI.

The BRD describes what the business expects.

The application discovery context describes what
actually exists in the application.

Your job is to determine the semantic relationship
between the two.

============================================================
IMPORTANT RULES
============================================================

1. The application discovery context is the source of truth
   for application functionality.

2. DO NOT invent any application functionality.

3. DO NOT invent pages.

4. DO NOT invent states.

5. DO NOT invent buttons.

6. DO NOT invent fields.

7. DO NOT invent workflows.

8. DO NOT invent actions.

9. DO NOT invent state IDs.

10. Every mapped state_id MUST already exist in the
    application discovery context.

11. A single BRD story may map to multiple application states.

12. Multiple BRD stories may map to the same application state.

13. Mapping must be semantic.

14. Do not rely only on exact keyword matching.

15. Use the following application evidence when determining
    a mapping:

    - page title
    - URL
    - visible UI text
    - labels
    - input fields
    - buttons
    - links
    - tables
    - forms
    - select options
    - interactive elements
    - application state
    - state transitions
    - action paths

16. A BRD story can require multiple screens or states.

17. If the application contains enough evidence to support
    the complete requirement, mark it as:

    "mapped"

18. If the application contains only part of the requirement,
    mark it as:

    "partially_mapped"

19. If there is insufficient evidence in the application
    discovery context, mark it as:

    "unmapped"

20. Never assume that a feature exists simply because the BRD
    requires it.

21. Every mapped or partially mapped story must contain
    evidence explaining why the mapping was made.

22. Confidence must be a number between 0 and 1.

23. Preserve the original BRD story ID exactly.

24. Do not modify the BRD story ID.

25. Do not return markdown.

26. Return ONLY valid JSON.

============================================================
BRD DATA
============================================================

{json.dumps(
    brd_data,
    indent=2,
    ensure_ascii=False,
    default=str
)}

============================================================
APPLICATION DISCOVERY CONTEXT
============================================================

{json.dumps(
    application_context,
    indent=2,
    ensure_ascii=False,
    default=str
)}

============================================================
OUTPUT FORMAT
============================================================

Return exactly this JSON structure:

{{
    "mappings": [
        {{
            "story_id": "US-001",

            "mapping_status": "mapped",

            "mapped_application_states": [
                {{
                    "state_id": "exact discovered state_id",
                    "url": "exact discovered URL",
                    "title": "exact discovered title"
                }}
            ],

            "mapped_ui_elements": [
                {{
                    "state_id": "exact discovered state_id",
                    "element": "exact UI element"
                }}
            ],

            "mapped_actions": [
                "exact discovered action"
            ],

            "evidence": [
                "reason supported by application discovery context"
            ],

            "confidence": 0.95
        }}
    ]
}}

============================================================
ALLOWED MAPPING STATUS
============================================================

Only these values are allowed:

"mapped"

"partially_mapped"

"unmapped"

============================================================
UNMAPPED REQUIREMENTS
============================================================

If a story is unmapped, return:

{{
    "story_id": "original story ID",
    "mapping_status": "unmapped",
    "mapped_application_states": [],
    "mapped_ui_elements": [],
    "mapped_actions": [],
    "evidence": [
        "No sufficient evidence found in the discovered application"
    ],
    "confidence": 0.0
}}

Do not invent an application state just to satisfy
the BRD requirement.
"""


# ============================================================
# APPLICATION DISCOVERY
# ============================================================

def discover_application_context(
    application_url
):
    """
    Launch Playwright and discover the application.

    Returns:
        dict:
            Complete application discovery context.
    """

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            headless=False
        )

        context = browser.new_context()

        try:

            application_context = discover_application(
                context=context,
                start_url=application_url
            )

            return application_context

        finally:

            context.close()
            browser.close()


# ============================================================
# GEMINI API CALL
# ============================================================

def call_gemini(
    brd_data,
    application_context
):
    """
    Send BRD data and application discovery context
    to Gemini and return the generated mapping.
    """

    if not GEMINI_API_KEY:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    prompt = build_mapping_prompt(
        brd_data=brd_data,
        application_context=application_context
    )

    headers = {
        "Content-Type": "application/json"
    }

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

    response = requests.post(
        GEMINI_URL,
        headers=headers,
        params={
            "key": GEMINI_API_KEY
        },
        json=payload,
        timeout=120
    )

    if not response.ok:

        raise RuntimeError(
            "Gemini API error "
            f"{response.status_code}: "
            f"{response.text}"
        )

    response_data = response.json()

    try:

        generated_text = (
            response_data
            ["candidates"][0]
            ["content"]
            ["parts"][0]
            ["text"]
        )

    except (KeyError, IndexError, TypeError):

        raise RuntimeError(
            "Unexpected Gemini API response:\n"
            + json.dumps(
                response_data,
                indent=2,
                ensure_ascii=False
            )
        )

    try:

        return json.loads(
            generated_text
        )

    except json.JSONDecodeError:

        raise RuntimeError(
            "Gemini returned invalid JSON:\n"
            + generated_text
        )


# ============================================================
# MAPPING VALIDATION
# ============================================================

def validate_mapping(
    mapping,
    application_context
):
    """
    Validate that Gemini only references states that
    actually exist in the discovered application.

    This provides a second layer of protection against
    hallucinated state IDs.
    """

    if not isinstance(mapping, dict):

        raise RuntimeError(
            "Gemini mapping must be a JSON object."
        )

    mappings = mapping.get("mappings")

    if not isinstance(mappings, list):

        raise RuntimeError(
            "Gemini response does not contain a valid "
            "'mappings' array."
        )

    discovered_states = {
        state.get("state_id"): state
        for state in application_context.get(
            "states",
            []
        )
        if state.get("state_id")
    }

    validated_mappings = []

    for item in mappings:

        if not isinstance(item, dict):
            continue

        story_id = item.get(
            "story_id"
        )

        status = item.get(
            "mapping_status"
        )

        if status not in {
            "mapped",
            "partially_mapped",
            "unmapped"
        }:

            status = "unmapped"

        mapped_states = []

        for state in item.get(
            "mapped_application_states",
            []
        ):

            if not isinstance(state, dict):
                continue

            state_id = state.get(
                "state_id"
            )

            if state_id not in discovered_states:
                continue

            actual_state = discovered_states[
                state_id
            ]

            mapped_states.append(
                {
                    "state_id": state_id,
                    "url": actual_state.get(
                        "url",
                        ""
                    ),
                    "title": actual_state.get(
                        "title",
                        ""
                    )
                }
            )

        # If Gemini claimed a mapping but all referenced
        # states were invalid, downgrade it.
        if (
            status in {
                "mapped",
                "partially_mapped"
            }
            and not mapped_states
        ):

            status = "unmapped"

        confidence = item.get(
            "confidence",
            0
        )

        try:

            confidence = float(
                confidence
            )

        except (
            TypeError,
            ValueError
        ):

            confidence = 0.0

        confidence = max(
            0.0,
            min(
                1.0,
                confidence
            )
        )

        validated_mappings.append(
            {
                "story_id": story_id,

                "mapping_status": status,

                "mapped_application_states":
                    mapped_states,

                "mapped_ui_elements":
                    item.get(
                        "mapped_ui_elements",
                        []
                    ),

                "mapped_actions":
                    item.get(
                        "mapped_actions",
                        []
                    ),

                "evidence":
                    item.get(
                        "evidence",
                        []
                    ),

                "confidence":
                    confidence
            }
        )

    return {
        "mappings": validated_mappings
    }


# ============================================================
# COMPLETE BRD → APPLICATION MAPPING PIPELINE
# ============================================================

def map_application_to_brd(
    brd_file_path,
    application_url
):
    """
    Complete end-to-end mapping pipeline.

    Flow:

        BRD Excel
            ↓
        brd_parser.py
            ↓
        BRD data

        Application URL
            ↓
        Playwright
            ↓
        application_discovery.py
            ↓
        Application context

        BRD data + Application context
            ↓
        Gemini
            ↓
        BRD ↔ Application mapping
            ↓
        Validation
            ↓
        Final result
    """

    # --------------------------------------------------------
    # STEP 1: READ BRD
    # --------------------------------------------------------

    brd_data = read_excel_data(
        brd_file_path
    )

    # --------------------------------------------------------
    # STEP 2: DISCOVER APPLICATION
    # --------------------------------------------------------

    application_context = (
        discover_application_context(
            application_url
        )
    )

    # --------------------------------------------------------
    # STEP 3: MAP BRD TO APPLICATION
    # --------------------------------------------------------

    mapping = call_gemini(
        brd_data=brd_data,
        application_context=application_context
    )

    # --------------------------------------------------------
    # STEP 4: VALIDATE GEMINI OUTPUT
    # --------------------------------------------------------

    validated_mapping = validate_mapping(
        mapping=mapping,
        application_context=application_context
    )

    # --------------------------------------------------------
    # STEP 5: RETURN COMPLETE RESULT
    # --------------------------------------------------------

    return {
        "brd": brd_data,

        "application_context":
            application_context,

        "mapping":
            validated_mapping
    }