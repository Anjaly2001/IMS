# Internship Management & Assessment System (IMS) — User Manual

This manual provides an overview of operations and workflows for each user role in the system.

---

## 1. Role Quick Reference

| Role | Primary Responsibilities |
|---|---|
| **System Admin** | Initial database setup, user accounts management, global lists. |
| **Department Admin** | Setup of Programmes, Batches, Academics, and Organisations. |
| **Student** | Profile check, internship logs submission, document uploads, viewing scorecards. |
| **Faculty Mentor (Coordinator)** | Verifying/approving internships, reviewing evaluator-submitted marks, and locking grades. |
| **Evaluator** | Grading student internship components (Worksheet, Viva, Certificate, PPO). |
| **HoD / Programme Coordinator** | High-level analytics dashboards, marks reports, progress monitoring. |

---

## 2. Operations Guide by Role

### 🔑 System / Department Administrator
1. **Initial Setup**:
   - Create Academic Programmes (e.g., *B.A. LL.B. (Hons.)*) and Batches.
   - Set up Faculty and Evaluator accounts under **User Management** and assign appropriate system roles.
2. **Student Database**:
   - Go to **Students** and click **Import Students**.
   - Upload Excel/CSV files matching required columns to bulk-register students quickly.
3. **Organisations Registry**:
   - Manage the directory of advocates, law firms, NGOs, and companies hosting student interns.

### 🎓 Student Portal
1. **Submit Internship**:
   - Navigate to the dashboard and press **Submit Internship**.
   - Input organisation details, start/end dates, mode (Offline/Online/Hybrid) and internship type.
2. **Document Uploads**:
   - View the created record and click **Upload Document** to add internship certificates or reports.
3. **Tracking & Progress**:
   - View your dashboard timeline to track progress (Submitted $\rightarrow$ Verified $\rightarrow$ Approved).
   - Open **View My Marks** or **Score Card** once grading completes.

### 👔 Faculty Mentor (Coordinator)
1. **Student Assignment**:
   - View assigned students under the **My Assigned Students** dashboard section.
2. **Verify Internships**:
   - Review incoming student logs. Use **Review / Verify** to accept the logs (moving status to `Verified`) or flag them with remarks for correction (`Needs Correction`).
   - Automatically fires a thank-you email to the hosting organisation upon record verification and approval.
3. **Approve & Lock Marks**:
   - Go to **Review / Lock** to check evaluator marks.
   - Adjust scores if needed, fill in remarks, and click **Lock** to finalize student grades.

### 📝 Evaluator
1. **Grade Internships**:
   - Find assignments waiting in the **Internships Ready for Marks Entry** dashboard list.
2. **Component Submission**:
   - Input marks into the grading template:
     - **Regular (Years 1-4)**: Worksheet (40), Viva (40), Certificate (20) — Total: 100.
     - **Assessment (Year 5)**: Worksheet (10), Viva (5), Certificate (5), PPO (10) — Total: 30.
   - Submit marks when complete. *Note: Marks cannot be edited by the evaluator after submission.*

### 📊 Head of Department (HoD)
1. **Overall Progress**:
   - Inspect completion charts showing aggregate stats per batch and year.
2. **Final Grade Calculation**:
   - Review automatically calculated marks using the **Best 7 of 8** algorithm (Years 1-4) scaled to 70 marks, combined with Year 5 assessment marks (30) for a total final grade.
3. **Report Generation**:
   - Export consolidated spreadsheets or PDF scorecards via the **Reports** hub.
