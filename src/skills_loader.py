import os
import yaml
from dataclasses import dataclass

# from config import GREEN,RED, RESET

SKILLS_DIR = os.path.dirname(os.path.abspath(__file__)) + "/skills"

BLUE = "\033[38;5;117m"
GREEN = "\033[38;5;46m"
YELLOW = "\033[38;5;220m"
RED = "\033[38;5;196m"
RESET = "\033[0m"


@dataclass
class Skill:
    name: str
    description: str
    body: str
    path: str


def get_skills(skill_dir: str):
    """Get skills within a given skill directory"""

    print(f"--- {GREEN} From get_skills {RESET} ---")

    skills = []

    if os.path.isdir(skill_dir):
        skill_list = os.listdir(skill_dir)
        if skill_list:
            for skill_folder in skill_list:
                if "SKILL.md" in os.listdir(skill_dir + "/" + skill_folder):
                    skill_path = skill_dir + "/" + skill_folder + "/" + "SKILL.md"
                    skill_metadata, skill_body, skill_msg = parse_skill(skill_path)
                    if skill_metadata and skill_body:
                        s = Skill(
                            skill_metadata["name"],
                            skill_metadata["description"],
                            skill_body,
                            skill_path,
                        )
                        skills.append(s)
            return skills
        else:
            print("There is no skills in given directory.")
    else:
        return skills


def parse_skill(skill_path: str):
    """Parse skill given a skill file path"""

    metadata = {}

    with open(skill_path, "r") as f:
        print(f"{GREEN}Reading skill file at {skill_path}{RESET}")
        lines = f.read().splitlines()

    if lines[0] == "---":  # skill metadata start
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":  # skill metadata end
                yaml_block = "\n".join(lines[1:i])
                metadata = yaml.safe_load(yaml_block)
                body = "\n".join(lines[i + 1 : len(lines) - 1])
                msg = f"{GREEN}Successful skill metadata and body extraction{RESET}\n"
                break

        return metadata, body, msg
    else:
        print(
            f"{RED}Error with skill file. It might not start by --- or is malformed.{RESET}\n"
        )
        msg = f"{RED}ERROR during skill metadata and body extraction{RESET}\n"

        return {}, lines, msg


def render_skills_catalog(skills: list):
    """Render skills catalog from a given skills list"""
    lines = [
        "## Available skills",
        "",
        "Each skill below is a set of on-demand instructions. When a user request "
        "matches a skill, call the `read_skill` tool with the skill's exact `name` "
        "to load its full instructions, then follow them.",
        "",
    ]
    for skill in sorted(skills, key=lambda s: s.name):
        lines.append(f"- {skill.name}: {skill.description}")
    return "\n".join(lines)


if __name__ == "__main__":

    s = Skill("my-skill", "this is my first skill", "skill body", "skill path")

    skill_dir = os.path.expanduser("~/Desktop/sunraise/src/skills")
    skills = get_skills(skill_dir)

    for skill in skills:
        print(skill)

    skill_catalog = render_skills_catalog(skills)
    print(f"{GREEN}--- skill catalog  ---{RESET}")
    print(skill_catalog)
    print(f"{GREEN}--- skill catalog end  ---{RESET}")
