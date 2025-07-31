
# --- /home/runner/workspace/contabilidad/__init__.py ---



# --- /home/runner/workspace/contabilidad/admin.py ---
from django.contrib import admin

# Register your models here.



# --- /home/runner/workspace/contabilidad/apps.py ---
from django.apps import AppConfig


class ContabilidadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'contabilidad'



# --- /home/runner/workspace/contabilidad/app.py ---
# def ready(self):
#   import contabilidad.signals  # cambia por el nombre real

from django.apps import AppConfig

class ContabilidadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'contabilidad'

    def ready(self):
        import contabilidad.signals


# --- /home/runner/workspace/contabilidad/permissions.py ---
# accounts/permissions.py

from rest_framework import permissions

class EsAdminEmpresa(permissions.BasePermission):
    """
    Permite solo a usuarios con rol administrador de la empresa.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.rol and request.user.rol.nombre == 'Administrador'



# --- /home/runner/workspace/contabilidad/models.py ---
from django.db import models
from django.utils import timezone
from accounts.models import Usuario, Empresa
from django.core.exceptions import ValidationError

# ---------------------- MODELO BASE DE CUENTAS ----------------------

class CuentaContable(models.Model):
    """
    Catálogo de cuentas contables según el plan contable de la empresa.
    Puede ser compartido entre empresas o personalizado por empresa.
    """
    CLASIFICACIONES = [
        ('activo', 'Activo'),
        ('pasivo', 'Pasivo'),
        ('patrimonio', 'Patrimonio'),
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
    ]

    codigo = models.CharField(max_length=10, help_text="Código único, ej: 1020")
    nombre = models.CharField(max_length=255, help_text="Ej: Banco BBVA")
    clasificacion = models.CharField(max_length=20, choices=CLASIFICACIONES)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='cuentas_contables')
    es_auxiliar = models.BooleanField(default=True, help_text="Marca si la cuenta es de movimiento o de agrupación")
    padre = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subcuentas')
    creada_en = models.DateTimeField(auto_now_add=True)

    @property
    def saldo(self):
        debe = sum(m.debe for m in self.movimientos.all())
        haber = sum(m.haber for m in self.movimientos.all())
        return debe - haber

    class Meta:
        verbose_name = "Cuenta Contable"
        verbose_name_plural = "Cuentas Contables"
        ordering = ['codigo']
        unique_together = ('codigo', 'empresa')

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def clean(self):
        super().clean()
        if CuentaContable.objects.filter(
            codigo=self.codigo,
            empresa=self.empresa
        ).exclude(pk=self.pk).exists():
            raise ValidationError(f"Ya existe una cuenta con el código '{self.codigo}' para esta empresa.")

    def save(self, *args, **kwargs):
        self.full_clean()  # <- Esto asegura que clean() se ejecute siempre
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.movimientos.exists():
            raise ValidationError("No se puede eliminar una cuenta contable que tiene movimientos registrados.")
        super().delete(*args, **kwargs)

# ---------------------- MODELO DE ASIENTOS ----------------------



class AsientoContable(models.Model):
    """
    Representa un asiento contable (doble partida).
    Puede ser generado automáticamente por otros módulos (ej: pagos).
    """
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='asientos_contables')
    fecha = models.DateField(default=timezone.now)
    concepto = models.CharField(max_length=255)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='asientos_creados')
    creado_en = models.DateTimeField(auto_now_add=True)
    conciliado = models.BooleanField(default=False, help_text="Indica si el asiento está conciliado o cerrado")

    # 🔗 Referencia al objeto origen (ej: Pago, Compra, etc.)
    referencia_id = models.PositiveBigIntegerField(null=True, blank=True, help_text="ID del objeto origen (ej: pago, compra, etc.)")
    referencia_tipo = models.CharField(max_length=100, null=True, blank=True, help_text="Tipo de objeto origen (ej: 'Pago', 'Compra')")

    # 🧾 Totales rápidos para reportes
    total_debe = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_haber = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # ⚙️ Indica si fue generado automáticamente
    es_automatico = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Asiento Contable"
        verbose_name_plural = "Asientos Contables"
        ordering = ['-fecha', '-creado_en']
        indexes = [
            models.Index(fields=['empresa', 'fecha']),
            models.Index(fields=['referencia_tipo', 'referencia_id']),
        ]

    def __str__(self):
        return f"Asiento #{self.id} - {self.concepto} ({self.fecha})"

    def save(self, *args, **kwargs):
        self.full_clean()  # Valida antes de guardar
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if not self.pk:
            # No validar detalles si el asiento no está guardado aún
            return

        detalles = list(self.detalles.all())

        if len(detalles) < 2:
            raise ValidationError("El asiento debe tener al menos dos líneas contables.")

        total_debe = sum(detalle.debe for detalle in detalles)
        total_haber = sum(detalle.haber for detalle in detalles)

        if total_debe != total_haber:
            raise ValidationError("La suma del Debe debe ser igual a la del Haber (partida doble).")

    def actualizar_totales(self):
        """
        Suma todos los debe/haber de sus detalles y actualiza los campos total_debe y total_haber.
        """
        self.total_debe = sum(d.debe for d in self.detalles.all())
        self.total_haber = sum(d.haber for d in self.detalles.all())
        self.save(update_fields=['total_debe', 'total_haber'])

# ---------------------- DETALLES DE ASIENTO ----------------------

class DetalleAsiento(models.Model):
    """
    Detalle de una línea contable (debe o haber).
    Usa una cuenta contable como FK.
    """
    asiento = models.ForeignKey(AsientoContable, on_delete=models.CASCADE, related_name='detalles')
    cuenta_contable = models.ForeignKey(CuentaContable, on_delete=models.PROTECT, related_name='movimientos')
    debe = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    haber = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción opcional para este movimiento.")

    class Meta:
        verbose_name = "Detalle de Asiento"
        verbose_name_plural = "Detalles de Asientos"
        ordering = ['cuenta_contable']
        indexes = [
            models.Index(fields=['asiento', 'cuenta_contable']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~(models.Q(debe=0) & models.Q(haber=0)),
                name='debe_o_haber_no_pueden_ser_cero',
            )
        ]

    def save(self, *args, **kwargs):
        self.full_clean()  # Ejecuta clean() antes de guardar
        super().save(*args, **kwargs)

    def clean(self):
        if self.debe < 0 or self.haber < 0:
            raise ValidationError("Debe y Haber no pueden ser negativos.")
        if self.debe == 0 and self.haber == 0:
            raise ValidationError("Debe o Haber deben tener un valor distinto de cero.")
        if self.debe > 0 and self.haber > 0:
            raise ValidationError("No puede tener valores en ambos campos a la vez.")

    def __str__(self):
        return f"{self.cuenta_contable.codigo} | Debe: {self.debe} | Haber: {self.haber}"



# --- /home/runner/workspace/contabilidad/urls.py ---
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from contabilidad.views.asiento_contable import AsientoContableViewSet
from contabilidad.views.cuenta_contable import CuentaContableViewSet
from contabilidad.views.reportes_contables import ReportesContablesView

router = DefaultRouter()
router.register(r'entries', AsientoContableViewSet, basename='asiento')
router.register(r'accounts', CuentaContableViewSet, basename='cuenta_contable')


urlpatterns = [
    path('', include(router.urls)),
    path('reports/', ReportesContablesView.as_view(), name='reportes-contables')
]





# --- /home/runner/workspace/contabilidad/signals.py ---
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DetalleAsiento

@receiver([post_save, post_delete], sender=DetalleAsiento)
def actualizar_totales_asiento(sender, instance, **kwargs):
    print(f"Signal disparado para DetalleAsiento id={instance.id}")
    asiento = instance.asiento
    if not asiento:
        print("¡El detalle no tiene asignado asiento!")
        return
    try:
        asiento.actualizar_totales()
        print(f"Asiento {asiento.id} actualizado: debe={asiento.total_debe}, haber={asiento.total_haber}")
    except Exception as e:
        print(f"Error actualizando totales del asiento {asiento.id}: {e}")


# --- /home/runner/workspace/contabilidad/migrations/__init__.py ---



# --- /home/runner/workspace/contabilidad/migrations/0001_initial.py ---
# Generated by Django 5.2.4 on 2025-07-30 21:47

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AsientoContable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(default=django.utils.timezone.now)),
                ('concepto', models.CharField(max_length=255)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('conciliado', models.BooleanField(default=False, help_text='Indica si el asiento está conciliado o cerrado')),
                ('referencia_id', models.PositiveBigIntegerField(blank=True, help_text='ID del objeto origen (ej: pago, compra, etc.)', null=True)),
                ('referencia_tipo', models.CharField(blank=True, help_text="Tipo de objeto origen (ej: 'Pago', 'Compra')", max_length=100, null=True)),
                ('total_debe', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('total_haber', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('es_automatico', models.BooleanField(default=False)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asientos_contables', to='core.empresa')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='asientos_creados', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Asiento Contable',
                'verbose_name_plural': 'Asientos Contables',
                'ordering': ['-fecha', '-creado_en'],
            },
        ),
        migrations.CreateModel(
            name='CuentaContable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(help_text='Código único, ej: 1020', max_length=10)),
                ('nombre', models.CharField(help_text='Ej: Banco BBVA', max_length=255)),
                ('clasificacion', models.CharField(choices=[('activo', 'Activo'), ('pasivo', 'Pasivo'), ('patrimonio', 'Patrimonio'), ('ingreso', 'Ingreso'), ('gasto', 'Gasto')], max_length=20)),
                ('es_auxiliar', models.BooleanField(default=True, help_text='Marca si la cuenta es de movimiento o de agrupación')),
                ('creada_en', models.DateTimeField(auto_now_add=True)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cuentas_contables', to='core.empresa')),
                ('padre', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subcuentas', to='contabilidad.cuentacontable')),
            ],
            options={
                'verbose_name': 'Cuenta Contable',
                'verbose_name_plural': 'Cuentas Contables',
                'ordering': ['codigo'],
            },
        ),
        migrations.CreateModel(
            name='DetalleAsiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('debe', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('haber', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('descripcion', models.TextField(blank=True, help_text='Descripción opcional para este movimiento.', null=True)),
                ('asiento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='contabilidad.asientocontable')),
                ('cuenta_contable', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='movimientos', to='contabilidad.cuentacontable')),
            ],
            options={
                'verbose_name': 'Detalle de Asiento',
                'verbose_name_plural': 'Detalles de Asientos',
                'ordering': ['cuenta_contable'],
            },
        ),
        migrations.AddIndex(
            model_name='asientocontable',
            index=models.Index(fields=['empresa', 'fecha'], name='contabilida_empresa_2ddfb3_idx'),
        ),
        migrations.AddIndex(
            model_name='asientocontable',
            index=models.Index(fields=['referencia_tipo', 'referencia_id'], name='contabilida_referen_82230c_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='cuentacontable',
            unique_together={('codigo', 'empresa')},
        ),
        migrations.AddIndex(
            model_name='detalleasiento',
            index=models.Index(fields=['asiento', 'cuenta_contable'], name='contabilida_asiento_f6ba5e_idx'),
        ),
        migrations.AddConstraint(
            model_name='detalleasiento',
            constraint=models.CheckConstraint(condition=models.Q(('debe', 0), ('haber', 0), _negated=True), name='debe_o_haber_no_pueden_ser_cero'),
        ),
    ]



# --- /home/runner/workspace/contabilidad/views/__init__.py ---
from contabilidad.views.asiento_contable import AsientoContableViewSet


# --- /home/runner/workspace/contabilidad/views/detalle_asiento.py ---
from rest_framework import serializers
from contabilidad.models import DetalleAsiento

class DetalleAsientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleAsiento
        fields = ['id', 'asiento', 'cuenta_contable', 'debe', 'haber', 'descripcion']
        read_only_fields = ['id']

    def validate(self, data):
        debe = data.get('debe', 0)
        haber = data.get('haber', 0)

        if debe < 0 or haber < 0:
            raise serializers.ValidationError("Debe y Haber no pueden ser negativos.")

        if debe == 0 and haber == 0:
            raise serializers.ValidationError("Debe o Haber deben tener un valor distinto de cero.")

        if debe > 0 and haber > 0:
            raise serializers.ValidationError("No puede tener valores en Debe y Haber al mismo tiempo.")

        return data



# --- /home/runner/workspace/contabilidad/views/cuenta_contable.py ---
# contabilidad/views/cuenta_contable.py

from rest_framework import viewsets, permissions
from contabilidad.models import CuentaContable
from contabilidad.serializers.cuenta_contable import CuentaContableSerializer
from django_filters.rest_framework import DjangoFilterBackend

class CuentaContableViewSet(viewsets.ModelViewSet):
    queryset = CuentaContable.objects.all()
    serializer_class = CuentaContableSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['empresa', 'codigo', 'padre']
    serializer_class = CuentaContableSerializer
    permission_classes = [permissions.IsAuthenticated]  # Aquí puedes agregar permisos personalizados

    def get_queryset(self):
        empresa = getattr(self.request.user, 'empresa_actual', None)
        if empresa:
            return CuentaContable.objects.filter(empresa=empresa).order_by('codigo')
        return CuentaContable.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['empresa'] = getattr(self.request.user, 'empresa_actual', None)
        return context



# --- /home/runner/workspace/contabilidad/views/asiento_contable.py ---
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from contabilidad.models import AsientoContable
from contabilidad.serializers.asiento_contable import AsientoContableSerializer
from rest_framework.exceptions import ValidationError


class AsientoContableViewSet(viewsets.ModelViewSet):
    queryset = AsientoContable.objects.all()
    serializer_class = AsientoContableSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['fecha', 'usuario', 'conciliado']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        empresa = getattr(self.request.user, 'empresa_actual', None)
        if empresa:
            return AsientoContable.objects.filter(empresa=empresa)\
                .select_related('empresa')\
                .prefetch_related('detalles')
        return AsientoContable.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['empresa'] = getattr(self.request.user, 'empresa_actual', None)
        return context

    def perform_create(self, serializer):
        empresa = getattr(self.request.user, 'empresa_actual', None)
        if not empresa:
            raise ValidationError("No se ha definido la empresa actual del usuario.")
        serializer.save(empresa=empresa)

    def update(self, request, *args, **kwargs):
        asiento = self.get_object()
        if asiento.conciliado:
            return Response(
                {"detail": "No se puede modificar un asiento contable ya conciliado."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)


    @action(detail=True, methods=['patch'], url_path='conciliar')
    def conciliar(self, request, pk=None):
        asiento = self.get_object()
        if asiento.conciliado:
            return Response({"detail": "Este asiento ya está conciliado."}, status=status.HTTP_400_BAD_REQUEST)

        asiento.conciliado = True
        asiento.save(update_fields=['conciliado'])
        return Response({"detail": "Asiento conciliado correctamente."}, status=status.HTTP_200_OK)


# --- /home/runner/workspace/contabilidad/views/reportes_contables.py ---
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from contabilidad.models import AsientoContable, DetalleAsiento, CuentaContable
from django.db.models import Sum, Q


class ReportesContablesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empresa = getattr(request.user, 'empresa_actual', None)
        tipo = request.query_params.get('tipo')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        if not empresa:
            raise ValidationError("El usuario no tiene empresa_actual definida.")
        if tipo not in ['journal', 'trial_balance', 'income_statement', 'balance_sheet']:
            raise ValidationError("Invalid report type.")

        if tipo == 'journal':
            return self.libro_diario(empresa, fecha_inicio, fecha_fin)
        elif tipo == 'trial_balance':
            return self.balance_comprobacion(empresa, fecha_inicio, fecha_fin)
        elif tipo == 'income_statement':
            return self.estado_resultados(empresa, fecha_inicio, fecha_fin)
        elif tipo == 'balance_sheet':
            return self.balance_general(empresa, fecha_inicio, fecha_fin)

    def libro_diario(self, empresa, fecha_inicio, fecha_fin):
        filtros = Q(empresa=empresa)
        if fecha_inicio:
            filtros &= Q(fecha__gte=fecha_inicio)
        if fecha_fin:
            filtros &= Q(fecha__lte=fecha_fin)

        asientos = AsientoContable.objects.filter(filtros).prefetch_related('detalles')
        resultado = []
        for asiento in asientos:
            resultado.append({
                'id': asiento.id,
                'fecha': asiento.fecha,
                'concepto': asiento.concepto,
                'detalles': [
                    {
                        'cuenta': d.cuenta_contable.codigo,
                        'nombre': d.cuenta_contable.nombre,
                        'debe': float(d.debe),
                        'haber': float(d.haber),
                        'descripcion': d.descripcion
                    } for d in asiento.detalles.all()
                ]
            })
        return Response({'libro_diario': resultado})

    def balance_comprobacion(self, empresa, fecha_inicio, fecha_fin):
        filtros = Q(asiento__empresa=empresa)
        if fecha_inicio:
            filtros &= Q(asiento__fecha__gte=fecha_inicio)
        if fecha_fin:
            filtros &= Q(asiento__fecha__lte=fecha_fin)

        detalles = DetalleAsiento.objects.filter(filtros).values(
            'cuenta_contable__codigo',
            'cuenta_contable__nombre'
        ).annotate(
            total_debe=Sum('debe'),
            total_haber=Sum('haber')
        ).order_by('cuenta_contable__codigo')
        return Response({'balance_comprobacion': list(detalles)})

    def estado_resultados(self, empresa, fecha_inicio, fecha_fin):
        cuentas = CuentaContable.objects.filter(
            empresa=empresa,
            clasificacion__in=['ingreso', 'gasto']
        )
        resultado = []
        total_ingresos = 0
        total_gastos = 0

        for cuenta in cuentas:
            movimientos = cuenta.movimientos.all()
            if fecha_inicio:
                movimientos = movimientos.filter(asiento__fecha__gte=fecha_inicio)
            if fecha_fin:
                movimientos = movimientos.filter(asiento__fecha__lte=fecha_fin)

            debe = movimientos.aggregate(s=Sum('debe'))['s'] or 0
            haber = movimientos.aggregate(s=Sum('haber'))['s'] or 0
            saldo = haber - debe if cuenta.clasificacion == 'ingreso' else debe - haber

            resultado.append({
                'codigo': cuenta.codigo,
                'nombre': cuenta.nombre,
                'clasificacion': cuenta.clasificacion,
                'saldo': float(saldo)
            })

            if cuenta.clasificacion == 'ingreso':
                total_ingresos += saldo
            else:
                total_gastos += saldo

        utilidad_neta = total_ingresos - total_gastos
        return Response({
            'estado_resultados': resultado,
            'totales': {
                'ingresos': float(total_ingresos),
                'gastos': float(total_gastos),
                'utilidad_neta': float(utilidad_neta)
            }
        })

    def balance_general(self, empresa, fecha_inicio, fecha_fin):
        cuentas = CuentaContable.objects.filter(
            empresa=empresa,
            clasificacion__in=['activo', 'pasivo', 'patrimonio']
        )
        resultado = []
        totales = {'activo': 0, 'pasivo': 0, 'patrimonio': 0}

        for cuenta in cuentas:
            movimientos = cuenta.movimientos.all()
            if fecha_inicio:
                movimientos = movimientos.filter(asiento__fecha__gte=fecha_inicio)
            if fecha_fin:
                movimientos = movimientos.filter(asiento__fecha__lte=fecha_fin)

            debe = movimientos.aggregate(s=Sum('debe'))['s'] or 0
            haber = movimientos.aggregate(s=Sum('haber'))['s'] or 0
            saldo = debe - haber if cuenta.clasificacion == 'activo' else haber - debe

            resultado.append({
                'codigo': cuenta.codigo,
                'nombre': cuenta.nombre,
                'clasificacion': cuenta.clasificacion,
                'saldo': float(saldo)
            })

            totales[cuenta.clasificacion] += saldo

        return Response({
            'balance_general': resultado,
            'totales': {k: float(v) for k, v in totales.items()}
        })



# --- /home/runner/workspace/contabilidad/serializers/__init__.py ---
# contabilidad/serializers/__init__.py
from .asiento_contable import AsientoContableSerializer
from .detalle_asiento import DetalleAsientoSerializer


# --- /home/runner/workspace/contabilidad/serializers/detalle_asiento.py ---
from rest_framework import serializers
from contabilidad.models import AsientoContable, DetalleAsiento, CuentaContable
from accounts.models import Usuario
from django.db import transaction


class DetalleAsientoSerializer(serializers.ModelSerializer):
  cuenta_contable_codigo = serializers.ReadOnlyField(source='cuenta_contable.codigo')
  cuenta_contable_nombre = serializers.ReadOnlyField(source='cuenta_contable.nombre')

  class Meta:
      model = DetalleAsiento
      fields = ['id', 'cuenta_contable', 'cuenta_contable_codigo', 'cuenta_contable_nombre', 'debe', 'haber', 'descripcion']

  def validate(self, data):
      debe = data.get('debe', 0)
      haber = data.get('haber', 0)

      if debe < 0 or haber < 0:
          raise serializers.ValidationError("Debe y Haber no pueden ser negativos.")
      if debe == 0 and haber == 0:
          raise serializers.ValidationError("Debe o Haber deben tener un valor distinto de cero.")
      if debe > 0 and haber > 0:
          raise serializers.ValidationError("No puede tener valores en ambos campos a la vez.")

      return data


# --- /home/runner/workspace/contabilidad/serializers/cuenta_contable.py ---
# contabilidad/serializers/cuenta_contable.py

from rest_framework import serializers
from contabilidad.models import CuentaContable

class CuentaContableSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuentaContable
        fields = ['id', 'codigo', 'nombre', 'clasificacion', 'empresa', 'es_auxiliar', 'padre', 'creada_en']
        read_only_fields = ['creada_en', 'empresa']

    def validate_codigo(self, value):
        empresa = self.context.get('empresa')
        if CuentaContable.objects.filter(codigo=value, empresa=empresa).exists():
            raise serializers.ValidationError("Ya existe una cuenta con ese código para esta empresa.")
        return value

    def validate(self, data):
        if data.get('padre') and data['padre'].empresa != self.context.get('empresa'):
            raise serializers.ValidationError("La cuenta padre debe pertenecer a la misma empresa.")
        return data

    def create(self, validated_data):
        empresa = self.context.get('empresa')
        validated_data['empresa'] = empresa
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # No permitimos cambiar empresa en update para evitar inconsistencias
        validated_data.pop('empresa', None)
        return super().update(instance, validated_data)



# --- /home/runner/workspace/contabilidad/serializers/asiento_contable.py ---
from rest_framework import serializers
from contabilidad.models import AsientoContable, DetalleAsiento, CuentaContable
from accounts.models import Usuario
from django.db import transaction
from contabilidad.serializers.detalle_asiento import DetalleAsientoSerializer

class AsientoContableSerializer(serializers.ModelSerializer):
    detalles = DetalleAsientoSerializer(many=True)
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all(), required=False, allow_null=True)
    empresa = serializers.PrimaryKeyRelatedField(read_only=True)
    total_debe = serializers.DecimalField(read_only=True, max_digits=14, decimal_places=2)
    total_haber = serializers.DecimalField(read_only=True, max_digits=14, decimal_places=2)
    conciliado = serializers.BooleanField(read_only=True)
    es_automatico = serializers.BooleanField(read_only=True)

    class Meta:
        model = AsientoContable
        fields = [
            'id', 'empresa', 'fecha', 'concepto', 'usuario', 'creado_en', 'conciliado',
            'referencia_id', 'referencia_tipo', 'total_debe', 'total_haber', 'es_automatico',
            'detalles'
        ]
        read_only_fields = ['creado_en']

    def validate(self, data):
        # Bloquear modificación si está conciliado
        if self.instance and self.instance.conciliado:
            raise serializers.ValidationError("No se puede modificar un asiento contable ya conciliado.")

        detalles = data.get('detalles', None)

        # Validar detalles solo si vienen en la petición
        if detalles is not None:
            if len(detalles) < 2:
                raise serializers.ValidationError("Debe haber al menos dos detalles en el asiento para cumplir partida doble.")

            total_debe = sum(d.get('debe', 0) for d in detalles)
            total_haber = sum(d.get('haber', 0) for d in detalles)

            if total_debe != total_haber:
                raise serializers.ValidationError(
                    "El total del debe debe ser igual al total del haber (partida doble)."
                )

        return data

    @transaction.atomic
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        empresa = self.context.get('empresa')
        if empresa:
            validated_data['empresa'] = empresa

        asiento = AsientoContable.objects.create(**validated_data)

        total_debe = 0
        total_haber = 0
        for detalle_data in detalles_data:
            detalle = DetalleAsiento.objects.create(asiento=asiento, **detalle_data)
            total_debe += detalle.debe
            total_haber += detalle.haber

        asiento.total_debe = total_debe
        asiento.total_haber = total_haber
        asiento.save(update_fields=['total_debe', 'total_haber'])
        return asiento

    @transaction.atomic
    def update(self, instance, validated_data):
        # Bloquear actualización si está conciliado
        if instance.conciliado:
            raise serializers.ValidationError("No se puede modificar un asiento contable ya conciliado.")

        detalles_data = validated_data.pop('detalles', None)

        # Actualizar campos permitidos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if detalles_data is not None:
            instance.detalles.all().delete()
            total_debe = 0
            total_haber = 0
            for detalle_data in detalles_data:
                detalle = DetalleAsiento.objects.create(asiento=instance, **detalle_data)
                total_debe += detalle.debe
                total_haber += detalle.haber

            instance.total_debe = total_debe
            instance.total_haber = total_haber
            instance.save(update_fields=['total_debe', 'total_haber'])

        return instance


        


# --- /home/runner/workspace/contabilidad/utils/asientos.py ---
from contabilidad.models import AsientoContable, DetalleAsiento, CuentaContable

def registrar_asiento_pago(pago, usuario):
    """
    Crea un asiento contable al registrar un pago a proveedor o cliente.
    """
    empresa = pago.empresa
    monto = pago.monto
    cuenta_banco = CuentaContable.objects.get(codigo='1020', empresa=empresa)

    if pago.cuenta_pagar:
        proveedor = pago.cuenta_pagar.proveedor
        cuenta_proveedor = CuentaContable.objects.get(codigo='2010', empresa=empresa)

        concepto = f"Pago a proveedor {proveedor.nombre}"
        descripcion = f"Disminución de cuenta por pagar a {proveedor.nombre}"

        asiento = AsientoContable.objects.create(
            empresa=empresa,
            fecha=pago.fecha,
            concepto=concepto,
            usuario=usuario,
            referencia_id=pago.id,
            referencia_tipo='Pago',
            es_automatico=True,
        )

        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_proveedor,
            debe=monto,
            descripcion=descripcion
        )
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_banco,
            haber=monto,
            descripcion="Pago realizado desde banco"
        )

    elif pago.cuenta_cobrar:
        cliente = pago.cuenta_cobrar.cliente
        cuenta_cliente = CuentaContable.objects.get(codigo='1050', empresa=empresa)

        concepto = f"Pago recibido de cliente {cliente.nombre}"
        descripcion = f"Disminución de cuenta por cobrar de {cliente.nombre}"

        asiento = AsientoContable.objects.create(
            empresa=empresa,
            fecha=pago.fecha,
            concepto=concepto,
            usuario=usuario,
            referencia_id=pago.id,
            referencia_tipo='Pago',
            es_automatico=True,
        )

        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_banco,
            debe=monto,
            descripcion="Ingreso en banco"
        )
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_cliente,
            haber=monto,
            descripcion=descripcion
        )
    else:
        raise ValueError("El pago no está vinculado ni a una cuenta por pagar ni por cobrar.")

    asiento.actualizar_totales()
    return asiento


# --- /home/runner/workspace/contabilidad/tests/__init__.py ---



# --- /home/runner/workspace/contabilidad/tests/test_models.py ---
import pytest
from django.core.exceptions import ValidationError
from contabilidad.models import AsientoContable

@pytest.mark.django_db
def test_no_modificar_conciliado(empresa, usuario):
    asiento = AsientoContable.objects.create(
        fecha="2025-07-21",
        empresa=empresa,
        usuario=usuario,
        conciliado=True,
        concepto="Concepto de prueba"
    )
    with pytest.raises(ValidationError):
        asiento.conciliado = True
        asiento.full_clean()  # dispara validaciones


# --- /home/runner/workspace/contabilidad/tests/conftest.py ---
import pytest
from contabilidad.models import AsientoContable, CuentaContable
from accounts.models import Usuario
from core.models import Empresa

@pytest.fixture
def empresa(db):
    return Empresa.objects.create(nombre="Empresa Test")

@pytest.fixture
def usuario(db, empresa):
    return Usuario.objects.create(username="user1", empresa=empresa)

@pytest.fixture
def cuenta_contable_1(db, empresa):
    return CuentaContable.objects.create(
        codigo="001",  # código único dentro de la empresa
        nombre="Cuenta 1",
        clasificacion="activo",  # debe estar dentro de las opciones válidas
        empresa=empresa
    )

@pytest.fixture
def cuenta_contable_2(db, empresa):
    return CuentaContable.objects.create(
        codigo="002",  # código único dentro de la empresa
        nombre="Cuenta 2",
        clasificacion="activo",  # debe estar dentro de las opciones válidas
        empresa=empresa
    )    

@pytest.fixture
def asiento_data(empresa, usuario, cuenta_contable_1, cuenta_contable_2):
    return {
        "fecha": "2025-07-21",
        "usuario": usuario.id,
        "concepto": "Concepto de prueba",
        "detalles": [
            {"cuenta_contable": cuenta_contable_1.id, "debe": 100, "haber": 0},
            {"cuenta_contable": cuenta_contable_2.id, "debe": 0, "haber": 100},
        ],
    }

@pytest.fixture
def asiento_creado(db, empresa, usuario):
    return AsientoContable.objects.create(
        fecha="2025-07-21",
        empresa=empresa,
        usuario=usuario,
        conciliado=False,
        concepto="test"
    )

@pytest.fixture
def asiento_conciliado(db, empresa, usuario, cuenta_contable_1, cuenta_contable_2):
    asiento = AsientoContable.objects.create(
        fecha="2025-07-21",
        empresa=empresa,
        usuario=usuario,
        conciliado=True,
        concepto="test"
    )
    # Añadir detalles válidos
    from contabilidad.models import DetalleAsiento
    DetalleAsiento.objects.create(
        asiento=asiento,
        cuenta_contable=cuenta_contable_1,
        debe=100,
        haber=0
    )
    DetalleAsiento.objects.create(
        asiento=asiento,
        cuenta_contable=cuenta_contable_2,
        debe=0,
        haber=100
    )
    return asiento


# --- /home/runner/workspace/contabilidad/tests/test_views.py ---
import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from contabilidad.models import AsientoContable, DetalleAsiento

@pytest.mark.django_db
def test_list_asientos_autenticado(usuario, empresa, asiento_creado):
    client = APIClient()
    client.force_authenticate(usuario)
    url = reverse('asiento-list')
    response = client.get(url)
    assert response.status_code == 200
    # Debe mostrar solo asientos de la empresa del usuario
    for item in response.data['results']:
        assert item['empresa'] == empresa.id

@pytest.mark.django_db
def test_update_bloqueado_si_conciliado(usuario, asiento_conciliado):
    client = APIClient()
    client.force_authenticate(usuario)
    url = reverse('asiento-detail', args=[asiento_conciliado.id])
    response = client.put(url, {'fecha': '2025-07-30'})
    assert response.status_code == 400
    assert 'No se puede modificar un asiento contable ya conciliado.' in response.data['detail']

@pytest.mark.django_db
def test_accion_conciliar(usuario, asiento_creado, cuenta_contable_1, cuenta_contable_2):
    DetalleAsiento.objects.create(asiento=asiento_creado, cuenta_contable=cuenta_contable_1, debe=100, haber=0)
    DetalleAsiento.objects.create(asiento=asiento_creado, cuenta_contable=cuenta_contable_2, debe=0, haber=100)

    client = APIClient()
    client.force_authenticate(usuario)
    url = reverse('asiento-conciliar', args=[asiento_creado.id])
    response = client.patch(url)
    assert response.status_code == 200
    assert response.data['detail'] == "Asiento conciliado correctamente."
    
# @pytest.mark.django_db
# def test_accion_conciliar(usuario, asiento_creado):
#     client = APIClient()
#     client.force_authenticate(usuario)
#     url = reverse('asiento-conciliar', args=[asiento_creado.id])
#     response = client.patch(url)
#     assert response.status_code == 200
#     assert response.data['detail'] == "Asiento conciliado correctamente."

@pytest.mark.django_db
def test_accion_conciliar_ya_conciliado(usuario, asiento_conciliado):
    client = APIClient()
    client.force_authenticate(usuario)
    url = reverse('asiento-conciliar', args=[asiento_conciliado.id])
    response = client.patch(url)
    assert response.status_code == 400
    assert response.data['detail'] == "Este asiento ya está conciliado."



# --- /home/runner/workspace/contabilidad/tests/test_serializers.py ---
import pytest
from contabilidad.serializers.asiento_contable import AsientoContableSerializer
from contabilidad.models import AsientoContable, DetalleAsiento

@pytest.mark.django_db
def test_serializer_valido_creacion(asiento_data, empresa, usuario):
    # asiento_data debe ser un dict válido para crear asiento
    serializer = AsientoContableSerializer(data=asiento_data, context={'empresa': empresa})
    assert serializer.is_valid(), serializer.errors
    asiento = serializer.save()
    assert asiento.empresa == empresa

@pytest.mark.django_db
def test_serializer_error_faltan_campos():
    serializer = AsientoContableSerializer(data={})
    assert not serializer.is_valid()
    assert 'fecha' in serializer.errors or 'detalles' in serializer.errors

@pytest.mark.django_db
def test_serializer_no_modificar_conciliado(asiento_conciliado, cuenta_contable_1, cuenta_contable_2):
    # Agregamos detalles válidos
    DetalleAsiento.objects.create(asiento=asiento_conciliado, cuenta_contable=cuenta_contable_1, debe=100, haber=0)
    DetalleAsiento.objects.create(asiento=asiento_conciliado, cuenta_contable=cuenta_contable_2, debe=0, haber=100)

    # ⚠️ Refrescamos el objeto desde la BD para que tenga los detalles correctamente cargados
    asiento_conciliado.refresh_from_db()

    serializer = AsientoContableSerializer(asiento_conciliado, data={'fecha': '2025-07-22'}, partial=True)
    assert not serializer.is_valid()
    assert 'No se puede modificar un asiento contable ya conciliado.' in str(serializer.errors)

# @pytest.mark.django_db
# def test_serializer_no_modificar_conciliado(asiento_conciliado):
#     serializer = AsientoContableSerializer(asiento_conciliado, data={'fecha': '2025-07-22'}, partial=True)
#     assert not serializer.is_valid()
#     assert 'No se puede modificar un asiento contable ya conciliado.' in str(serializer.errors)



# --- /home/runner/workspace/contabilidad/tests/test_reportes.py ---
import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from accounts.models import Usuario
from contabilidad.models import CuentaContable, AsientoContable, DetalleAsiento
from core.models import Empresa
from datetime import date


@pytest.fixture
def setup_contabilidad(db):
    empresa = Empresa.objects.create(nombre="Nova Corp")
    usuario = Usuario.objects.create_user(
        username="testuser", password="1234", empresa=empresa
    )

    cuenta_activo = CuentaContable.objects.create(
        empresa=empresa, codigo="1001", nombre="Caja", clasificacion="activo"
    )
    cuenta_ingreso = CuentaContable.objects.create(
        empresa=empresa, codigo="4001", nombre="Ventas", clasificacion="ingreso"
    )

    asiento = AsientoContable.objects.create(
        empresa=empresa, fecha=date(2025, 7, 1), concepto="Venta inicial", usuario=usuario
    )

    DetalleAsiento.objects.create(
        asiento=asiento, cuenta_contable=cuenta_activo, debe=1000, haber=0, descripcion="Ingreso en caja"
    )
    DetalleAsiento.objects.create(
        asiento=asiento, cuenta_contable=cuenta_ingreso, debe=0, haber=1000, descripcion="Venta realizada"
    )

    return usuario


@pytest.mark.django_db
def test_journal_report(setup_contabilidad):
    client = APIClient()
    client.force_authenticate(user=setup_contabilidad)

    url = reverse('reportes-contables') + '?tipo=journal'
    response = client.get(url)

    assert response.status_code == 200
    assert 'libro_diario' in response.data
    assert isinstance(response.data['libro_diario'], list)


@pytest.mark.django_db
def test_trial_balance_report(setup_contabilidad):
    client = APIClient()
    client.force_authenticate(user=setup_contabilidad)

    url = reverse('reportes-contables') + '?tipo=trial_balance'
    response = client.get(url)

    assert response.status_code == 200
    assert 'balance_comprobacion' in response.data
    assert isinstance(response.data['balance_comprobacion'], list)


@pytest.mark.django_db
def test_income_statement_report(setup_contabilidad):
    client = APIClient()
    client.force_authenticate(user=setup_contabilidad)

    url = reverse('reportes-contables') + '?tipo=income_statement'
    response = client.get(url)

    assert response.status_code == 200
    assert 'estado_resultados' in response.data
    assert 'totales' in response.data


@pytest.mark.django_db
def test_balance_sheet_report(setup_contabilidad):
    client = APIClient()
    client.force_authenticate(user=setup_contabilidad)

    url = reverse('reportes-contables') + '?tipo=balance_sheet'
    response = client.get(url)

    assert response.status_code == 200
    assert 'balance_general' in response.data
    assert 'totales' in response.data



# --- /home/runner/workspace/contabilidad/helpers/asientos.py ---
from decimal import Decimal
from django.db import transaction
from contabilidad.models import AsientoContable, DetalleAsiento, CuentaContable
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError

def redondear_decimal(valor, decimales=2):
    if not isinstance(valor, Decimal):
        valor = Decimal(str(valor))
    return valor.quantize(Decimal('1.' + '0' * decimales), rounding=ROUND_HALF_UP)

def generar_asiento_para_venta(venta, usuario):
    empresa = venta.empresa
    try:
        cuenta_clientes = CuentaContable.objects.get(codigo='1050', empresa=empresa)
        cuenta_ingresos = CuentaContable.objects.get(codigo='4010', empresa=empresa)
        cuenta_iva = CuentaContable.objects.get(codigo='2080', empresa=empresa)
    except ObjectDoesNotExist as e:
        raise ValidationError(f"No existe la cuenta contable requerida: {str(e)}")

    # Cálculo del total e IVA
    total = redondear_decimal(venta.total)
    iva_tasa = Decimal("0.16")
    base = redondear_decimal(total / (1 + iva_tasa))
    iva = redondear_decimal(total - base)

    with transaction.atomic():
        asiento = AsientoContable.objects.create(
            empresa=empresa,
            fecha=venta.fecha,
            concepto=f"Venta #{venta.id} a {venta.cliente.nombre}",
            usuario=usuario,
            referencia_id=venta.id,
            referencia_tipo='Venta',
            es_automatico=True,
        )

        # DEBE: Cliente por cobrar (total completo)
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_clientes,
            debe=total,
            haber=Decimal('0.00'),
            descripcion="Venta - Cliente por cobrar"
        )

        # HABER: Ingresos (base sin IVA)
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_ingresos,
            debe=Decimal('0.00'),
            haber=base,
            descripcion="Venta - Ingresos"
        )

        # HABER: IVA por pagar
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_iva,
            debe=Decimal('0.00'),
            haber=iva,
            descripcion="Venta - IVA por pagar"
        )

        asiento.actualizar_totales()
        venta.asiento_contable = asiento
        venta.save()
        return asiento


from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction

def generar_asiento_para_compra(compra, usuario):
    empresa = compra.empresa
    try:
        cuenta_costo = CuentaContable.objects.get(codigo='5010', empresa=empresa)
        cuenta_iva_acreditar = CuentaContable.objects.get(codigo='1180', empresa=empresa)
        cuenta_proveedores = CuentaContable.objects.get(codigo='2010', empresa=empresa)
    except ObjectDoesNotExist as e:
        raise ValidationError(f"No existe la cuenta contable requerida: {str(e)}")

    # Cálculo del total e IVA
    total = redondear_decimal(compra.total)
    iva_tasa = Decimal("0.16")
    base = redondear_decimal(total / (1 + iva_tasa))
    iva = redondear_decimal(total - base)

    with transaction.atomic():
        asiento = AsientoContable.objects.create(
            empresa=empresa,
            fecha=compra.fecha,
            concepto=f"Compra #{compra.id} de {compra.proveedor.nombre}",
            usuario=usuario,
            referencia_id=compra.id,
            referencia_tipo='Compra',
            es_automatico=True,
        )

        # DEBE: Costo de ventas (base sin IVA)
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_costo,
            debe=base,
            haber=Decimal('0.00'),
            descripcion="Compra - Costo de ventas"
        )

        # DEBE: IVA por acreditar
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_iva_acreditar,
            debe=iva,
            haber=Decimal('0.00'),
            descripcion="Compra - IVA por acreditar"
        )

        # HABER: Proveedores por pagar (total completo)
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta_contable=cuenta_proveedores,
            debe=Decimal('0.00'),
            haber=total,
            descripcion="Compra - Proveedores por pagar"
        )

        asiento.actualizar_totales()
        # Se elimina la asignación para evitar error
        # compra.asiento_contable = asiento
        # compra.save()

        return asiento

# def generar_asiento_para_compra(compra, usuario):
#     empresa = compra.empresa
#     try:
#         cuenta_costo = CuentaContable.objects.get(codigo='5010', empresa=empresa)
#         cuenta_iva_acreditar = CuentaContable.objects.get(codigo='1180', empresa=empresa)
#         cuenta_proveedores = CuentaContable.objects.get(codigo='2010', empresa=empresa)
#     except ObjectDoesNotExist as e:
#         raise ValidationError(f"No existe la cuenta contable requerida: {str(e)}")

#     # Cálculo del total e IVA
#     total = redondear_decimal(compra.total)
#     iva_tasa = Decimal("0.16")
#     base = redondear_decimal(total / (1 + iva_tasa))
#     iva = redondear_decimal(total - base)

#     with transaction.atomic():
#         asiento = AsientoContable.objects.create(
#             empresa=empresa,
#             fecha=compra.fecha,
#             concepto=f"Compra #{compra.id} de {compra.proveedor.nombre}",
#             usuario=usuario,
#             referencia_id=compra.id,
#             referencia_tipo='Compra',
#             es_automatico=True,
#         )

#         # DEBE: Costo de ventas (base sin IVA)
#         DetalleAsiento.objects.create(
#             asiento=asiento,
#             cuenta_contable=cuenta_costo,
#             debe=base,
#             haber=Decimal('0.00'),
#             descripcion="Compra - Costo de ventas"
#         )

#         # DEBE: IVA por acreditar
#         DetalleAsiento.objects.create(
#             asiento=asiento,
#             cuenta_contable=cuenta_iva_acreditar,
#             debe=iva,
#             haber=Decimal('0.00'),
#             descripcion="Compra - IVA por acreditar"
#         )

#         # HABER: Proveedores por pagar (total completo)
#         DetalleAsiento.objects.create(
#             asiento=asiento,
#             cuenta_contable=cuenta_proveedores,
#             debe=Decimal('0.00'),
#             haber=total,
#             descripcion="Compra - Proveedores por pagar"
#         )

#         asiento.actualizar_totales()
#         compra.asiento_contable = asiento
#         compra.save()
#         return asiento

