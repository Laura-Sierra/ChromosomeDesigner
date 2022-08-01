from email.policy import default
from django import forms
from django.forms import formset_factory, BaseFormSet
from django.core.validators import FileExtensionValidator
from djangoformsetjs.utils import formset_media_js
from django.utils.safestring import mark_safe
from django.core.validators import RegexValidator

class FragmentForm(forms.Form):
    class Media(object):
        # The form must have `formset_media_js` in its Media
        js = formset_media_js + (
            # Other form javascript...
        )
    name = forms.CharField(label='Fragment name: ', label_suffix="", required=True, max_length=20, widget = forms.TextInput(attrs={'class':'form-control','id':'id_name','placeholder':'e.g.: URA3'}))
    start = forms.IntegerField(label='Start position: ', label_suffix="",required=True, min_value=1, widget = forms.NumberInput(attrs={'placeholder':'1'}))
    end = forms.IntegerField(label='End position: ',label_suffix="",required=True, min_value=1, widget = forms.NumberInput(attrs={ 'placeholder':'1000'}))
    genbank = forms.FileField(label='Genebank file (.gb .gbk): ',label_suffix="",required=True, validators=[FileExtensionValidator( ['gb', 'gbk'] ) ])

    # Restrictions
    #alphanumeric = RegexValidator(r'^[CAGTcagt]+$', 'Only A,T,G or C are allowed.')
    #Seq1 = forms.CharField(label='FW primer (5\' \u2192 3\'):', label_suffix="", required=False, min_length=75 ,max_length=100, validators=[alphanumeric])
    #Seq2 = forms.CharField(label='RV primer (5\' \u2192 3\'):', label_suffix="", required=False, min_length=75 ,max_length=100, validators=[alphanumeric])

    Restrictions  = forms.BooleanField(label='Restrictions: ', label_suffix="",required=False) 

    GC_min = forms.IntegerField(label='Min (GC content %): ', label_suffix="",required=False, widget=forms.NumberInput(attrs={'type':'range', 'value':'40', 'id':'slider-1', 'step': '1', 'min': '0', 'max': '100', 'oninput': 'slideOne()'})) # Minimum GC% content
    GC_max = forms.IntegerField(label='Max (GC content %): ', label_suffix="",required=False, widget=forms.NumberInput(attrs={'type':'range', 'value':'60',  'id':'slider-2', 'step': '1', 'min': '0', 'max': '100', 'oninput': 'slideTwo()'})) # Maximum GC% content
    
    Ta_min = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'type':'range', 'value':'58', 'id':'slider-13', 'step': '1', 'min': '55', 'max': '70', 'oninput': 'slideOne3()'})) # Minimum annealing temperature
    Ta_max = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'type':'range', 'value':'64',  'id':'slider-23', 'step': '1', 'min': '55', 'max': '70', 'oninput': 'slideTwo3()'})) # Maximum annealing temperature

    
    Tm_dif = forms.FloatField(label=mark_safe('Max (T<sub>m_FWD</sub> - T<sub>m_RV</sub>)) '), label_suffix="",required=False,  widget=forms.NumberInput(attrs={'type':'range', 'id':'slider-24','value':'5', 'step': '0.5', 'min': '0', 'max': '5'})) # Temperature difference between FW and RV primers
    #Ta_min = forms.IntegerField(label=mark_safe('Min (T<sub>annealing</sub>) '), label_suffix="",required=False, min_value=0, max_value=8) 
    #Ta_max = forms.IntegerField(label=mark_safe('Max (T<sub>annealing</sub>) '), label_suffix="",required=False, min_value=0, max_value=72) 
    Range  = forms.BooleanField(label='Range:  ', label_suffix="",required=False, initial = True) 
    # Search in a range of X nucleotides before and after the fragment
    # Do this if primers that meet the conditions cannot be found within the specified start and end positions.
    # Start  adding nucleotide by nucleotide

    def clean(self):
        cleaned_data = super(FragmentForm, self).clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        msg = forms.ValidationError("The length of the fragment should be larger than 60 bp.")

        if start != None and end != None and abs(start-end)<60:
            self.add_error('end', msg)

    

FragmentFormSet = formset_factory(FragmentForm, min_num=2, extra=0, can_delete=True, can_order=True)



class Form_settings(forms.Form):
    GC_min = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'type':'range', 'value':'40', 'id':'slider-15', 'step': '1', 'min': '0', 'max': '100', 'oninput': 'slideOne()'})) # Minimum GC% content
    GC_max = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'type':'range', 'value':'60',  'id':'slider-25', 'step': '1', 'min': '0', 'max': '100', 'oninput': 'slideTwo()'})) # Maximum GC% content
    Ta_min = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'type':'range', 'value':'58', 'id':'slider-16', 'step': '1', 'min': '55', 'max': '70'})) # Minimum annealing temperature
    Ta_max = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'type':'range', 'value':'64',  'id':'slider-26', 'step': '1', 'min': '55', 'max': '70'})) # Maximum annealing temperature
    Tm_dif = forms.FloatField(required=False,  widget=forms.NumberInput(attrs={'type':'range', 'id':'slider-27','value':'5', 'step': '0.5', 'min': '0', 'max': '5'})) # Temperature difference between FW and RV primers
    Range  = forms.BooleanField(label='Range:  ', label_suffix="",required=False, initial= True) 


class Form_excel(forms.Form):
    ExcelFile = forms.FileField(label='Excel file (.xlsx): ',label_suffix="",required=False, validators=[FileExtensionValidator( ['xlsx'] ) ])
    #Genbanks = forms.FileField(label='Genbank files (.gb .gbk): ',label_suffix="",required=False, validators=[FileExtensionValidator( ['gb', 'gbk'] ) ], widget=forms.ClearableFileInput(attrs={'multiple': True}))

