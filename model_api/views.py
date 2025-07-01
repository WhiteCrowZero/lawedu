from pydub import AudioSegment
from lib.src.img_module import ImageAliyunModule
from lib.src.llm_module import MainAliyunModule
from lib.src.s2t_module import S2TTencentCloudModule
from lib.src.t2s_module import TtsMakerModule
from lib.src.utils import data_processing
from lib.src.integrated_modules import AiApiModule

import uuid
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Roles
from django.shortcuts import render
from django.db.models import Q


# 初始化模型
def model_init():
    # 语音识别
    config = data_processing.load_config_json("lib/doc/tencentcloud_config.json")
    s2t_module = S2TTencentCloudModule(api_config=config)
    # 图像识别
    aliyun_config = data_processing.load_config_json("lib/doc/aliyun_config.json")
    img_module = ImageAliyunModule(api_config=aliyun_config, model="qwen2.5-vl-7b-instruct")
    # 大模型
    llm_module = MainAliyunModule(api_config=aliyun_config, model="qwen-turbo-latest")
    # 语音合成
    ttsmaker_config = data_processing.load_config_json("lib/doc/ttsmaker_config.json")
    t2s_module = TtsMakerModule(audio_root='media/output', api_config=ttsmaker_config)
    return AiApiModule(
        s2t_module=s2t_module,
        img_module=img_module,
        llm_module=llm_module,
        t2s_module=t2s_module,
        prompt_config="lib/doc/prompt_config.json"
    )


model_api = model_init()


# 录音
@csrf_exempt
@require_POST
def upload_audio(request):
    """
    接收上传的音频文件，转成 MP3 并保存在 media/converted/ 目录下，
    返回 JSON: { "mp3_path": "<MEDIA_URL>converted/<filename>.mp3" }
    """
    audio_file = request.FILES.get('audio')
    if not audio_file:
        return JsonResponse({'error': 'No audio file provided'}, status=400)

    rel_path = save_audio(audio_file)
    if isinstance(rel_path, JsonResponse):
        return rel_path
    return JsonResponse({'mp3_path': rel_path}, status=200)


def save_audio(audio_file):
    """
    保存上传的音频文件并转换为MP3格式
    返回MP3文件的绝对路径
    """
    try:
        # 获取MEDIA_ROOT的绝对路径
        media_root = Path(settings.MEDIA_ROOT).resolve()

        # 确保所有目录路径都是绝对路径
        upload_dir = media_root / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)

        convert_dir = media_root / "converted"
        convert_dir.mkdir(parents=True, exist_ok=True)

        # 保存原始文件
        orig_ext = audio_file.name.rsplit('.', 1)[-1].lower()
        orig_name = f"{uuid.uuid4().hex}.{orig_ext}"
        orig_path = upload_dir / orig_name

        with open(orig_path, 'wb') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        # 转换并保存为MP3
        try:
            sound = AudioSegment.from_file(str(orig_path), format=orig_ext)
            mp3_name = f"{uuid.uuid4().hex}.mp3"
            mp3_path = convert_dir / mp3_name

            # logger.info(f"Converting audio to: {mp3_path}")
            sound.export(str(mp3_path), format='mp3')

            # 返回绝对路径的字符串表示（跨平台）
            mp3_path = str(mp3_path.resolve())
            print(mp3_path)
            return mp3_path

        except Exception as e:
            # logger.error(f"Audio conversion failed: {str(e)}")
            return JsonResponse({'error': f'Failed to export MP3: {str(e)}'}, status=500)

    except Exception as e:
        # logger.exception("Unhandled error in save_audio")
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)


# 图像
@csrf_exempt
@require_POST
def upload_image(request):
    try:
        # 1. 检查是否有文件上传
        image_file = request.FILES.get('image')
        if not image_file:
            return JsonResponse({'error': 'No image file provided'}, status=400)

        # 2. 创建存储目录（确保绝对路径）
        image_dir = Path(settings.MEDIA_ROOT) / 'images'
        image_dir.mkdir(parents=True, exist_ok=True)

        # 3. 生成唯一文件名
        ext = image_file.name.split('.')[-1].lower()
        image_name = f"{uuid.uuid4().hex}.{ext}"
        image_path = image_dir / image_name

        # 4. 保存文件
        with open(image_path, 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        # 5. 构造并返回响应（包含绝对路径）
        # 获取服务器上的绝对路径
        absolute_file_path = str(image_path.resolve())
        print(absolute_file_path)
        return JsonResponse({'image_path': absolute_file_path})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def save_upload(f, subdir):
    """保存上传文件到 media/{subdir}/，返回绝对路径字符串"""
    dst = Path(settings.MEDIA_ROOT) / subdir
    dst.mkdir(parents=True, exist_ok=True)
    ext = f.name.rsplit('.', 1)[-1].lower()
    name = f"{uuid.uuid4().hex}.{ext}"
    path = dst / name
    with open(path, 'wb') as wf:
        for chunk in f.chunks():
            wf.write(chunk)

    if subdir == 'uploads':
        convert_dir = Path(settings.MEDIA_ROOT) / "converted"
        convert_dir.mkdir(parents=True, exist_ok=True)
        sound = AudioSegment.from_file(str(path), format='webm')
        mp3_name = f"{uuid.uuid4().hex}.mp3"
        mp3_path = convert_dir / mp3_name
        sound.export(str(mp3_path), format='mp3')

        # 返回绝对路径的字符串表示（跨平台）
        path = str(mp3_path.resolve())
        print(path)
    return str(path)


@csrf_exempt
@require_POST
def infer(request):
    """
    统一推理接口：POST multipart/form-data
    接收: text (字符串), image (file), audio (file)
    返回: JSON { reply: 文本, audio_path: '/media/converted/xxx.mp3' }
    """
    text = request.POST.get('text', '').strip()
    img_f = request.FILES.get('image')
    aud_f = request.FILES.get('audio')
    if not (text or img_f or aud_f):
        return JsonResponse({'error': '至少提供 text, image 或 audio 之一'}, status=400)

    img_path = save_upload(img_f, 'images') if img_f else None
    aud_path = save_upload(aud_f, 'uploads') if aud_f else None

    # 每次新对话前重置上下文
    model_api.add_context()

    try:
        # 调用模型统一接口（返回 (文本, 本地音频绝对路径)）
        reply_text, out_audio = model_api.predict(
            context_index=0,
            audio_file=aud_path,
            img_file=img_path,
            chat_text=text,
        )

        return JsonResponse({'reply': reply_text, 'audio_path': out_audio})
    except:
        return JsonResponse({'error': '模型推理失败'}, status=500)


# 模型角色
@csrf_exempt
@require_POST
def set_role(request):
    role = request.POST.get('role', '')
    if not role:
        return JsonResponse({'error': '请提供角色'}, status=400)
    try:
        prompt_config = Roles.objects.get(name=role).prompt
        model_api.set_role(prompt_config)
        return JsonResponse({'role': role})
    except:
        return JsonResponse({'error': '设置角色失败'}, status=500)




def role_list(request):
    # 获取搜索关键词
    search_query = request.GET.get('search', '')

    # 根据搜索关键词过滤角色
    roles = Roles.objects.all().order_by('-updated_at')

    if search_query:
        roles = roles.filter(
            Q(name__icontains=search_query) |
            Q(desc__icontains=search_query) |
            Q(prompt__icontains=search_query)
        )

    # 传递到模板
    context = {
        'roles': roles,
        'search_query': search_query,
    }
    return render(request, 'model_api/role_list.html', context)

def model_index(request):
    return render(request, 'model_api/model.html')
