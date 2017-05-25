import os
import pymongo
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


def keyword_search_mongodb(data):
    """
    @brief      enables keyword searching in mongodb
    @return     {"tags":{"$regex":"UK"},"summary":{"$regex":"fifth"}
    """
    _data = {}
    for k, v in data.iteritems():
        _data[k] = {'$regex': v}
    return _data


@api_view(['GET'])
def search(request):
    if not request.GET.keys():
        return Response({'err_msg': ('Our deepest apology but this is '
                                     'search only and not for listing all '
                                     'data, please include GET parameters '
                                     'on the API request')},
                        status.HTTP_400_BAD_REQUEST)
    # the only available GET Parameters keys for search
    available_search = ['title', 'tags', 'summary']
    valid_search = list(set(request.GET.keys()) - set(available_search))
    if valid_search:
        return Response({'err_msg': ('You have entered an invalid key search. '
                                     'Available keys are \'title\', \'tags\', '
                                     '\'summary\', \'text\''),
                         'err_keys': valid_search},
                        status.HTTP_400_BAD_REQUEST)
    ssl = os.path.join(settings.BASE_DIR, 'project', 'ssl.crt')
    client = pymongo.MongoClient(settings.MONGODB_URL, ssl_ca_certs=ssl)
    db = client.get_default_database()
    collection = db.exam
    _find = keyword_search_mongodb(request.GET)
    res = collection.count(_find)
    if not res:
        return Response({'err_msg': 'search did not match anything'},
                        status.HTTP_404_NOT_FOUND)
    ret = []
    for x in collection.find(_find):
        x.pop('_id', None)
        ret.append(x)
    return Response(ret)
