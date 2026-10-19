#here we will to create the plugin 
from django.utils import timezone
from datetime import datetime, time, timedelta
from django.db.models import Count
import pytz
#from apps.agenda.models import Appointment

class DashboardDentistPlugin:
    name='DashboardDentistPlugin'

    def is_active(self, request):
        return True #this after checking from the database
    
    def is_valid(self,request, data=None):
        #here we will to check all the conditions to return the form
        return True 
    
    def get_name(self):
        return self.name
    
    def save(self, customer, data):
        #code to save address in database
        pass

    def update(self, customer, data):
        #code to update address in database
        pass

    def delete(self, customer):
        #code to delete address from database
        pass

    def search(self, query):
        #code to search address in database
        pass
    







    #------------------------------------------------------------
    def get_next_appointments_today(self, user, limit=20):
        from apps.agenda.models import Appointment
        """
        Returns the next N appointments for today for the given user,
        respecting the user's timezone.
        """

        user_tz = pytz.timezone(user.timezone or "UTC")

        # Ahora en la timezone del usuario
        now_user_tz = timezone.now().astimezone(user_tz)

        # 3️⃣ Inicio y fin del día (00:00 - 23:59:59)
        start_of_day = datetime.combine(
            now_user_tz.date(),
            time.min
        )
        end_of_day = datetime.combine(
            now_user_tz.date(),
            time.max
        )
        # 4️⃣ Hacerlos timezone-aware
        start_of_day = user_tz.localize(start_of_day)
        end_of_day = user_tz.localize(end_of_day)

        # 5️⃣ Convertir a UTC (como Django guarda en DB)
        start_utc = start_of_day.astimezone(pytz.UTC)
        end_utc = end_of_day.astimezone(pytz.UTC)

        appointments=Appointment.objects.filter(
            user=user,
            date_start__gte=start_utc,
            date_start__lte=end_utc,
            status__in=[
                Appointment.PENDING,
                Appointment.CONFIRMED,
            ]
        ).order_by("date_start")[:limit]

        data = []
        for appointment in appointments:
            data.append({
                "id": appointment.id,
                "date": appointment.date_start,
                "title": appointment.title if appointment.title else "N/A",
                "description": appointment.description if appointment.description else "N/A",
                "doctor": appointment.user.name if appointment.user else "N/A",
                "status": appointment.status,
            })

        return data


    def get_today_appointments_count(self, user):
        """
        Returns how many appointments the user has today,
        respecting the user's timezone.
        """
        from apps.agenda.models import Appointment
        # 1️⃣ Obtener timezone del usuario
        user_tz = pytz.timezone(user.timezone or "UTC")

        # 2️⃣ Fecha actual en la timezone del usuario
        now_user_tz = timezone.now().astimezone(user_tz)

        # 3️⃣ Inicio y fin del día (00:00 - 23:59:59)
        start_of_day = datetime.combine(
            now_user_tz.date(),
            time.min
        )
        end_of_day = datetime.combine(
            now_user_tz.date(),
            time.max
        )

        # 4️⃣ Hacerlos timezone-aware
        start_of_day = user_tz.localize(start_of_day)
        end_of_day = user_tz.localize(end_of_day)

        # 5️⃣ Convertir a UTC (como Django guarda en DB)
        start_utc = start_of_day.astimezone(pytz.UTC)
        end_utc = end_of_day.astimezone(pytz.UTC)

        # 6️⃣ Query eficiente
        return Appointment.objects.filter(
            user=user,
            date_start__gte=start_utc,
            date_start__lte=end_utc,
            status__in=[
                Appointment.PENDING,
                Appointment.CONFIRMED
            ]
        ).count()

    def _get_week_range_utc(self, user):
        """
        Returns (start_utc, end_utc) for the current week
        using the user's timezone.
        """
        user_tz = pytz.timezone(user.timezone or "UTC")
        now = timezone.now().astimezone(user_tz)

        # Lunes de esta semana
        start_week_date = now.date() - timedelta(days=now.weekday())
        end_week_date = start_week_date + timedelta(days=6)

        start_week = user_tz.localize(datetime.combine(start_week_date, time.min))
        end_week = user_tz.localize(datetime.combine(end_week_date, time.max))

        return (
            start_week.astimezone(pytz.UTC),
            end_week.astimezone(pytz.UTC)
        )

    def get_week_scheduled_appointments(self, user):
        from apps.agenda.models import Appointment
        start_utc, end_utc = self._get_week_range_utc(user)

        return Appointment.objects.filter(
            user=user,
            date_start__range=(start_utc, end_utc),
            status__in=[
                Appointment.PENDING,
                Appointment.CONFIRMED
            ]
        ).count()

    def get_week_cancelled_appointments(self, user):
        from apps.agenda.models import Appointment
        start_utc, end_utc = self._get_week_range_utc(user)

        return Appointment.objects.filter(
            user=user,
            date_start__range=(start_utc, end_utc),
            status=Appointment.CANCELLED
        ).count()

    def get_week_attended_appointments(self, user):
        from apps.agenda.models import Appointment
        start_utc, end_utc = self._get_week_range_utc(user)

        return Appointment.objects.filter(
            user=user,
            date_start__range=(start_utc, end_utc),
            status=Appointment.COMPLETED
        ).count()


    #this is for get the information of the plugin
    def get_information(self, request, data=None):
        #code to search address in database
        dataInformation = {
            "get_next_appointments_today": self.get_next_appointments_today(request.user),
            "today_appointments_count": self.get_today_appointments_count(request.user),
            "scheduled": self.get_week_scheduled_appointments(request.user),
            "cancelled": self.get_week_cancelled_appointments(request.user),
            "attended": self.get_week_attended_appointments(request.user),
            "appointment_status_pie": self.get_appointment_status_pie_data(request.user),
            "appointment_type_pie": self.get_appointment_type_pie_data(request.user),
        }
        return {"plugin": self.name, "data": dataInformation}

    #------------------------------------------------------------
    def get_appointment_status_pie_data(self, user, limit=300):
        """
        Returns appointment count grouped by status
        based on the latest N appointments.
        """
        from apps.agenda.models import Appointment
        
        # Subquery: get last N appointment IDs
        last_appointments_ids = (
            Appointment.objects
            .filter(user=user)
            .order_by('-date_start')
            .values_list('id', flat=True)[:limit]
        )

        # Group by status
        status_summary = (
            Appointment.objects
            .filter(id__in=last_appointments_ids)
            .values('status')
            .annotate(total=Count('id'))
            .order_by()
        )

        # Convert to dict {status: total}
        result = {item['status']: item['total'] for item in status_summary}

        return result

    def get_appointment_type_pie_data(self, user, limit=200):
        """
        Returns appointment count grouped by TypeAppoint
        based on the latest N appointments.
        """
        from apps.agenda.models import Appointment, TypeAppoint

        # Get last N appointment IDs
        last_appointments_ids = (
            Appointment.objects
            .filter(user=user)
            .order_by('-date_start')
            .values_list('id', flat=True)[:limit]
        )

        # Group by appointment type
        type_summary = (
            Appointment.objects
            .filter(
                id__in=last_appointments_ids,
                id_type_appoint__isnull=False
            )
            .values(
                'id_type_appoint__id',
                'id_type_appoint__name',
                'id_type_appoint__color'
            )
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        # Format result for charts
        result = [
            {
                'type_id': item['id_type_appoint__id'],
                'label': item['id_type_appoint__name'],
                'value': item['total'],
                'color': item['id_type_appoint__color']
            }
            for item in type_summary
        ]

        return result


#here we will to save the plugin to the registry
from core.plugins.registry import plugins
plugins.register(
    module="dashboard",
    action="view_information_dashboard", #this is the view where we want to use the plugin
    plugin=DashboardDentistPlugin() #this is the plugin instance
)