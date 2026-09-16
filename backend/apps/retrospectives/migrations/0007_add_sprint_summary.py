import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retrospectives', '0006_add_phase_durations'),
    ]

    operations = [
        migrations.CreateModel(
            name='SprintSummary',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('total_stories', models.PositiveIntegerField()),
                ('completed', models.PositiveIntegerField()),
                ('carryover', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('retrospective', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sprint_summary',
                    to='retrospectives.retrospective',
                )),
            ],
            options={
                'verbose_name': 'Sprint Summary',
            },
        ),
    ]
