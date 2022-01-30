from rest_framework import generics, status, views, response
from organization.models import Institute, Campus, Stream
from django.db.models import Q, Count, Max, Sum, Min, Avg
from organization.serializers import CampusSerialize, InstituteSerialize
from rest_framework.decorators import api_view
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from django.contrib import messages
from django.http import HttpResponse
from .serializers import *
from .models import *
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from tablib import Dataset
from accounts.models import Accounts

class GraduateList(generics.ListAPIView):
    serializer_class = GraduatesSerializer

    def get(self, request):
        send_data = {}
        cmps = Campus.objects.all()
        for cmp in cmps:
            send_data[cmp.name] = {}
            ints = Campus.objects.get(name=cmp.name).institute_set.all()
            for int in ints:
                send_data[cmp.name][int.name] = []
                ug = Graduates.objects.filter(
                    Q(under_campus=cmp) & Q(under_institute=int)
                    & Q(is_ug=True))
                ug_data = GraduatesSerializer(ug, many=True).data
                pg = Graduates.objects.filter(
                    Q(under_campus=cmp) & Q(under_institute=int)
                    & Q(is_ug=False))
                pg_data = GraduatesSerializer(pg, many=True).data
                send_data[cmp.name][int.name].append(ug_data)
                send_data[cmp.name][int.name].append(pg_data)

        return response.Response({'status': 'OK', 'result': send_data})


# --
#
# {  }
#
# --


class InstituteGradList(generics.ListAPIView):
    serializer_class = InstituteGradListSeralizer

    def get(self, request, institute):
        inst = Institute.objects.get(name=institute)
        grds = Graduates.objects.filter(under_institute=inst)
        send_data = InstituteGradListSeralizer(grds, many=True).data

        # [
        #     # students detalis[student_details,placement_details,salary] ,
        #     #
        #     # ug details[student_details,placement_details,salary] ,
        #     #
        #     # pg details[student_details,placement_details,salary]
        # ]
        return response.Response({'status': 'OK', 'result': send_data})


class Overall(generics.ListAPIView):
    serializer_class = GraduatesSerializer

    def get(self, request, stream):
        send_data = {}
        stream_data = Stream.objects.filter(name=stream)
        inst_data = Institute.objects.filter(stream=stream_data[0].id)
        for inst in inst_data:
            send_data[inst.name] = []
            graduates = Graduates.objects.filter(under_institute=inst.id)
            #data = GraduatesSerialize(graduates, many=True).data
            data = InstituteGradListSeralizer(graduates, many=True).data
            send_data[inst.name].append(data)

        return response.Response({'status': 'OK', 'result': send_data})


class Gbstats(generics.ListAPIView):
    serializer_class = GBstatsSerializer

    def get(self, request):
        send_data = {'UG': {}, 'PG': {}}
        ug_grad = Graduates.objects.filter(is_ug=True)
        pg_grad = Graduates.objects.filter(is_ug=False)

        send_data['UG'] = GBstatsSerializer(ug_grad).data
        send_data['PG'] = GBstatsSerializer(pg_grad).data

        return response.Response({'status': 'OK', 'result': send_data})


class SelectGraduates(generics.ListAPIView):
    queryset = Graduates.objects.all()
    serializer_class = GraduatesSerializer

    def get(self, request, institute, grad):
        inst = Institute.objects.filter(name=institute)
        if grad == 'ug':
            grads = Graduates.objects.filter(under_institute=inst[0].id,
                                             is_ug=True)
            send_data = GraduatesSerializer(grads, many=True).data
        elif grad == 'pg':

            grads = Graduates.objects.filter(under_institute=inst[0].id,
                                             is_ug=False)
            send_data = GraduatesSerializer(grads, many=True).data
        else:
            send_data = []
        return response.Response({'status': 'OK', 'result': send_data})


class UpdateGraduates(generics.UpdateAPIView):
    queryset = Graduates.objects.all()
    serializer_class = UpdateGraduatesSerializer

    def patch(self, request, eid, pk, *args, **kwargs):
        try:
            user = Accounts.objects.get(eid=eid)
        except:
            return response.Response({
                'status': 'error',
                'result': 'email is not authenticated'
            })

        try:
            qs = Graduates.objects.get(id=pk)
        except:
            return response.Response({
                'status': 'error',
                'result': 'institute does not exist'
            })

        if not user.can_edit:
            return response.Response({
                'status': 'error',
                'result': 'permission denied'
            })

        data = request.data
        serializer = UpdateGraduatesSerializer(qs, data=data, partial=True)

        if not serializer.is_valid():
            return response.Response({
                'status': 'error',
                'result': 'Invalid data'
            })

        serializer.save()
        return response.Response({
            'status': 'OK',
            'message': "send data succefully"
        })

    def put(self, request, eid, pk, *args, **kwargs):
        try:
            user = Accounts.objects.get(eid=eid)
        except:
            return response.Response({
                'status': 'error',
                'result': 'email is not authenticated'
            })

        try:
            qs = Graduates.objects.get(id=pk)
        except:
            return response.Response({
                'status': 'error',
                'result': 'institute does not exist'
            })

        if not user.can_edit:
            return response.Response({
                'status': 'error',
                'result': 'permission denied'
            })
        data = request.data

        serializer = UpdateGraduatesSerializer(qs, data=data)

        if not serializer.is_valid():
            return response.Response({
                'status': 'error',
                'result': 'Invalid data'
            })

        serializer.save()

        return response.Response({
            'status': 'OK',
            'message': "send data succefully"
        })


'''class FileUploadView(views.APIView):
    parser_classes = [FileUploadParser]

    def put(self, request, format=None):
        excel_file = request.data['file']
        print(excel_file)
        dataset = Dataset()
        if not excel_file.name.endswith('.xlsx'):
            return Response("File should be excel only", status=404)
        imported_data = dataset.load(excel_file.read(),
                                     headers=False,
                                     format='xlsx')
        print("imported_data: \n", imported_data)

        data = {}
        try:
            under_campus = Campus.objects.get(name=imported_data[0][1])
            under_institute = Institute.objects.get(name=imported_data[1][1])
            is_ug = imported_data[-1][1]
        except Campus.DoesNotExist:
            return Response("Campus Invalid: " + str(imported_data))
        except Institute.DoesNotExist:
            return Response("Institute Invalid" + str(imported_data[1]))

        for key_val in imported_data[2:-1]:
            data[key_val[0]] = key_val[1]
        qs, create = Graduates.objects.get_or_create(
            under_campus=under_campus,
            under_institute=under_institute,
            is_ug=is_ug)
        qs.total_students = data['total_students']
        qs.total_final_years = data['total_final_years']
        qs.total_higher_study_and_pay_crt = data[
            'total_higher_study_and_pay_crt']
        qs.total_not_intrested_in_placments = data[
            'total_not_intrested_in_placments']
        qs.total_backlogs_opted_for_placements = data[
            'total_backlogs_opted_for_placements']
        qs.total_backlogs_opted_for_higherstudies = data[
            'total_backlogs_opted_for_higherstudies']
        qs.total_backlogs_opted_for_other_career_options = data[
            'total_backlogs_opted_for_other_career_options']
        qs.total_offers = data['total_offers']
        qs.total_multiple_offers = data['total_multiple_offers']
        qs.highest_salary = data['highest_salary']
        qs.lowest_salary = data['lowest_salary']
        qs.average_salary = data['average_salary']
        qs.save()

        return Response("Data sent", status=204)

    def post(self, request, format=None):
        excel_file = request.data['file']
        dataset = Dataset()
        if not excel_file.name.endswith('.xlsx'):
            return Response("File should be excel only", status=404)
        imported_data = dataset.load(excel_file.read(),
                                     headers=False,
                                     format='xlsx')
        data = {}
        try:
            under_campus = Campus.objects.get(name=imported_data[0][1])
            under_institute = Institute.objects.get(name=imported_data[1][1])
        except Campus.DoesNotExist:
            return Response("Campus Invalid: " + str(imported_data))
        except Institute.DoesNotExist:
            return Response("Institute Invalid" + str(imported_data[1]))

        for key_val in imported_data[2:]:
            data[key_val[0]] = key_val[1]

        qs = Graduates(under_campus=under_campus,
                       under_institute=under_institute,
                       **data)
        qs.save()
        return Response("Data sent", status=204)'''
