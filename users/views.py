from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import UserRegisterForm, TaskCreateForm
from .models import Task
from django.shortcuts import render
from django.utils import timezone

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def index(request):
    tasks = Task.objects.filter(user=request.user).order_by('completed', 'deadline')
    active_count = tasks.filter(completed=False).count() # Считаем только невыполненные
    return render(request, 'users/index.html', {
        'tasks': tasks,
        'active_count': active_count
    })

@login_required
def add_task(request):
    if request.method == 'POST':
        form = TaskCreateForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('index')
    else:
        form = TaskCreateForm()
    return render(request, 'users/add_task.html', {'form': form})

@login_required
def complete_task(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user)
    task.completed = not task.completed
    task.save()
    return redirect('index')

@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user)
    task.delete()
    return redirect('index')

def logout_view(request):
    logout(request)
    return redirect('login')

def edit_task(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user)
    if request.method == 'POST':
        form = TaskCreateForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = TaskCreateForm(instance=task)
    return render(request, 'users/add_task.html', {'form': form, 'edit_mode': True})






import secrets
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Task, Profile  # Не забудь импортировать Profile


@login_required
def profile_view(request):
    user = request.user

    # Получаем профиль текущего пользователя
    profile, created = Profile.objects.get_or_create(user=user)

    # Если кода привязки еще нет, генерируем его
    if not profile.tg_auth_code and not profile.telegram_chat_id:
        profile.tg_auth_code = secrets.token_hex(4)  # Создаст короткий код вроде 'a1b2c3d4'
        profile.save()

    # Твоя старая логика подсчета задач
    user_tasks = Task.objects.filter(user=user)
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(completed=True).count()

    from django.utils import timezone
    now = timezone.now()
    failed_tasks = user_tasks.filter(completed=False, deadline__lt=now).count()

    if total_tasks > 0:
        productivity_rate = round((completed_tasks / total_tasks) * 100)
    else:
        productivity_rate = 0

    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'failed_tasks': failed_tasks,
        'productivity_rate': productivity_rate,
        'tg_auth_code': profile.tg_auth_code,
        'telegram_chat_id': profile.telegram_chat_id,
        # ЗАМЕНИ НА ЮЗЕРНЕЙМ СВОЕГО БОТА (без @)
        'bot_username': 'DeadLTracker_ForSite_Bot'
    }

    return render(request, 'users/profile.html', context)