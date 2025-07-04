from django.shortcuts import render


def handler404(request):
    """404错误页面处理"""
    print(f"404错误: {request.path}")

    return render(request, '404.html', status=404)


def handler500(request):
    """500错误页面处理"""
    return render(request, '500.html', status=500)
