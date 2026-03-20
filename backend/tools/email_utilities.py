"""
Email Utilities Tool for MAHER Orchestrator

Provides email automation capabilities including:
- Generate Outlook-compatible email drafts
- Attach files to emails
- Auto-fill email content from MAHER data
- Schedule email sending
- Parse incoming emails
- Email template management
"""

from typing import Dict, Any, List, Optional, Union
import os
import json
import re
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import base64

try:
    import email
    from email.parser import Parser
    from email.policy import default
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    IMPORT_ERROR = str(e)


def generate_email_draft(
    to: Union[str, List[str]],
    subject: str,
    body: str,
    cc: Optional[Union[str, List[str]]] = None,
    bcc: Optional[Union[str, List[str]]] = None,
    attachments: Optional[List[str]] = None,
    format: str = "html",
    priority: str = "normal"
) -> Dict[str, Any]:
    """
    Generate an email draft (Outlook-compatible)

    Args:
        to: Recipient email address(es)
        subject: Email subject
        body: Email body content
        cc: CC recipients
        bcc: BCC recipients
        attachments: List of file paths to attach
        format: 'html' or 'plain'
        priority: 'high', 'normal', or 'low'

    Returns:
        Email draft data structure
    """
    if not DEPENDENCIES_AVAILABLE:
        return {
            "success": False,
            "error": f"Required dependencies not available: {IMPORT_ERROR}"
        }

    try:
        # Normalize recipients to lists
        to_list = [to] if isinstance(to, str) else to
        cc_list = [cc] if isinstance(cc, str) else (cc or [])
        bcc_list = [bcc] if isinstance(bcc, str) else (bcc or [])

        # Create email structure
        email_draft = {
            "to": to_list,
            "cc": cc_list,
            "bcc": bcc_list,
            "subject": subject,
            "body": body,
            "format": format,
            "priority": priority,
            "attachments": attachments or [],
            "created_at": datetime.now().isoformat(),
            "draft_id": f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }

        # Create MIME message for export
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['To'] = ', '.join(to_list)

        if cc_list:
            msg['Cc'] = ', '.join(cc_list)

        # Set priority header
        if priority == "high":
            msg['X-Priority'] = '1'
            msg['Importance'] = 'high'
        elif priority == "low":
            msg['X-Priority'] = '5'
            msg['Importance'] = 'low'

        # Add body
        if format == "html":
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))

        # Generate mailto link for quick sending
        mailto_link = f"mailto:{','.join(to_list)}?subject={subject}"

        return {
            "success": True,
            "draft": email_draft,
            "mime_message": msg.as_string(),
            "mailto_link": mailto_link,
            "recipient_count": len(to_list) + len(cc_list) + len(bcc_list),
            "message": "Email draft generated successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate email: {str(e)}"
        }


def attach_files_to_email(
    email_draft: Dict[str, Any],
    file_paths: List[str]
) -> Dict[str, Any]:
    """
    Attach files to an email draft

    Args:
        email_draft: Email draft structure from generate_email_draft
        file_paths: List of file paths to attach

    Returns:
        Updated email draft with attachments
    """
    if not DEPENDENCIES_AVAILABLE:
        return {
            "success": False,
            "error": f"Required dependencies not available: {IMPORT_ERROR}"
        }

    try:
        attached_files = []
        total_size = 0

        for file_path in file_paths:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }

            file_size = os.path.getsize(file_path)
            total_size += file_size

            attached_files.append({
                "path": file_path,
                "filename": os.path.basename(file_path),
                "size": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2)
            })

        # Update email draft
        email_draft["attachments"] = attached_files
        email_draft["total_attachment_size"] = total_size
        email_draft["total_attachment_size_mb"] = round(total_size / (1024 * 1024), 2)

        return {
            "success": True,
            "draft": email_draft,
            "attached_files": len(attached_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "message": f"Attached {len(attached_files)} files successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to attach files: {str(e)}"
        }


def create_email_from_template(
    template_name: str,
    data: Dict[str, Any],
    templates_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create email from a template with data substitution

    Args:
        template_name: Name of the email template
        data: Data to fill into template placeholders
        templates_dir: Directory containing templates

    Returns:
        Generated email content
    """
    try:
        # Built-in templates if no directory specified
        templates = {
            "maintenance_notification": {
                "subject": "Scheduled Maintenance: {equipment_name}",
                "body": """
                <html>
                <body>
                    <h2>Scheduled Maintenance Notification</h2>
                    <p>Dear Team,</p>
                    <p>This is to inform you about scheduled maintenance for:</p>
                    <ul>
                        <li><strong>Equipment:</strong> {equipment_name}</li>
                        <li><strong>Equipment ID:</strong> {equipment_id}</li>
                        <li><strong>Scheduled Date:</strong> {maintenance_date}</li>
                        <li><strong>Duration:</strong> {duration}</li>
                        <li><strong>Technician:</strong> {technician}</li>
                    </ul>
                    <p><strong>Maintenance Tasks:</strong></p>
                    <p>{tasks}</p>
                    <p>Please plan accordingly.</p>
                    <p>Best regards,<br>MAHER Maintenance System</p>
                </body>
                </html>
                """
            },
            "incident_report": {
                "subject": "Incident Report: {incident_type} - {equipment_name}",
                "body": """
                <html>
                <body>
                    <h2>Incident Report</h2>
                    <p><strong>Incident Type:</strong> {incident_type}</p>
                    <p><strong>Equipment:</strong> {equipment_name}</p>
                    <p><strong>Date/Time:</strong> {incident_datetime}</p>
                    <p><strong>Severity:</strong> {severity}</p>
                    <p><strong>Description:</strong></p>
                    <p>{description}</p>
                    <p><strong>Immediate Actions Taken:</strong></p>
                    <p>{actions_taken}</p>
                    <p><strong>Follow-up Required:</strong> {followup_required}</p>
                    <p>Generated by MAHER System</p>
                </body>
                </html>
                """
            },
            "inspection_summary": {
                "subject": "Inspection Summary: {equipment_name}",
                "body": """
                <html>
                <body>
                    <h2>Equipment Inspection Summary</h2>
                    <p><strong>Equipment:</strong> {equipment_name}</p>
                    <p><strong>Inspector:</strong> {inspector}</p>
                    <p><strong>Inspection Date:</strong> {inspection_date}</p>
                    <p><strong>Overall Status:</strong> {status}</p>
                    <p><strong>Findings:</strong></p>
                    <p>{findings}</p>
                    <p><strong>Recommendations:</strong></p>
                    <p>{recommendations}</p>
                    <p>This is an automated report from MAHER.</p>
                </body>
                </html>
                """
            }
        }

        # Get template
        if template_name not in templates:
            return {
                "success": False,
                "error": f"Template '{template_name}' not found",
                "available_templates": list(templates.keys())
            }

        template = templates[template_name]

        # Fill template with data
        subject = template["subject"].format(**data)
        body = template["body"].format(**data)

        return {
            "success": True,
            "subject": subject,
            "body": body,
            "template_used": template_name,
            "message": "Email created from template successfully"
        }

    except KeyError as e:
        return {
            "success": False,
            "error": f"Missing required template field: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Template processing failed: {str(e)}"
        }


def schedule_email(
    email_draft: Dict[str, Any],
    send_datetime: str,
    recurrence: Optional[str] = None
) -> Dict[str, Any]:
    """
    Schedule an email for future sending

    Args:
        email_draft: Email draft to schedule
        send_datetime: When to send (ISO format or relative like '+2 hours')
        recurrence: Optional recurrence pattern ('daily', 'weekly', 'monthly')

    Returns:
        Scheduled email information
    """
    try:
        # Parse send datetime
        if send_datetime.startswith('+'):
            # Relative time
            match = re.match(r'\+(\d+)\s*(hour|day|week)s?', send_datetime)
            if match:
                amount = int(match.group(1))
                unit = match.group(2)

                if unit == 'hour':
                    scheduled_time = datetime.now() + timedelta(hours=amount)
                elif unit == 'day':
                    scheduled_time = datetime.now() + timedelta(days=amount)
                elif unit == 'week':
                    scheduled_time = datetime.now() + timedelta(weeks=amount)
            else:
                return {
                    "success": False,
                    "error": "Invalid relative time format"
                }
        else:
            # Absolute time
            scheduled_time = datetime.fromisoformat(send_datetime)

        scheduled_email = {
            "draft": email_draft,
            "scheduled_time": scheduled_time.isoformat(),
            "recurrence": recurrence,
            "status": "scheduled",
            "schedule_id": f"sched_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }

        return {
            "success": True,
            "scheduled_email": scheduled_email,
            "scheduled_for": scheduled_time.isoformat(),
            "time_until_send": str(scheduled_time - datetime.now()),
            "message": "Email scheduled successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Scheduling failed: {str(e)}"
        }


def parse_email(
    email_content: str,
    parse_attachments: bool = False
) -> Dict[str, Any]:
    """
    Parse an email message

    Args:
        email_content: Raw email content (RFC 822 format)
        parse_attachments: Whether to extract attachment info

    Returns:
        Parsed email data
    """
    if not DEPENDENCIES_AVAILABLE:
        return {
            "success": False,
            "error": f"Required dependencies not available: {IMPORT_ERROR}"
        }

    try:
        # Parse email
        msg = Parser(policy=default).parsestr(email_content)

        # Extract basic fields
        parsed = {
            "from": msg.get('From', ''),
            "to": msg.get('To', ''),
            "cc": msg.get('Cc', ''),
            "subject": msg.get('Subject', ''),
            "date": msg.get('Date', ''),
            "message_id": msg.get('Message-ID', '')
        }

        # Extract body
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    parsed['body_plain'] = part.get_payload(decode=True).decode()
                elif content_type == 'text/html':
                    parsed['body_html'] = part.get_payload(decode=True).decode()
        else:
            parsed['body'] = msg.get_payload(decode=True).decode()

        # Extract attachments info
        if parse_attachments:
            attachments = []
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue

                filename = part.get_filename()
                if filename:
                    attachments.append({
                        "filename": filename,
                        "content_type": part.get_content_type(),
                        "size": len(part.get_payload(decode=True))
                    })

            parsed['attachments'] = attachments

        return {
            "success": True,
            "parsed_email": parsed,
            "has_attachments": len(parsed.get('attachments', [])) > 0,
            "message": "Email parsed successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Email parsing failed: {str(e)}"
        }


def extract_email_addresses(
    text: str
) -> Dict[str, Any]:
    """
    Extract email addresses from text

    Args:
        text: Text to extract email addresses from

    Returns:
        List of found email addresses
    """
    try:
        # Email regex pattern
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(pattern, text)

        # Remove duplicates while preserving order
        unique_emails = list(dict.fromkeys(emails))

        return {
            "success": True,
            "emails": unique_emails,
            "count": len(unique_emails),
            "message": f"Found {len(unique_emails)} email addresses"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Email extraction failed: {str(e)}"
        }


def validate_email_address(
    email_address: str
) -> Dict[str, Any]:
    """
    Validate an email address format

    Args:
        email_address: Email address to validate

    Returns:
        Validation result
    """
    try:
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        is_valid = bool(re.match(pattern, email_address))

        # Extract components
        if is_valid:
            local, domain = email_address.split('@')
            domain_parts = domain.split('.')

            result = {
                "valid": True,
                "email": email_address,
                "local_part": local,
                "domain": domain,
                "tld": domain_parts[-1] if domain_parts else ""
            }
        else:
            result = {
                "valid": False,
                "email": email_address,
                "error": "Invalid email format"
            }

        return {
            "success": True,
            "validation": result,
            "message": "Valid email" if is_valid else "Invalid email"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Validation failed: {str(e)}"
        }


def create_outlook_mailto_link(
    to: Union[str, List[str]],
    subject: str = "",
    body: str = "",
    cc: Optional[Union[str, List[str]]] = None
) -> Dict[str, Any]:
    """
    Create an Outlook-compatible mailto link

    Args:
        to: Recipient email(s)
        subject: Email subject
        body: Email body
        cc: CC recipients

    Returns:
        Mailto link and HTML code
    """
    try:
        import urllib.parse

        # Build mailto link
        to_str = ','.join(to) if isinstance(to, list) else to

        params = []
        if subject:
            params.append(f"subject={urllib.parse.quote(subject)}")
        if body:
            params.append(f"body={urllib.parse.quote(body)}")
        if cc:
            cc_str = ','.join(cc) if isinstance(cc, list) else cc
            params.append(f"cc={urllib.parse.quote(cc_str)}")

        mailto_link = f"mailto:{to_str}"
        if params:
            mailto_link += "?" + "&".join(params)

        # Create HTML link
        html_link = f'<a href="{mailto_link}">Send Email</a>'

        return {
            "success": True,
            "mailto_link": mailto_link,
            "html_link": html_link,
            "message": "Mailto link created successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create mailto link: {str(e)}"
        }


def generate_email_signature(
    name: str,
    title: str,
    company: str = "MAHER Maintenance Systems",
    phone: Optional[str] = None,
    email: Optional[str] = None,
    website: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate HTML email signature

    Args:
        name: Person's name
        title: Job title
        company: Company name
        phone: Phone number
        email: Email address
        website: Website URL

    Returns:
        HTML signature
    """
    try:
        signature_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 12px; color: #333;">
            <p style="margin: 0; padding: 0;">
                <strong style="font-size: 14px;">{name}</strong><br>
                <em>{title}</em><br>
                <strong>{company}</strong>
            </p>
            <p style="margin: 5px 0; padding: 0;">
        """

        if phone:
            signature_html += f'Phone: {phone}<br>'
        if email:
            signature_html += f'Email: <a href="mailto:{email}">{email}</a><br>'
        if website:
            signature_html += f'Web: <a href="{website}">{website}</a><br>'

        signature_html += """
            </p>
        </div>
        """

        return {
            "success": True,
            "signature_html": signature_html.strip(),
            "message": "Email signature generated successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Signature generation failed: {str(e)}"
        }
