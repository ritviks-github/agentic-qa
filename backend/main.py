from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
from gemini_mapper import map_application_to_brd
from application_discovery import discover_application
from test_case_generator import generate_test_cases


app = FastAPI()


@app.get("/health")
def get_health():
    return {
        "status": "Health Check Success!!"
    }


class DiscoveryRequest(BaseModel):
    url: str


@app.post("/discover")
def discover(request: DiscoveryRequest):
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=False
            )

            context = browser.new_context()

            try:
                application_context = discover_application(
                    context=context,
                    start_url=request.url
                )

            finally:
                context.close()
                browser.close()

        return {
            "status": "success",
            "message": "Application discovery completed",
            "data": application_context
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

class MappingRequest(BaseModel):
    brd_file_path: str
    application_url: str


@app.post("/map-context")
def map_context(request: MappingRequest):

    try:

        result = map_application_to_brd(
            brd_file_path=request.brd_file_path,
            application_url=request.application_url
        )

        return {
            "status": "success",
            "message": "BRD and application context mapped successfully",
            "data": result
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


class TestCaseGenerationRequest(BaseModel):
    brd_file_path: str
    application_url: str


@app.post("/generate-test-cases")
def generate_test_cases_endpoint(
    request: TestCaseGenerationRequest
):
    try:

        # Run the mapping pipeline first
        mapping_response = map_context(
            MappingRequest(
                brd_file_path=request.brd_file_path,
                application_url=request.application_url
            )
        )

        # Get the "data" returned by /map-context
        mapping_result = mapping_response["data"]

        # Extract all three required inputs
        brd = mapping_result.get("brd", {})

        application_context = mapping_result.get(
            "application_context",
            {}
        )

        mapping = mapping_result.get(
            "mapping",
            {}
        )

        # Generate test cases using all three
        result = generate_test_cases(
            brd=brd,
            application_context=application_context,
            mapping=mapping,
            prompt_file_path=(
                r"C:\Users\Rishabh Bhardwaj"
                r"\OneDrive\Desktop\application-testing"
                r"\backend\test_gen_prompt.txt"
            )
        )

        return {
            "status": "success",
            "message": "Test cases generated successfully",
            "data": result
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )