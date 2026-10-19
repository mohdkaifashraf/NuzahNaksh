from django import forms
from accounts.models import Address

class AddressForm(forms.ModelForm):


    class Meta:
        model = Address
        fields = ['full_name',
                 'phone_number',
                 'address_line_1',
                 'address_line_2',
                 'city',
                 'state',
                 'postal_code',
                 'country',
                 'address_type',
                 'other_address_type'
                ]