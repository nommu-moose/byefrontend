from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('template', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataForFiltering',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('domain', models.CharField(max_length=120)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('birthday', models.DateField()),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('account_credits', models.FloatField(default=0)),
            ],
        ),
    ]
