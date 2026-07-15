# get_weather tool func definition
from skills_loader import Skill, parse_skill, SKILLS_DIR


def read_skill(skill_name: str):
    """Read a skill body from a given skill_name"""

    skill_path = SKILLS_DIR + "/" + skill_name + "/" + "SKILL.md"

    skill_metadata, skill_body, skill_msg = parse_skill(skill_path)

    if skill_metadata and skill_body:
        s = Skill(
            skill_metadata["name"],
            skill_metadata["description"],
            skill_body,
            skill_path,
        )

        return {"skill": skill_name, "body": s.body}


# read_skill tool config definition for anthropic
anthropic_read_skill_tool = {
    "name": "read_skill",
    "description": "Read a skill body",
    "input_schema": {
        "type": "object",
        "properties": {"skill_name": {"type": "string"}},
        "required": ["skill_name"],
    },
}

# read_skill tool config definition for google
google_read_skill_tool = {
    "name": "read_skill",
    "description": "Read a skill body",
    "parameters": {
        "type": "object",
        "properties": {
            "skill_name": {"type": "string"},
        },
        "required": ["skill_name"],
    },
}

# read_skill tool config definition for mistral
mistral_read_skill_tool = {
    "type": "function",
    "function": {
        "name": "read_skill",
        "description": "Read a skill body",
        "parameters": {
            "type": "object",
            "properties": {"skill_name": {"type": "string"}},
            "required": ["skill_name"],
        },
    },
}
