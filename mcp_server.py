import os
import sys

import django

# --- Django setup ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "secops.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from django.db.models import Count
from mcp.server.fastmcp import FastMCP

from incidents.models import Incident

mcp = FastMCP("SecOps Tracker")

TYPES = [c[0] for c in Incident.TYPE_CHOICES]
SEVERITIES = [c[0] for c in Incident.SEVERITY_CHOICES]
STATUSES = [c[0] for c in Incident.STATUS_CHOICES]


def fmt(i: Incident) -> str:
    return (
        f"#{i.id} [{i.severity.upper()}] {i.title} | "
        f"type={i.incident_type} | status={i.status} | "
        f"assigned={i.assigned_to or 'nobody'}"
    )


# ================= TOOLS =================
@mcp.tool()
def report_incident(
    title: str, description: str, incident_type: str = "other", severity: str = "low"
) -> str:
    """Report a new security incident."""
    if incident_type not in TYPES:
        return f"Invalid incident_type. Use one of: {TYPES}"
    if severity not in SEVERITIES:
        return f"Invalid severity. Use one of: {SEVERITIES}"
    i = Incident.objects.create(
        title=title, description=description,
        incident_type=incident_type, severity=severity,
    )
    return f"Incident created: {fmt(i)}"


@mcp.tool()
def update_incident_status(incident_id: int, status: str, notes: str = "") -> str:
    """Change an incident's status (open, investigating, resolved, closed)."""
    if status not in STATUSES:
        return f"Invalid status. Use one of: {STATUSES}"
    try:
        i = Incident.objects.get(id=incident_id)
    except Incident.DoesNotExist:
        return f"Incident {incident_id} not found."
    i.status = status
    if notes:
        i.resolution_notes = notes
    i.save()
    return f"Updated: {fmt(i)}"


@mcp.tool()
def assign_incident(incident_id: int, analyst: str) -> str:
    """Assign an incident to a security analyst."""
    try:
        i = Incident.objects.get(id=incident_id)
    except Incident.DoesNotExist:
        return f"Incident {incident_id} not found."
    i.assigned_to = analyst
    i.save()
    return f"Assigned: {fmt(i)}"


@mcp.tool()
def search_incidents(keyword: str = "", severity: str = "", status: str = "") -> str:
    """Search incidents by keyword, severity and/or status."""
    qs = Incident.objects.all()
    if keyword:
        qs = qs.filter(title__icontains=keyword) | qs.filter(description__icontains=keyword)
    if severity:
        qs = qs.filter(severity=severity)
    if status:
        qs = qs.filter(status=status)
    items = [fmt(i) for i in qs.order_by("-reported_at")[:20]]
    return "\n".join(items) or "No incidents found."


# ================= RESOURCES =================
@mcp.resource("incidents://open")
def open_incidents() -> str:
    """All incidents that are not resolved or closed."""
    qs = Incident.objects.exclude(status__in=["resolved", "closed"])
    return "\n".join(fmt(i) for i in qs) or "No open incidents."


@mcp.resource("incidents://critical")
def critical_incidents() -> str:
    """All critical-severity incidents."""
    qs = Incident.objects.filter(severity="critical")
    return "\n".join(fmt(i) for i in qs) or "No critical incidents."


@mcp.resource("stats://summary")
def stats_summary() -> str:
    """Counts of incidents by type and by status."""
    by_type = Incident.objects.values("incident_type").annotate(n=Count("id"))
    by_status = Incident.objects.values("status").annotate(n=Count("id"))
    lines = ["By type:"] + [f"  {r['incident_type']}: {r['n']}" for r in by_type]
    lines += ["By status:"] + [f"  {r['status']}: {r['n']}" for r in by_status]
    return "\n".join(lines)


@mcp.resource("incident://{incident_id}")
def incident_details(incident_id: int) -> str:
    """Full details of one incident."""
    try:
        i = Incident.objects.get(id=incident_id)
    except Incident.DoesNotExist:
        return "Not found."
    return (
        f"{fmt(i)}\nReported: {i.reported_at}\n"
        f"Description: {i.description}\nNotes: {i.resolution_notes or '-'}"
    )


# ================= PROMPTS =================
@mcp.prompt()
def incident_report(incident_id: int) -> str:
    """Write a formal incident report."""
    return (
        f"Read the resource incident://{incident_id} and write a formal security "
        "incident report with: Summary, Impact, Timeline, Root Cause, "
        "Actions Taken, and Recommendations."
    )


@mcp.prompt()
def response_playbook(incident_type: str) -> str:
    """Create a response playbook for an incident type."""
    return (
        f"Create a step-by-step response playbook for a '{incident_type}' incident. "
        "Include: Detection, Containment, Eradication, Recovery, and Lessons Learned."
    )


@mcp.prompt()
def triage_open_incidents() -> str:
    """Prioritize all open incidents."""
    return (
        "Read the resource incidents://open and prioritize the incidents by "
        "severity and urgency. Explain your ranking and suggest the next action "
        "for each one."
    )


if __name__ == "__main__":
    mcp.run()