# Generated by Django 4.0.3 on 2022-05-03 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auctionitem_highest_bidder'),
    ]

    operations = [
        migrations.AddField(
            model_name='auctionitem',
            name='current_price',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True),
        ),
    ]
