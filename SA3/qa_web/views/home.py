"""
Controller for home page operations
"""

from django.shortcuts import render

def homepage(request):
    """Displays the website's home page.

    :param request: Request data provided by the WSGI
    :return: Rendered template displaying the home page
    """
    return render(request, "qa_web/home.html")
