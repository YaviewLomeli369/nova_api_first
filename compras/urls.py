from compras.views.proveedor_views import ProveedorViewSet


from rest_framework import routers
from django.urls import path, include
from compras.views.compra_views import CompraViewSet, ReceivePurchase , CompraReceiveView, CompraRecepcionParcialAPIView, CompraCancelarAPIView
from compras.views.pago import PagoCompraCreateView, PagoCompraListView, PagoCompraDetailView

router = routers.DefaultRouter()
router.register(r'providers', ProveedorViewSet, basename='proveedor')
router.register(r'purchases', CompraViewSet, basename='purchases')

urlpatterns = [
    path('', include(router.urls)),
    # path('purchases/<int:id>/receive/', ReceivePurchase.as_view(), name='receive_purchase')
    path('purchases/<int:pk>/receive/', CompraReceiveView.as_view(), name='compra-receive'),
    path('purchases/<int:pk>/partial-reception/', CompraRecepcionParcialAPIView.as_view(), name='compra-recepcion-parcial'),
    path('purchases/<int:pk>/cancelar/', CompraCancelarAPIView.as_view(), name='cancelar_compra'),
    path('payments/', PagoCompraListView.as_view(), name='lista-pagos-compra'),     # GET ?compra_id=1
    path('payments/register/', PagoCompraCreateView.as_view(), name='registrar-pago-compra'),  # POST
    path('payments/<int:pk>/', PagoCompraDetailView.as_view(), name='detalle-pago-compra'),
]