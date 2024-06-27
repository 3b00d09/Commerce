from django import forms
from PIL import Image
from django.forms import ModelForm
from .models import Auctionitem, Bid, Comment

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ("comment",)
        labels = {"comment":"Add Comment"}
        widgets = {"comment": forms.Textarea(attrs={"class":"comment-form", "rows":"3"})}

class NewBid(ModelForm):
    class Meta:
        model = Bid
        fields = ("price",)
        labels={"price: Your Price"}
        widgets = {"price": forms.NumberInput}

class NewListing(ModelForm):
    class Meta:
        model = Auctionitem
        fields = ("name",
        "description",
        "category",
        "starting_price",
        "image")

        labels = {"name": "Item Name",
        "description": "Item Description",
        "category": "Item Category",
        "starting_price": "Bid Starting Price",
        "image": "(Optional) Image",
        }
    
        widgets = {"name": forms.TextInput(attrs={"class":"form-control"}),
        "description": forms.Textarea(attrs={"class":"form-control description-field"}),
        "starting_price": forms.NumberInput(attrs={"class":"form-control bid-field"}),
        "image": forms.FileInput(attrs={"class":"form-control image-upload-field"}),
        }

class CategoryFilter(ModelForm):
    class Meta:
        model = Auctionitem

        fields=("category",)

        labels ={
            "category" : "Item Category"
        }
