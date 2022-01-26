from rest_framework import serializers, status
from organization.models import Institute
from .models import Graduates
from django.db.models import Q, Count, Max, Sum, Min, Avg


class GraduatesSerialize(serializers.ModelSerializer):
    class Meta:
        model = Graduates
        fields = ('id', 'under_institute_name', 'under_campus_name',
                  'total_students', 'total_final_years',
                  'total_higher_study_and_pay_crt',
                  'total_not_intrested_in_placments', 'total_backlogs',
                  'total_students_eligible', 'total_offers',
                  'total_multiple_offers', 'total_placed',
                  'total_yet_to_place', 'highest_salary', 'average_salary',
                  'lowest_salary', 'is_ug')


class CampusGradListSeralizer(serializers.ModelSerializer):
    pass


class InstituteGradListSeralizer(serializers.ModelSerializer):
    student_details = serializers.SerializerMethodField('_student_details')
    placement_details = serializers.SerializerMethodField('_placement_details')
    salary = serializers.SerializerMethodField('_salary')

    def _student_details(self, obj):
        return {
            "total_students": obj.total_students,
            "total_final_years": obj.total_final_years,
            "total_backlogs": obj.total_backlogs,
            "total_higher_study_and_pay_crt":
            obj.total_higher_study_and_pay_crt
        }

    def _placement_details(self, obj):
        return {
            "total_students_eligible": obj.total_students_eligible,
            "total_not_intrested_in_placments":
            obj.total_not_intrested_in_placments,
            "total_offers": obj.total_offers,
            "placed": obj.total_placed,
            "yet_to_place": obj.total_yet_to_place,
            "total_multiple_offers": obj.total_multiple_offers
        }

    def _salary(self, obj):
        return {
            "highest": obj.highest_salary,
            "average": obj.average_salary,
            "lowest": obj.lowest_salary
        }

    class Meta:
        model = Graduates
        fields = ['student_details', 'placement_details', 'salary', 'is_ug']


class GBstatsSerializer(serializers.ModelSerializer):
    student_details = serializers.SerializerMethodField('_student_details')
    placement_details = serializers.SerializerMethodField('_placement_details')
    salary = serializers.SerializerMethodField('_salary')

    def _student_details(self, obj):
        total_backlogs_opted_for_higherstudies = Graduates.objects.filter(
            id__in=obj).aggregate(
                sum=Sum('total_backlogs_opted_for_higherstudies')).get('sum')
        total_backlogs_opted_for_placements = Graduates.objects.filter(
            id__in=obj).aggregate(
                sum=Sum('total_backlogs_opted_for_placements')).get('sum')
        total_backlogs_opted_for_other_career_options = Graduates.objects.filter(
            id__in=obj).aggregate(sum=Sum(
                'total_backlogs_opted_for_other_career_options')).get('sum')

        serializer = (Graduates.objects.filter(id__in=obj).aggregate(
            total_student=Sum('total_students'),
            total_final_years=Sum('total_final_years'),
            total_higher_study_and_pay_crt=Sum(
                'total_higher_study_and_pay_crt')))
        serializer.update({
            'total_backlog': (total_backlogs_opted_for_higherstudies +
                              total_backlogs_opted_for_other_career_options +
                              total_backlogs_opted_for_placements)
        })

        return serializer

    def _placement_details(self, obj):
        total_final_years = Graduates.objects.filter(id__in=obj).aggregate(
            Sum('total_final_years'))['total_final_years__sum']
        total_backlogs_opted_for_higherstudies = Graduates.objects.filter(
            id__in=obj).aggregate(
                Sum('total_backlogs_opted_for_higherstudies'))['total_backlogs_opted_for_higherstudies__sum']
        total_backlogs_opted_for_placements = Graduates.objects.filter(
            id__in=obj).aggregate(
                Sum('total_backlogs_opted_for_placements'))['total_backlogs_opted_for_placements__sum']
        total_backlogs_opted_for_other_career_options = Graduates.objects.filter(
            id__in=obj).aggregate(Sum(
                'total_backlogs_opted_for_other_career_options'))['total_backlogs_opted_for_other_career_options__sum']
        total_backlogs = (total_backlogs_opted_for_higherstudies +
                          total_backlogs_opted_for_other_career_options +
                          total_backlogs_opted_for_placements)
        total_not_intrested_in_placments = Graduates.objects.filter(
            id__in=obj).aggregate(Sum('total_not_intrested_in_placments')
                                  )['total_not_intrested_in_placments__sum']
        total_offers = Graduates.objects.filter(id__in=obj).aggregate(
            Sum('total_offers'))['total_offers__sum']
        total_multiple_offers = Graduates.objects.filter(id__in=obj).aggregate(
            Sum('total_multiple_offers'))['total_multiple_offers__sum']
        total_students_eligible = (total_final_years - total_backlogs +
                                   total_not_intrested_in_placments)

        serializer = (Graduates.objects.filter(id__in=obj).aggregate(
            total_not_intrested_in_placments=Sum(
                total_not_intrested_in_placments),
            total_offers=Sum(total_offers),
            total_multiple_offers=Sum(total_multiple_offers)))

        serializer.update({
            "placed": (total_offers - total_multiple_offers),
            "yet_to_place": (total_students_eligible - (total_offers - total_multiple_offers)),
            "total_students_eligible": (total_final_years - total_backlogs + total_not_intrested_in_placments)
        })

        return serializer

    def _salary(self, obj):
        return (Graduates.objects.filter(id__in=obj).aggregate(
            highest=Max("highest_salary"),
            average=Avg("average_salary"),
            lowest=Min("lowest_salary")))

    class Meta:
        model = Graduates
        fields = ['student_details', 'placement_details', 'salary', 'is_ug']