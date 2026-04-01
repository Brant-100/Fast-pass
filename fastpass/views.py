from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import FastPassBookingForm, GuestLookupForm
from .models import Attraction, FastPass, Guest, ThemeZone, TimeSlot


def home(request):
    avg_result = Attraction.objects.filter(
        attraction_type='ride',
        is_operational=True,
    ).aggregate(Avg('current_wait_minutes'))
    avg_wait = avg_result['current_wait_minutes__avg']

    context = {
        'zone_count': ThemeZone.objects.filter(is_open=True).count(),
        'attraction_count': Attraction.objects.filter(is_operational=True).count(),
        'avg_wait': avg_wait,
        'featured': Attraction.objects.filter(is_operational=True).order_by(
            'current_wait_minutes'
        )[:3],
    }
    return render(request, 'fastpass/home.html', context)


def zone_list(request):
    zones = ThemeZone.objects.filter(is_open=True).annotate(
        num_attractions=Count('attractions')
    )
    return render(request, 'fastpass/zone_list.html', {'zones': zones})


def zone_detail(request, zone_id):
    zone = get_object_or_404(ThemeZone, id=zone_id)
    attractions = zone.attractions.filter(is_operational=True).order_by(
        'current_wait_minutes'
    )
    context = {'zone': zone, 'attractions': attractions}
    return render(request, 'fastpass/zone_detail.html', context)


def attraction_list(request):
    attractions = Attraction.objects.filter(is_operational=True)
    zone_id = request.GET.get('zone')
    attraction_type = request.GET.get('type')
    if zone_id:
        attractions = attractions.filter(zone_id=zone_id)
    if attraction_type:
        attractions = attractions.filter(attraction_type=attraction_type)
    attractions = attractions.order_by('current_wait_minutes')
    context = {
        'attractions': attractions,
        'zones': ThemeZone.objects.filter(is_open=True),
    }
    return render(request, 'fastpass/attraction_list.html', context)


def attraction_detail(request, pk):
    attraction = get_object_or_404(Attraction, pk=pk)
    time_slots = attraction.time_slots.filter(is_active=True)
    context = {'attraction': attraction, 'time_slots': time_slots}
    return render(request, 'fastpass/attraction_detail.html', context)


def short_wait_rides(request):
    rides = Attraction.objects.filter(
        attraction_type='ride',
        is_operational=True,
        current_wait_minutes__lt=30,
    ).order_by('current_wait_minutes')
    return render(request, 'fastpass/short_waits.html', {'rides': rides})


def guest_login(request):
    if request.method == 'POST':
        form = GuestLookupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                guest = Guest.objects.get(email=email)
            except Guest.DoesNotExist:
                messages.error(request, 'No guest found with that email.')
            else:
                request.session['guest_id'] = guest.id
                request.session.modified = True
                messages.success(
                    request,
                    f'Welcome back, {guest.first_name}!',
                )
                return redirect('fastpass:guest_dashboard', guest_id=guest.id)
    else:
        form = GuestLookupForm()
    return render(request, 'fastpass/guest_login.html', {'form': form})


def guest_dashboard(request, guest_id):
    guest = get_object_or_404(Guest, id=guest_id)
    today = timezone.localdate()
    todays_passes = guest.fastpasses.filter(booking_date=today).order_by(
        'time_slot__start_time'
    )
    confirmed_count = todays_passes.filter(status='confirmed').count()
    remaining = guest.daily_fastpass_limit - confirmed_count
    context = {
        'guest': guest,
        'todays_passes': todays_passes,
        'remaining_passes': remaining,
    }
    return render(request, 'fastpass/guest_dashboard.html', context)


def book_fastpass(request, attraction_id):
    attraction = get_object_or_404(Attraction, id=attraction_id)
    guest_id = request.session.get('guest_id')
    if not guest_id:
        messages.info(request, 'Please enter your email to book a FastPass.')
        return redirect('fastpass:guest_login')

    guest = get_object_or_404(Guest, id=guest_id)
    today = timezone.localdate()

    if not attraction.fastpass_enabled:
        messages.error(request, "This attraction doesn't offer FastPass.")
        return redirect('fastpass:attraction_detail', pk=attraction.id)

    slot_qs = TimeSlot.objects.filter(attraction=attraction, is_active=True)
    if not slot_qs.exists():
        messages.error(
            request,
            'No FastPass time slots are available for this attraction yet.',
        )
        return redirect('fastpass:attraction_detail', pk=attraction.id)

    todays_count = FastPass.objects.filter(
        guest=guest,
        booking_date=today,
        status='confirmed',
    ).count()
    if todays_count >= guest.daily_fastpass_limit:
        messages.error(
            request,
            f"You've reached your daily limit of {guest.daily_fastpass_limit} FastPasses.",
        )
        return redirect('fastpass:guest_dashboard', guest_id=guest.id)

    already_booked = FastPass.objects.filter(
        guest=guest,
        attraction=attraction,
        booking_date=today,
    ).exists()
    if already_booked:
        messages.warning(
            request,
            'You already have a FastPass for this attraction today.',
        )
        return redirect('fastpass:guest_dashboard', guest_id=guest.id)

    if request.method == 'POST':
        form = FastPassBookingForm(attraction, request.POST)
        if form.is_valid():
            time_slot = form.cleaned_data['time_slot']
            try:
                FastPass.objects.create(
                    guest=guest,
                    attraction=attraction,
                    time_slot=time_slot,
                    booking_date=today,
                    status=FastPass.CONFIRMED,
                )
            except IntegrityError:
                messages.error(
                    request,
                    'That booking could not be saved (it may already exist). '
                    'Refresh and try again.',
                )
            else:
                messages.success(
                    request,
                    (
                        f'FastPass booked for {attraction.name} at '
                        f'{time_slot.start_time.strftime("%I:%M %p")}!'
                    ),
                )
                return redirect('fastpass:guest_dashboard', guest_id=guest.id)
        else:
            messages.error(
                request,
                'Please choose a valid time slot from the list, then confirm.',
            )
    else:
        form = FastPassBookingForm(attraction)

    context = {'form': form, 'attraction': attraction, 'guest': guest}
    return render(request, 'fastpass/book_fastpass.html', context)
