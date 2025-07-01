from django.views import generic
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from .models import Video
from helpers import get_page_list, ajax_required


class IndexView(generic.ListView):
    template_name = 'video/index.html'
    context_object_name = 'video_list'
    paginate_by = 12

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        page = context['page_obj']
        context['page_list'] = get_page_list(paginator, page)
        return context

    def get_queryset(self):
        return Video.objects.get_published_list()


class SearchListView(generic.ListView):
    template_name = 'video/search.html'
    context_object_name = 'video_list'
    paginate_by = 8
    keyword = ''

    def get_queryset(self):
        self.keyword = self.request.GET.get("q", "")
        return Video.objects.get_search_list(self.keyword)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SearchListView, self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        page_list = get_page_list(paginator, page)
        context['page_list'] = page_list
        context['q'] = self.keyword
        return context


class VideoDetailView(generic.DetailView):
    model = Video
    template_name = 'video/detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object()
        obj.increase_view_count()
        return obj

    def get_context_data(self, **kwargs):
        context = super(VideoDetailView, self).get_context_data(**kwargs)
        recommend_list = Video.objects.get_recommend_list()
        context['recommend_list'] = recommend_list
        return context
