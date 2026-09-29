from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from App.models import Notificacion


@login_required(login_url='login')
def listar_notificaciones(request):
    """
    Vista completa para listar las notificaciones del usuario autenticado.
    """
    filtro = request.GET.get('filtro', 'todas').strip().lower()
    qs = Notificacion.objects.filter(usuario=request.user).select_related('reserva')

    total_notificaciones = qs.count()
    total_no_leidas = qs.filter(leido=False).count()
    total_leidas = qs.filter(leido=True).count()

    if filtro == 'no_leidas':
        notificaciones = qs.filter(leido=False).order_by('-fecha_creacion')
    elif filtro == 'alta':
        notificaciones = qs.filter(prioridad='alta').order_by('-fecha_creacion')
    elif filtro == 'leidas':
        notificaciones = qs.filter(leido=True).order_by('-fecha_creacion')
    else:
        notificaciones = qs.order_by('-fecha_creacion')

    contexto = {
        'notificaciones': notificaciones,
        'filtro_actual': filtro,
        'total_notificaciones': total_notificaciones,
        'total_no_leidas': total_no_leidas,
        'total_leidas': total_leidas,
    }
    return render(request, 'usuario/notificacion/notificaciones.html', contexto)


@login_required(login_url='login')
def marcar_notificacion_leida(request, notificacion_id):
    """
    Marca una notificación como leída y redirige al destino relacionado.
    """
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    notificacion.leido = True
    notificacion.save(update_fields=['leido'])

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({'status': 'ok', 'mensaje': 'Notificación marcada como leída'})

    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        redirect_to = next_url
    else:
        redirect_to = notificacion.get_destino_url()

    messages.success(request, 'Notificación marcada como leída.')
    return redirect(redirect_to)


@login_required(login_url='login')
def badge_notificaciones(request):
    """
    Retorna el badge con el conteo de notificaciones no leídas para HTMX.
    """
    total_no_leidas = Notificacion.objects.filter(usuario=request.user, leido=False).count()
    if total_no_leidas > 0:
        return HttpResponse(f'<span id="badgeCampanaNotif" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger border border-2 border-white fw-bold shadow d-flex align-items-center justify-content-center animate-pulse">{total_no_leidas}</span>')
    else:
        return HttpResponse('<span id="badgeCampanaNotif" class="d-none"></span>')


@login_required(login_url='login')
def marcar_todas_leidas(request):
    """
    Marca todas las notificaciones del usuario como leídas.
    """
    Notificacion.objects.filter(usuario=request.user, leido=False).update(leido=True)
    if request.headers.get('HX-Request'):
        response = HttpResponse()
        response['HX-Refresh'] = 'true'
        return response
        
    messages.success(request, 'Todas las notificaciones han sido marcadas como leídas.')
    return redirect(request.META.get('HTTP_REFERER', 'listar_notificaciones'))


@login_required(login_url='login')
def eliminar_notificacion(request, notificacion_id):
    """
    Elimina una notificación del usuario.
    """
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    notificacion.delete()

    if request.headers.get('HX-Request'):
        return HttpResponse('')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({'status': 'ok', 'mensaje': 'Notificación eliminada'})
    
    messages.success(request, 'Notificación eliminada.')
    return redirect(request.META.get('HTTP_REFERER', 'listar_notificaciones'))
