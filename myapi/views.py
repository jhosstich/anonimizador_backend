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
from scrubadub.detectors.catalogue import register_detector
from scrubadub.detectors.base import Detector
from scrubadub.filth import PhoneFilth
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
            {'match': '626175308', 'filth_type': 'phone', 'ignore_case': True},   
        ])

        # Crear un objeto Scrubber que limpiará el texto
        scrubber = scrubadub.Scrubber(locale='es')

        # Agregar el detector personalizado al Scrubber
        scrubber.add_detector(supplied_filth_detector)

        # Definir el texto que se desea anonimizar
        texto = "Jhoselin Oscco, Ana López y Juan Pérez fueron a una reunión. Jhoselin dijo que llegaría tarde. Jhoselin dijo que vivia en la Gran Vía, Madrid, Madrid, que su numero de telefono es 626175308. El numero de telefono de Ana Lopez es  626175309  y la podemos contactar en cualquier momento."
        # Llamar al método clean() del Scrubber para anonimizar el texto
        anon_text= scrubber.clean(texto)

        # Retornar el texto anonimizado en la respuesta HTTP
        return Response(anon_text)
    

#methos to updathe Phone detector of Scrubadub
@register_detector
class PhoneDetector(Detector):
 
    filth_cls = PhoneFilth
    name = 'phone'
    autoload = True

    def iter_filth(self, text, document_name=None):
        for match in phonenumbers.PhoneNumberMatcher(text, self.region):
            phone_number = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
            if phone_number == '626175308':  # modify the phone number here
                yield PhoneFilth(
                    beg=match.start,
                    end=match.end,
                    text=phone_number,
                    detector_name=self.name,
                    document_name=document_name,
                    locale=self.locale,
                )