from django.core.management.base import BaseCommand
from accounts.models import City, Source, CommunicationSkill

CITIES = [
    'Lahore', 'Karachi', 'Islamabad', 'Rawalpindi', 'Hyderabad', 'Multan', 'Peshawar', 'Quetta', 'Faisalabad', 'Sialkot', 'Gujranwala', 'Bahawalpur', 'Sargodha', 'Sukkur', 'Abbottabad', 'Mardan', 'Dera Ghazi Khan', 'Sahiwal', 'Mirpur', 'Jhelum', 'Rahim Yar Khan', 'Sheikhupura', 'Gujrat', 'Kasur', 'Okara', 'Wah', 'Mingora', 'Chiniot', 'Kamoke', 'Hafizabad', 'Kohat', 'Jacobabad', 'Shikarpur', 'Khanewal', 'Muzaffargarh', 'Khanpur', 'Gojra', 'Bahawalnagar', 'Mandi Bahauddin', 'Tando Adam', 'Jaranwala', 'Pakpattan', 'Khairpur', 'Daska', 'Dadu', 'Muridke', 'Burewala', 'Jhang', 'Samundri', 'Turbat', 'Shahdadkot', 'Shahkot', 'Lodhran', 'Charsadda', 'Swabi', 'Tando Allahyar', 'Chakwal', 'Mianwali', 'Kot Addu', 'Nowshera', 'Jalalpur Jattan', 'Chishtian', 'Attock', 'Vehari', 'Kamalia', 'Umerkot', 'Mian Channu', 'Jaranwala', 'Tando Muhammad Khan', 'Hasilpur', 'Ghotki', 'Haroonabad', 'Narowal', 'Kandhkot', 'Kahror Pakka', 'Kamber Ali Khan', 'Karak', 'Kundian', 'Dipalpur', 'Pattoki', 'Tando Jam', 'Hujra Shah Muqeem', 'Kahror Pakka', 'Kandhkot', 'Kamber Ali Khan', 'Karak', 'Kundian', 'Dipalpur', 'Pattoki', 'Tando Jam', 'Hujra Shah Muqeem'
]
SOURCES = [
    'LinkedIn', 'Rozee.pk', 'Referral', 'Social Media', 'Recruiter', 'Company Website', 'Job Fair', 'Other'
]
COMM_SKILLS = [
    'Excellent', 'Good', 'Average', 'Below Average', 'Poor'
]

class Command(BaseCommand):
    help = 'Populate City, Source, and CommunicationSkill models with common values.'

    def handle(self, *args, **kwargs):
        for city in CITIES:
            City.objects.get_or_create(name=city)
        for source in SOURCES:
            Source.objects.get_or_create(name=source)
        for skill in COMM_SKILLS:
            CommunicationSkill.objects.get_or_create(name=skill)
        self.stdout.write(self.style.SUCCESS('Cities, sources, and communication skills populated successfully.')) 