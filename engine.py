"""Fireverse Artifact Engine.

Generates cinematic 7-scene episodes centered on a single artifact from the
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


@dataclass
class LegendaryIdentity:
    element: str
    energy_color: str


SCENE_BEATS: List[SceneBeat] = [
    SceneBeat("Discovery inside vault", "Introduce the artifact in a sacred hidden chamber."),
    SceneBeat("Archive reveal with relic rows", "Show relic curiosity with future-episode hints on both sides."),
    SceneBeat("Energy awakening", "Establish the first controlled surge of legendary energy."),
    SceneBeat("Activation buildup with distorted silhouette", "Escalate pressure and hint at danger without full reveal."),
    SceneBeat("Explosive release + inner vision legendary reveal", "Transition into inner vision world for cinematic climax."),
    SceneBeat("Calm containment + micro shimmer twist", "Restore order, then inject a very brief ominous shimmer."),
    SceneBeat("Energy leak to next artifact", "Create urgent cliffhanger linking directly to the next episode."),
]

LEGENDARY_COLOR_RULES: Dict[str, LegendaryIdentity] = {
    "electric": LegendaryIdentity(element="electric", energy_color="yellow"),
    "ice": LegendaryIdentity(element="ice", energy_color="blue"),
    "fire": LegendaryIdentity(element="fire", energy_color="red/orange"),
}

AUTO_CINEMATIC_PROMPT_MODE = True


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
    identity: LegendaryIdentity,
    reveal_scale: str,
    episode_intensity: str,
    next_artifact: Dict[str, str],
) -> List[Dict[str, str]]:
    pacing_map = {
        1: director["pacing"]["scene_1_to_3"],
        2: director["pacing"]["scene_1_to_3"],
        3: director["pacing"]["scene_1_to_3"],
        4: director["pacing"]["scene_4"],
        5: director["pacing"]["scene_5"],
        6: director["pacing"]["scene_6"],
        7: director["pacing"]["scene_7"],
    }

    lore = vault["core_lore"]

    scene_five_reveal = (
        f"fully in a storm-torn inner vision realm" if reveal_scale == "full" else f"as a fragmented silhouette in the inner vision realm"
    )

    narration = [
        f"Inside the sealed vault sanctum, the {artifact['name']} rises from a dormant cradle of runes.",
        f"Archive lanes ignite with relics on both sides, each relic whispering unfinished legends beyond {lore[0]}",
        f"A steady pulse expands as {artifact['power']} awakens in {identity.energy_color} energy bands.",
        f"Containment rings strain while a distorted, partial silhouette of {spirit['name']} fractures through static.",
        f"The chamber detonates into light, then plunges inward—an inner vision realm reveals {spirit['name']} {scene_five_reveal}.",
        f"Containment returns to silence, yet a sub-second shimmer darts behind the altar as if tracking the wielder.",
        f"Residual energy leaks from the {artifact['name']} and lashes into the sealed {next_artifact['name']}, forcing an urgent camera snap.",
    ]

    scene_summaries = [
        f"The sacred chamber introduces the dormant {artifact['name']} and the first omen of awakening.",
        "Archive corridors reveal colossal relic rows while the camera maps left-right spatial depth for future threats.",
        f"A controlled ignition sequence spreads {identity.energy_color} energy through glyph rings and floor channels.",
        f"Containment geometry distorts as a fragmented silhouette of {spirit['name']} appears without full manifestation.",
        f"An inner vision transition reveals {spirit['name']} in legendary form and reframes the artifact's destiny.",
        "The chamber regains composure while a fleeting shimmer implies hidden surveillance in the background.",
        f"A rapid energy leak bridges to {next_artifact['name']} and ends on a hard cliffhanger cut.",
    ]

    visual_focus = [
        f"Discovery chamber altar reveals {artifact['name']} with {artifact['visual_motif']} detail under blue ambient vault haze.",
        "Symmetrical archive corridor with massive relics on both sides, each artifact imposing and curiosity-driven.",
        f"Legendary {identity.energy_color} veins race across glyphs and overtake ambient blue tones.",
        f"Activation rings spin while only a distorted partial silhouette of {spirit['name']} flickers in warped glass reflections.",
        "Explosive release, camera rush into artifact core, transition into an inner vision world with storm-charged cinematic danger.",
        "Vault stabilizes to calm blue ambiance; a near-invisible shimmer/shadow crosses frame for less than one second.",
        f"Rapid whip-pan from current altar to the sealed {next_artifact['name']} as leaked energy arcs across the vault, with optional dark sorcerer-like silhouette in background.",
    ]

    transition_notes = [
        "Fade in from darkness to sacred archive silence.",
        "Slow lateral glide between towering relic rows on left and right.",
        f"Push-in toward artifact core as {identity.energy_color} ignition overtakes ambient blue light.",
        "Stutter-zoom with lens distortion; silhouette remains fragmented and never fully clear.",
        "Explosive flash -> camera rush into artifact -> hard transition to inner vision world (not vault reality).",
        "Breath-hold static frame after containment, then micro shimmer less than one second.",
        "Whip-pan following leaked energy into next sealed relic to form an urgent cliffhanger cut.",
    ]

    scenes: List[Dict[str, str]] = []
    safety_line = "; ".join(director["safety_rules"])

    camera_paths = {
        1: "Start with a 24mm wide lens, descend from ceiling centerline to a waist-level dolly push toward the altar at frame center",
        2: "Execute a left-to-right lateral tracking move along the corridor axis while keeping relic rows locked on both sides",
        3: "Push in from medium-wide to close-up on the core, then orbit 35 degrees clockwise around the artifact",
        4: "Apply a controlled stutter-zoom inward with slight handheld vibration while maintaining the silhouette in rear-midground",
        5: "Crash-zoom into the artifact core, crossfade through whiteout, then glide forward through the inner vision horizon",
        6: "Hold a static master shot for six seconds, then perform a subtle 10-degree pan to catch the shimmer crossing background",
        7: "Whip-pan from current altar to the sealed next relic pedestal, ending in a snap-in close-up with no camera drift",
    }

    layout_notes = {
        1: "Artifact centered on elevated altar; spirit sigils etched in concentric circles on the floor; rear walls lined with dormant runes.",
        2: "Main subject stays in center lane; towering relic columns occupy left and right thirds; distant vault gate anchors deep background.",
        3: "Energy filaments originate at artifact apex, travel through ring conduits at knee height, and rebound to ceiling glyph nodes.",
        4: "Containment rings form a 3-layer cylindrical cage around subject; fragmented silhouette appears in upper-right reflective shard.",
        5: "Inner vision realm opens beneath subject into a storm valley; legendary figure stands full-height on a ridge in mid-background.",
        6: "Primary altar remains foreground center; shimmer streak traverses rear-left to rear-right behind support pillars.",
        7: f"Leaked energy exits frame right from {artifact['name']} and strikes {next_artifact['name']} at frame-left pedestal across the vault span.",
    }

    energy_behavior = {
        1: "Energy remains dormant with only faint pulse every two seconds.",
        2: "Background glyphs flicker at low amplitude, no uncontrolled discharge.",
        3: "Pulses accelerate from 40% to 70% intensity in synchronized waves.",
        4: "Containment strain creates jagged arcs that stop short of full release.",
        5: "Full legendary surge erupts, then channels into coherent streams within the inner vision world.",
        6: "Energy drops to near-zero, then emits one micro shimmer under 0.5 seconds.",
        7: "Energy pressure spikes rapidly, leaks in violent bursts, and transfers momentum to the next sealed artifact.",
    }

    timing_notes = {
        1: "Timing: 0-3s reveal environment, 3-7s push to artifact, 7-10s omen pulse.",
        2: "Timing: 0-4s lateral scan, 4-8s relic emphasis, 8-10s lock on central path.",
        3: "Timing: 0-2s calm hold, 2-6s ignition rise, 6-10s controlled orbit.",
        4: "Timing: 0-4s ring strain, 4-8s distortion spikes, 8-10s freeze before rupture.",
        5: "Timing: 0-2s explosive flash, 2-5s inner vision transition, 5-10s full legendary reveal tableau.",
        6: "Timing: 0-6s stillness, 6-9s tension hold, 9-10s micro shimmer.",
        7: "Timing: 0-3s pressure build, 3-7s rapid leak transfer, 7-10s cliffhanger lock before cut.",
    }

    for idx, beat in enumerate(SCENE_BEATS, start=1):
        image_prompt = (
            "Cinematic anime realism still frame. "
            f"Environment: {visual_focus[idx - 1]} "
            f"Subject placement: {layout_notes[idx]} "
            "Lighting: volumetric god rays, high-contrast rim light, reflective floor bounce, atmospheric fog layering. "
            "Atmosphere style: mythic sacred vault, dramatic yet grounded realism, sharp depth separation from foreground to deep background. "
            "Safety: PG-13 fantasy only, no gore, no explicit content, no dismemberment, no hateful symbols."
        )
        video_prompt = (
            f"Grok-optimized 10-second cinematic anime realism shot for scene {idx} '{beat.name}'. "
            f"Camera motion: {camera_paths[idx]}. "
            f"Spatial layout: {layout_notes[idx]} "
            f"Energy behavior: {energy_behavior[idx]} "
            f"Pacing profile: {pacing_map[idx]} with clean acceleration and controlled deceleration. "
            f"{timing_notes[idx]} "
            "Anti-randomness constraints: lock character count to named subjects only, preserve object continuity across all frames, "
            "keep energy color fixed, avoid random extra props, avoid spontaneous costume changes, avoid geometry warping, "
            "maintain consistent lens and horizon line. "
            "Background elements must remain visible: rune walls, floating dust motes, relic silhouettes, distant vault architecture. "
            "Output must stay safe-for-all-audiences with no graphic violence or explicit material."
        )

        if idx == 5:
            video_prompt += (
                " Mandatory story event: perform explicit inner vision transition and show the full legendary reveal at stable full-body scale."
            )
            image_prompt += " Mandatory story event: depict the inner vision transition and complete legendary reveal."

        if idx == 7:
            video_prompt += (
                f" Mandatory story event: execute a rapid energy leak transition into {next_artifact['name']} and end on a severe cliffhanger beat."
            )
            image_prompt += f" Mandatory story event: show rapid energy leakage toward {next_artifact['name']} with cliffhanger tension."

        scenes.append(
            {
                "scene_number": idx,
                "scene_summary": scene_summaries[idx - 1],
                "duration_seconds": director["scene_duration_seconds"],
                "beat": beat.name,
                "purpose": beat.purpose,
                "pacing_stage": pacing_map[idx],
                "visual_focus": visual_focus[idx - 1],
                "narration": narration[idx - 1],
                "legendary_energy_color": identity.energy_color,
                "legendary_element": identity.element,
                "legendary_reveal_scale": reveal_scale if idx == 5 else ("partial" if idx == 4 else "minor"),
                "episode_intensity": episode_intensity,
                "cinematic_transition_notes": transition_notes[idx - 1],
                "safe_image_prompt": image_prompt,
                "cinematic_video_prompt": video_prompt,
                "image_prompt": image_prompt,
                "video_prompt": video_prompt,
                "narration_line": narration[idx - 1],
                "safety_requirements": safety_line,
            }
        )

    return scenes


def _infer_legendary_identity(artifact: Dict[str, str]) -> LegendaryIdentity:
    signals = " ".join(
        [artifact["name"], artifact["origin"], artifact["power"], artifact["consequence"], artifact["visual_motif"]]
    ).lower()

    fire_words = {"ember", "fire", "flame", "molten", "volcanic", "infernal", "solar", "plasma"}
    ice_words = {"ice", "frost", "glacial", "blizzard", "winter", "cryo"}
    electric_words = {"electric", "lightning", "thunder", "storm", "voltaic", "kinetic", "spark"}

    if any(word in signals for word in fire_words):
        return LEGENDARY_COLOR_RULES["fire"]
    if any(word in signals for word in ice_words):
        return LEGENDARY_COLOR_RULES["ice"]
    if any(word in signals for word in electric_words):
        return LEGENDARY_COLOR_RULES["electric"]

    ordered = list(LEGENDARY_COLOR_RULES.values())
    return ordered[sum(ord(char) for char in artifact["name"]) % len(ordered)]


def _choose_next_artifact(artifacts: List[Dict[str, str]], artifact_name: str) -> Dict[str, str]:
    current_index = next((idx for idx, item in enumerate(artifacts) if item["name"] == artifact_name), None)
    if current_index is None:
        return artifacts[0]
    return artifacts[(current_index + 1) % len(artifacts)]


def _episode_intensity(episode_number: int) -> str:
    return "high" if episode_number % 3 == 0 else "standard"


def _determine_reveal_scale(episode_intensity: str) -> str:
    return "full" if episode_intensity == "high" else "partial"


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
    identity = _infer_legendary_identity(artifact)
    next_artifact = _choose_next_artifact(world["artifacts"], artifact["name"])
    episode_intensity = _episode_intensity(episode_number)
    reveal_scale = _determine_reveal_scale(episode_intensity)

    rng = Random(f"{_safe_slug(artifact_name)}-{episode_number}")
    spirit = world["spirits"][rng.randrange(0, len(world["spirits"]))]

    scenes = _build_scene_content(
        artifact,
        spirit,
        world["vault"],
        world["director"],
        identity,
        reveal_scale,
        episode_intensity,
        next_artifact,
    )

    title = _build_title(artifact, episode_number)
    thumbnail_concept = _build_thumbnail(artifact, spirit)
    hook = f"A sealed relic calls to the chosen hand—and the vault listens."
    cliffhanger = f"Leaked {identity.energy_color} energy surges into the sealed {next_artifact['name']}, forcing a vault-wide emergency."

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
        "auto_cinematic_prompt_mode": AUTO_CINEMATIC_PROMPT_MODE,
        "tone": world["director"]["language_style"],
        "episode_card": episode_card,
        "spirit_entity": spirit,
        "legendary_identity": {"element": identity.element, "energy_color": identity.energy_color},
        "legendary_reveal_scale_system": {
            "minor": "energy only",
            "partial": "silhouette",
            "full": "rare cinematic climax",
            "scene_5_selected_scale": reveal_scale,
            "episode_intensity": episode_intensity,
        },
        "next_episode_teaser_artifact": next_artifact["name"],
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
