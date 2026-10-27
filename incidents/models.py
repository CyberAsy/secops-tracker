from django.db import models


class Incident(models.Model):
    TYPE_CHOICES = [
        ("phishing", "Phishing"),
        ("malware", "Malware"),
        ("unauthorized_access", "Unauthorized Access"),
        ("data_leak", "Data Leak"),
        ("other", "Other"),
    ]
    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]
    STATUS_CHOICES = [
        ("open", "Open"),
        ("investigating", "Investigating"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    incident_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default="other")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default="low")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    assigned_to = models.CharField(max_length=100, blank=True)
    resolution_notes = models.TextField(blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.severity}] {self.title}"