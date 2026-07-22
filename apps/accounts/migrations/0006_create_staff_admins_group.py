from django.db import migrations

def create_staff_admins_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    # Create the group
    group, created = Group.objects.get_or_create(name="Staff Admins")

    # Define minimal permissions:
    # - View palettes (palettes)
    # - View contact enquiries (core)
    # - Change contact enquiries (core)
    # - View user profiles (accounts)
    # - View activity logs (accounts)
    permission_codenames = [
        ("view_palette", "palettes"),
        ("view_contactenquiry", "core"),
        ("change_contactenquiry", "core"),
        ("view_userprofile", "accounts"),
        ("view_useractivitylog", "accounts"),
    ]

    for codename, app_label in permission_codenames:
        try:
            perm = Permission.objects.get(codename=codename, content_type__app_label=app_label)
            group.permissions.add(perm)
        except Permission.DoesNotExist:
            pass

def remove_staff_admins_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name="Staff Admins").delete()

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0005_user_must_change_password_user_phone_number_and_more'),
    ]

    operations = [
        migrations.RunPython(create_staff_admins_group, remove_staff_admins_group),
    ]
