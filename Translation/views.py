'''
Created on 26-Feb-2018

@author: Vishnu
'''

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework import permissions
from .SimilarTranslation import Similar

@permission_classes((permissions.AllowAny,))
class Translation(viewsets.ViewSet):
    def create(self, request):
        question = request.data
        if question['messageSource'] == 'userInitiatedReset':
            result = {}
            result['messageSource'] = 'messageFromBot'
            result['result'] = '嗨，我是你的虛擬助理..我該如何幫助你..？'
            result['success'] = True
            return Response(result)
        result = {}
        result['result'] = Similar(question['messageText'])
        if len(result['result'].split()) > 0:
            result['success'] = True
            reply = result
            return Response(reply)
        else:
            result['success'] = False
            reply = result
            return Response(reply, status=401)
    