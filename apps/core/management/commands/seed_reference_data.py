from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.models import (
    BusinessCategory,
    ColorFamily,
    DesignStyle,
    Language,
    Mood,
)


class Command(BaseCommand):
    help = (
        "Seeds languages, business categories, moods, "
        "design styles, and color families."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Seeding Skilite Build reference data..."
            )
        )

        language_results = self.seed_languages()
        category_results = self.seed_business_categories()
        mood_results = self.seed_moods()
        style_results = self.seed_design_styles()
        color_results = self.seed_color_families()

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Skilite Build reference data seeded successfully."
            )
        )

        self.stdout.write(
            f"Languages: {language_results['created']} created, "
            f"{language_results['updated']} updated."
        )

        self.stdout.write(
            f"Business categories: "
            f"{category_results['created']} created, "
            f"{category_results['updated']} updated."
        )

        self.stdout.write(
            f"Moods: {mood_results['created']} created, "
            f"{mood_results['updated']} updated."
        )

        self.stdout.write(
            f"Design styles: {style_results['created']} created, "
            f"{style_results['updated']} updated."
        )

        self.stdout.write(
            f"Color families: {color_results['created']} created, "
            f"{color_results['updated']} updated."
        )

    def seed_languages(self):
        """
        Insert the languages initially supported by the platform.
        """

        languages = [
            {
                "code": "en",
                "name": "English",
                "native_name": "English",
                "is_active": True,
                "is_default": True,
            },
            {
                "code": "tw",
                "name": "Twi",
                "native_name": "Twi",
                "is_active": True,
                "is_default": False,
            },
            {
                "code": "gaa",
                "name": "Ga",
                "native_name": "Ga",
                "is_active": True,
                "is_default": False,
            },
            {
                "code": "fr",
                "name": "French",
                "native_name": "Français",
                "is_active": True,
                "is_default": False,
            },
        ]

        # Ensure that English is the only initial default language.
        Language.objects.update(is_default=False)

        return self.upsert_records(
            model=Language,
            records=languages,
            lookup_field="code",
        )

    def seed_business_categories(self):
        """
        Insert configurable business categories.
        """

        categories = [
            {
                "slug": "technology",
                "name": "Technology",
                "description": (
                    "Software, information technology, digital products, "
                    "telecommunications, and technology services."
                ),
                "icon": "fa-solid fa-laptop-code",
                "display_order": 1,
                "is_active": True,
            },
            {
                "slug": "finance",
                "name": "Finance",
                "description": (
                    "Banking, insurance, investment, accounting, "
                    "and financial services."
                ),
                "icon": "fa-solid fa-building-columns",
                "display_order": 2,
                "is_active": True,
            },
            {
                "slug": "restaurant-food",
                "name": "Restaurant and Food",
                "description": (
                    "Restaurants, cafés, catering services, "
                    "bakeries, and food businesses."
                ),
                "icon": "fa-solid fa-utensils",
                "display_order": 3,
                "is_active": True,
            },
            {
                "slug": "healthcare",
                "name": "Healthcare",
                "description": (
                    "Hospitals, clinics, pharmacies, laboratories, "
                    "and health-related services."
                ),
                "icon": "fa-solid fa-heart-pulse",
                "display_order": 4,
                "is_active": True,
            },
            {
                "slug": "education",
                "name": "Education",
                "description": (
                    "Schools, universities, training centres, "
                    "online courses, and educational services."
                ),
                "icon": "fa-solid fa-graduation-cap",
                "display_order": 5,
                "is_active": True,
            },
            {
                "slug": "beauty-cosmetics",
                "name": "Beauty and Cosmetics",
                "description": (
                    "Beauty salons, cosmetics, skincare, haircare, "
                    "and personal-care businesses."
                ),
                "icon": "fa-solid fa-wand-sparkles",
                "display_order": 6,
                "is_active": True,
            },
            {
                "slug": "construction",
                "name": "Construction",
                "description": (
                    "Construction companies, engineering firms, "
                    "contractors, and building services."
                ),
                "icon": "fa-solid fa-helmet-safety",
                "display_order": 7,
                "is_active": True,
            },
            {
                "slug": "logistics-transport",
                "name": "Logistics and Transport",
                "description": (
                    "Transportation, delivery, shipping, warehousing, "
                    "and logistics services."
                ),
                "icon": "fa-solid fa-truck-fast",
                "display_order": 8,
                "is_active": True,
            },
            {
                "slug": "fashion",
                "name": "Fashion",
                "description": (
                    "Clothing brands, fashion designers, boutiques, "
                    "uniforms, and accessories."
                ),
                "icon": "fa-solid fa-shirt",
                "display_order": 9,
                "is_active": True,
            },
            {
                "slug": "corporate-services",
                "name": "Corporate Services",
                "description": (
                    "Consulting, professional services, agencies, "
                    "and corporate organisations."
                ),
                "icon": "fa-solid fa-briefcase",
                "display_order": 10,
                "is_active": True,
            },
            {
                "slug": "agriculture",
                "name": "Agriculture",
                "description": (
                    "Farming, agribusiness, food production, "
                    "and agricultural services."
                ),
                "icon": "fa-solid fa-seedling",
                "display_order": 11,
                "is_active": True,
            },
            {
                "slug": "real-estate",
                "name": "Real Estate",
                "description": (
                    "Property sales, rentals, estate development, "
                    "and property management."
                ),
                "icon": "fa-solid fa-house",
                "display_order": 12,
                "is_active": True,
            },
            {
                "slug": "hospitality-tourism",
                "name": "Hospitality and Tourism",
                "description": (
                    "Hotels, resorts, travel agencies, tourism, "
                    "and guest services."
                ),
                "icon": "fa-solid fa-hotel",
                "display_order": 13,
                "is_active": True,
            },
            {
                "slug": "nonprofit-ngo",
                "name": "Nonprofit and NGO",
                "description": (
                    "Foundations, charities, nonprofit organisations, "
                    "and community initiatives."
                ),
                "icon": "fa-solid fa-hand-holding-heart",
                "display_order": 14,
                "is_active": True,
            },
        ]

        return self.upsert_records(
            model=BusinessCategory,
            records=categories,
            lookup_field="slug",
        )

    def seed_moods(self):
        """
        Insert emotional tones used by the recommendation engine.
        """

        moods = [
            {
                "slug": "professional",
                "name": "Professional",
                "description": (
                    "Reliable, structured, credible, and business-focused."
                ),
                "is_active": True,
            },
            {
                "slug": "friendly",
                "name": "Friendly",
                "description": (
                    "Warm, approachable, welcoming, and conversational."
                ),
                "is_active": True,
            },
            {
                "slug": "elegant",
                "name": "Elegant",
                "description": (
                    "Refined, graceful, polished, and sophisticated."
                ),
                "is_active": True,
            },
            {
                "slug": "energetic",
                "name": "Energetic",
                "description": (
                    "Active, exciting, bright, and attention-grabbing."
                ),
                "is_active": True,
            },
            {
                "slug": "calm",
                "name": "Calm",
                "description": (
                    "Peaceful, balanced, soft, and reassuring."
                ),
                "is_active": True,
            },
            {
                "slug": "luxurious",
                "name": "Luxurious",
                "description": (
                    "Premium, exclusive, sophisticated, and prestigious."
                ),
                "is_active": True,
            },
            {
                "slug": "modern",
                "name": "Modern",
                "description": (
                    "Contemporary, clean, innovative, and forward-looking."
                ),
                "is_active": True,
            },
            {
                "slug": "playful",
                "name": "Playful",
                "description": (
                    "Fun, colourful, creative, and youthful."
                ),
                "is_active": True,
            },
            {
                "slug": "trustworthy",
                "name": "Trustworthy",
                "description": (
                    "Secure, dependable, honest, and reassuring."
                ),
                "is_active": True,
            },
            {
                "slug": "bold",
                "name": "Bold",
                "description": (
                    "Strong, confident, dramatic, and visually striking."
                ),
                "is_active": True,
            },
        ]

        return self.upsert_records(
            model=Mood,
            records=moods,
            lookup_field="slug",
        )

    def seed_design_styles(self):
        """
        Insert visual styles used by recommendation rules.
        """

        styles = [
            {
                "slug": "minimal",
                "name": "Minimal",
                "description": (
                    "Simple layouts, limited decoration, "
                    "and generous spacing."
                ),
                "is_active": True,
            },
            {
                "slug": "modern",
                "name": "Modern",
                "description": (
                    "Contemporary layouts, clean components, "
                    "and current design patterns."
                ),
                "is_active": True,
            },
            {
                "slug": "corporate",
                "name": "Corporate",
                "description": (
                    "Structured and professional presentation "
                    "for organisations."
                ),
                "is_active": True,
            },
            {
                "slug": "creative",
                "name": "Creative",
                "description": (
                    "Expressive layouts, artistic elements, "
                    "and distinctive visual choices."
                ),
                "is_active": True,
            },
            {
                "slug": "luxury",
                "name": "Luxury",
                "description": (
                    "Premium typography, refined spacing, "
                    "and sophisticated colour combinations."
                ),
                "is_active": True,
            },
            {
                "slug": "bold",
                "name": "Bold",
                "description": (
                    "Large typography, strong contrast, "
                    "and striking visual elements."
                ),
                "is_active": True,
            },
            {
                "slug": "classic",
                "name": "Classic",
                "description": (
                    "Traditional, balanced, familiar, "
                    "and timeless presentation."
                ),
                "is_active": True,
            },
            {
                "slug": "futuristic",
                "name": "Futuristic",
                "description": (
                    "Technology-focused layouts, gradients, "
                    "and innovative visual effects."
                ),
                "is_active": True,
            },
            {
                "slug": "organic",
                "name": "Organic",
                "description": (
                    "Natural shapes, earth-inspired colours, "
                    "and relaxed layouts."
                ),
                "is_active": True,
            },
            {
                "slug": "editorial",
                "name": "Editorial",
                "description": (
                    "Typography-led layouts inspired by magazines "
                    "and publishing."
                ),
                "is_active": True,
            },
        ]

        return self.upsert_records(
            model=DesignStyle,
            records=styles,
            lookup_field="slug",
        )

    def seed_color_families(self):
        """
        Insert general colour groups used by recommendations.
        """

        color_families = [
            {
                "slug": "red",
                "name": "Red",
                "sample_hex": "#EF4444",
                "description": "Strong, energetic, urgent, and passionate.",
                "is_active": True,
            },
            {
                "slug": "orange",
                "name": "Orange",
                "sample_hex": "#F97316",
                "description": "Warm, friendly, active, and enthusiastic.",
                "is_active": True,
            },
            {
                "slug": "yellow",
                "name": "Yellow",
                "sample_hex": "#EAB308",
                "description": "Optimistic, bright, cheerful, and energetic.",
                "is_active": True,
            },
            {
                "slug": "green",
                "name": "Green",
                "sample_hex": "#22C55E",
                "description": "Natural, healthy, successful, and balanced.",
                "is_active": True,
            },
            {
                "slug": "teal",
                "name": "Teal",
                "sample_hex": "#14B8A6",
                "description": "Calm, modern, refreshing, and professional.",
                "is_active": True,
            },
            {
                "slug": "cyan",
                "name": "Cyan",
                "sample_hex": "#06B6D4",
                "description": "Fresh, digital, clean, and innovative.",
                "is_active": True,
            },
            {
                "slug": "blue",
                "name": "Blue",
                "sample_hex": "#3B82F6",
                "description": "Trustworthy, professional, secure, and calm.",
                "is_active": True,
            },
            {
                "slug": "indigo",
                "name": "Indigo",
                "sample_hex": "#6366F1",
                "description": "Intelligent, creative, modern, and confident.",
                "is_active": True,
            },
            {
                "slug": "purple",
                "name": "Purple",
                "sample_hex": "#A855F7",
                "description": "Creative, premium, imaginative, and luxurious.",
                "is_active": True,
            },
            {
                "slug": "pink",
                "name": "Pink",
                "sample_hex": "#EC4899",
                "description": "Creative, expressive, warm, and playful.",
                "is_active": True,
            },
            {
                "slug": "brown",
                "name": "Brown",
                "sample_hex": "#92400E",
                "description": "Earthy, dependable, natural, and traditional.",
                "is_active": True,
            },
            {
                "slug": "gray",
                "name": "Gray",
                "sample_hex": "#6B7280",
                "description": "Neutral, balanced, professional, and practical.",
                "is_active": True,
            },
            {
                "slug": "black",
                "name": "Black",
                "sample_hex": "#000000",
                "description": "Powerful, elegant, premium, and sophisticated.",
                "is_active": True,
            },
            {
                "slug": "white",
                "name": "White",
                "sample_hex": "#FFFFFF",
                "description": "Clean, simple, open, and minimal.",
                "is_active": True,
            },
        ]

        return self.upsert_records(
            model=ColorFamily,
            records=color_families,
            lookup_field="slug",
        )

    def upsert_records(self, model, records, lookup_field):
        """
        Insert missing records and update existing records.

        The stable field, such as code or slug, is used to find
        the existing record.
        """

        created_count = 0
        updated_count = 0

        for record in records:
            lookup_value = record[lookup_field]

            defaults = {
                key: value
                for key, value in record.items()
                if key != lookup_field
            }

            _, created = model.objects.update_or_create(
                **{
                    lookup_field: lookup_value,
                },
                defaults=defaults,
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        return {
            "created": created_count,
            "updated": updated_count,
        }