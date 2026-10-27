from django import forms
from .models import Incident


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ["title", "description", "incident_type", "severity"]


class IncidentUpdateForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ["status", "assigned_to", "resolution_notes"]