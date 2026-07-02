from django import forms
from django.db.models import Q
from .models import InternshipRecord, MentorAssignment
from accounts.models import User

class InternshipRecordForm(forms.ModelForm):
    class Meta:
        model = InternshipRecord
        fields = ['student','organisation','internship_type','internship_number','related_semester',
                  'academic_phase','reporting_officer_name','reporting_officer_contact','reporting_officer_email',
                  'start_date','end_date','mode','nature_of_work',
                  'stipend_received','stipend_amount','student_remarks',
                  'certificate','report','completion_status','remarks']
        widgets = {
            'start_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'end_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        self.bound_student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)
        for name, f in self.fields.items():
            if 'class' not in f.widget.attrs:
                f.widget.attrs['class'] = 'form-control'

    def clean_reporting_officer_contact(self):
        value = (self.cleaned_data.get('reporting_officer_contact') or '').strip()
        if value:
            compact = value.replace(' ', '').replace('-', '')
            if not compact.lstrip('+').isdigit() or len(compact.lstrip('+')) < 8:
                raise forms.ValidationError('Enter a valid contact number.')
        return value

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student') or self.bound_student
        internship_type = cleaned_data.get('internship_type')
        internship_number = (cleaned_data.get('internship_number') or '').strip()
        related_semester = (cleaned_data.get('related_semester') or '').strip()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        stipend_received = cleaned_data.get('stipend_received')
        stipend_amount = cleaned_data.get('stipend_amount')
        certificate = cleaned_data.get('certificate')
        report = cleaned_data.get('report')
        completion_status = cleaned_data.get('completion_status')

        if internship_number:
            cleaned_data['internship_number'] = internship_number.upper()
            duplicate = InternshipRecord.objects.filter(
                student=student,
                internship_number__iexact=internship_number,
            )
            if self.instance.pk:
                duplicate = duplicate.exclude(pk=self.instance.pk)
            if student and duplicate.exists():
                self.add_error('internship_number', 'This student already has an internship with this number.')

        if student and start and end:
            if end <= start:
                self.add_error('end_date', 'End date must be after start date.')
            if start < student.degree_start_date:
                self.add_error('start_date', 'Internship cannot start before the student degree starts.')
            if end > student.degree_end_date:
                self.add_error('end_date', 'Internship cannot end after the student degree ends.')

        if internship_type == 'assessment' and not related_semester:
            self.add_error('related_semester', 'Related semester is required for an assessment internship.')

        if stipend_received:
            if stipend_amount is None:
                self.add_error('stipend_amount', 'Enter the stipend amount.')
            elif stipend_amount <= 0:
                self.add_error('stipend_amount', 'Stipend amount must be greater than zero.')
        elif stipend_amount not in (None, 0):
            self.add_error('stipend_amount', 'Remove the amount or mark stipend as received.')

        if completion_status == 'completed' and not certificate:
            self.add_error('certificate', 'Certificate is required when the internship is marked completed.')

        for field_name, upload in (('certificate', certificate), ('report', report)):
            if upload and upload.size > 10 * 1024 * 1024:
                self.add_error(field_name, 'Upload a file smaller than 10 MB.')

        return cleaned_data


class StudentInternshipSubmissionForm(InternshipRecordForm):
    class Meta(InternshipRecordForm.Meta):
        fields = ['organisation', 'internship_type', 'internship_number', 'related_semester',
                  'academic_phase', 'reporting_officer_name', 'reporting_officer_contact',
                  'reporting_officer_email', 'start_date', 'end_date', 'mode',
                  'nature_of_work', 'stipend_received', 'stipend_amount',
                  'student_remarks']


class InternshipDocumentUploadForm(forms.ModelForm):
    class Meta:
        model = InternshipRecord
        fields = ['certificate', 'report', 'completion_status', 'student_remarks']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        certificate = cleaned_data.get('certificate') or self.instance.certificate
        report = cleaned_data.get('report') or self.instance.report
        completion_status = cleaned_data.get('completion_status')

        if completion_status == 'completed':
            if not certificate:
                self.add_error('certificate', 'Certificate is required before marking the internship completed.')
            if not report:
                self.add_error('report', 'Report is required before marking the internship completed.')

        for field_name, upload in (
            ('certificate', cleaned_data.get('certificate')),
            ('report', cleaned_data.get('report')),
        ):
            if upload and upload.size > 10 * 1024 * 1024:
                self.add_error(field_name, 'Upload a file smaller than 10 MB.')
        return cleaned_data


class MentorAssignmentForm(forms.ModelForm):
    class Meta:
        model = MentorAssignment
        fields = ['student','faculty','effective_from','effective_to','assignment_level','related_semester','internship_record','reason_for_change','remarks']
        widgets = {
            'effective_from': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'effective_to': forms.DateInput(attrs={'type':'date','class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['faculty'].queryset = User.objects.filter(role__in=['faculty_mentor','evaluator'])
        for name, f in self.fields.items():
            if 'class' not in f.widget.attrs:
                f.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        faculty = cleaned_data.get('faculty')
        effective_from = cleaned_data.get('effective_from')
        effective_to = cleaned_data.get('effective_to')
        assignment_level = cleaned_data.get('assignment_level')
        internship_record = cleaned_data.get('internship_record')

        if faculty and faculty.role not in ('faculty_mentor', 'evaluator'):
            self.add_error('faculty', 'Select a faculty mentor or evaluator.')
        if effective_from and effective_to and effective_to < effective_from:
            self.add_error('effective_to', 'Effective-to date cannot be before effective-from date.')
        if student and effective_from and effective_from < student.degree_start_date:
            self.add_error('effective_from', 'Assignment cannot start before the student degree starts.')
        if student and effective_to and effective_to > student.degree_end_date:
            self.add_error('effective_to', 'Assignment cannot end after the student degree ends.')
        if assignment_level == 'internship' and not internship_record:
            self.add_error('internship_record', 'Select the internship for an internship-specific assignment.')
        if student and internship_record and internship_record.student_id != student.id:
            self.add_error('internship_record', 'Selected internship does not belong to this student.')

        if student and faculty and effective_from:
            overlaps = MentorAssignment.objects.filter(student=student, faculty=faculty)
            if self.instance.pk:
                overlaps = overlaps.exclude(pk=self.instance.pk)
            if effective_to:
                overlaps = overlaps.filter(effective_from__lte=effective_to).filter(
                    Q(effective_to__isnull=True) |
                    Q(effective_to__gte=effective_from)
                )
            else:
                overlaps = overlaps.filter(
                    Q(effective_to__isnull=True) |
                    Q(effective_to__gte=effective_from)
                )
            if overlaps.exists():
                self.add_error(None, 'This faculty member already has an overlapping assignment for this student.')
        return cleaned_data

class VerificationForm(forms.ModelForm):
    class Meta:
        model = InternshipRecord
        fields = ['verification_status','faculty_remarks','remarks']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['verification_status'].choices = [
            ('needs_correction', 'Needs Correction'),
            ('verified', 'Verified'),
            ('rejected', 'Rejected'),
        ]
        for f in self.fields.values():
            f.widget.attrs['class'] = 'form-control'
