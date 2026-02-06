# Generated migration for mainapp

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock', models.PositiveIntegerField(default=0)),
                ('image', models.ImageField(blank=True, null=True, upload_to='products/')),
                ('gender', models.CharField(choices=[('men', 'Men'), ('women', 'Women'), ('kids', 'Kids')], max_length=10)),
                ('product_type', models.CharField(choices=[('tshirt', 'T-Shirt'), ('shirt', 'Shirt'), ('saree', 'Saree'), ('pyjama', 'Pyjama'), ('jeans', 'Jeans'), ('kurta', 'Kurta'), ('dress', 'Dress'), ('lehenga', 'Lehenga'), ('blouse', 'Blouse'), ('trouser', 'Trouser'), ('jacket', 'Jacket'), ('other', 'Other')], default='other', max_length=20)),
                ('rating', models.DecimalField(decimal_places=1, default=0, max_digits=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mainapp.category')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('discount_type', models.CharField(choices=[('percent', 'Percentage'), ('fixed', 'Fixed Amount')], max_length=10)),
                ('discount_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('min_order_value', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('max_uses', models.PositiveIntegerField(blank=True, null=True)),
                ('used_count', models.PositiveIntegerField(default=0)),
                ('valid_from', models.DateTimeField(blank=True, null=True)),
                ('valid_to', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('discount_percent', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('valid_from', models.DateTimeField(blank=True, null=True)),
                ('valid_to', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.category')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.product')),
            ],
        ),
    ]
