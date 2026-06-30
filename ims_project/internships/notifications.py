"""
Email Automation Module (per SRS):

Trigger: When Faculty Coordinator approves an internship record.
System sends an email to the organisation/advocate/law firm thanking them
for providing the internship opportunity, including student name,
programme, and internship duration.

Uses Django's email backend — defaults to printing to the console
(see ims_project/settings.py) so this works without any SMTP setup for
local testing; switch USE_SMTP_EMAIL=True for real delivery.
"""
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import ActivityLog


def send_organisation_thank_you(internship_record, triggered_by=None):
    """
    Sends the approval thank-you email to the organisation contact for the
    given internship record. Silently does nothing (and logs why) if the
    organisation has no email on file, so approval workflows never fail
    just because email data is missing.

    Returns True if an email was sent, False otherwise.
    """
    org = internship_record.organisation
    student = internship_record.student

    if not org.email:
        ActivityLog.objects.create(
            user=triggered_by, action='Skipped organisation email (no email on file)',
            module='Email Automation', record_id=str(internship_record.pk),
        )
        return False

    subject = f'Thank You for Hosting {student.name} — Internship Completed'
    body = (
        f"Dear {org.contact_person or org.name},\n\n"
        f"Thank you for providing an internship opportunity to our student.\n\n"
        f"Student Name: {student.name}\n"
        f"Programme: {student.programme.name}\n"
        f"Internship Duration: {internship_record.start_date} to {internship_record.end_date}\n\n"
        f"We truly appreciate your continued support of our students' practical training "
        f"and look forward to future collaboration.\n\n"
        f"Warm regards,\n"
        f"Internship Management & Assessment System\n"
        f"{student.programme.name} Programme"
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[org.email],
            fail_silently=False,
        )
        ActivityLog.objects.create(
            user=triggered_by, action=f'Sent thank-you email to {org.email}',
            module='Email Automation', record_id=str(internship_record.pk),
        )
        return True
    except Exception as e:
        ActivityLog.objects.create(
            user=triggered_by, action=f'Failed to send email to {org.email}: {e}',
            module='Email Automation', record_id=str(internship_record.pk),
        )
        return False
