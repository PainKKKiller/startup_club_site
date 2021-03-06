from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from .forms import EditProjectForm, EditVacancyForm
from django.contrib.auth.decorators import login_required
from .models import Project, Vacancy, Post
from django.utils.translation import activate
from django.contrib.auth import get_user_model
from utils.mailer import mail_to_users

User = get_user_model()



def home(request):
    post = Post.objects.get(slug='home')
    return render(request, 'index.html', { 'home': post.body })

def projects(request):
    #projects = Project.objects.all()
    projects = Project.objects.filter(ratings__isnull=False).order_by('-ratings__average')
    context = { 'projects': projects }
    return render(request, 'projectslist.html', context)

def project_details(request, slug):
    activate('ru-RU')
    project = Project.objects.get(slug=slug)
    can_edit = False
    if request.user in project.founders.all():
        can_edit = True
    context = { 'project': project, 'can_edit': can_edit }
    return render(request, 'projectdetails.html', context)

@login_required
def project_edit(request, slug):
    if request.method == 'POST':
        if slug == 'new':
            projectForm = EditProjectForm(data=request.POST, files=request.FILES)
        else:
            project = Project.objects.get(slug=slug)
            projectForm = EditProjectForm(data=request.POST, files=request.FILES, instance=project)
        if projectForm.is_valid():
            project = projectForm.save()
            project.founders.add(request.user)
            project.save()
            current_site = get_current_site(request)
            print(current_site, current_site.domain)
            mail_creation_helper(slug == 'new', request.user, project, current_site.domain)
            messages.success(request, ('Вы успешно отредактировали свой проект'))
            return redirect('project_details', slug=project.slug)
        else:
            messages.error(request, ('Какие то ошибки не дают сохранить проект'))
            context = { 'form': projectForm, 'slug': slug }
            return render(request, 'projectedit.html', context)
    else:
        if slug == 'new':
            form = EditProjectForm()
        else:
            project = Project.objects.get(slug=slug)
            form = EditProjectForm(instance=project)
        context = { 'form': form, 'slug': slug }
        return render(request, 'projectedit.html', context)

def vacancies(request):
    vacancies = Vacancy.objects.all()
    context = { 'vacancies': vacancies }
    return render(request, 'vacancieslist.html', context)

def vacancy_details(request, id):
    vacancy = Vacancy.objects.get(pk=id)
    can_edit = (request.user.id == vacancy.author.id)
    context = { 'vacancy': vacancy, 'can_edit': can_edit }
    return render(request, 'vacancydetails.html', context)

def vacancy_edit(request, id):
    if request.method == 'POST':
        if id == 0:
           form = EditVacancyForm(data=request.POST, user=request.user)
        else:
            vacancy = Vacancy.objects.get(pk=id)
            form = EditVacancyForm(data=request.POST, user=request.user, instance=vacancy)
        if form.is_valid():
            vacancy = form.save()
            vacancy.save()
            messages.success(request, ('Вы успешно отредактировали вакансию'))
            return redirect('vacancy_details', id=vacancy.id)
        else:
            messages.error(request, ('Какие то ошибки не дают сохранить вакансию'))
            context = { 'form': form, 'id': id }
            return render(request, 'vacancyedit.html', context)
    else:
        if id == 0:
            form = EditVacancyForm(user=request.user)
        else:
            vacancy = Vacancy.objects.get(pk=id)
            form = EditVacancyForm(user=request.user, instance=vacancy)
    context = { 'form': form, 'id': id }
    return render(request, 'vacancyedit.html', context)

@login_required
def vacancy_delete(request, id):
    vacancy = Vacancy.objects.get(pk=id)
    if vacancy.author.id == request.user.id:
        vacancy.delete()
        messages.success(request, ('Вы удалили вакансию'))
        return redirect('vacancies')

def mail_creation_helper(is_new, user, project, domain):
    if is_new:
        subject_mail = 'Ваш проект создан'
        html_message = render_to_string('emails/addedtoproject.html', {
            'user': user,
            'domain': domain,
            'project': project,
        })
        txt_message = render_to_string('emails/addedtoproject.txt', {
            'user': user,
            'domain': domain,
            'project': project,
        })
    else:
        subject_mail = 'Ваш проект отредактирован'
        html_message = render_to_string('emails/editedproject.html', {
            'user': user,
            'domain': domain,
            'project': project,
        })
        txt_message = render_to_string('emails/editedproject.txt', {
            'user': user,
            'domain': domain,
            'project': project,
        })
    mails = [ founder.email for founder in project.founders.all()]
    resp = mail_to_users(subject_mail, html_content= html_message, txt_content=txt_message, mails=mails)
    return resp

def contacts(request):
    if request.method == 'GET':
        return render(request, 'contacts.html')
    else:
        mails = [ admin.email for admin in User.objects.filter(is_staff=True)]
        txt_message = render_to_string('emails/messagetoadmins.txt', {
            'name': request.POST['name'],
            'email': request.POST['email'],
            'message': request.POST['message']
        })
        resp = mail_to_users("Письмо в администрацию стартап клуба", html_content=None, txt_content=txt_message, mails=mails)
        if resp == 1:
            messages.success(request, ('Ваше сообщение отправлено'))
        else:
            messages.error(request, ('Ваше cообщение отправить не удалось, возникла какая то проблема на сервере'))
        return render(request, 'contacts.html')

def useful(request):
    posts = Post.objects.filter(post_type='useful')
    context = { 'posts': posts }
    print(posts)
    return render(request, 'usefullist.html', context)

def post_details(request, post_type, slug):
    post = Post.objects.get(slug=slug)
    print('post_details', post, post.can_comment)
    context = { 'post': post }
    return render(request, 'postdetails.html', context)

def news(request):
    posts = Post.objects.filter(post_type='news')
    context = { 'posts': posts }
    print(posts)
    return render(request, 'newslist.html', context)