from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retrospectives', '0005_allow_self_vote'),
    ]

    operations = [
        migrations.AddField(
            model_name='retrospective',
            name='phase_durations',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
