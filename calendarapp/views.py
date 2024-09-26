from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Event
from .forms import EventForm
from datetime import datetime, timedelta

def calendar_view(request, year=None, month=None):
    # Get the current date if no month and year are provided
    today = datetime.today()
    if not year:
        year = today.year
    if not month:
        month = today.month

    # Set the first day of the provided month and calculate the next month
    month_start = datetime(year, month, 1)
    if month == 12:
        next_month_start = datetime(year + 1, 1, 1)
    else:
        next_month_start = datetime(year, month + 1, 1)

    # Calculate the number of days in the current month
    days_in_month = (next_month_start - timedelta(days=1)).day
    days = [month_start + timedelta(days=i) for i in range(days_in_month)]
    
    # Initialize hours of the day (24-hour format)
    hours = list(range(24))

    # Initialize a matrix to hold events by day and hour
    calendar_matrix = [[[] for _ in range(days_in_month)] for _ in range(24)]

    # Query events for the current month and year
    events = Event.objects.filter(
        start_time__month=month,
        start_time__year=year
    )

    # Populate the matrix with events
    for event in events:
        event_day = event.start_time.day - 1  # zero-indexed day
        event_hour = event.start_time.hour
        calendar_matrix[event_hour][event_day].append(event)

    # Get the month name for the title
    month_name = month_start.strftime('%B %Y')

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

    # Calculate the previous and next month (handle year transition)
    if month == 1:
        previous_month = 12
        previous_year = year - 1
    else:
        previous_month = month - 1
        previous_year = year

    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    # Prepare the context for rendering the template
    context = {
        'days': days,
        'calendar_data': calendar_data,
        'month_name': month_name,
        'current_year': year,
        'current_month': month,
        'previous_month': previous_month,
        'previous_year': previous_year,
        'next_month': next_month,
        'next_year': next_year,
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