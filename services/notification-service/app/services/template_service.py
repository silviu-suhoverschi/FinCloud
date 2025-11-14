"""
Notification template service using Jinja2
"""

from pathlib import Path
from typing import Any

import structlog
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape

logger = structlog.get_logger()


class TemplateService:
    """Template rendering service"""

    def __init__(self):
        # Set up Jinja2 environment
        template_dir = Path(__file__).parent.parent / "templates"
        template_dir.mkdir(exist_ok=True)

        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

        # Add custom filters
        self.env.filters["currency"] = self._currency_filter

    def _currency_filter(self, value: float, currency: str = "USD") -> str:
        """Format value as currency"""
        if currency == "USD":
            return f"${value:,.2f}"
        elif currency == "EUR":
            return f"€{value:,.2f}"
        elif currency == "GBP":
            return f"£{value:,.2f}"
        else:
            return f"{value:,.2f} {currency}"

    def render_template(
        self,
        template_name: str,
        context: dict[str, Any],
    ) -> str:
        """
        Render a template

        Args:
            template_name: Template filename
            context: Template context variables

        Returns:
            Rendered template string
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(
                "template_render_failed",
                template=template_name,
                error=str(e),
            )
            raise

    def render_string(
        self,
        template_string: str,
        context: dict[str, Any],
    ) -> str:
        """
        Render a template from string

        Args:
            template_string: Template string
            context: Template context variables

        Returns:
            Rendered template string
        """
        try:
            template = Template(template_string)
            return template.render(**context)
        except Exception as e:
            logger.error(
                "template_string_render_failed",
                error=str(e),
            )
            raise

    def get_email_template(
        self,
        notification_type: str,
        context: dict[str, Any],
    ) -> tuple[str, str]:
        """
        Get email template (plain text and HTML)

        Args:
            notification_type: Type of notification
            context: Template context

        Returns:
            Tuple of (plain_text, html)
        """
        try:
            # Try to load custom templates
            text_template = f"email/{notification_type}.txt"
            html_template = f"email/{notification_type}.html"

            plain_text = self.render_template(text_template, context)
            html = self.render_template(html_template, context)

            return plain_text, html

        except Exception:
            # Fall back to default template
            plain_text = self._get_default_text_template(notification_type, context)
            html = self._get_default_html_template(notification_type, context)
            return plain_text, html

    def _get_default_text_template(
        self,
        notification_type: str,
        context: dict[str, Any],
    ) -> str:
        """Get default plain text template"""
        subject = context.get("subject", "Notification")
        message = context.get("message", "")

        return f"""
{subject}

{message}

---
This is an automated notification from FinCloud.
"""

    def _get_default_html_template(
        self,
        notification_type: str,
        context: dict[str, Any],
    ) -> str:
        """Get default HTML template"""
        subject = context.get("subject", "Notification")
        message = context.get("message", "")

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
        }}
        .content {{
            background: #f9fafb;
            padding: 30px;
            border-radius: 0 0 8px 8px;
        }}
        .footer {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            font-size: 12px;
            color: #6b7280;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{subject}</h1>
    </div>
    <div class="content">
        <p>{message}</p>
    </div>
    <div class="footer">
        <p>This is an automated notification from FinCloud.</p>
    </div>
</body>
</html>
"""
