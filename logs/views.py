from django.shortcuts import render, redirect, get_object_or_404
from .models import Student, LateLog
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import io
from .forms import StudentForm
from django.http import HttpResponse, JsonResponse
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from django.utils.timezone import localtime  # Import the localtime function
import base64
import pytz
import random
from django.shortcuts import render
from django.db.models import Q
from .models import Student
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .forms import LoginForm
from django.utils.timezone import localtime


def home(request):
    return redirect('login')  # Redirect root URL to the login page

def chart_reports(request):
    from plotly.graph_objects import Bar, Figure

    late_logs = LateLog.objects.select_related('student')
    data = pd.DataFrame(list(late_logs.values(
        'student__year_level',
        'student__section',
        'student__first_name',
        'student__last_name',
        'student__learner_reference_number',
        'late_minutes',
        'scan_time'
    )))

    # Convert scan_time to local time
    data['scan_time'] = pd.to_datetime(data['scan_time'], errors='coerce')
    data['scan_time'] = data['scan_time'].apply(localtime)  # Apply localtime to each scan_time

    selected_year_level = request.GET.get('year_level', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    if start_date and end_date:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        utc = pytz.UTC
        start_date = utc.localize(start_date)
        end_date = utc.localize(end_date)

        if start_date.date() == end_date.date():
            data = data[data['scan_time'].dt.date == start_date.date()]
        else:
            data = data[(data['scan_time'] >= start_date) & (data['scan_time'] <= end_date)]

    if selected_year_level:
        data = data[data['student__year_level'] == int(selected_year_level)]

    fixed_colors = {
        7: 'green',
        8: 'yellow',
        9: 'red',
        10: 'blue',
        11: 'pink',
        12: 'violet'
    }

    # === Year Level Chart ===
    year_level_data = data.groupby('student__year_level')['student__first_name'].count().reset_index()
    year_level_data['student__year_level'] = year_level_data['student__year_level'].astype(str)

    year_level_chart = px.bar(
        year_level_data,
        x='student__year_level',
        y='student__first_name',
        color='student__year_level',
        color_discrete_map={str(k): v for k, v in fixed_colors.items()},
        labels={
            'student__year_level': 'Year Level',
            'student__first_name': 'Number of Late Entries'
        },
        title="Late Entries by Year Level"
    )
    year_level_chart_html = year_level_chart.to_html(full_html=False)

    # === Section Chart ===
    section_group = data.groupby('student__section')['student__first_name'].count().sort_values(ascending=False)
    section_data_all = section_group.reset_index()
    section_data_all.columns = ['section', 'late_count']

    section_colors = {}
    for section in section_data_all['section']:
        section_years = data[data['student__section'] == section]['student__year_level']
        dominant_year = section_years.mode()[0] if not section_years.empty else None
        section_colors[section] = fixed_colors.get(dominant_year, 'gray')

    section_bars = [
        Bar(
            x=[row['section']],
            y=[row['late_count']],
            marker_color=section_colors.get(row['section'], 'gray'),
            name=row['section']
        )
        for _, row in section_data_all.iterrows()
    ]

    section_chart = Figure(data=section_bars)
    section_chart.update_layout(
        title="Late Entries by Section",
        xaxis_title="Section",
        yaxis_title="Number of Late Entries",
        xaxis=dict(range=[-0.5, 9.5] if len(section_data_all) > 10 else None),
        showlegend=False
    )
    section_chart_html = section_chart.to_html(full_html=False)

    # === Student Chart ===
    data['student_name'] = data['student__first_name'] + ' ' + data['student__last_name'] + ' (' + data['student__learner_reference_number'].astype(str) + ')'
    student_data_all = data.groupby('student_name').agg({
        'late_minutes': 'count',
        'student__year_level': 'first'
    }).reset_index().sort_values(by='late_minutes', ascending=False)

    student_colors = {
        row['student_name']: fixed_colors.get(row['student__year_level'], 'gray')
        for _, row in student_data_all.iterrows()
    }

    student_bars = [
        Bar(
            x=[row['student_name']],
            y=[row['late_minutes']],
            marker_color=student_colors.get(row['student_name'], 'gray'),
            name=row['student_name']
        )
        for _, row in student_data_all.iterrows()
    ]

    student_chart = Figure(data=student_bars)
    student_chart.update_layout(
        title="Late Entries by Student",
        xaxis_title="Student",
        yaxis_title="Number of Late Entries",
        xaxis=dict(range=[-0.5, 9.5] if len(student_data_all) > 10 else None),
        showlegend=False
    )
    student_chart_html = student_chart.to_html(full_html=False)

    years = sorted(data['scan_time'].dt.year.dropna().unique(), reverse=True)

    context = {
        'year_level_chart': year_level_chart_html,
        'section_chart': section_chart_html,
        'student_chart': student_chart_html,
        'year_levels': ['7', '8', '9', '10', '11', '12'],
        'selected_year_level': selected_year_level,
        'selected_month': start_date,
        'selected_year': start_date,
        'months': ["January", "February", "March", "April", "May", "June", "July",
                   "August", "September", "October", "November", "December"],
        'years': years
    }

    return render(request, 'logs/chart_reports.html', context)


def logout_view(request):
    logout(request)  # Logs the user out
    return redirect('login')  # Redirects the user to the login page after logout

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')  # Redirect to the main page after login
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')  # Render login page


def edit_student(request, student_id):
    student = get_object_or_404(Student, pk=student_id)  # Fetch student by ID

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)  # Bind the form with the student instance
        if form.is_valid():
            form.save()  # Save the updated data to the database
            return redirect('students')  # Redirect to the student list after saving
    else:
        form = StudentForm(instance=student)  # Pre-fill the form with the current student's data

    return render(request, 'logs/edit_student.html', {'form': form, 'student': student})

def view_students(request):
    query = request.GET.get('search', '')
    year_level_filter = request.GET.get('year_level', '')

    students = Student.objects.all()

    if query:
        students = students.filter(
            Q(first_name__icontains=query) |
            Q(middle_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(learner_reference_number__icontains=query)
        )

    if year_level_filter and year_level_filter != 'All':
        students = students.filter(year_level=year_level_filter)

    year_levels = Student.objects.values_list('year_level', flat=True).distinct().order_by('year_level')

    return render(request, 'logs/students.html', {
        'students': students,
        'year_levels': year_levels,
        'selected_year': year_level_filter,
        'search_query': query,
    })



@login_required
def index(request):
    return render(request, 'logs/index.html')  # This will render the index.html file

def register_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('students')  # Redirect to the student list after registration
    else:
        form = StudentForm()

    return render(request, 'logs/register_student.html', {'form': form})

from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def scan_qr(request):
    if request.method == "POST":
        qr_data = request.POST.get("qr_data")
        print("Received from mobile:", qr_data)

        if not qr_data:
            return JsonResponse({'message': 'Missing QR data.'}, status=400)

        try:
            # Parse the scanned QR data
            first_name, middle_name, last_name, year_level, section = qr_data.split(',')
            first_name = first_name.strip()
            middle_name = middle_name.strip()
            last_name = last_name.strip()
            year_level = int(year_level.strip())
            section = section.strip()

            # Check if the student exists
            student = Student.objects.filter(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name
            ).first()

            if not student:
                # Create new student if not found
                student = Student.objects.create(
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    year_level=year_level,
                    section=section
                )

            today = timezone.localdate()
            if LateLog.objects.filter(student=student, scan_time__date=today).exists():
                return JsonResponse({'message': 'This QR code has already been scanned today.'})

            now = timezone.now()
            expected_time = now.replace(hour=7, minute=30, second=0, microsecond=0)
            late_minutes = max(0, int((now - expected_time).total_seconds() // 60))

            LateLog.objects.create(
                student=student,
                scan_time=now,
                late_minutes=late_minutes
            )

            return JsonResponse({
                'message': f'{student.first_name} {student.last_name} logged successfully!',
                'late_minutes': late_minutes
            })

        except Exception as e:
            return JsonResponse({'message': f'Error: {str(e)}'}, status=400)

    return render(request, 'logs/scan_qr.html')

    # For GET requests, render the scanner page
    return render(request, 'logs/scan_qr.html')


from .models import Student

from datetime import datetime
from django.utils import timezone

def view_reports(request):
    query = request.GET.get('search', '')
    year_level = request.GET.get('year_level', '')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')

    logs = LateLog.objects.select_related('student').order_by('-scan_time')

    if query:
        logs = logs.filter(
            Q(student__first_name__icontains=query) |
            Q(student__last_name__icontains=query) |
            Q(student__middle_name__icontains=query)
        )

    if year_level:
        logs = logs.filter(student__year_level=year_level)

    # Handle date range filtering
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            logs = logs.filter(scan_time__date__gte=start_date, scan_time__date__lte=end_date)
        except ValueError:
            pass  # If the date is invalid, no filter is applied

    # Convert scan_time to local time for display
    for log in logs:
        log.scan_time = localtime(log.scan_time)  # Convert each scan_time to local time

    # Get today's late logs count
    today_count = LateLog.objects.filter(scan_time__date=timezone.localdate()).count()

    year_levels = ['7', '8', '9', '10', '11', '12']  # Example, adjust as needed

    return render(request, 'logs/view_reports.html', {
        'logs': logs,
        'search': query,
        'year_level': year_level,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'year_levels': year_levels,
        'today_count': today_count  # Pass count to template
    })



def student_list(request):
    search_query = request.GET.get('search', '')
    year_level_filter = request.GET.get('year_level', '')

    students = Student.objects.all()

    if search_query:
        students = students.filter(
            learner_reference_number__icontains=search_query
        ) | students.filter(
            first_name__icontains=search_query
        ) | students.filter(
            middle_name__icontains=search_query
        ) | students.filter(
            last_name__icontains=search_query
        )

    if year_level_filter:
        students = students.filter(year_level=year_level_filter)

    students = students.order_by('last_name', 'first_name', 'middle_name')

    # Export to Excel
    if 'export' in request.GET:
        df = pd.DataFrame(list(students.values(
            'learner_reference_number',
            'last_name',
            'first_name',
            'middle_name',
            'year_level',
            'section'
        )))
        df.rename(columns={
            'learner_reference_number': 'LRN',
            'last_name': 'Last Name',
            'first_name': 'First Name',
            'middle_name': 'Middle Name',
            'year_level': 'Year Level',
            'section': 'Section',
        }, inplace=True)

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="student_list.xlsx"'
        df.to_excel(response, index=False)
        return response

    return render(request, 'student_list.html', {
        'students': students,
        'year_levels': Student.objects.values_list('year_level', flat=True).distinct(),
        'selected_year': year_level_filter,
        'search_query': search_query,
    })


def export_report(request):
    # Retrieve filters from the URL parameters
    search = request.GET.get('search', '')
    year_level = request.GET.get('year_level', '')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')

    # Start with the base query
    logs = LateLog.objects.select_related('student').order_by('scan_time')

    # Apply filters if available
    if search:
        logs = logs.filter(
            Q(student__first_name__icontains=search) |
            Q(student__last_name__icontains=search) |
            Q(student__middle_name__icontains=search)
        )

    if year_level:
        logs = logs.filter(student__year_level=year_level)

    # Handle date range filtering
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            logs = logs.filter(scan_time__date__gte=start_date, scan_time__date__lte=end_date)
        except ValueError:
            pass  # If the date is invalid, no filter is applied

    # Generate Excel response
    wb = openpyxl.Workbook()
    ws = wb.active

    # Title and styles for the Excel sheet
    title_font = Font(bold=True, size=14)
    subtitle_font = Font(bold=True, size=12)
    center_align = Alignment(horizontal='center')
    bold_font = Font(bold=True)
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )

    # Add school name and report title in the first two rows
    ws.merge_cells('A1:F1')
    ws['A1'] = 'CLAVER NATIONAL HIGH SCHOOL'
    ws['A1'].font = title_font
    ws['A1'].alignment = center_align

    ws.merge_cells('A2:F2')
    ws['A2'] = 'Late Logs Report'
    ws['A2'].font = subtitle_font
    ws['A2'].alignment = center_align

    # Add headers in row 3
    headers = ['Learner Reference Number', 'Student Name', 'Year Level', 'Section', 'Date', 'Time']
    ws.append(headers)

    for col_num, header in enumerate(headers, start=1):
        cell = ws.cell(row=3, column=col_num)
        cell.font = bold_font
        cell.alignment = center_align
        cell.border = thin_border

    # Table data starts from row 4
    for log in logs:
        student_name = f"{log.student.last_name}, {log.student.first_name} {log.student.middle_name}"
        scan_time = localtime(log.scan_time).replace(tzinfo=None)
        date = scan_time.strftime("%B %d, %Y")
        time = scan_time.strftime("%I:%M %p")

        row = [
            log.student.learner_reference_number,
            student_name,
            log.student.year_level,
            log.student.section,
            date,
            time
        ]
        ws.append(row)

        # Apply border to the newly added row
        for col_num in range(1, 7):
            ws.cell(row=ws.max_row, column=col_num).border = thin_border

    # Footer with total count
    ws.append([])
    ws.append(['', '', '', '', f"Total Late Entries: {logs.count()}"])
    footer_cell = ws.cell(row=ws.max_row, column=6)
    footer_cell.font = bold_font
    footer_cell.alignment = center_align

    # Adjust column widths
    for i, column_cells in enumerate(ws.columns, 1):
        max_length = 0
        for cell in column_cells:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        column_letter = get_column_letter(i)
        ws.column_dimensions[column_letter].width = max_length + 2

    # Export file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=late_logs.xlsx'
    wb.save(response)
    return response

def export_student_list(request):
    # Get search and year level filter values
    search_query = request.GET.get('search', '')
    year_level_filter = request.GET.get('year_level', '')

    # Start with the base query
    students = Student.objects.all()

    # Apply search filter if present
    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) |
            Q(middle_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(learner_reference_number__icontains=search_query)
        )

    # Apply year level filter if present
    if year_level_filter:
        students = students.filter(year_level=year_level_filter)

    # Prepare the data for export
    data = students.values(
        'learner_reference_number',
        'first_name',
        'middle_name',
        'last_name',
        'year_level',
        'section'
    )

    # Convert data to a pandas DataFrame
    df = pd.DataFrame(list(data))

    # Rename columns for better readability in the export
    df.rename(columns={
        'learner_reference_number': 'LRN',
        'first_name': 'First Name',
        'middle_name': 'Middle Name',
        'last_name': 'Last Name',
        'year_level': 'Year Level',
        'section': 'Section',
    }, inplace=True)

    # Prepare the response as an Excel file
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="student_list.xlsx"'
    df.to_excel(response, index=False)

    return response