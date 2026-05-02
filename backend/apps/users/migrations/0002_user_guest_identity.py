from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		("users", "0001_initial"),
	]

	operations = [
		migrations.AddField(
			model_name="user",
			name="is_guest",
			field=models.BooleanField(default=False),
		),
		migrations.AddField(
			model_name="user",
			name="public_email",
			field=models.EmailField(blank=True, max_length=254),
		),
	]