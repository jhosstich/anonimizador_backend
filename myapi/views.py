from http.client import HTTPResponse
from rest_framework.response import Response
import io
import PyPDF2
from django.shortcuts import render
from rest_framework import viewsets
from .serializers import HeroSerializer
from .models import Hero
from rest_framework.views import APIView

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


class TXTProcessViewSet(APIView):
    def post(self, request, *args, **kwargs):
        pdfFileObj = request.FILES['file'].read() 
        pdfReader = PyPDF2.PdfFileReader(io.BytesIO(pdfFileObj))
        numPages = pdfReader.numPages
        page = pdfReader.pages[0]
        text = page.extract_text()
        print(text, flush=True)

        return Response(text)
