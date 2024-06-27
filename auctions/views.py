from pyexpat import model
from unicodedata import category
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import CommentForm , NewBid, NewListing, CategoryFilter
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime

from django.http import JsonResponse

from .models import Auctionitem, User, Comment, Bid, WatchList


def index(request):

    form = CategoryFilter
    return render (request, "auctions/index.html",{
    "listings": Auctionitem.objects.all(),
    "form": form
})

def view_listing(request, listing_id):
    
    # when my other functions redirect to this url via GET, it will handle getting the context, no need to do it in the 
    # functions themselves 
    try:
        bids = Bid.objects.get(item=listing_id)
    except Bid.DoesNotExist:
        bids = None
    
    bid_form = NewBid
    comment_form = CommentForm
    in_watchlist = False

    # check for invalid listing id from the url 
    try:
        item = Auctionitem.objects.get(id = listing_id)
    except:
        url = reverse("commerce:index")
        return HttpResponseRedirect(url)

    # check if item already exists in watchlist so we either display add or remove to watchlist
    try: 
        watchlist = WatchList.objects.get(author = request.user)
        for items in watchlist.item.all():
            if item == items:
                in_watchlist = True
                break
    except:
        pass

    return render (request, "auctions/listingpage.html",{
    "listing": item,
    "comments":Comment.objects.filter(item = listing_id),
    "bids":bids,
    "bid_form":bid_form,
    "comment_form":comment_form,
    "current_user":request.user,
    "in_watchlist": in_watchlist
    })



def login_view(request):
    
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("commerce:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    
    logout(request)
    return HttpResponseRedirect(reverse("commerce:index"))


def register(request):
    
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("commerce:index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url="commerce:login")
def submit_comment(request, listing_id):
    
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            # if the form is valid, we grab the comment content and then we get the item and author
            new_comment = request.POST.get('comment')
            item = Auctionitem.objects.get(id = listing_id)
            # store the data in an instance that gets saved onto the comments table
            new_comment = Comment(item = item, comment = new_comment, author = request.user, time = datetime.now())
            new_comment.save()
            url = reverse("commerce:view_listing", kwargs={"listing_id": listing_id})
            return HttpResponseRedirect(url)
        
        # invalid comment submitted
        else:
            url = reverse("commerce:view_listing", kwargs={"listing_id": listing_id})
            return HttpResponseRedirect(url)
    # if user tries to access the url submitcomment directly which is illegal, they get redirected
    else:
        url = reverse("commerce:view_listing", kwargs={"listing_id": listing_id})
        return HttpResponseRedirect(url)


@login_required(login_url="commerce:login")
def submit_bid(request,listing_id):
    
    if request.method == "POST":
        form = NewBid(request.POST)
        if form.is_valid():
            first_bid = False
            try:
                bid_item = Bid.objects.get(item=listing_id)
                bid_price = getattr(bid_item, "price")

            except Bid.DoesNotExist:
                bid_item = Auctionitem.objects.get(id = listing_id)
                bid_price = getattr(bid_item, "starting_price")
                first_bid = True

            
            bid_submitted = int(request.POST.get("price"))
            
            if first_bid:
                # handle first bid submitted here
                if bid_price <= bid_submitted:
                    bid_item = Auctionitem.objects.get(id=listing_id)
                    new_bid = Bid(item = bid_item, bidder = request.user, price = bid_submitted)
                    new_bid.save()
                    Auctionitem.objects.filter(id = listing_id).update(highest_bidder = request.user, current_price = bid_submitted)
                    messages.success(request, 'Bid Submitted!')
                    url = reverse("commerce:view_listing", kwargs={"listing_id": listing_id})
                    return HttpResponseRedirect(url)
                else:
                    messages.error(request, 'Invalid Bid Submission.')
                    url = reverse("commerce:view_listing", kwargs={"listing_id": listing_id})
                    return HttpResponseRedirect(url) 

            if bid_submitted > bid_price:
                # handle valid bid
                bidder = request.user
                price = bid_submitted
                bid_item.price = price
                bid_item.bidder = bidder
                bid_item.save()
                Auctionitem.objects.filter(id = listing_id).update(highest_bidder = request.user, current_price = bid_submitted)
                messages.success(request, 'Bid Submitted!')
                url = reverse("commerce:view_listing", kwargs={"listing_id": listing_id})
                return HttpResponseRedirect(url)                
            else:
                # handle bid thats valid but lower than current bid
                messages.error(request, 'Invalid Bid Submission.')
                url = reverse("commerce:view_listing", kwargs={"listing_id": listing_id})
                return HttpResponseRedirect(url)
        # invalid bid submitted or GET request
        else:
            url = reverse("commerce:view_listing", kwargs={"listing_id": listing_id})
            return HttpResponseRedirect(url)


@login_required(login_url="commerce:login")
def create_listing(request):

    if request.method == "POST":
        form = NewListing(request.POST, request.FILES)
        if form.is_valid():
            # save the form data in an item instance. we do this so we can add user later 
            item = form.save(commit = False)
            # commit false tells django to wait before sending this instance to the DB because we have more to do 
            item.seller = request.user
            item.save()
            messages.success(request, 'Auction Item Added!')
            url = reverse("commerce:create")
            return HttpResponseRedirect(url)  
        else:
            messages.error(request, 'Invalid Submission')
            url = reverse("commerce:create")
            return HttpResponseRedirect(url)  
    
    else:
        form = NewListing
        return render(request, "auctions/create.html", {
            "form": form
        })


def close_bid(request, listing_id):

    Auctionitem.objects.filter(id = listing_id).update(state = "Closed")
    url = reverse("commerce:view_listing", kwargs={"listing_id": listing_id})
    return HttpResponseRedirect(url) 


def category_filter(request):

    if request.method == "POST":
        requested_category = request.POST.get("category")
        url = reverse("commerce:view_category", kwargs={"category": requested_category})
        return HttpResponseRedirect(url)
    else:
        url = reverse("commerce:index")
        return HttpResponseRedirect(url)

def view_category(request, category):
    form = CategoryFilter
    category = category.lower()
    items = Auctionitem.objects.filter(category = category)
    return render(request, "auctions/index.html",{
        "listings": items,
        "form": form
    })


@login_required(login_url="commerce:login")
def add_watchlist(request, listing_id):

    if request.method == "POST":
        # we try to add item to watchlist if one exists, else we create a new watchlist and add the item to it
        try:
            user = WatchList.objects.get(author = request.user)
            watchlist_item = Auctionitem.objects.get(id = listing_id)
            user.item.add(watchlist_item)
        except:
            new_watchlist = WatchList(author = request.user)
            new_watchlist.save()
            new_watchlist.item.add(Auctionitem.objects.get(id = listing_id))
            new_watchlist.save()


        url = reverse("commerce:view_listing", kwargs={"listing_id": listing_id})
        return HttpResponseRedirect(url)
    else:
        url = reverse("commerce:view_listing", kwargs={"listing_id": listing_id})
        return HttpResponseRedirect(url)


@login_required(login_url="commerce:login")
def remove_watchlist (request, listing_id):

    if request.method == "POST":
        try:
            watchlist = WatchList.objects.get(author = request.user)
            item = Auctionitem.objects.get(id = listing_id)
            watchlist.item.remove(item)
        except:
            url = reverse("commerce:view_listing", kwargs={"listing_id": listing_id})
            return HttpResponseRedirect(url)

        url = reverse("commerce:view_watchlist")
        return HttpResponseRedirect(url)
    else:
        url = reverse("commerce:view_watchlist")
        return HttpResponseRedirect(url)


@login_required(login_url="commerce:login")
def view_watchlist(request):
    
    form = CategoryFilter
    # need to check if the user has a watchlist 
    try:
        watchlist_items = WatchList.objects.get(author = request.user)
        return render (request, "auctions/watchlist.html",{
        "listing": watchlist_items,
        "form": form
        })

    except:
        return render (request, "auctions/watchlist.html",{
        "listing": None,
        "form": form
        })
    


def testAPI(request):
    item = Auctionitem.objects.get(id = "13")
    return JsonResponse(item.serialize())