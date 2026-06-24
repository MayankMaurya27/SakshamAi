"""Unit tests for accessibility service."""

from config.constants import AccessibilityProfile, LearningMode
from services.accessibility_service import resolve_mode


def test_resolve_mode_no_profile():
    """Without profile, base mode should be returned."""
    assert resolve_mode(LearningMode.LEARN, None) == LearningMode.LEARN
    assert resolve_mode(LearningMode.HINDI, None) == LearningMode.HINDI


def test_resolve_mode_beginner():
    """Beginner profile should return base mode."""
    assert resolve_mode(LearningMode.LEARN, AccessibilityProfile.BEGINNER) == LearningMode.LEARN
    assert resolve_mode(LearningMode.SIMPLIFY, AccessibilityProfile.BEGINNER) == LearningMode.SIMPLIFY


def test_resolve_mode_dyslexia():
    """Dyslexia profile should override to DYSLEXIA mode."""
    assert resolve_mode(LearningMode.LEARN, AccessibilityProfile.DYSLEXIA) == LearningMode.DYSLEXIA


def test_resolve_mode_visual():
    """Visual profile should override to VISUAL mode."""
    assert resolve_mode(LearningMode.SIMPLIFY, AccessibilityProfile.VISUAL) == LearningMode.VISUAL
