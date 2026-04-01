from django.db import models


class ThemeZone(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Attraction(models.Model):
    RIDE = 'ride'
    SHOW = 'show'
    EXPERIENCE = 'experience'
    DINING = 'dining'

    TYPE_CHOICES = [
        (RIDE, 'Ride'),
        (SHOW, 'Show'),
        (EXPERIENCE, 'Experience'),
        (DINING, 'Dining'),
    ]

    THRILL_CHOICES = [
        (1, 'Mild - All Ages'),
        (2, 'Moderate - Some Thrills'),
        (3, 'Thrilling - Not for the Faint of Heart'),
        (4, 'Extreme - Hold onto Your Ewok!'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    attraction_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=RIDE
    )

    zone = models.ForeignKey(
        ThemeZone,
        on_delete=models.CASCADE,
        related_name='attractions'
    )

    thrill_level = models.IntegerField(choices=THRILL_CHOICES, default=1)
    min_height_cm = models.IntegerField(default=0)
    duration_minutes = models.IntegerField(default=5)

    current_wait_minutes = models.IntegerField(default=0)
    is_operational = models.BooleanField(default=True)
    fastpass_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['zone', 'name']

    def __str__(self):
        return f"{self.name} ({self.zone.name})"


class TimeSlot(models.Model):
    attraction = models.ForeignKey(
        Attraction,
        on_delete=models.CASCADE,
        related_name='time_slots'
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    max_fastpasses = models.IntegerField(default=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['attraction', 'start_time']
        unique_together = ['attraction', 'start_time']

    def __str__(self):
        return f"{self.attraction.name}: {self.start_time.strftime('%I:%M %p')}"


class Guest(models.Model):
    STANDARD = 'standard'
    SILVER = 'silver'
    GOLD = 'gold'
    PLATINUM = 'platinum'

    MEMBERSHIP_CHOICES = [
        (STANDARD, 'Standard - Day Pass'),
        (SILVER, 'Silver - Season Pass'),
        (GOLD, 'Gold - Premium Season Pass'),
        (PLATINUM, 'Platinum - VIP All-Access'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    membership_tier = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_CHOICES,
        default=STANDARD
    )

    daily_fastpass_limit = models.IntegerField(default=3)
    height_cm = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class FastPass(models.Model):
    CONFIRMED = 'confirmed'
    USED = 'used'
    CANCELLED = 'cancelled'
    EXPIRED = 'expired'

    STATUS_CHOICES = [
        (CONFIRMED, 'Confirmed'),
        (USED, 'Used'),
        (CANCELLED, 'Cancelled'),
        (EXPIRED, 'Expired'),
    ]

    guest = models.ForeignKey(
        Guest,
        on_delete=models.CASCADE,
        related_name='fastpasses'
    )

    attraction = models.ForeignKey(
        Attraction,
        on_delete=models.CASCADE,
        related_name='fastpasses'
    )

    time_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name='fastpasses'
    )

    booking_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=CONFIRMED
    )

    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-booking_date', 'time_slot__start_time']
        verbose_name_plural = "FastPasses"
        unique_together = ['guest', 'attraction', 'booking_date']

    def __str__(self):
        return f"{self.guest.full_name} - {self.attraction.name}"
