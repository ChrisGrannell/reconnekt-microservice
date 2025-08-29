from datetime import datetime
# hello world
def build_prompt(data: dict) -> str:
    name = data.get("name", "Unknown")
    company = data.get("company", "Unknown")
    linkedin = data.get("linkedin", "Unknown")
    met_via = data.get("met_via", "Unknown")
    notes_next = data.get("notes_for_next_time", "")
    output_type = data.get("output_type", "Email")
    
    historical_notes = data.get("historical_notes", [])
    notes_lines = ""
    for note in historical_notes:
        date = note.get("date", "")
        text = note.get("note", "")
        notes_lines += f"- {date}: {text}\n"
    
    prompt = f"""You are writing a {output_type.lower()} to re-engage or connect with the following person.

Name: {name}
Company: {company}
LinkedIn: {linkedin}
Met via: {met_via}

Notes for next time:
{notes_next}

Historical notes:
{notes_lines.strip()}

Please respond with only the {output_type.lower()}, written in a friendly, professional tone.
"""

    if output_type.lower() == "linkedin connection request":
        prompt += "\nIMPORTANT: It must be under 300 characters."

    if output_type.lower() == "text":
        prompt += "\nIMPORTANT: Be ultra short and informal, like a quick SMS."

    return prompt
