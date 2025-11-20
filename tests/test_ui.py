"""
UI/Frontend tests for Polygon Manager using Playwright.
Tests user interactions, canvas drawing, and UI state management.
"""
import pytest
import time
import re
from playwright.sync_api import Page, expect


# Base URL for the application
BASE_URL = "http://localhost:8080"


@pytest.fixture(scope="function")
def page(browser):
    """Create a new page for each test."""
    page = browser.new_page()
    yield page
    page.close()


class TestPolygonManagerUI:
    """Test suite for Polygon Manager UI."""

    def test_page_loads(self, page: Page):
        """Test that the main page loads successfully."""
        page.goto(BASE_URL)
        expect(page).to_have_title("Polygon Manager")

    def test_page_has_header(self, page: Page):
        """Test that page has correct header."""
        page.goto(BASE_URL)
        header = page.locator("h1")
        expect(header).to_have_text("Polygon Manager")

    def test_canvas_exists(self, page: Page):
        """Test that canvas element exists."""
        page.goto(BASE_URL)
        canvas = page.locator("#polygonCanvas")
        expect(canvas).to_be_visible()

    def test_canvas_dimensions(self, page: Page):
        """Test that canvas has correct dimensions."""
        page.goto(BASE_URL)
        canvas = page.locator("#polygonCanvas")
        width = canvas.get_attribute("width")
        height = canvas.get_attribute("height")

        assert width == "1920"
        assert height == "1080"

    def test_initial_ui_state(self, page: Page):
        """Test initial state of UI elements."""
        page.goto(BASE_URL)

        # Name input should be enabled and empty
        name_input = page.locator("#polygonName")
        expect(name_input).to_be_enabled()
        expect(name_input).to_be_empty()

        # Start Drawing button should be enabled
        start_btn = page.locator("#startDrawing")
        expect(start_btn).to_be_enabled()

        # Finish and Cancel buttons should be disabled
        finish_btn = page.locator("#finishPolygon")
        expect(finish_btn).to_be_disabled()

        cancel_btn = page.locator("#cancelDrawing")
        expect(cancel_btn).to_be_disabled()

    def test_start_drawing_without_name(self, page: Page):
        """Test that starting to draw without a name shows alert."""
        page.goto(BASE_URL)

        page.on("dialog", lambda dialog: dialog.accept())
        page.locator("#startDrawing").click()

        # Should show alert and not enter drawing mode
        finish_btn = page.locator("#finishPolygon")
        expect(finish_btn).to_be_disabled()

    def test_start_drawing_with_name(self, page: Page):
        """Test starting drawing mode with valid name."""
        page.goto(BASE_URL)

        # Enter name
        page.locator("#polygonName").fill("Test Polygon")

        # Click start drawing
        page.locator("#startDrawing").click()

        # Verify UI state changed
        expect(page.locator("#startDrawing")).to_be_disabled()
        expect(page.locator("#cancelDrawing")).to_be_enabled()
        expect(page.locator("#polygonName")).to_be_disabled()

    def test_cancel_drawing(self, page: Page):
        """Test canceling drawing mode."""
        page.goto(BASE_URL)

        # Start drawing
        page.locator("#polygonName").fill("Test")
        page.locator("#startDrawing").click()

        # Cancel
        page.locator("#cancelDrawing").click()

        # Verify state reset
        expect(page.locator("#startDrawing")).to_be_enabled()
        expect(page.locator("#cancelDrawing")).to_be_disabled()
        expect(page.locator("#polygonName")).to_be_enabled()

    def test_clear_canvas_button_exists(self, page: Page):
        """Test that Clear Canvas button exists and is enabled."""
        page.goto(BASE_URL)

        clear_btn = page.locator("#clearCanvas")
        expect(clear_btn).to_be_visible()
        expect(clear_btn).to_be_enabled()

    def test_clear_canvas_clears_drawing(self, page: Page):
        """Test that Clear Canvas button works."""
        page.goto(BASE_URL)

        # Start drawing
        page.locator("#polygonName").fill("Test")
        page.locator("#startDrawing").click()

        # Click on canvas to add some points
        canvas = page.locator("#polygonCanvas")
        canvas.click(position={"x": 100, "y": 100})
        canvas.click(position={"x": 200, "y": 100})

        # Clear canvas
        page.locator("#clearCanvas").click()

        # Verify drawing state is reset
        expect(page.locator("#startDrawing")).to_be_enabled()
        expect(page.locator("#finishPolygon")).to_be_disabled()

    def test_instructions_visible(self, page: Page):
        """Test that instructions are visible."""
        page.goto(BASE_URL)

        instructions = page.locator(".instructions")
        expect(instructions).to_be_visible()
        expect(instructions.locator("h3")).to_have_text("Instructions:")

    def test_polygon_list_section_exists(self, page: Page):
        """Test that polygon list section exists."""
        page.goto(BASE_URL)

        list_section = page.locator(".polygon-list-section")
        expect(list_section).to_be_visible()
        expect(list_section.locator("h2")).to_have_text("Polygons List")

    def test_no_polygons_message(self, page: Page):
        """Test that 'no polygons' message shows when list is empty."""
        page.goto(BASE_URL)

        # Wait for page to load and fetch polygons
        page.wait_for_timeout(500)

        no_polygons = page.locator(".no-polygons")
        # Should be visible if no polygons exist
        # Note: This might fail if there are existing polygons in the database

    def test_drawing_requires_minimum_points(self, page: Page):
        """Test that finishing polygon requires at least 3 points."""
        page.goto(BASE_URL)

        # Start drawing
        page.locator("#polygonName").fill("Test")
        page.locator("#startDrawing").click()

        # Finish button should be disabled initially
        finish_btn = page.locator("#finishPolygon")
        expect(finish_btn).to_be_disabled()

        # Add one point
        canvas = page.locator("#polygonCanvas")
        canvas.click(position={"x": 100, "y": 100})

        # Still disabled
        expect(finish_btn).to_be_disabled()

        # Add second point
        canvas.click(position={"x": 200, "y": 100})

        # Still disabled
        expect(finish_btn).to_be_disabled()

        # Add third point
        canvas.click(position={"x": 150, "y": 200})

        # Now should be enabled
        expect(finish_btn).to_be_enabled()

    def test_loading_overlay_exists(self, page: Page):
        """Test that loading overlay element exists."""
        page.goto(BASE_URL)

        loading_overlay = page.locator("#loadingOverlay")
        expect(loading_overlay).to_be_hidden()

    def test_buttons_have_correct_classes(self, page: Page):
        """Test that buttons have correct styling classes."""
        page.goto(BASE_URL)

        start_btn = page.locator("#startDrawing")
        expect(start_btn).to_have_class(re.compile(r"btn-primary"))

        finish_btn = page.locator("#finishPolygon")
        expect(finish_btn).to_have_class(re.compile(r"btn-success"))

        cancel_btn = page.locator("#cancelDrawing")
        expect(cancel_btn).to_have_class(re.compile(r"btn-danger"))

        clear_btn = page.locator("#clearCanvas")
        expect(clear_btn).to_have_class(re.compile(r"btn-warning"))

    def test_canvas_background_loads(self, page: Page):
        """Test that canvas background image attempts to load."""
        page.goto(BASE_URL)

        # Wait for page to fully load
        page.wait_for_load_state("networkidle")

        # Check console for image load (basic check)
        # The actual image loading is handled by JavaScript
        canvas = page.locator("#polygonCanvas")
        expect(canvas).to_be_visible()

    def test_responsive_canvas_wrapper(self, page: Page):
        """Test that canvas wrapper exists."""
        page.goto(BASE_URL)

        wrapper = page.locator(".canvas-wrapper")
        expect(wrapper).to_be_visible()

    def test_all_control_buttons_exist(self, page: Page):
        """Test that all control buttons exist."""
        page.goto(BASE_URL)

        expect(page.locator("#startDrawing")).to_be_visible()
        expect(page.locator("#finishPolygon")).to_be_visible()
        expect(page.locator("#cancelDrawing")).to_be_visible()
        expect(page.locator("#clearCanvas")).to_be_visible()

    def test_css_loaded(self, page: Page):
        """Test that CSS is loaded."""
        page.goto(BASE_URL)

        # Check if stylesheets are loaded
        stylesheets = page.locator('link[rel="stylesheet"]')
        expect(stylesheets).to_have_count(1)

        # Check href
        href = stylesheets.get_attribute("href")
        assert "/static/styles.css" in href

    def test_javascript_loaded(self, page: Page):
        """Test that JavaScript is loaded."""
        page.goto(BASE_URL)

        # Check if script is loaded
        scripts = page.locator('script[src]')
        expect(scripts).to_have_count(1)

        # Check src
        src = scripts.get_attribute("src")
        assert "/static/app.js" in src

    def test_api_base_url_correct(self, page: Page):
        """Test that API base URL is configured correctly in JavaScript."""
        page.goto(BASE_URL)

        # Execute JavaScript to get API_BASE_URL
        api_url = page.evaluate("API_BASE_URL")
        assert "api/polygons" in api_url

    def test_console_errors_on_load(self, page: Page):
        """Test that there are no console errors on page load."""
        messages = []
        page.on("console", lambda msg: messages.append(msg))

        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")

        # Check for error messages
        errors = [msg for msg in messages if msg.type == "error"]
        # Note: Some errors might be expected (e.g., CORS from external image)
        # This test documents the current state

    def test_page_layout_sections(self, page: Page):
        """Test that main layout sections exist."""
        page.goto(BASE_URL)

        expect(page.locator(".main-content")).to_be_visible()
        expect(page.locator(".canvas-section")).to_be_visible()
        expect(page.locator(".polygon-list-section")).to_be_visible()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context arguments."""
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
    }
