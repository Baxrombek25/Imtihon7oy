from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import RegisterSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from .models import Journal
from .serializers import JournalSerializer
from django.core.paginator import Paginator
from django.db.models import Q



@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    serializer = RegisterSerializer(request.user)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = request.user
    user.username = request.data.get('username', user.username)
    user.email = request.data.get('email', user.email)
    user.save()
    serializer = RegisterSerializer(user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    if not user.check_password(old_password):
        return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
    user.set_password(new_password)
    user.save()
    return Response({'success': 'Password changed successfully'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def reset_password_request(request):
    email = request.data.get('email')
    User = get_user_model()
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_link = f"http://localhost:8000/api/reset-password-confirm/{uid}/{token}/"   
    send_mail(
        subject="Password Reset Request",
        message=f"Click the link to reset your password: {reset_link}",
        from_email=None,
        recipient_list=[email],
    )
    return Response({'success': 'Password reset email sent'})

@api_view(['POST'])
def reset_password_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        return Response({'error': 'Invalid link'}, status=400)
    if not default_token_generator.check_token(user, token):
        return Response({'error': 'Invalid or expired token'}, status=400)
    new_password = request.data.get('new_password')
    user.set_password(new_password)
    user.save()
    return Response({'success': 'Password has been reset'})

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def journal_list_create(request):
    if request.method == 'GET':
        journals = Journal.objects.filter(author=request.user)
        serializer = JournalSerializer(journals, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = JournalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def journal_detail(request, pk):
    try:
        journal = Journal.objects.get(pk=pk, author=request.user)
    except Journal.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = JournalSerializer(journal)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = JournalSerializer(journal, data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        journal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def filter_journals(request):
    queryset = Journal.objects.all()
    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(
            title__icontains=search
        ) | queryset.filter(
            description__icontains=search
        )
    author = request.GET.get('author')
    if author:
        queryset = queryset.filter(authorusernameicontains=author)
    status_param = request.GET.get('status')
    if status_param:
        queryset = queryset.filter(status=status_param)
    ordering = request.GET.get('ordering')
    if ordering:
        queryset = queryset.order_by(ordering)
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 5)
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page)
    serializer = JournalSerializer(page_obj, many=True)
    return Response({
        'count': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'results': serializer.data
    }, status=status.HTTP_200_OK)

from rest_framework.permissions import IsAuthenticated
from .models import JournalEntry
from .serializers import JournalEntrySerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def journal_list(request):
    journals = JournalEntry.objects.filter(user=request.user)
    serializer = JournalEntrySerializer(journals, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def journal_create(request):
    serializer = JournalEntrySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def journal_detail(request, pk):
    try:
        journal = JournalEntry.objects.get(pk=pk, user=request.user)
    except JournalEntry.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = JournalEntrySerializer(journal)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def journal_update(request, pk):
    try:
        journal = JournalEntry.objects.get(pk=pk, user=request.user)
    except JournalEntry.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = JournalEntrySerializer(journal, data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def journal_delete(request, pk):
    try:
        journal = JournalEntry.objects.get(pk=pk, user=request.user)
    except JournalEntry.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
    journal.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def journal_list(request):
    journals = JournalEntry.objects.filter(user=request.user)
    search = request.GET.get('search')
    if search:
        journals = journals.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search)
        )
    created_date = request.GET.get('created_at')
    if created_date:
        journals = journals.filter(created_at__date=created_date)
    sort_by = request.GET.get('sort')
    if sort_by:
        journals = journals.order_by(sort_by)
    serializer = JournalEntrySerializer(journals, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def journal_list(request):
    user = request.user
    lang = request.GET.get('lang', 'uz')
    journals = JournalEntry.objects.filter(user=user)
    result = []
    for journal in journals:
        if lang == 'ru':
            title = journal.title_ru or journal.title_uz
            content = journal.content_ru or journal.content_uz
        elif lang == 'en':
            title = journal.title_en or journal.title_uz
            content = journal.content_en or journal.content_uz
        else:
            title = journal.title_uz
            content = journal.content_uz
        result.append({
            'id': journal.id,
            'title': title,
            'content': content,
            'created_at': journal.created_at,
        })
    return Response(result)