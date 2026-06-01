from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("flight", "0004_alter_flightseat_status"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE flight_flightseat
                ADD COLUMN IF NOT EXISTS pending_until timestamp with time zone NULL;

                ALTER TABLE flight_flightseat
                ADD COLUMN IF NOT EXISTS pending_by_id bigint NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]