"""
Skill Loader - Loads and parses markdown skill definitions from .skills folder.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from backend.models.schemas import Skill


class SkillLoader:
    """Loads and manages skills from markdown files."""

    def __init__(self, skills_dir: str = ".skills"):
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, Skill] = {}
        self._loaded = False

    def load_skills(self) -> Dict[str, Skill]:
        """Load all skills from the .skills directory."""
        if not self.skills_dir.exists():
            print(f"Warning: Skills directory {self.skills_dir} does not exist")
            return self.skills

        for md_file in self.skills_dir.glob("*.md"):
            try:
                skill = self._parse_skill_file(md_file)
                if skill:
                    self.skills[skill.tool_name] = skill
                    print(f"Loaded skill: {skill.tool_name}")
            except Exception as e:
                print(f"Error loading skill from {md_file}: {e}")

        self._loaded = True
        return self.skills

    def _parse_skill_file(self, file_path: Path) -> Optional[Skill]:
        """Parse a single markdown skill file."""
        content = file_path.read_text(encoding='utf-8')

        # Extract YAML frontmatter
        frontmatter_match = re.match(
            r'^---\s*\n(.*?)\n---\s*\n',
            content,
            re.DOTALL
        )

        if not frontmatter_match:
            print(f"Warning: No frontmatter found in {file_path}")
            return None

        frontmatter_yaml = frontmatter_match.group(1)
        try:
            metadata = yaml.safe_load(frontmatter_yaml)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML in {file_path}: {e}")
            return None

        # Extract execution code (everything after frontmatter)
        execution_code = content[frontmatter_match.end():].strip()

        # Build skill object
        skill = Skill(
            tool_name=metadata.get('tool_name', file_path.stem),
            description=metadata.get('description', ''),
            arguments=metadata.get('arguments', []),
            execution_code=execution_code,
            category=metadata.get('category', 'general')
        )

        return skill

    def get_skill(self, tool_name: str) -> Optional[Skill]:
        """Get a specific skill by name."""
        if not self._loaded:
            self.load_skills()
        return self.skills.get(tool_name)

    def get_all_skills(self) -> Dict[str, Skill]:
        """Get all loaded skills."""
        if not self._loaded:
            self.load_skills()
        return self.skills

    def get_skills_by_category(self, category: str) -> List[Skill]:
        """Get all skills in a specific category."""
        if not self._loaded:
            self.load_skills()
        return [s for s in self.skills.values() if s.category == category]

    def reload(self):
        """Reload all skills from disk."""
        self.skills.clear()
        self._loaded = False
        self.load_skills()


# Global skill loader instance
_skill_loader: Optional[SkillLoader] = None


def get_skill_loader(skills_dir: Optional[str] = ".skills") -> SkillLoader:
    """Get the global skill loader instance."""
    global _skill_loader
    if _skill_loader is None:
        _skill_loader = SkillLoader(skills_dir=skills_dir)
        _skill_loader.load_skills()
    return _skill_loader


def reload_skills(skills_dir: Optional[str] = ".skills"):
    """Reload all skills."""
    global _skill_loader
    if _skill_loader:
        _skill_loader.reload()
    else:
        _skill_loader = SkillLoader(skills_dir=skills_dir)
        _skill_loader.load_skills()
