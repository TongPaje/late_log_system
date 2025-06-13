# logs/models.py

from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
from django.core.validators import RegexValidator
from django.utils.timezone import now

from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    user_type = models.CharField(max_length=50, choices=[('student', 'Student'), ('teacher', 'Teacher')])
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username



class Student(models.Model):
    learner_reference_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    sex = models.CharField(max_length=1)
    year_level = models.IntegerField()
    section = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class LateLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  # Cascade deletion
    scan_time = models.DateTimeField()
    late_minutes = models.IntegerField()

    def __str__(self):
        return f"Late Log for {self.student} at {self.scan_time}"



class Student(models.Model):
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    sex = models.CharField(
        max_length=1, 
        choices=SEX_CHOICES,
        default='M'
    )
    
    YEAR_LEVEL_CHOICES = [
        (7, 'Grade 7'),
        (8, 'Grade 8'),
        (9, 'Grade 9'),
        (10, 'Grade 10'),
        (11, 'Grade 11'),
        (12, 'Grade 12'),
    ]
    
    # Fields for student information
    learner_reference_number = models.CharField(
        max_length=12, 
        unique=True, 
        validators=[RegexValidator(r'^\d{12}$', 'Learner reference number must be exactly 12 digits and contain numbers only')],
    )
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    section = models.CharField(max_length=50)
    year_level = models.IntegerField(choices=YEAR_LEVEL_CHOICES)
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)  # QR code field
    
    # New fields
    birthday = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], default='M')
    address = models.CharField(max_length=255, blank=True, null=True)
    parent_name = models.CharField(max_length=255)
    contact_number = models.CharField(
        max_length=11, 
        validators=[RegexValidator(r'^\d{11}$', 'Contact number must be exactly 11 digits.')],
    )

    sex = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')],)

    class Meta:
        ordering = ['last_name', 'first_name']  # Default ordering by last name then first name

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    def save(self, *args, **kwargs):    
        # Capitalize names and section
        self.first_name = self.first_name.upper()
        self.middle_name = self.middle_name.upper() if self.middle_name else ''
        self.last_name = self.last_name.upper()
        self.section = self.section.upper()

        # Capitalize address and parent name
        self.address = self.address.upper()
        self.parent_name = self.parent_name.upper()

        # Ensure no numbers in names or section
        if any(char.isdigit() for char in self.first_name + self.middle_name + self.last_name + self.section):
            raise ValueError("Names and section cannot contain numbers.")

        # Generate QR code if it doesn't exist yet
        if not self.qr_code:
            self.generate_qr_code()

        super().save(*args, **kwargs)  # Call the original save method

    def generate_qr_code(self):
        # Create a QR code with student details
        qr_data = f"{self.first_name},{self.middle_name},{self.last_name},{self.year_level},{self.section}"
        qr = qrcode.make(qr_data)

        # Save the QR code image to a file-like object in memory
        qr_image = BytesIO()
        qr.save(qr_image, 'PNG')
        qr_image.seek(0)

        # Save the QR code image to the student's `qr_code` field
        self.qr_code.save(f"{self.first_name}_{self.last_name}_qr.png", File(qr_image), save=False)


class LateLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    scan_time = models.DateTimeField(default=now)
    late_minutes = models.IntegerField()

    def __str__(self):
        return f"{self.student} - {self.scan_time} - {self.late_minutes} min"
