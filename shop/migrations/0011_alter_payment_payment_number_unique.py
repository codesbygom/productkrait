from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0010_alter_product_image_alter_product_thumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_number',
            field=models.CharField(max_length=100, unique=True, verbose_name='Payment number'),
        ),
    ]
