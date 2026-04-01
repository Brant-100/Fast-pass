from django import forms

from .models import TimeSlot


class GuestLookupForm(forms.Form):
    email = forms.EmailField(
        label='Your Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'class': 'form-input',
        }),
    )


class FastPassBookingForm(forms.Form):
    time_slot = forms.ModelChoiceField(
        queryset=TimeSlot.objects.none(),
        label='Select Time',
        widget=forms.Select(attrs={'class': 'form-input'}),
        empty_label=None,
        help_text='Pick one available slot, then confirm.',
    )

    def __init__(self, attraction, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['time_slot'].queryset = TimeSlot.objects.filter(
            attraction=attraction,
            is_active=True,
        ).order_by('start_time')
