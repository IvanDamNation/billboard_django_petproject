from .models import SubRubric


def billboard_context_processor(request):
    context = {'rubrics': SubRubric.objects.all()}
    return context
