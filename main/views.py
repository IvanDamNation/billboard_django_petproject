from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.core.signing import BadSignature
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from billboard_idn_prj.settings import SEARCH_PAGINATION
from .forms import ChangeUserInfoForm, RegisterUserForm, SearchForm, BillboardForm, AdditionalImageFormset
from .models import AdvUser, SubRubric, Billboard
from .utilities import signer


class BBLoginView(LoginView):
    template_name = 'main/login.html'


class BBLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'main/logout.html'


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'main/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('main:profile')
    success_message = 'Данные пользователя изменены'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Пароль пользователя изменён'


class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'main/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('main:register_done')


class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('main:index')

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удалён')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


def index(request):
    last_10 = Billboard.objects.filter(is_active=True)[:10]
    context = {'last_10': last_10}
    return render(request, 'main/index.html', context)


def by_rubric(request, pk):
    rubric = get_object_or_404(SubRubric, pk=pk)
    announcement_search = Billboard.objects.filter(is_active=True, rubric=pk)
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        announcement_search = announcement_search.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(announcement_search, SEARCH_PAGINATION)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {
        'rubric': rubric,
        'page': page,
        'announcement_search': page.object_list,
        'form': form
    }
    return render(request, 'main/by_rubric.html', context)


def detail(request, rubric_pk, pk):
    billboard = get_object_or_404(Billboard, pk=pk)
    additional_images = billboard.additionalimage_set.all()
    context = {'billboard': billboard, 'additional_images': additional_images}
    return render(request, 'main/detail.html', context)


@login_required
def profile(request):
    user_announcements = Billboard.objects.filter(author=request.user.pk)
    context = {'user_announcements': user_announcements}
    return render(request, 'main/profile.html', context)


@login_required
def profile_detail(request, pk):
    billboard = get_object_or_404(Billboard, pk=pk)
    additional_images = billboard.additionalimage_set.all()
    context = {'billboard': billboard, 'additional_images': additional_images}
    return render(request, 'main/profile_detail.html', context)


@login_required
def announcement_add(request):
    if request.method == 'POST':
        form = BillboardForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save()
            formset = AdditionalImageFormset(request.POST, request.FILES, instance=announcement)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление добавлено')
                return redirect('main:profile')
    else:
        form = BillboardForm(initial={'author': request.user.pk})
        formset = AdditionalImageFormset()
    context = {'form': form, 'formset': formset}
    return render(request, 'main/announcement_add.html', context)


@login_required
def announcement_change(request, pk):
    announcement = get_object_or_404(Billboard, pk=pk)
    if request.method == 'POST':
        form = BillboardForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            announcement = form.save()
            formset = AdditionalImageFormset(request.POST, request.FILES, instance=announcement)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление исправлено')
                return redirect('main:profile')
    else:
        form = BillboardForm(instance=announcement)
        formset = AdditionalImageFormset(instance=announcement)
    context = {'form': form, 'formset': formset}
    return render(request, 'main/announcement_change.html', context)


@login_required
def announcement_delete(request, pk):
    announcement = get_object_or_404(Billboard, pk=pk)
    if request.method == 'POST':
        announcement.delete()
        messages.add_message(request, messages.SUCCESS, 'Объявление удалено')
        return redirect('main:profile')
    else:
        context = {'announcement': announcement}
        return render(request, 'main/announcement_delete.html', context)


def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'main/bad_signature.html')

    user = get_object_or_404(AdvUser, username=username)

    if user.is_activated:
        template = 'main/user_is_activated.html'
    else:
        template = 'main/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)


def other_page(request, page):
    try:
        template = get_template(f"main/{page}.html")
    except TemplateDoesNotExist:
        raise Http404

    return HttpResponse(template.render(request=request))
