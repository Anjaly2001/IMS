"""
Final Year Calculation Engine — implements the exact 5-step process from
the SRS:

    Step 1: Take Internship 1-8 (the 8 regular internships, each out of 100
            via Worksheet 40 + Viva 40 + Certificate 20)
    Step 2: Pick the Best 7 scores automatically
    Step 3: Calculate the average — Best 7 Total / 7
    Step 4: Convert to 70 marks — Average x 70 / 100
    Step 5: Add the Assessment Internship score (out of 30, via
            Worksheet 10 + Viva 5 + Certificate 5 + PPO 10)

    Regular Internship Component (70) + Assessment Internship (30)
        = Final Internship Marks (100)

If the assessment internship hasn't been marked yet, the result is flagged
"provisional" and only the regular-internship component (out of 70) is
shown, so reports remain meaningful before the 5th year.
"""
from internships.models import InternshipRecord
from assessments.models import InternshipMarks

BEST_N = 7
TOTAL_REGULAR = 8
REGULAR_MAX_RAW = 100      # each regular internship is scored out of 100
REGULAR_CONVERTED_MAX = 70  # converted onto a 70-mark scale
ASSESSMENT_MAX = 30         # assessment internship is scored out of 30 directly


def get_total_marks(internship_record):
    """
    Retrieves the final calculated total marks for a specific InternshipRecord.

    Args:
        internship_record (InternshipRecord): The record to examine.

    Returns:
        float: Auto-calculated total from the related InternshipMarks instance,
               or None if marks are not yet populated.
    """
    try:
        marks = internship_record.marks
    except InternshipMarks.DoesNotExist:
        return None
    return marks.total


def calculate_student_score(student):
    """
    Consolidates internship marks and executes the Best-7-of-8 calculation process.

    Processing Steps:
      1. Fetch all completed 'regular' internship records for the student.
      2. Sum and sort the scores, keeping only the best 7 of the 8 scores (ignores lowest).
      3. Compute average mark over the available best scores (up to 7).
      4. Convert the average out of 100 to a 70-mark scale (Average * 0.7).
      5. Read the 5th-year 'assessment' internship score (up to 30 marks).
      6. Combine the converted regular score (out of 70) and assessment score (out of 30) for a total out of 100.

    Args:
        student (Student): Target student profile instance.

    Returns:
        dict: Dict containing marks list, best7 list, average, regular component total,
              assessment score, final sum, completeness flag, and provisional flag status.
    """
    regular_qs = InternshipRecord.objects.filter(
        student=student, internship_type='regular'
    ).order_by('internship_number')

    regular_marks = []
    numeric_marks = []
    for record in regular_qs:
        mark = get_total_marks(record)
        regular_marks.append({
            'internship': record,
            'number': record.internship_number,
            'mark': mark,
        })
        if mark is not None:
            numeric_marks.append(mark)

    regular_count = len(numeric_marks)

    # Step 2: Pick the best 7 automatically (or fewer, if fewer are entered
    # so far — partial data still shows a sensible in-progress average)
    best_marks = sorted(numeric_marks, reverse=True)[:BEST_N]
    best7_total = round(sum(best_marks), 2) if best_marks else None

    # Step 3: Calculate the average — Best 7 Total / 7
    # (divides by the count actually available when fewer than 7 marks
    # exist yet, so an in-progress average isn't artificially dragged down)
    regular_avg = round(best7_total / len(best_marks), 2) if best_marks else None

    # Step 4: Convert to 70 marks — Average x 70 / 100
    regular_converted = round(regular_avg * REGULAR_CONVERTED_MAX / REGULAR_MAX_RAW, 2) if regular_avg is not None else None

    # Step 5: Assessment Internship (5th year, out of 30 directly)
    assessment_record = InternshipRecord.objects.filter(
        student=student, internship_type='assessment'
    ).order_by('-start_date').first()
    assessment_mark = get_total_marks(assessment_record) if assessment_record else None

    is_provisional = assessment_mark is None
    if regular_converted is None:
        final_score = None
    elif is_provisional:
        # Not yet eligible for full consolidation — show the regular
        # component alone (out of 70) so it's clear it's partial
        final_score = regular_converted
    else:
        final_score = round(regular_converted + assessment_mark, 2)

    complete = (regular_count >= TOTAL_REGULAR) and (assessment_mark is not None)

    return {
        'regular_marks': regular_marks,
        'best7': best_marks,
        'best7_total': best7_total,
        'regular_avg': regular_avg,
        'regular_converted': regular_converted,
        'regular_count': regular_count,
        'assessment_mark': assessment_mark,
        'assessment_internship': assessment_record,
        'final_score': final_score,
        'is_provisional': is_provisional,
        'complete': complete,
    }
