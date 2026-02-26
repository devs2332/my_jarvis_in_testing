"""
Browser automation tool using Playwright.
"""

import logging
from typing import Type, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


class BrowserInput(BaseModel):
    url: str = Field(description="URL to navigate to")
    action: str = Field(
        default="get_content",
        description="Action: 'get_content', 'screenshot', 'click', 'fill'",
    )
    selector: Optional[str] = Field(
        default=None, description="CSS selector for click/fill actions",
    )
    value: Optional[str] = Field(
        default=None, description="Value for fill action",
    )


class BrowserAutomationTool(BaseTool):
    name: str = "browser_automation"
    description: str = (
        "Automate browser actions — navigate to URLs, extract content, "
        "take screenshots, click elements, or fill forms."
    )
    args_schema: Type[BaseModel] = BrowserInput

    async def _arun(self, url: str, action: str = "get_content", **kwargs) -> str:
        """Execute browser automation action."""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto(url, wait_until="domcontentloaded", timeout=30000)

                if action == "get_content":
                    content = await page.content()
                    # Extract text content
                    text = await page.evaluate("document.body.innerText")
                    result = text[:5000]  # Limit output size

                elif action == "screenshot":
                    screenshot = await page.screenshot()
                    result = f"Screenshot captured ({len(screenshot)} bytes)"

                elif action == "click" and kwargs.get("selector"):
                    await page.click(kwargs["selector"])
                    result = f"Clicked element: {kwargs['selector']}"

                elif action == "fill" and kwargs.get("selector"):
                    await page.fill(kwargs["selector"], kwargs.get("value", ""))
                    result = f"Filled element: {kwargs['selector']}"

                else:
                    title = await page.title()
                    result = f"Page loaded: {title}"

                await browser.close()
                return result

        except ImportError:
            return "Error: Playwright not installed. Run: pip install playwright && playwright install"
        except Exception as e:
            logger.error(f"Browser tool error: {e}")
            return f"Browser error: {str(e)}"

    def _run(self, *args, **kwargs) -> str:
        return "Use async version (_arun)"
