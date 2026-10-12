import hashlib

import json

import re

from collections import deque

from typing import Any, Dict, List, Optional

from playwright.sync_api import Page, BrowserContext

# ============================================================

# DOM CONFIGURATION

# ============================================================

VALID_ATTRIBUTES = {

    "id",

    "name",

    "type",

    "placeholder",

    "href",

    "role",

    "required",

    "disabled",

    "readonly",

    "checked",

    "selected",

    "min",

    "max",

    "step",

    "pattern",

    "maxlength",

    "minlength",

    "autocomplete",

    "title",

    "data-testid",

    "aria-label",

    "aria-labelledby",

    "aria-describedby",

}

MEANINGFUL_TAGS = {

    "html",

    "body",

    "main",

    "nav",

    "header",

    "footer",

    "section",

    "article",

    "aside",

    "h1",

    "h2",

    "h3",

    "h4",

    "h5",

    "h6",

    "p",

    "label",

    "form",

    "input",

    "textarea",

    "select",

    "option",

    "button",

    "a",

    "table",

    "thead",

    "tbody",

    "tfoot",

    "tr",

    "th",

    "td",

    "ul",

    "ol",

    "li",

    "fieldset",

    "legend",

}

IGNORED_TAGS = {

    "script",

    "style",

    "noscript",

    "template",

    "svg",

    "canvas",

    "iframe",

    "meta",

    "link",

}

FRAMEWORK_ID_PATTERNS = [

    r"^\_\_",

    r"^react",

    r"^vue",

    r"^ng-",

    r"^ember",

]

DANGEROUS_WORDS = {

    "delete",

    "remove",

    "destroy",

    "logout",

    "log out",

    "sign out",

    "pay",

    "purchase",

    "transfer",

    "approve",

    "reject",

    "terminate",

    "close account",

}

# ============================================================

# DISCOVERY LIMITS

# ============================================================

MAX_STATES = 100

MAX_DEPTH = 8

# ============================================================

# HELPERS

# ============================================================

def normalize_text(text: Optional[str]) -> str:

    if not text:

        return ""

    text = re.sub(r"\s+", " ", text)

    return text.strip()

def normalize_url(url: str) -> str:

    return url.split("#")[0]

def is_framework_generated_id(value: str) -> bool:

    for pattern in FRAMEWORK_ID_PATTERNS:

        if re.search(

            pattern,

            value,

            re.IGNORECASE

        ):

            return True

    return False

def contains_dangerous_word(text: str) -> bool:

    text = normalize_text(text).lower()

    return any(

        word in text

        for word in DANGEROUS_WORDS

    )

# ============================================================

# SANITIZED DOM EXTRACTION

# ============================================================

def extract_sanitized_dom(

    page: Page

) -> Dict[str, Any]:

    """

    Extracts the application DOM into a clean,

    testing-oriented representation.

    CSS classes, inline styles, scripts,

    framework internals and runtime values

    are intentionally excluded.

    """

    return page.evaluate(

        r"""

        ({

            meaningfulTags,

            validAttributes,

            ignoredTags,

            frameworkIdPatterns

        }) => {

            function normalizeText(text) {

                if (!text) {

                    return "";

                }

                return text

                    .replace(/\s+/g, " ")

                    .trim();

            }

            function isVisible(element) {

                const style =

                    window.getComputedStyle(element);

                const rect =

                    element.getBoundingClientRect();

                return (

                    style.display !== "none" &&

                    style.visibility !== "hidden" &&

                    style.opacity !== "0" &&

                    rect.width > 0 &&

                    rect.height > 0

                );

            }

            function isFrameworkId(value) {

                if (!value) {

                    return false;

                }

                return frameworkIdPatterns.some(

                    pattern =>

                        new RegExp(

                            pattern,

                            "i"

                        ).test(value)

                );

            }

            function getDirectText(element) {

                let text = "";

                for (

                    const node

                    of element.childNodes

                ) {

                    if (

                        node.nodeType === Node.TEXT_NODE

                    ) {

                        text +=

                            " " +

                            node.textContent;

                    }

                    if (

                        node.nodeType === Node.ELEMENT_NODE &&

                        ["LABEL", "OPTION"]

                            .includes(node.nodeName)

                    ) {

                        text +=

                            " " +

                            node.textContent;

                    }

                }

                return normalizeText(text);

            }

            function getAttributes(element) {

                const result = {};

                for (

                    const attribute

                    of element.attributes

                ) {

                    const name =

                        attribute.name;

                    const value =

                        attribute.value;

                    const lowerName =

                        name.toLowerCase();

                    // Remove CSS classes.

                    if (lowerName === "class") {

                        continue;

                    }

                    // Remove inline styles.

                    if (lowerName === "style") {

                        continue;

                    }

                    const isAllowed =

                        validAttributes.includes(

                            lowerName

                        ) ||

                        lowerName.startsWith(

                            "aria-"

                        );

                    if (!isAllowed) {

                        continue;

                    }

                    // Remove framework-generated IDs.

                    if (

                        lowerName === "id" &&

                        isFrameworkId(value)

                    ) {

                        continue;

                    }

                    // Do not capture entered values.

                    if (

                        lowerName === "value"

                    ) {

                        continue;

                    }

                    result[lowerName] =

                        normalizeText(value);

                }

                return result;

            }

            function isInteractive(element) {

                const tag =

                    element.tagName.toLowerCase();

                if (

                    [

                        "button",

                        "a",

                        "input",

                        "select",

                        "textarea"

                    ].includes(tag)

                ) {

                    return true;

                }

                const role =

                    element.getAttribute(

                        "role"

                    );

                if (

                    role &&

                    [

                        "button",

                        "link",

                        "tab",

                        "menuitem",

                        "checkbox",

                        "radio"

                    ].includes(role)

                ) {

                    return true;

                }

                return element.hasAttribute(

                    "onclick"

                );

            }

            function getElementLabel(element) {

                const ariaLabel =

                    element.getAttribute(

                        "aria-label"

                    );

                if (ariaLabel) {

                    return normalizeText(

                        ariaLabel

                    );

                }

                const labelledBy =

                    element.getAttribute(

                        "aria-labelledby"

                    );

                if (labelledBy) {

                    const labels =

                        labelledBy

                            .split(/\s+/)

                            .map(

                                id =>

                                    document

                                        .getElementById(id)

                            )

                            .filter(Boolean)

                            .map(

                                el =>

                                    normalizeText(

                                        el.innerText

                                    )

                            )

                            .filter(Boolean);

                    if (labels.length) {

                        return labels.join(" ");

                    }

                }

                if (element.id) {

                    const label =

                        document.querySelector(

                            `label[for="${CSS.escape(element.id)}"]`

                        );

                    if (label) {

                        return normalizeText(

                            label.innerText

                        );

                    }

                }

                const parentLabel =

                    element.closest("label");

                if (parentLabel) {

                    return normalizeText(

                        parentLabel.innerText

                    );

                }

                return "";

            }

            function buildNode(element) {

                if (

                    !element ||

                    element.nodeType !==

                        Node.ELEMENT_NODE

                ) {

                    return null;

                }

                const tag =

                    element.tagName.toLowerCase();

                if (

                    ignoredTags.includes(tag)

                ) {

                    return null;

                }

                if (!isVisible(element)) {

                    return null;

                }

                const children = [];

                for (

                    const child

                    of element.children

                ) {

                    const childNode =

                        buildNode(child);

                    if (childNode) {

                        children.push(

                            childNode

                        );

                    }

                }

                const directText =

                    getDirectText(element);

                const attributes =

                    getAttributes(element);

                const node = {

                    tag

                };

                if (directText) {

                    node.text =

                        directText;

                }

                if (

                    Object.keys(attributes)

                        .length > 0

                ) {

                    node.attributes =

                        attributes;

                }

                if (

                    isInteractive(element)

                ) {

                    node.interactive =

                        true;

                }

                const label =

                    getElementLabel(element);

                if (label) {

                    node.label =

                        label;

                }

                if (tag === "select") {

                    const options =

                        Array.from(

                            element.options || []

                        ).map(option => ({

                            text:

                                normalizeText(

                                    option.textContent

                                ),

                            value:

                                option.value,

                            selected:

                                option.selected

                        }));

                    if (options.length > 0) {

                        node.options =

                            options;

                    }

                }

                if (children.length > 0) {

                    node.children =

                        children;

                }

                /*

                 * Collapse meaningless wrapper

                 * elements while preserving their

                 * useful children.

                 */

                const isMeaningful =

                    meaningfulTags.includes(

                        tag

                    );

                const hasUsefulData =

                    directText ||

                    Object.keys(attributes)

                        .length > 0 ||

                    label ||

                    isInteractive(element) ||

                    children.length > 0;

                if (

                    !isMeaningful &&

                    hasUsefulData

                ) {

                    if (

                        children.length === 1 &&

                        !directText

                    ) {

                        return children[0];

                    }

                    return {

                        tag: "group",

                        ...(directText

                            ? {

                                text:

                                    directText

                            }

                            : {}),

                        ...(children.length

                            ? {

                                children

                            }

                            : {})

                    };

                }

                if (

                    !isMeaningful &&

                    !hasUsefulData

                ) {

                    return null;

                }

                return node;

            }

            const root =

                document.documentElement ||

                document.body;

            return buildNode(root);

        }

        """,

        {

            "meaningfulTags":

                list(MEANINGFUL_TAGS),

            "validAttributes":

                list(VALID_ATTRIBUTES),

            "ignoredTags":

                list(IGNORED_TAGS),

            "frameworkIdPatterns":

                FRAMEWORK_ID_PATTERNS,

        }

    )

# ============================================================

# INTERACTIVE ELEMENT DISCOVERY

# ============================================================

def extract_interactive_elements(

    page: Page

) -> List[Dict[str, Any]]:

    """

    Uses the DOM internally to find elements

    that can cause UI state changes.

    These temporary discovery IDs are never

    included in the LLM context.

    """

    return page.evaluate(

        r"""

        () => {

            const selector = [

                "a",

                "button",

                "input",

                "select",

                "textarea",

                "[role='button']",

                "[role='link']",

                "[role='tab']",

                "[role='menuitem']",

                "[onclick]"

            ].join(",");

            const elements =

                Array.from(

                    document.querySelectorAll(

                        selector

                    )

                );

            const results = [];

            elements.forEach(

                (element, index) => {

                    const rect =

                        element.getBoundingClientRect();

                    const style =

                        window.getComputedStyle(

                            element

                        );

                    const visible =

                        style.display !== "none" &&

                        style.visibility !== "hidden" &&

                        style.opacity !== "0" &&

                        rect.width > 0 &&

                        rect.height > 0;

                    if (!visible) {

                        return;

                    }

                    const discoveryId =

                        `ai-discovery-${index}`;

                    element.setAttribute(

                        "data-ai-discovery-id",

                        discoveryId

                    );

                    results.push({

                        discovery_id:

                            discoveryId,

                        tag:

                            element.tagName

                                .toLowerCase(),

                        text:

                            (

                                element.innerText ||

                                ""

                            )

.replace(/\s+/g, " ")

                                .trim(),

                        aria_label:

                            element.getAttribute(

                                "aria-label"

                            ) || "",

                        id:

                            element.getAttribute(

                                "id"

                            ) || "",

                        name:

                            element.getAttribute(

                                "name"

                            ) || "",

                        type:

                            element.getAttribute(

                                "type"

                            ) || "",

                        href:

                            element.getAttribute(

                                "href"

                            ) || "",

                        role:

                            element.getAttribute(

                                "role"

                            ) || "",

                        disabled:

                            element.disabled === true ||

                            element.getAttribute(

                                "aria-disabled"

                            ) === "true",

                        checked:

                            element.checked === true

                    });

                }

            );

            return results;

        }

        """

    )

# ============================================================

# ACTION SAFETY

# ============================================================

def is_safe_action(

    element: Dict[str, Any]

) -> bool:

    combined_text = " ".join(

        [

            element.get("text", ""),

            element.get("aria_label", ""),

        ]

    )

    return not contains_dangerous_word(

        combined_text

    )

# ============================================================

# STATE FINGERPRINT

# ============================================================

def create_state_fingerprint(

    url: str,

    sanitized_dom: Dict[str, Any]

) -> str:

    normalized = json.dumps(

        {

            "url":

                normalize_url(url),

            "dom":

                sanitized_dom

        },

        sort_keys=True,

        separators=(",", ":")

    )

    return hashlib.sha256(

        normalized.encode("utf-8")

    ).hexdigest()[:16]

# ============================================================

# STATE CAPTURE

# ============================================================

def capture_state(

    page: Page

) -> Dict[str, Any]:

    url = normalize_url(page.url)

    dom = extract_sanitized_dom(page)

    state_id = create_state_fingerprint(

            url,

            dom

        )

    return {

        "state_id":

            state_id,

        "url":

            url,

        "title":

            normalize_text(

                page.title()

            ),

        "dom":

            dom

    }

# ============================================================

# ACTION DESCRIPTION

# ============================================================

def describe_action(

    element: Dict[str, Any]

) -> Dict[str, Any]:

    action = {

        "tag":

            element.get("tag"),

        "text":

            normalize_text(

                element.get(

                    "text",

                    ""

                )

            )

    }

    for key in [

        "aria_label",

        "id",

        "name",

        "type",

        "href",

        "role"

    ]:

        value = element.get(key)

        if value:

            action[key] = value

    return action

# ============================================================

# PERFORM INTERACTION

# ============================================================

def perform_interaction(

    page: Page,

    element: Dict[str, Any]

) -> bool:

    discovery_id = element["discovery_id"]

    locator = page.locator(

        f'[data-ai-discovery-id="{discovery_id}"]'

    ).first

    if locator.count() == 0:

        return False

    if not locator.is_visible():

        return False

    try:

        tag = element["tag"]

        element_type = element.get(

                "type",

                ""

            ).lower()

        if tag == "input":

            if element_type in {

                "checkbox",

                "radio"

            }:

                locator.check(

                    force=False

                )

                page.wait_for_timeout(

                    300

                )

                return True

            return False

        if tag in {

            "button",

            "a",

            "textarea"

        }:

            locator.click(

                timeout=3000,

                force=False

            )

            page.wait_for_timeout(

                500

            )

            return True

        if tag == "select":

            # Do not arbitrarily select

            # options during discovery.

            return False

        role = element.get(

                "role",

                ""

            )

        if role in {

            "button",

            "link",

            "tab",

            "menuitem"

        }:

            locator.click(

                timeout=3000,

                force=False

            )

            page.wait_for_timeout(

                500

            )

            return True

        return False

    except Exception:

        return False

# ============================================================

# ACTION PATH REPLAY

# ============================================================

def replay_action_path(

    page: Page,

    action_path: List[Dict[str, Any]]

) -> bool:

    for action in action_path:

        elements = extract_interactive_elements(

                page

            )

        matched = None

        for element in elements:

            if (

                action.get("tag") and

                element.get("tag")

                != action.get("tag")

            ):

                continue

            if (

                action.get("aria_label") and

                element.get("aria_label")

                == action.get(

                    "aria_label"

                )

            ):

                matched = element

                break

            if (

                action.get("id") and

                element.get("id")

                == action.get("id")

            ):

                matched = element

                break

            if (

                action.get("name") and

                element.get("name")

                == action.get("name")

            ):

                matched = element

                break

            if (

                action.get("text") and

                normalize_text(

                    element.get(

                        "text",

                        ""

                    )

                )

                == normalize_text(

                    action.get(

                        "text",

                        ""

                    )

                )

            ):

                matched = element

                break

            if (

                action.get("href") and

                element.get("href")

                == action.get("href")

            ):

                matched = element

                break

        if not matched:

            return False

        if not is_safe_action(

            matched

        ):

            return False

        if not perform_interaction(

            page,

            matched

        ):

            return False

    return True

# ============================================================

# APPLICATION DISCOVERY

# ============================================================

def discover_application(
    context: BrowserContext,
    start_url: str
) -> Dict[str, Any]:
    states = {}
    transitions = []
    discovered_states = set()
    visited_states = set()
    transition_keys = set()
    queue = deque()

    page = context.new_page()
    try:
        page.goto(start_url, wait_until="domcontentloaded")
        page.wait_for_timeout(500)
        initial_state = capture_state(page)
    finally:
        page.close()

    initial_state_id = initial_state["state_id"]
    states[initial_state_id] = initial_state
    discovered_states.add(initial_state_id)

    queue.append({
        "state_id": initial_state_id,
        "action_path": [],
        "depth": 0
    })

    while queue:
        current = queue.popleft()
        current_state_id = current["state_id"]
        action_path = current["action_path"]
        depth = current["depth"]

        if current_state_id in visited_states:
            continue

        visited_states.add(current_state_id)

        if depth >= MAX_DEPTH or len(states) >= MAX_STATES:
            continue

        page = context.new_page()
        try:
            page.goto(start_url, wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            if action_path and not replay_action_path(page, action_path):
                continue

            interactive_elements = extract_interactive_elements(page)

            for element in interactive_elements:
                if len(states) >= MAX_STATES:
                    break

                if not is_safe_action(element):
                    continue

                action = describe_action(element)
                new_action_path = [*action_path, action]

                interaction_page = context.new_page()
                try:
                    interaction_page.goto(
                        start_url,
                        wait_until="domcontentloaded"
                    )
                    interaction_page.wait_for_timeout(500)

                    if action_path and not replay_action_path(
                        interaction_page,
                        action_path
                    ):
                        continue

                    current_elements = extract_interactive_elements(
                        interaction_page
                    )
                    matching_element = None

                    for candidate in current_elements:
                        if describe_action(candidate) == action:
                            matching_element = candidate
                            break

                    if not matching_element:
                        continue

                    if not perform_interaction(
                        interaction_page,
                        matching_element
                    ):
                        continue

                    resulting_state = capture_state(interaction_page)
                    resulting_state_id = resulting_state["state_id"]

                    if resulting_state_id not in discovered_states:
                        discovered_states.add(resulting_state_id)
                        states[resulting_state_id] = resulting_state

                        if depth + 1 <= MAX_DEPTH:
                            queue.append({
                                "state_id": resulting_state_id,
                                "action_path": new_action_path,
                                "depth": depth + 1
                            })

                    if resulting_state_id != current_state_id:
                        transition_key = (
                            current_state_id,
                            resulting_state_id,
                            json.dumps(action, sort_keys=True)
                        )

                        if transition_key not in transition_keys:
                            transition_keys.add(transition_key)
                            transitions.append({
                                "from": current_state_id,
                                "to": resulting_state_id,
                                "action": action,
                                "action_path": new_action_path
                            })
                finally:
                    interaction_page.close()
        finally:
            page.close()

    return {
        "start_url": start_url,
        "states": list(states.values()),
        "transitions": transitions,
        "metadata": {
            "state_count": len(states),
            "transition_count": len(transitions),
            "visited_state_count": len(visited_states),
            "max_depth": MAX_DEPTH
        }
    }
        