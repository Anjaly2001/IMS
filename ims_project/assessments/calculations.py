"""
Marks calculation logic for the Internship Management System.

Default departmental formula (configurable in principle, hard-coded here per
the project's current scope):

    Regular Internship Score  = average of BEST 7 of the 8 regular
                                 internship viva marks (out of 100 each)
    Assessment Internship Score = viva mark of the 5th-year assessment
                                 internship (out of 100)
    Final Consolidated Score  = 0.70 * Regular Internship Score
                               + 0.30 * Assessment Internship Score

If the assessment internship has not been completed/marked yet, the final
score falls back to the Regular Internship Score alone (flagged as
"provisional") so reports remain useful before the 5th year.
"""
from internships.models import InternshipRecord
from assessments.models import AssessmentMark

REGULAR_WEIGHT = 0.70
ASSESSMENT_WEIGHT = 0.30
BEST_N = 7
TOTAL_REGULAR = 8


def get_viva_mark(internship_record):
    """Return the float viva mark for an internship record, or None."""
    viva = AssessmentMark.objects.filter(
        internship_record=internship_record, assessment_type='viva'
    ).order_by('-assessment_date', '-id').first()
    if viva:
        return float(viva.marks_awarded)
    return None


def calculate_student_score(student):
    """
    Compute the full marks breakdown for a student.
    - Regular score = Worksheet (40) + Viva (40) + Certificate (20) = 100
    - Best 7 scores of 8 regular internships are averaged
    - Converted to 70 marks (avg * 70 / 100)
    - Assessment Internship = Worksheet (10) + Viva (5) + Certificate (5) + PPO (10) = 30
    - Final Consolidated Score = Regular Component (70) + Assessment Component (30) = 100
    """
    regular_records = InternshipRecord.objects.filter(
        student=student, internship_type='regular'
    ).select_related('assessment_mark').order_by('internship_number')

    regular_marks = []
    numeric_marks = []
    for record in regular_records:
        mark = None
        if hasattr(record, 'assessment_mark') and record.assessment_mark:
            mark = float(record.assessment_mark.total_marks)
            numeric_marks.append(mark)
        regular_marks.append({
            'internship': record,
            'number': record.internship_number,
            'mark': mark,
        })

    regular_count = len(numeric_marks)
    best_marks = sorted(numeric_marks, reverse=True)[:7]
    
    if best_marks:
        regular_avg = sum(best_marks) / len(best_marks)
        regular_70_comp = regular_avg * 0.70
    else:
        regular_avg = None
        regular_70_comp = 0.0

    # Assessment (5th-year) internship
    assessment_record = InternshipRecord.objects.filter(
        student=student, internship_type='assessment'
    ).select_related('assessment_mark').order_by('-start_date').first()

    assessment_mark = None
    if assessment_record and hasattr(assessment_record, 'assessment_mark') and assessment_record.assessment_mark:
        assessment_mark = float(assessment_record.assessment_mark.total_marks)

    is_provisional = (assessment_mark is None)
    if regular_avg is None:
        final_score = None
    elif is_provisional:
        # Before assessment, final score defaults to regular avg
        final_score = round(regular_avg, 2)
    else:
        final_score = round(regular_70_comp + assessment_mark, 2)

    complete = (regular_count >= 8) and (assessment_mark is not None)

    return {
        'regular_marks': regular_marks,
        'best7': best_marks,
        'regular_avg': round(regular_avg, 2) if regular_avg is not None else None,
        'regular_70_comp': round(regular_70_comp, 2) if regular_avg is not None else None,
        'regular_count': regular_count,
        'assessment_mark': assessment_mark,
        'assessment_internship': assessment_record,
        'final_score': final_score,
        'is_provisional': is_provisional,
        'complete': complete,
    }
