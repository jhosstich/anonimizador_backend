from http.client import HTTPResponse
import re
import phonenumbers
from rest_framework.response import Response
import io
import PyPDF2
from django.shortcuts import render
from rest_framework import viewsets
from .serializers import HeroSerializer
from .models import Hero
from rest_framework.views import APIView
# scrubadub
# from scrubadub.detectors import NameDetector
from scrubadub import clean
import scrubadub
import scrubadub_spacy
# ----


class HeroViewSet(viewsets.ModelViewSet):
    queryset = Hero.objects.all().order_by('name')
    serializer_class = HeroSerializer


class PDFProcessViewSet(APIView):
    def post(self, request, *args, **kwargs):
        pdfFileObj = request.FILES['file'].read()
        pdfReader = PyPDF2.PdfFileReader(io.BytesIO(pdfFileObj))
        numPages = pdfReader.numPages
        page = pdfReader.pages[0]
        text = page.extract_text()
        print(text, flush=True)

        return Response(text)


class TXTProcessViewSetScrubadub(APIView):
    def post(self, request, *args, **kwargs):

        file_uploaded = request.FILES['file']
        file_content = file_uploaded.read().decode('utf-8')

        # Definir un detector personalizado para nombres propios
        supplied_filth_detector = scrubadub.detectors.UserSuppliedFilthDetector([
            {'match': 'Jhoselin', 'filth_type': 'name', 'ignore_case': True},
            {'match': 'Oscco', 'filth_type': 'name', 'ignore_case': True},
        ])

        # Crear un objeto Scrubber que limpiará el texto
        scrubber = scrubadub.Scrubber(locale='es')

        print(file_content, flush=True)

        # Agregar el detector personalizado al Scrubber
        scrubber.add_detector(supplied_filth_detector)

        # Definir el texto que se desea anonimizar
        texto = "Jhoselin Oscco, Ana López y Juan Pérez fueron a una reunión. Jhoselin dijo que llegaría tarde. Jhoselin dijo que vivia en la Gran Vía, Madrid, Madrid, que su numero de telefono es 626175308 y que la podiamos contactar en cualquier momento."
        # Llamar al método clean() del Scrubber para anonimizar el texto
        anon_text= scrubber.clean(file_content)

        # Retornar el texto anonimizado en la respuesta HTTP
        return Response(anon_text)
