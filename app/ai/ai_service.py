from __future__ import annotations

from datetime import date


def chat_assistant(message: str, context: dict | None = None):
    # TODO: Integrate Google Gemini API later
    context = context or {}
    normalized_message = (message or "").strip()
    lower_message = normalized_message.lower()
    scholarships = context.get("scholarships", [])

    answer = (
        "This is the local fallback assistant. It does not call any AI model yet, "
        "but it can still respond using the scholarship data already available in ScholarAI."
    )
    matched_topic = "general"

    if "deadline" in lower_message or "closing" in lower_message:
        matched_topic = "deadlines"
        if scholarships:
            names = ", ".join(item["scholarship_name"] for item in scholarships[:3])
            answer = (
                f"The most relevant deadline-related scholarships in your current context are {names}. "
                "Open each scholarship detail page to verify the final application date before applying."
            )
        else:
            answer = (
                "Use the closing-soon filters or the deadline reminder API to find scholarships that are ending soon."
            )
    elif "compare" in lower_message or "difference" in lower_message:
        matched_topic = "comparison"
        answer = (
            "The best comparison flow is to shortlist up to three scholarships, then compare amount, deadline, "
            "CGPA, income limit, categories, states, and branch support side by side."
        )
    elif "eligible" in lower_message or "eligibility" in lower_message:
        matched_topic = "eligibility"
        answer = (
            "ScholarAI calculates eligibility with deterministic backend rules. "
            "Enter your profile in the recommendation or eligibility pages to see scored matches and why they qualify."
        )
    elif "document" in lower_message or "apply" in lower_message:
        matched_topic = "application"
        answer = (
            "Check the scholarship detail page for required documents, official website, and direct application link. "
            "You can also use the application email placeholder to draft an outreach message."
        )

    return {
        "status": "placeholder",
        "mode": "rule_based_fallback",
        "message": "AI chat assistant is not integrated yet.",
        "answer": answer,
        "matched_topic": matched_topic,
        "suggested_prompts": [
            "Which scholarships are closing soon?",
            "How should I compare two scholarships?",
            "Why am I eligible for a scholarship?",
        ],
    }


def summarize_scholarship(scholarship: dict):
    # TODO: Integrate Google Gemini API later
    amount = _format_amount(scholarship.get("scholarship_amount"))
    deadline = scholarship.get("application_end_date") or "the listed deadline"
    categories = _format_list(scholarship.get("categories"), empty_value="open-category students")
    states = _format_list(scholarship.get("states"), empty_value="students across India")

    highlights = [
        f"Provider: {scholarship.get('provider_name') or 'Not specified'}",
        f"Amount: {amount}",
        f"Deadline: {deadline}",
        f"Best fit: {scholarship.get('degree') or 'Degree not listed'} students in {scholarship.get('branch') or 'multiple branches'}",
    ]
    cautions = []
    if scholarship.get("minimum_cgpa") is not None:
        cautions.append(f"Requires at least {scholarship['minimum_cgpa']} CGPA.")
    if scholarship.get("maximum_family_income") is not None:
        cautions.append(
            f"Family income should be within {scholarship['maximum_family_income']}."
        )
    if not cautions:
        cautions.append("Review the full eligibility description before applying.")

    return {
        "status": "placeholder",
        "message": "Scholarship summary AI is not integrated yet.",
        "summary": (
            f"{scholarship.get('scholarship_name')} is a {scholarship.get('scholarship_type', 'scholarship')} "
            f"opportunity from {scholarship.get('provider_name')}. It is currently aimed at {categories} in {states}, "
            f"with an application deadline on {deadline}."
        ),
        "highlights": highlights,
        "cautions": cautions,
    }


def compare_scholarships(items: list[dict]):
    # TODO: Integrate Google Gemini API later
    if not items:
        return {
            "status": "placeholder",
            "message": "Scholarship comparison AI is not integrated yet.",
            "summary": "Add scholarships to comparison to see a generated overview later.",
            "strengths": [],
        }

    strengths = []
    for item in items:
        strengths.append(
            {
                "scholarship_name": item["scholarship_name"],
                "best_for": (
                    f"{item['degree']} students in {item['branch']} who want a "
                    f"{item['scholarship_type']} scholarship with deadline {item.get('application_end_date') or 'TBA'}."
                ),
            }
        )

    return {
        "status": "placeholder",
        "message": "Scholarship comparison AI is not integrated yet.",
        "summary": (
            "This fallback comparison highlights practical differences only from stored scholarship data. "
            "Use amount, income limit, CGPA, deadline, and branch fit as your first decision filters."
        ),
        "strengths": strengths,
    }


def eligibility_explanation(student_profile: dict, results: list[dict]):
    # TODO: Integrate Google Gemini API later
    if not results:
        return {
            "status": "placeholder",
            "message": "Eligibility explanation AI is not integrated yet.",
            "summary": (
                "No strong matches were found from the backend rules for the current profile. "
                "Try widening branch, category, or income-related inputs."
            ),
            "next_steps": [
                "Review your state and category selections.",
                "Check whether your branch or academic year is too narrow.",
                "Explore the main scholarship listing with broader filters.",
            ],
        }

    top_match = results[0]
    eligible_count = sum(1 for item in results if item["status_label"] == "eligible")
    partial_count = sum(
        1 for item in results if item["status_label"] == "partially_eligible"
    )

    return {
        "status": "placeholder",
        "message": "Eligibility explanation AI is not integrated yet.",
        "summary": (
            f"Based on backend scoring, the strongest current match is {top_match['scholarship']['scholarship_name']}. "
            f"You have {eligible_count} fully eligible and {partial_count} partially eligible recommendations."
        ),
        "next_steps": [
            "Prioritize scholarships with the highest score and nearest deadline.",
            "Open each scholarship to review required documents and provider links.",
            "Use comparison view to shortlist the strongest final options.",
        ],
        "student_snapshot": {
            "state_code": student_profile.get("state_code"),
            "category_slug": student_profile.get("category_slug"),
            "degree": student_profile.get("degree"),
            "branch": student_profile.get("branch"),
        },
    }


def generate_email(scholarship: dict, student_profile: dict | None = None):
    # TODO: Integrate Google Gemini API later
    student_profile = student_profile or {}
    student_name = student_profile.get("student_name") or "Student"
    college_name = student_profile.get("college_name") or "my college"
    branch = student_profile.get("branch") or scholarship.get("branch") or "B.Tech"

    subject = f"Inquiry about {scholarship.get('scholarship_name')} application"
    body = (
        f"Dear {scholarship.get('provider_name') or 'Scholarship Team'},\n\n"
        f"My name is {student_name}, and I am interested in applying for the "
        f"{scholarship.get('scholarship_name')}.\n"
        f"I am currently pursuing {branch} at {college_name}.\n"
        "I would like to confirm the eligibility requirements, required documents, "
        "and any important application instructions before I proceed.\n\n"
        "Please let me know if there are any additional steps I should complete.\n\n"
        "Sincerely,\n"
        f"{student_name}"
    )

    return {
        "status": "placeholder",
        "message": "Email generation AI is not integrated yet.",
        "subject": subject,
        "body": body,
        "generated_on": date.today().isoformat(),
    }


def _format_amount(value) -> str:
    """Return a human-readable scholarship amount string."""
    if value in (None, ""):
        return "Amount varies"
    return str(value)


def _format_list(values, empty_value: str) -> str:
    """Format simple list values for placeholder responses."""
    if not values:
        return empty_value
    return ", ".join(str(item) for item in values)
