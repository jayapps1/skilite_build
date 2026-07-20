from dataclasses import dataclass
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify

from apps.core.choices import (
    ColorRole,
    ModerationStatus,
    PaletteSource,
    PaletteVisibility,
    ThemeMode,
)
from apps.palettes.models import Palette, PaletteColor

from .models import (
    RecommendationRequest,
    RecommendationRequestAvoidedColor,
    RecommendationRule,
)


class RecommendationServiceError(Exception):
    """
    Base exception for recommendation-service failures.
    """


class RecommendationMatchError(RecommendationServiceError):
    """
    Raised when no compatible recommendation rule is found.
    """


class IncompleteTemplateError(RecommendationServiceError):
    """
    Raised when a recommendation template does not contain
    all required semantic colour roles.
    """


@dataclass(frozen=True)
class RecommendationResult:
    """
    Result returned after successfully generating a palette.
    """

    recommendation_request: RecommendationRequest
    selected_rule: RecommendationRule
    generated_palette: Palette
    score: int


class RecommendationService:
    """
    Matches recommendation input against active rules and creates
    a new user-owned palette from the selected template.
    """

    MOOD_MATCH_SCORE = 30
    DESIGN_STYLE_MATCH_SCORE = 25
    PREFERRED_COLOR_MATCH_SCORE = 20
    SPECIFIC_RULE_SCORE = 5

    @classmethod
    @transaction.atomic
    def generate(
        cls,
        *,
        user,
        business_category,
        theme_mode,
        mood=None,
        design_style=None,
        preferred_color_family=None,
        avoided_color_families=None,
    ) -> RecommendationResult:
        """
        Generate and save a recommendation palette.

        The method:

        1. Validates the requesting user and input.
        2. Finds compatible active recommendation rules.
        3. Selects the highest-scoring rule.
        4. Copies its 13 semantic colours.
        5. Creates a RecommendationRequest history record.
        """

        if not user or not user.is_authenticated:
            raise RecommendationServiceError(
                "You must be signed in to save a recommendation."
            )

        valid_theme_modes = set(ThemeMode.values)

        if theme_mode not in valid_theme_modes:
            raise RecommendationServiceError(
                "The selected theme mode is invalid."
            )

        avoided_color_families = list(
            avoided_color_families or []
        )

        avoided_family_ids = {
            color_family.pk
            for color_family in avoided_color_families
        }

        if (
            preferred_color_family
            and preferred_color_family.pk in avoided_family_ids
        ):
            raise RecommendationServiceError(
                "The preferred colour family cannot also be avoided."
            )

        rules = (
            RecommendationRule.objects
            .active()
            .filter(
                business_category=business_category,
                theme_mode=theme_mode,
                template_palette__is_active=True,
                template_palette__source_type=(
                    PaletteSource.RECOMMENDATION_TEMPLATE
                ),
            )
            .select_related(
                "business_category",
                "mood",
                "design_style",
                "preferred_color_family",
                "template_palette",
                "template_palette__business_category",
                "template_palette__dominant_color_family",
            )
            .prefetch_related(
                "avoided_color_families",
                "template_palette__colors",
            )
        )

        scored_rules = []

        for rule in rules:
            score = cls._score_rule(
                rule=rule,
                mood=mood,
                design_style=design_style,
                preferred_color_family=preferred_color_family,
                avoided_family_ids=avoided_family_ids,
            )

            if score is not None:
                scored_rules.append(
                    (
                        score,
                        cls._specificity(rule),
                        -rule.pk,
                        rule,
                    )
                )

        if not scored_rules:
            raise RecommendationMatchError(
                "No compatible recommendation could be found for "
                "the selected options. Remove one or more avoided "
                "colours or try another preference."
            )

        score, _, _, selected_rule = max(scored_rules)

        template_palette = selected_rule.template_palette

        color_map = cls._get_complete_template_colors(
            template_palette
        )

        generated_palette = cls._create_generated_palette(
            user=user,
            business_category=business_category,
            selected_rule=selected_rule,
            template_palette=template_palette,
            theme_mode=theme_mode,
            color_map=color_map,
        )

        recommendation_request = (
            RecommendationRequest.objects.create(
                user=user,
                business_category=business_category,
                mood=mood,
                design_style=design_style,
                preferred_color_family=preferred_color_family,
                selected_rule=selected_rule,
                generated_palette=generated_palette,
                theme_mode=theme_mode,
                session_key="",
            )
        )

        for color_family in avoided_color_families:
            RecommendationRequestAvoidedColor.objects.update_or_create(
                recommendation_request=recommendation_request,
                color_family=color_family,
                defaults={},
            )

        return RecommendationResult(
            recommendation_request=recommendation_request,
            selected_rule=selected_rule,
            generated_palette=generated_palette,
            score=score,
        )

    @classmethod
    def _score_rule(
        cls,
        *,
        rule,
        mood,
        design_style,
        preferred_color_family,
        avoided_family_ids,
    ):
        """
        Return a score for a compatible rule.

        Return None when the rule conflicts with the request.
        A null rule criterion works as a wildcard, allowing
        fallback rules to match.
        """

        template = rule.template_palette

        if (
            template.business_category_id
            and template.business_category_id
            != rule.business_category_id
        ):
            return None

        if template.theme_mode != rule.theme_mode:
            return None

        if (
            template.dominant_color_family_id
            and template.dominant_color_family_id
            in avoided_family_ids
        ):
            return None

        if (
            rule.preferred_color_family_id
            and rule.preferred_color_family_id
            in avoided_family_ids
        ):
            return None

        rule_avoided_ids = {
            color_family.pk
            for color_family
            in rule.avoided_color_families.all()
        }

        if (
            preferred_color_family
            and preferred_color_family.pk in rule_avoided_ids
        ):
            return None

        score = rule.priority

        if rule.mood_id:
            if not mood or mood.pk != rule.mood_id:
                return None

            score += cls.MOOD_MATCH_SCORE

        if rule.design_style_id:
            if (
                not design_style
                or design_style.pk != rule.design_style_id
            ):
                return None

            score += cls.DESIGN_STYLE_MATCH_SCORE

        if rule.preferred_color_family_id:
            if (
                not preferred_color_family
                or preferred_color_family.pk
                != rule.preferred_color_family_id
            ):
                return None

            score += cls.PREFERRED_COLOR_MATCH_SCORE

        score += (
            cls._specificity(rule)
            * cls.SPECIFIC_RULE_SCORE
        )

        return score

    @staticmethod
    def _specificity(rule):
        """
        Count how many optional matching criteria a rule defines.
        """

        return sum(
            [
                bool(rule.mood_id),
                bool(rule.design_style_id),
                bool(rule.preferred_color_family_id),
            ]
        )

    @staticmethod
    def _get_complete_template_colors(template_palette):
        """
        Return the template's role-to-HEX map after validating
        that all 13 semantic roles exist.
        """

        color_map = {
            color.role: color.hex_value.upper()
            for color in template_palette.colors.all()
        }

        expected_roles = set(ColorRole.values)
        actual_roles = set(color_map)

        missing_roles = sorted(
            expected_roles - actual_roles
        )

        unexpected_roles = sorted(
            actual_roles - expected_roles
        )

        if missing_roles or unexpected_roles:
            raise IncompleteTemplateError(
                f"The recommendation template "
                f"'{template_palette.name}' is incomplete. "
                f"Missing roles: {missing_roles}. "
                f"Unexpected roles: {unexpected_roles}."
            )

        return color_map

    @staticmethod
    def _create_generated_palette(
        *,
        user,
        business_category,
        selected_rule,
        template_palette,
        theme_mode,
        color_map,
    ):
        """
        Create the user-owned palette and copy all semantic colours.
        """

        theme_label = ThemeMode(theme_mode).label

        palette_name = (
            f"{business_category.name} "
            f"{theme_label} Recommendation"
        )

        slug_base = slugify(
            f"{user.username}-{business_category.slug}-"
            f"{theme_mode}-recommendation"
        )

        unique_slug = (
            f"{slug_base[:160]}-{uuid4().hex[:12]}"
        )

        generated_palette = Palette.objects.create(
            owner=user,
            business_category=business_category,
            dominant_color_family=(
                template_palette.dominant_color_family
            ),
            source_palette=template_palette,
            name=palette_name,
            slug=unique_slug,
            description=(
                f"Generated from the recommendation rule "
                f"'{selected_rule.name}'."
            ),
            source_type=PaletteSource.RECOMMENDATION,
            theme_mode=theme_mode,
            visibility=PaletteVisibility.PRIVATE,
            moderation_status=ModerationStatus.DRAFT,
            allow_export=True,
            is_published=False,
            is_featured=False,
            is_active=True,
            published_at=None,
        )

        try:
            for role in ColorRole.values:
                PaletteColor.objects.create(
                    palette=generated_palette,
                    role=role,
                    hex_value=color_map[role],
                )
        except (KeyError, ValidationError) as exc:
            raise IncompleteTemplateError(
                "The selected recommendation template could not "
                "be copied because its colour data is invalid."
            ) from exc

        return generated_palette