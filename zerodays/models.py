from django.db import models
from django.contrib.auth.models import User
from users.models import BaseModel
from django.utils import timezone




class ZeroDayCategory (BaseModel):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey('self' ,null=True , blank=True , on_delete=models.CASCADE, related_name='subcategories')


    def __str__(self):
        return self.title
    

    class Meta:
        verbose_name = 'ZeroDay Category'
        verbose_name_plural = 'ZeroDay Categories'
        ordering = ['title']




class ZeroDay (BaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='zerodays')
    title = models.CharField(max_length=150 , blank=False , null=False)
    category = models.ForeignKey(ZeroDayCategory , on_delete = models.CASCADE )
    description = models.TextField(help_text="Detailed description of the zero-day vulnerability.")
    cve_reference = models.CharField(max_length=50, blank=True, null=True, help_text="Optional CVE reference if it exists.")
    reported_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False, help_text="Indicates whether the zero-day has been verified.")

    def __str__(self):
        return f"{self.category.title} by {self.owner}"

    class Meta:
        verbose_name = 'Zero Day'
        verbose_name_plural = 'Zero Days'
        ordering = ['-reported_at']




class ZeroDayAuction(BaseModel):
    zeroday = models.OneToOneField(ZeroDay, on_delete=models.CASCADE, related_name='auction')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='zeroday_auctions')
    starting_price = models.DecimalField(max_digits=10, decimal_places=2 , default=0.00)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    last_bid_time = models.DateTimeField(blank=True, null=True, help_text="Last time a bid was placed.")

    def __str__(self):
        return f"Auction for {self.zeroday} by {self.seller}"

    class Meta:
        verbose_name = 'Zero Day Auction'
        verbose_name_plural = 'Zero Day Auctions'
        ordering = ['-start_time']



class ZeroDayBid (BaseModel):
    auction = models.ForeignKey(ZeroDayAuction , on_delete=models.CASCADE)
    bidder = models.ForeignKey(User , on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10 , decimal_places=2 , default=0.00)
    is_winning = models.BooleanField(default=False)


    def __str__(self):
        return f"Bid ({self.auction.zeroday.title}) by ({self.bidder.username}) : {self.amount} $"

    class Meta :
        verbose_name = 'Zero Day Bid'
        verbose_name_plural = 'Zero Day Bids'





class ZeroDayDeal(BaseModel):
    auction = models.ForeignKey(ZeroDayAuction, on_delete=models.CASCADE, related_name='deals')
    buyer_bid = models.ForeignKey(ZeroDayBid, on_delete=models.CASCADE, related_name='deal')
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    completed_at = models.DateField()
    
    DEAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    ]
    deal_status = models.CharField(max_length=20, choices=DEAL_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Deal for Auction #{self.auction.id} - Status: {self.deal_status}"

    class Meta:
        verbose_name = "ZeroDay Deal"
        verbose_name_plural = "ZeroDay Deals"
        ordering = ['-completed_at']
