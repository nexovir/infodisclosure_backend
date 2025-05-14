from django.contrib import admin
from django.contrib.admin import register
from .models import *
import nested_admin
from rating.models import Rating
from django.contrib.contenttypes.admin import GenericTabularInline



class SubCategoryInline(nested_admin.NestedTabularInline):
    model = ZeroDayCategory
    fk_name = 'parent'
    extra = 1
    prepopulated_fields = {'slug': ('title',)}
    fields = ('title', 'slug', 'is_active',)



class RatingInline(GenericTabularInline):
    model = Rating
    extra = 0
    readonly_fields = ('user', 'score', 'comment', 'created_at')



@register(ZeroDayCategory)
class ZeroDayCategoryAdmin(nested_admin.NestedModelAdmin):
    list_display = ['title' , 'slug' , 'parent']
    inlines = [SubCategoryInline]
    prepopulated_fields = {'slug': ('title',)}




@register(ZeroDay)
class ZeroDayAdmin(admin.ModelAdmin):
    list_display = ['id','owner' , 'category' , 'reported_at' , 'is_verified', 'is_active']
    list_editable = ['is_verified' , 'is_active']
    inlines = [RatingInline]




@register(ZeroDayAuction)
class ZeroDayAuctionAdmin (admin.ModelAdmin):
    list_display = ['zeroday' , 'seller' , 'starting_price' , 'current_price' , 'start_time' , 'end_time' , 'last_bid_time' ,'is_active']
    list_editable = ['is_active' , ]




@register(ZeroDayBid)
class ZeroDayBidAdmin (admin.ModelAdmin):
    list_display = ['auction' , 'bidder', 'amount' , 'is_winning' , 'is_active']
    list_editable = ['is_active']



@register(ZeroDayDeal)
class ZeroDayDealAdmin(admin.ModelAdmin):
    list_display = ['auction' , 'buyer_bid' , 'final_price' , 'completed_at' , 'deal_status' , 'is_active']
    list_editable = ['is_active' , 'deal_status']