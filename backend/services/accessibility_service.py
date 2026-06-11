"""Accessibility profile to prompt mode mapping."""

from config.constants import AccessibilityProfile, LearningMode


def resolve_mode(
    base_mode: LearningMode,
    accessibility_profile: AccessibilityProfile | None = None,
) -> LearningMode:
    """
    Resolve the effective learning mode based on accessibility profile.

    Accessibility profiles override the base mode prompt template.
    """
    if accessibility_profile is None:
        return base_mode

    profile_map = {
        AccessibilityProfile.BEGINNER: LearningMode.BEGINNER,
        AccessibilityProfile.DYSLEXIA: LearningMode.DYSLEXIA,
        AccessibilityProfile.VISUAL: LearningMode.VISUAL,
    }
    return profile_map.get(accessibility_profile, base_mode)
