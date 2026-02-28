"""Fireverse Artifact Engine.

Generates cinematic 6-scene episodes centered on a single artifact from the
Fireverse Artifact Vault.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from random import Random
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "outputs"


@dataclass
class SceneBeat:
    name: str
    purpose: str


SCENE_BEATS: List[SceneBeat] = [
    SceneBeat("Mythic discovery", "Introduce artifact legend and first visual reveal."),
    SceneBeat("Archive atmosphere / lore hint", "Deepen vault lore with environmental tension."),
    SceneBeat("Energy awakening", "Show first signs of power ignition."),
    SceneBeat("Activation buildup", "Escalate rhythm and stakes before release."),
    SceneBeat("Explosive power release", "Deliver high-intensity activation climax."),
    SceneBeat("Mystery aftermath / cliffhanger", "Close with unresolved omen and sequel hook."),
]


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _read_template(path: Path) -> str:
    with path.open("r", encoding="utf-8") as file:
        return file.read().strip()


def _safe_slug(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in value).strip("_")


def _load_world_state() -> Dict[str, Any]:
    return {
        "artifacts": _read_json(DATA_DIR / "artifacts.json"),
        "spirits": _read_json(DATA_DIR / "spirit_entities.json"),
        "vault": _read_json(DATA_DIR / "vault_memory.json"),
        "director": _read_json(DATA_DIR / "director_settings.json"),
        "episode_template": _read_template(TEMPLATES_DIR / "episode_template.txt"),
        "scene_template": _read_template(TEMPLATES_DIR / "scene_template.txt"),
        "prompt_template": _read_template(TEMPLATES_DIR / "prompt_template.txt"),
    }


def _select_artifact(artifacts: List[Dict[str, str]], artifact_name: str) -> Dict[str, str]:
    target = artifact_name.strip().lower()
    for artifact in artifacts:
        if artifact["name"].lower() == target:
            return artifact
    available_names = ", ".join(a["name"] for a in artifacts)
    raise ValueError(f"Artifact '{artifact_name}' not found. Available: {available_names}")


def _build_title(artifact: Dict[str, str], episode_number: int) -> str:
    return f"{artifact['name']} Unsealed: Vault Episode {episode_number} Ignites the Fireverse"


def _build_thumbnail(artifact: Dict[str, str], spirit: Dict[str, str]) -> str:
    return (
        f"Close-up of {artifact['name']} ({artifact['visual_motif']}) floating above a glowing altar, "
        f"with {spirit['name']} emerging from shadowed runes, cinematic contrast, bold text: 'UNSEALED'."
    )


def _build_scene_content(
    artifact: Dict[str, str],
    spirit: Dict[str, str],
    vault: Dict[str, Any],
    director: Dict[str, Any],
) -> List[Dict[str, str]]:
    pacing_map = {
        1: director["pacing"]["scene_1_to_3"],
        2: director["pacing"]["scene_1_to_3"],
        3: director["pacing"]["scene_1_to_3"],
        4: director["pacing"]["scene_4"],
        5: director["pacing"]["scene_5"],
        6: director["pacing"]["scene_6"],
    }

    lore = vault["core_lore"]
    warnings = vault["warnings"]

    narration = [
        f"In the silent deep of the vault, the {artifact['name']} is found where prayers turned to stone.",
        f"Obsidian columns breathe with memory: {lore[0]}",
        f"A pulse answers the chamber as {artifact['power']} stirs beneath etched sigils.",
        f"The air tightens; {spirit['name']} appears, testing intent before release.",
        f"Then ignition—{artifact['consequence']} as the chamber erupts in controlled cosmic fire.",
        f"When the light fades, a final echo remains: {warnings[2]}",
    ]

    visual_focus = [
        f"Dusty altar reveal of {artifact['name']} with {artifact['visual_motif']} detail.",
        "Wide vault corridor, torchlight, living runes and sacred mechanical doors.",
        "Energy veins race across floor glyphs toward artifact core.",
        f"Wielder silhouette reaches forward while {spirit['nature']} circles above.",
        "Shockwave of light, particles, and vault geometry warping in rhythmic bursts.",
        "Smoldering chamber, fragmented symbol hovering in darkness.",
    ]

    scenes: List[Dict[str, str]] = []
    safety_line = "; ".join(director["safety_rules"])

    for idx, beat in enumerate(SCENE_BEATS, start=1):
        image_prompt = (
            f"Cinematic still, {visual_focus[idx - 1]} mythic archive aesthetic, volumetric lighting, "
            f"PG-13 fantasy tone, no gore, no explicit content."
        )
        video_prompt = (
            f"10-second cinematic shot for '{beat.name}'. Camera motion tailored for {pacing_map[idx]} pacing, "
            f"focus on {artifact['name']}, include subtle environmental particles, high dynamic range, "
            f"mythic mystery tone, safe-for-all-audiences storytelling."
        )

        scenes.append(
            {
                "scene_number": idx,
                "duration_seconds": director["scene_duration_seconds"],
                "beat": beat.name,
                "purpose": beat.purpose,
                "pacing_stage": pacing_map[idx],
                "visual_focus": visual_focus[idx - 1],
                "narration": narration[idx - 1],
                "safe_image_prompt": image_prompt,
                "cinematic_video_prompt": video_prompt,
                "safety_requirements": safety_line,
            }
        )

    return scenes


def generate_artifact_episode(artifact_name: str, episode_number: int) -> Dict[str, Any]:
    """Generate and persist one Fireverse artifact episode.

    Args:
        artifact_name: Name of artifact from data/artifacts.json.
        episode_number: Sequential episode number for output naming.

    Returns:
        Dictionary with title, thumbnail, scene plan, prompts, and narration.
    """
    world = _load_world_state()
    artifact = _select_artifact(world["artifacts"], artifact_name)

    rng = Random(f"{_safe_slug(artifact_name)}-{episode_number}")
    spirit = world["spirits"][rng.randrange(0, len(world["spirits"]))]

    scenes = _build_scene_content(artifact, spirit, world["vault"], world["director"])

    title = _build_title(artifact, episode_number)
    thumbnail_concept = _build_thumbnail(artifact, spirit)
    hook = f"A sealed relic calls to the chosen hand—and the vault listens."
    cliffhanger = f"A hidden chamber unlocks after the {artifact['name']} activation signature is recorded."

    episode_card = world["episode_template"].format(
        episode_number=episode_number,
        title=title,
        artifact_name=artifact["name"],
        vault_name=world["vault"]["site_name"],
        spirit_name=spirit["name"],
        hook=hook,
        cliffhanger=cliffhanger,
    )

    episode_payload: Dict[str, Any] = {
        "episode_number": episode_number,
        "artifact": artifact,
        "title": title,
        "thumbnail_concept": thumbnail_concept,
        "director_style": world["director"]["director_style"],
        "tone": world["director"]["language_style"],
        "episode_card": episode_card,
        "spirit_entity": spirit,
        "scene_plan": scenes,
        "narration_lines": [scene["narration"] for scene in scenes],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"artifact_episode_{episode_number}.json"
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(episode_payload, file, indent=2, ensure_ascii=False)

    return episode_payload


def main() -> None:
    """Simple executable test run for immediate validation."""
    sample_artifact = "Ember Crown"
    sample_episode = 1
    episode = generate_artifact_episode(sample_artifact, sample_episode)
    print(f"Generated: outputs/artifact_episode_{sample_episode}.json")
    print(f"Title: {episode['title']}")
    print(f"Scenes: {len(episode['scene_plan'])}")


if __name__ == "__main__":
    main()
