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

    Returns a dict:
        regular_marks: list of {internship, number, mark} for all regular internships
        best7: list of the best 7 marks actually used (numeric only)
        regular_avg: average of best 7 (None if fewer than 7 marks exist)
        regular_count: how many regular internships have a viva mark
        assessment_mark: float or None
        assessment_internship: the InternshipRecord or None
        final_score: float or None
        is_provisional: True if assessment internship mark missing
        complete: True if all 8 regular + assessment internship are marked
    """
    regular_qs = InternshipRecord.objects.filter(
        student=student, internship_type='regular'
    ).order_by('internship_number')

    regular_marks = []
    numeric_marks = []
    for record in regular_qs:
        mark = get_viva_mark(record)
        regular_marks.append({
            'internship': record,
            'number': record.internship_number,
            'mark': mark,
        })
        if mark is not None:
            numeric_marks.append(mark)

    regular_count = len(numeric_marks)

    # Best N of the marks actually entered (if fewer than BEST_N exist,
    # use whatever is available so partial data still shows a sensible average).
    best_marks = sorted(numeric_marks, reverse=True)[:BEST_N]
    regular_avg = round(sum(best_marks) / len(best_marks), 2) if best_marks else None

    # Assessment (5th-year, 3-month) internship
    assessment_record = InternshipRecord.objects.filter(
        student=student, internship_type='assessment'
    ).order_by('-start_date').first()
    assessment_mark = get_viva_mark(assessment_record) if assessment_record else None

    is_provisional = assessment_mark is None
    if regular_avg is None:
        final_score = None
    elif is_provisional:
        # Not yet eligible for full consolidation — show regular average only
        final_score = regular_avg
    else:
        final_score = round(
            REGULAR_WEIGHT * regular_avg + ASSESSMENT_WEIGHT * assessment_mark, 2
        )

    complete = (regular_count >= TOTAL_REGULAR) and (assessment_mark is not None)

    return {
        'regular_marks': regular_marks,
        'best7': best_marks,
        'regular_avg': regular_avg,
        'regular_count': regular_count,
        'assessment_mark': assessment_mark,
        'assessment_internship': assessment_record,
        'final_score': final_score,
        'is_provisional': is_provisional,
        'complete': complete,
    }
