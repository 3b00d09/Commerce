from django.contrib import admin

from .models import Auctionitem, User, Bid, Comment, WatchList

class ItemDisplay(admin.ModelAdmin):
    list_display = ("id", "name", "seller", "starting_price","category")

class BidDisplay(admin.ModelAdmin):
    list_display = ("id", "item", "bidder","price")

class CommentDisplay(admin.ModelAdmin):
    list_display = ("author", "comment", "item")



# Register your models here.
admin.site.register(User)
admin.site.register(Auctionitem, ItemDisplay)
admin.site.register(Bid, BidDisplay)
admin.site.register(Comment, CommentDisplay)
admin.site.register(WatchList)



