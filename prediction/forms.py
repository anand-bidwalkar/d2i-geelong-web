from django import forms
from .models import Suburb

class SuburbForm(forms.Form):
    suburb = forms.ModelChoiceField(queryset=Suburb.objects.all(),empty_label="Choose Suburb")


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['Product'].queryset = Product.objects.none()
        self.fields["suburb"].choices = [("", "Choose Suburb"),] + \
                list(self.fields["suburb"].choices)[1:]


class WeatherForm(forms.Form):
    mintemp = forms.DecimalField(max_digits=4, decimal_places=2)
    maxtemp = forms.DecimalField(max_digits=4, decimal_places=2)
    rainfall = forms.ChoiceField(choices = [(0, 'No'), (1, 'Yes')])
    month = forms.ChoiceField(choices = [(0, 'January'), (1, 'February'), (2, 'March'), (3, 'April'), (4, 'May'), (5, 'June'), (6, 'July'), (7, 'August'), (8, 'September'), (9, 'October'), (10, 'November'), (11, 'December')])
    weekday = forms.ChoiceField(choices = [(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')])

class RegionForm(forms.Form):
    prcp = forms.DecimalField(max_digits=4, decimal_places=2)
    tavg = forms.DecimalField(max_digits=4, decimal_places=2)
    #cbdreg = forms.ChoiceField(choices = [(0, 'CBD'), (1, 'Regional')])
    cbdreg = forms.HiddenInput()