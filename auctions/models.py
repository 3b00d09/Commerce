from secrets import choice
from tokenize import Triple
from turtle import ondrag
from unicodedata import category
from django.contrib.auth.models import AbstractUser
from django.db import models

CHOICES = (('furniture', 'Furniture'),('kitchen', 'Kitchen'),
        ('decor', 'Decor'),('electronics', 'Electronics'),('toys', 'Toys'),
        ('books', 'Books'), ('outdoor', 'Outdoor'), ('art', 'Art'), ('other', "Other"))

OPTIONS = (('Active','Active'), ('Closed', 'Closed'))

class User(AbstractUser):
    pass

class Auctionitem(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(null=True, max_length=225)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=64, choices=CHOICES)
    starting_price = models.DecimalField(decimal_places=2, max_digits = 12)
    image = models.ImageField(upload_to="images", null = True, blank = True)
    state = models.CharField(max_length=64, choices=OPTIONS, default="Active")
    highest_bidder = models.ForeignKey(User, on_delete=models.CASCADE, null = True, related_name="highest_bidder")
    current_price = models.DecimalField(decimal_places=2, max_digits = 12, null = True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }
    def __str__(self):
        return f"{self.name}"

class Bid(models.Model):
    #make this table store the prices of the items 
    item = models.ForeignKey(Auctionitem, on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2, max_digits = 12)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.item}"

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    time = models.DateTimeField()
    item = models.ForeignKey(Auctionitem, on_delete=models.CASCADE)
    
class WatchList(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ManyToManyField(Auctionitem, blank=True, related_name="items")