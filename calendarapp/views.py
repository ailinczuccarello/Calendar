from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Event
from .forms import EventForm
from datetime import datetime, timedelta

def calendar_view(request):
    today = datetime.today()
    month_start = today.replace(day=1)
    next_month = month_start.replace(month=today.month % 12 + 1, day=1)
    days_in_month = (next_month - timedelta(days=1)).day

    days = [month_start + timedelta(days=i) for i in range(days_in_month)]
    hours = list(range(24))

    # Initialize a matrix to hold events by day and hour
    calendar_matrix = [[[] for _ in range(days_in_month)] for _ in range(24)]

    events = Event.objects.filter(
        start_time__month=today.month,
        start_time__year=today.year
    )

    # Populate the matrix with events
    for event in events:
        event_day = event.start_time.day - 1  # zero-indexed day
        event_hour = event.start_time.hour
        calendar_matrix[event_hour][event_day].append(event)

    # Get the month name for the title
    month_name = today.strftime('%B %Y')  # Full month name and year


    # Create a simple data structure for the template
    calendar_data = []
    for hour in range(24):
        row = {
            "hour": hour,
            "events": []
        }
        for day in range(days_in_month):
            row["events"].append(calendar_matrix[hour][day])
        calendar_data.append(row)

    context = {
        'days': days,
        'calendar_data': calendar_data,
        'month_name': month_name,
    }
    return render(request, 'calendarapp/calendar.html', context)
def events_json(request):
    events = Event.objects.all()
    events_data = [{
        'title': event.title,
        'start': event.start_time.isoformat(),
        'end': event.end_time.isoformat(),
    } for event in events]
    return JsonResponse(events_data, safe=False)


def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('calendar')  # Redirect to the calendar view after saving
    else:
        form = EventForm()
    return render(request, 'calendarapp/add_event.html', {'form': form})