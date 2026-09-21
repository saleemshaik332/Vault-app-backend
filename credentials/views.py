from bson import ObjectId
from bson.errors import InvalidId
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from vaultproject.crypto_utils import encrypt_value, decrypt_value, mask_value
from .mongo import get_collection, MongoUnavailable


def serialize_entry(doc, reveal=False):
    data = {
        'id': str(doc['_id']),
        'service_name': doc.get('service_name', ''),
        'username_or_email': doc.get('username_or_email', ''),
        'url': doc.get('url', ''),
        'notes': doc.get('notes', ''),
        'is_deleted': doc.get('is_deleted', False),
        'deleted_at': doc.get('deleted_at'),
        'created_at': doc.get('created_at'),
        'updated_at': doc.get('updated_at'),
    }
    password_plain = decrypt_value(doc.get('password_encrypted', ''))
    data['password'] = password_plain if reveal else mask_value(password_plain, visible_chars=0)
    return data


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def credential_list_create(request):
    try:
        collection = get_collection()
    except MongoUnavailable as exc:
        return Response({'error': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    if request.method == 'GET':
        docs = collection.find({'owner_id': request.user.id, 'is_deleted': False})
        return Response([serialize_entry(d) for d in docs])

    payload = request.data
    if not payload.get('service_name') or not payload.get('password'):
        return Response({'error': 'service_name and password are required.'}, status=400)

    now = timezone.now().isoformat()
    doc = {
        'owner_id': request.user.id,
        'service_name': payload.get('service_name', ''),
        'username_or_email': payload.get('username_or_email', ''),
        'password_encrypted': encrypt_value(payload.get('password', '')),
        'url': payload.get('url', ''),
        'notes': payload.get('notes', ''),
        'is_deleted': False,
        'deleted_at': None,
        'created_at': now,
        'updated_at': now,
    }
    result = collection.insert_one(doc)
    doc['_id'] = result.inserted_id
    return Response(serialize_entry(doc, reveal=True), status=status.HTTP_201_CREATED)


def _get_owned_doc(collection, request, pk, include_deleted=True):
    try:
        oid = ObjectId(pk)
    except InvalidId:
        return None
    query = {'_id': oid, 'owner_id': request.user.id}
    return collection.find_one(query)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def credential_detail(request, pk):
    try:
        collection = get_collection()
    except MongoUnavailable as exc:
        return Response({'error': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    doc = _get_owned_doc(collection, request, pk)
    if not doc:
        return Response({'error': 'Not found.'}, status=404)

    if request.method == 'GET':
        # Reveal the real password only on explicit single-record fetch (e.g. "show password" click)
        return Response(serialize_entry(doc, reveal=True))

    if request.method == 'PUT':
        payload = request.data
        update = {
            'service_name': payload.get('service_name', doc.get('service_name', '')),
            'username_or_email': payload.get('username_or_email', doc.get('username_or_email', '')),
            'url': payload.get('url', doc.get('url', '')),
            'notes': payload.get('notes', doc.get('notes', '')),
            'updated_at': timezone.now().isoformat(),
        }
        if payload.get('password'):
            update['password_encrypted'] = encrypt_value(payload['password'])
        collection.update_one({'_id': doc['_id']}, {'$set': update})
        doc = collection.find_one({'_id': doc['_id']})
        return Response(serialize_entry(doc, reveal=True))

    if request.method == 'DELETE':
        collection.update_one(
            {'_id': doc['_id']},
            {'$set': {'is_deleted': True, 'deleted_at': timezone.now().isoformat()}}
        )
        return Response({'message': 'Moved to trash.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def credential_trash(request):
    try:
        collection = get_collection()
    except MongoUnavailable as exc:
        return Response({'error': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    docs = collection.find({'owner_id': request.user.id, 'is_deleted': True})
    return Response([serialize_entry(d) for d in docs])


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def credential_restore(request, pk):
    try:
        collection = get_collection()
    except MongoUnavailable as exc:
        return Response({'error': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    doc = _get_owned_doc(collection, request, pk)
    if not doc:
        return Response({'error': 'Not found.'}, status=404)
    collection.update_one({'_id': doc['_id']}, {'$set': {'is_deleted': False, 'deleted_at': None}})
    doc = collection.find_one({'_id': doc['_id']})
    return Response(serialize_entry(doc))


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def credential_permanent_delete(request, pk):
    try:
        collection = get_collection()
    except MongoUnavailable as exc:
        return Response({'error': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    doc = _get_owned_doc(collection, request, pk)
    if not doc:
        return Response({'error': 'Not found.'}, status=404)
    collection.delete_one({'_id': doc['_id']})
    return Response(status=204)
