from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import IncidentForm, IncidentUpdateForm
from .models import Incident


def dashboard(request):
    total = Incident.objects.count()
    labels = dict(Incident.TYPE_CHOICES)
    by_type = []
    for r in Incident.objects.values("incident_type").annotate(n=Count("id")):
        by_type.append({
            "label": labels.get(r["incident_type"], r["incident_type"]),
            "n": r["n"],
            "pct": round(r["n"] * 100 / total) if total else 0,
        })
    context = {
        "total": total,
        "open_count": Incident.objects.exclude(status__in=["resolved", "closed"]).count(),
        "critical_count": Incident.objects.filter(severity="critical").count(),
        "resolved_count": Incident.objects.filter(status__in=["resolved", "closed"]).count(),
        "by_type": by_type,
        "recent": Incident.objects.order_by("-reported_at")[:5],
    }
    return render(request, "incidents/dashboard.html", context)


def incident_list(request):
    qs = Incident.objects.all().order_by("-reported_at")
    q = request.GET.get("q", "")
    severity = request.GET.get("severity", "")
    status = request.GET.get("status", "")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if severity:
        qs = qs.filter(severity=severity)
    if status:
        qs = qs.filter(status=status)
    return render(request, "incidents/list.html", {
        "incidents": qs,
        "q": q, "severity": severity, "status": status,
        "severities": Incident.SEVERITY_CHOICES,
        "statuses": Incident.STATUS_CHOICES,
    })


def incident_detail(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    if request.method == "POST":
        form = IncidentUpdateForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            return redirect("incident_detail", pk=pk)
    else:
        form = IncidentUpdateForm(instance=incident)
    return render(request, "incidents/detail.html", {"incident": incident, "form": form})


def incident_create(request):
    if request.method == "POST":
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save()
            return redirect("incident_detail", pk=incident.pk)
    else:
        form = IncidentForm()
    return render(request, "incidents/form.html", {"form": form})