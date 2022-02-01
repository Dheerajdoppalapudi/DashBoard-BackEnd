from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.contrib import admin
from django.urls import reverse
from django.urls import path
from django import forms
from .models import *
from import_export import resources
from tablib import Dataset
from import_export.admin import ImportExportModelAdmin, ImportMixin, ImportForm, ConfirmImportForm
from organization.models import *
from django.db.models import Q
from .serializers import *


class GraduatesResource(resources.ModelResource):

    class meta:
        model = Graduates


class ExcelImportForm(forms.Form):
    excel_upload = forms.FileField()


class GraduatesAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path('upload-excel/', self.upload_excel),
        ]
        return new_urls + urls

    def upload_excel(self, request):

        if request.method == "POST":
            graduate_resource = GraduatesResource()
            dataset = Dataset()
            excel_file = request.FILES["excel_upload"]

            if not excel_file.name.endswith('.xlsx'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)

            imported_data = dataset.load(excel_file.read(),
                                         headers=False,
                                         format='xlsx')
            print("imported_data: \n", imported_data)

            data = {}
            for key_val in imported_data:
                data[key_val[0]] = key_val[1]
            print(data)

            try:
                qs = Graduates.objects.get(
                    Q(under_campus=Campus.objects.get(
                        name=data['under_campus']))
                    & Q(under_institute=Institute.objects.get(
                        name=data['under_institute']))
                    & Q(is_ug=data['is_ug']))
            except KeyError as e:
                messages.warning(request, 'The wrong file format')
                return HttpResponseRedirect(request.path_info)
            except Graduates.DoesNotExist:
                messages.warning(request,
                                 'Invalid Data Graduated Data does not exist')
                return HttpResponseRedirect(request.path_info)

            serializer = GraduatesSerializer(qs, data=data)
            if not serializer.is_valid():
                messages.warning(request,
                                 'Invalid Data serializer is not valid')
                return HttpResponseRedirect(request.path_info)

            serializer.save()

            messages.info(request, 'Updated Data')
            HttpResponseRedirect(request.path_info)

        form = ExcelImportForm()
        data = {"form": form}

        return render(request, "admin/excel_upload.html", data)


admin.site.register(Graduates, GraduatesAdmin)
