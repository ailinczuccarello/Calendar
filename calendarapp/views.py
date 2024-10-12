from django.shortcuts import render, redirect, get_object_or_404
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
    
    # Get the starting and ending rows from the POST request, default to 0 and 23
    current_start_row = int(request.POST.get('start_row', 0))
    current_end_row = int(request.POST.get('end_row', 23))

    # Ensure the end row is greater than or equal to the start row
    if current_end_row < current_start_row:
        current_end_row = current_start_row

    # Initialize hours of the day based on selected rows
    hours = list(range(current_start_row, current_end_row + 1))  # Include both start and end rows

    # Create a list of hours from 0 to 23
    hours_list = list(range(24))  # This will be passed to the template

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
        if current_start_row <= event_hour <= current_end_row:  # Check if the hour is within the selected rows
            calendar_matrix[event_hour - current_start_row][event_day].append(event)

    # Get the month name for the title
    month_name = month_start.strftime('%B %Y')

    # Create a simple data structure for the template
    calendar_data = []
    for hour in hours:
        row = {
            "hour": hour,
            "events": []
        }
        for day in range(days_in_month):
            row["events"].append(calendar_matrix[hour - current_start_row][day])
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
        'current_start_row': current_start_row,  # Pass the current starting row to the template
        'current_end_row': current_end_row,      # Pass the current ending row to the template
        'hours_list': hours_list,  # Pass the list of hours to the template
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

def edit_event_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)  # Retrieve the event by its ID

    if request.method == 'POST':
        if 'delete' in request.POST:  # Check if the delete button was pressed
            event.delete()  # Delete the event
            return redirect('calendar')  # Redirect to the calendar view after deletion
        else:
            form = EventForm(request.POST, instance=event)  # Bind form to the existing event
            if form.is_valid():
                form.save()  # Save the updated event to the database
                return redirect('calendar')  # Redirect to the calendar view
    else:
        form = EventForm(instance=event)  # Populate the form with current event data

    return render(request, 'calendarapp/edit_event.html', {'form': form, 'event': event})
