# Python 内置
import os
# Django
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
# 项目内
from ..models import ValveDocument
@login_required
def download_document(request, doc_id):
    document = get_object_or_404(ValveDocument, id=doc_id)

    file_path = document.file.path
    if not os.path.exists(file_path):
        raise Http404("文件不存在")

    return FileResponse(
        open(file_path, 'rb'),
        as_attachment=True,
        filename=os.path.basename(file_path)
    )