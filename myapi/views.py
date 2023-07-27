import random
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
import spacy
import scrubadub
from faker import Faker

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
        # print(text, flush=True)
        return Response(text)


class TXTProcessViewSetScrubadub(APIView):
    def post(self, request, *args, **kwargs):
        file_uploaded = request.FILES['file']
        texto = file_uploaded.read().decode('utf-8')

        name = request.data.get('name', '')  # Get the provided name from the API request
        surname = request.data.get('surname', '')  # Get the provided surname from the API request
        direccion  = request.data.get('direccion', '')  # Get the provided surname from the API request
        # dni = request.data.get('dni', '') 
        phone = request.data.get('phone', '')
        # credit_card = request.data.get('credit_card', '')

  
        # Detect phone numbers
        phone_numbers = detect_phone_numbers(texto, phone)
        for phone_number in phone_numbers:
            texto = texto.replace(phone_number, generate_fake_phone_number())

        # Detect names
        names = detect_names(texto, name, surname)
        for name in names:
            texto = texto.replace(name, generate_fake_data())

        # Detect addresses
        addresses = detect_addresses(texto)
        for address in addresses:
            texto = texto.replace(address, generate_fake_data())

        # # Anonymize credit card numbers
        # texto = anonymize_credit_card_numbers(texto)

        return Response(texto)



def detect_phone_numbers(text, phone):
    matches = []
    phone_number_regex = re.compile(r'\b(?:\d{2}[ -]?\d{2}[ -]?\d{2}[ -]?\d{3})\b')

    # Formatear el número de teléfono introducido en formato E.164
    formatted_phone = phonenumbers.format_number(phonenumbers.parse(phone, "ES"), phonenumbers.PhoneNumberFormat.E164)
    
    for match in phonenumbers.PhoneNumberMatcher(text, "ES"):
        phone_number = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
        if formatted_phone.__eq__(phone_number):
            matches.append(match.raw_string)
    
    return matches


def detect_names(text, name, surname):
    nlp = spacy.load('es_core_news_sm')
    doc = nlp(text)
    # return [ent.text for ent in doc.ents if ent.label_ == 'PER']
    target_names = name.split() + surname.split()
    full_name = name + ' ' + surname  # Concatenate name and surname with a space in between
    target_names.append(full_name)
    target_names.append(name +' '+ surname.split()[0])

    threshold = 2  # Umbral de distancia para considerar una coincidencia

    detected_names = []
    for ent in doc.ents:
        if ent.label_ == 'PER':
            detected_name = ent.text
            for target_name in target_names:

                if damerau_levenshtein_distance(detected_name, target_name) <= threshold:
                    detected_names.append(detected_name)

    return detected_names

def generate_fake_data():
    fake = Faker()
    consonants = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'y', 'z']
    name = ''
    length = random.randint(4, 8)  # Determina la longitud del nombre

    for i in range(length):
        if i % 2 == 0:  # Alterna entre consonantes y vocales
            name += random.choice(consonants)
        else:
            name += fake.random_letter()

    return name.capitalize()

def generate_fake_phone_number()->str: 
    fake = Faker()
    return fake.phone_number() + 'Anon'

def detect_addresses(text):
    nlp = spacy.load('es_core_news_sm')
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ == 'LOC']

# def detect_credit_card_numbers(text):
#     credit_card_regex = re.compile(r'\b(?:\d[ -]*?){13,16}\b')
#     matches = credit_card_regex.findall(text)
#     return matches


def anonymize_credit_card_numbers(text):
    scrubber = scrubadub.Scrubber()
    # Remove the existing "credit_card" detector if it exists
    if 'credit_card' in scrubber.detectors:
        scrubber.remove_detector('credit_card')
    # Add the new "credit_card" detector
    scrubber.add_detector(scrubadub.detectors.CreditCardDetector())
    anonymized_text = scrubber.clean(
        text, replace_with='[ANONYMIZED_CREDIT_CARD]', detectors=['credit_card'])
    return anonymized_text

# El algoritmo de Damerau-Levenshtein es una variante del algoritmo de Levenshtein que también tiene en cuenta las transposiciones de caracteres
# (intercambio de posiciones adyacentes) además de las operaciones de inserción, eliminación y sustitución de caracteres.
def damerau_levenshtein_distance(word1, word2):
    # print('----------------')
    # print(word1)
    # print(word2)

    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i]
                                   [j - 1], dp[i - 1][j - 1])
            if i > 1 and j > 1 and word1[i - 1] == word2[j - 2] and word1[i - 2] == word2[j - 1]:
                dp[i][j] = min(dp[i][j], dp[i - 2][j - 2] + 1)

    return dp[m][n]
