import email
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Optional

import httpx
from config import settings


class NotificationService:
    async def send_slack(
        self,
        webhook_url: str,
        repository_name: str,
        gate_result: Dict,
        run_url: Optional[str] = None,
    ) -> bool:
        passed = gate_result.get("passed", False)
        color = "#22c55e" if passed else "#ef4444"
        status = "✅ PASSED" if passed else "❌ FAILED"
        checks_text = "\n".join(
            f"{'✅' if c['passed'] else '❌'} {c['name']}: {c['message']}"
            for c in gate_result.get("checks", [])
        )
        attachment = {
            "color": color,
            "title": f"Code Intelligence: {repository_name} — {status}",
            "text": checks_text,
            "footer": "Code Intelligence Platform",
        }
        if run_url:
            attachment["title_link"] = run_url
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    webhook_url, json={"attachments": [attachment]}, timeout=10.0
                )
                return r.status_code == 200
        except Exception as e:
            print(f"Slack notification failed: {e}")
            return False

    def send_email(
        self,
        to_email: str,
        repository_name: str,
        gate_result: Dict,
        html_report: Optional[str] = None,
    ) -> bool:
        if (
            not settings.smtp_host
            or not settings.smtp_user
            or not settings.smtp_password
        ):
            print("SMTP not configured — skipping email")
            return False
        passed = gate_result.get("passed", False)
        subject = f"[Code Intelligence] {repository_name} — {'PASSED ✅' if passed else 'FAILED ❌'}"
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_user
        msg["To"] = to_email
        text_body = (
            f"Code Intelligence Quality Gate\n"
            f"Repository: {repository_name}\n"
            f"Status: {'PASSED' if passed else 'FAILED'}\n\n"
            + "\n".join(
                f"{'✅' if c['passed'] else '❌'} {c['name']}: {c['message']}"
                for c in gate_result.get("checks", [])
            )
        )
        msg.attach(MIMEText(text_body, "plain"))
        if html_report:
            msg.attach(MIMEText(html_report, "html"))
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                settings.smtp_host, settings.smtp_port, context=context
            ) as server:
                server.login(settings.smtp_user, settings.smtp_password)
                server.sendmail(settings.smtp_user, to_email, msg.as_string())
            return True
        except Exception as e:
            print(f"Email notification failed: {e}")
            return False
