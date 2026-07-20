from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.choices import (
    PaletteSource,
    ThemeMode,
)
from apps.core.models import (
    BusinessCategory,
    ColorFamily,
    DesignStyle,
    Mood,
)
from apps.palettes.models import Palette
from apps.recommendations.models import (
    RecommendationRule,
    RecommendationRuleAvoidedColor,
)


RULE_BLUEPRINTS = [
    {
        "category_slug": "technology",
        "mood_slug": "modern",
        "style_slug": "futuristic",
        "preferred_family_slug": "blue",
        "avoided_family_slugs": [
            "brown",
            "red",
        ],
    },
    {
        "category_slug": "finance",
        "mood_slug": "trustworthy",
        "style_slug": "corporate",
        "preferred_family_slug": "blue",
        "avoided_family_slugs": [
            "pink",
            "orange",
        ],
    },
    {
        "category_slug": "restaurant-food",
        "mood_slug": "friendly",
        "style_slug": "organic",
        "preferred_family_slug": "red",
        "avoided_family_slugs": [
            "gray",
            "indigo",
        ],
    },
    {
        "category_slug": "healthcare",
        "mood_slug": "calm",
        "style_slug": "minimal",
        "preferred_family_slug": "teal",
        "avoided_family_slugs": [
            "red",
            "black",
        ],
    },
    {
        "category_slug": "education",
        "mood_slug": "energetic",
        "style_slug": "modern",
        "preferred_family_slug": "blue",
        "avoided_family_slugs": [
            "brown",
            "black",
        ],
    },
    {
        "category_slug": "beauty-cosmetics",
        "mood_slug": "elegant",
        "style_slug": "luxury",
        "preferred_family_slug": "pink",
        "avoided_family_slugs": [
            "gray",
            "brown",
        ],
    },
    {
        "category_slug": "construction",
        "mood_slug": "bold",
        "style_slug": "corporate",
        "preferred_family_slug": "orange",
        "avoided_family_slugs": [
            "pink",
            "purple",
        ],
    },
    {
        "category_slug": "logistics-transport",
        "mood_slug": "professional",
        "style_slug": "modern",
        "preferred_family_slug": "blue",
        "avoided_family_slugs": [
            "pink",
            "purple",
        ],
    },
]


class Command(BaseCommand):
    help = (
        "Seeds primary and fallback recommendation rules "
        "for supported business categories."
    )

    requires_migrations_checks = True

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Seeding Skilite Build recommendation rules..."
            )
        )

        rule_counts = {
            "created": 0,
            "updated": 0,
        }

        avoided_counts = {
            "created": 0,
            "updated": 0,
            "deleted": 0,
        }

        for blueprint in RULE_BLUEPRINTS:
            category = self.get_required_object(
                BusinessCategory,
                slug=blueprint["category_slug"],
                is_active=True,
            )

            mood = self.get_required_object(
                Mood,
                slug=blueprint["mood_slug"],
                is_active=True,
            )

            design_style = self.get_required_object(
                DesignStyle,
                slug=blueprint["style_slug"],
                is_active=True,
            )

            preferred_family = self.get_required_object(
                ColorFamily,
                slug=blueprint["preferred_family_slug"],
                is_active=True,
            )

            avoided_families = [
                self.get_required_object(
                    ColorFamily,
                    slug=slug,
                    is_active=True,
                )
                for slug in blueprint[
                    "avoided_family_slugs"
                ]
            ]

            for theme_mode, theme_slug in (
                (ThemeMode.LIGHT, "light"),
                (ThemeMode.DARK, "dark"),
            ):
                template_slug = (
                    f"system-template-"
                    f"{blueprint['category_slug']}-"
                    f"{theme_slug}"
                )

                template_palette = self.get_required_template(
                    slug=template_slug,
                    category=category,
                    theme_mode=theme_mode,
                )

                primary_rule, primary_created = (
                    RecommendationRule.objects.update_or_create(
                        name=(
                            f"{category.name} - "
                            f"{theme_mode.label} - Primary"
                        ),
                        defaults={
                            "description": (
                                f"Primary {theme_mode.label.lower()} "
                                f"recommendation rule for "
                                f"{category.name.lower()} businesses."
                            ),
                            "business_category": category,
                            "mood": mood,
                            "design_style": design_style,
                            "preferred_color_family": (
                                preferred_family
                            ),
                            "template_palette": template_palette,
                            "created_by": None,
                            "theme_mode": theme_mode,
                            "priority": 100,
                            "is_active": True,
                        },
                    )
                )

                self.update_rule_count(
                    rule_counts,
                    primary_created,
                )

                current_counts = self.sync_avoided_colors(
                    rule=primary_rule,
                    avoided_families=avoided_families,
                )

                self.merge_counts(
                    avoided_counts,
                    current_counts,
                )

                fallback_rule, fallback_created = (
                    RecommendationRule.objects.update_or_create(
                        name=(
                            f"{category.name} - "
                            f"{theme_mode.label} - Fallback"
                        ),
                        defaults={
                            "description": (
                                f"Fallback {theme_mode.label.lower()} "
                                f"recommendation rule for "
                                f"{category.name.lower()} businesses "
                                "when no more specific rule matches."
                            ),
                            "business_category": category,
                            "mood": None,
                            "design_style": None,
                            "preferred_color_family": None,
                            "template_palette": template_palette,
                            "created_by": None,
                            "theme_mode": theme_mode,
                            "priority": 10,
                            "is_active": True,
                        },
                    )
                )

                self.update_rule_count(
                    rule_counts,
                    fallback_created,
                )

                current_counts = self.sync_avoided_colors(
                    rule=fallback_rule,
                    avoided_families=avoided_families,
                )

                self.merge_counts(
                    avoided_counts,
                    current_counts,
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Recommendation rules seeded successfully."
            )
        )

        self.stdout.write(
            f"Rules: {rule_counts['created']} created, "
            f"{rule_counts['updated']} updated."
        )

        self.stdout.write(
            f"Avoided colour records: "
            f"{avoided_counts['created']} created, "
            f"{avoided_counts['updated']} updated, "
            f"{avoided_counts['deleted']} removed."
        )

    def sync_avoided_colors(
        self,
        rule,
        avoided_families,
    ):
        desired_ids = {
            family.id
            for family in avoided_families
        }

        stale_queryset = (
            RecommendationRuleAvoidedColor.objects.filter(
                recommendation_rule=rule,
            ).exclude(
                color_family_id__in=desired_ids,
            )
        )

        deleted_count, _ = stale_queryset.delete()

        counts = {
            "created": 0,
            "updated": 0,
            "deleted": deleted_count,
        }

        for color_family in avoided_families:
            _, created = (
                RecommendationRuleAvoidedColor.objects
                .update_or_create(
                    recommendation_rule=rule,
                    color_family=color_family,
                    defaults={},
                )
            )

            if created:
                counts["created"] += 1
            else:
                counts["updated"] += 1

        return counts

    def get_required_template(
        self,
        slug,
        category,
        theme_mode,
    ):
        try:
            template = Palette.objects.get(
                slug=slug,
                is_active=True,
            )
        except Palette.DoesNotExist as exc:
            raise CommandError(
                f"Missing recommendation template '{slug}'. "
                "Run: python manage.py seed_palette_templates"
            ) from exc

        if (
            template.source_type
            != PaletteSource.RECOMMENDATION_TEMPLATE
        ):
            raise CommandError(
                f"Palette '{slug}' is not a recommendation template."
            )

        if template.business_category_id != category.id:
            raise CommandError(
                f"Template '{slug}' belongs to the wrong "
                "business category."
            )

        if template.theme_mode != theme_mode:
            raise CommandError(
                f"Template '{slug}' has the wrong theme mode."
            )

        return template

    def get_required_object(
        self,
        model,
        **lookup,
    ):
        try:
            return model.objects.get(**lookup)
        except model.DoesNotExist as exc:
            lookup_description = ", ".join(
                f"{key}={value}"
                for key, value in lookup.items()
            )

            raise CommandError(
                f"Missing {model.__name__} record: "
                f"{lookup_description}. "
                "Run: python manage.py seed_reference_data"
            ) from exc

    def update_rule_count(
        self,
        counts,
        created,
    ):
        if created:
            counts["created"] += 1
        else:
            counts["updated"] += 1

    def merge_counts(
        self,
        destination,
        source,
    ):
        for key in destination:
            destination[key] += source[key]
