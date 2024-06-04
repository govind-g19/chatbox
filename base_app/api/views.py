from rest_framework.decorators import api_view
from rest_framework.response import Response
from base_app.models import Room
from .serializer import RoomSerializer

@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET/api',
        'GET/api_room',
        'GET/api_room/:id'
    ]
    return Response(routes)

@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    print(serializer)
    return Response(serializer.data)

@api_view(['GET'])
def getRoom(request, id):
    room = Room.objects.get(id=id)
    serializer = RoomSerializer(room, many=False)
    print(serializer)
    return Response(serializer.data)
