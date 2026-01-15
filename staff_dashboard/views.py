from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from orders.models import Order
from products.models import Product
from staff_dashboard.decorators import staff_required
from staff_dashboard.forms import ProductAdminForm


# ======================================================================
# PERIODS
# ======================================================================
@dataclass(frozen=True)
class Period:
    key: str
    title: str
    days: int


PERIODS: list[Period] = [
    Period(key="today", title="Today", days=1),
    Period(key="7d", title="7 days", days=7),
    Period(key="30d", title="30 days", days=30),
]


def _get_period(request: HttpRequest) -> Period:
    key = (request.GET.get("period") or "7d").strip().lower()
    for p in PERIODS:
        if p.key == key:
            return p
    return PERIODS[1]  # 7d


def _daterange_endpoints(today: date, days: int) -> tuple[date, date]:
    """
    Возвращает (start, end_inclusive) для периода длиной days,
    включительно по обеим границам.
    """
    start = today - timedelta(days=days - 1)
    end = today
    return start, end


def _previous_period(start: date, end: date) -> tuple[date, date]:
    """
    Предыдущий период такой же длины, непосредственно перед текущим.
    """
    length = (end - start).days + 1
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=length - 1)
    return prev_start, prev_end


def _pct_change(current: Decimal, previous: Decimal) -> tuple[int | None, str]:
    """
    current vs previous:
      pct: int (абс. процент) или None (если previous==0 и current>0)
      dir: "up"|"down"|"flat"
    """
    if previous == 0:
        if current == 0:
            return 0, "flat"
        return None, "up"

    change = (current - previous) / previous * Decimal("100")
    pct = int(abs(change).quantize(Decimal("1")))

    if change > 0:
        return pct, "up"
    if change < 0:
        return pct, "down"
    return 0, "flat"


def _sum_or_zero(qs, field: str) -> Decimal:
    return qs.aggregate(v=Sum(field))["v"] or Decimal("0")


# ======================================================================
# DASHBOARD
# ======================================================================
@staff_required
def dashboard(request: HttpRequest) -> HttpResponse:
    User = get_user_model()

    period = _get_period(request)
    today = timezone.localdate()

    start, end = _daterange_endpoints(today, period.days)
    prev_start, prev_end = _previous_period(start, end)

    # --- Products (на текущую дату) ---
    products_total = Product.objects.count()
    products_active = Product.objects.filter(is_active=True).count()
    products_inactive = products_total - products_active
    out_of_stock = Product.objects.filter(stock=0).count()

    # --- Orders (период) ---
    orders_qs = Order.objects.all()
    curr_orders_qs = orders_qs.filter(created_at__date__range=(start, end))
    prev_orders_qs = orders_qs.filter(created_at__date__range=(prev_start, prev_end))

    orders_total = orders_qs.count()
    orders_curr = curr_orders_qs.count()
    orders_prev = prev_orders_qs.count()
    orders_pct, orders_dir = _pct_change(Decimal(orders_curr), Decimal(orders_prev))

    # Pending
    pending_statuses = [Order.STATUS_PENDING, Order.STATUS_PENDING_PAYMENT]
    pending_total = orders_qs.filter(status__in=pending_statuses).count()
    pending_curr = curr_orders_qs.filter(status__in=pending_statuses).count()
    pending_prev = prev_orders_qs.filter(status__in=pending_statuses).count()
    pending_pct, pending_dir = _pct_change(Decimal(pending_curr), Decimal(pending_prev))

    # Sales
    sales_base = orders_qs.exclude(status=Order.STATUS_CANCELLED)
    sales_total = _sum_or_zero(sales_base, "total_price")
    sales_curr = _sum_or_zero(
        sales_base.filter(created_at__date__range=(start, end)),
        "total_price",
    )
    sales_prev = _sum_or_zero(
        sales_base.filter(created_at__date__range=(prev_start, prev_end)),
        "total_price",
    )
    sales_pct, sales_dir = _pct_change(sales_curr, sales_prev)

    # Avg check (по периоду)
    avg_check_curr = (sales_curr / Decimal(orders_curr)) if orders_curr else Decimal("0")
    avg_check_prev = (sales_prev / Decimal(orders_prev)) if orders_prev else Decimal("0")
    avg_check_pct, avg_check_dir = _pct_change(avg_check_curr, avg_check_prev)

    # Users (если есть date_joined)
    users_total = User.objects.count()
    users_curr: int | None = None
    users_pct: int | None = None
    users_dir = "flat"

    if hasattr(User, "date_joined"):
        users_curr_count = User.objects.filter(
            date_joined__date__range=(start, end)
        ).count()
        users_prev_count = User.objects.filter(
            date_joined__date__range=(prev_start, prev_end)
        ).count()

        users_curr = users_curr_count
        users_pct, users_dir = _pct_change(
            Decimal(users_curr_count),
            Decimal(users_prev_count),
        )
    context = {
        # periods
        "period_key": period.key,
        "period_title": period.title,
        "periods": PERIODS,
        "start": start,
        "end": end,
        "prev_start": prev_start,
        "prev_end": prev_end,
        # products
        "products_total": products_total,
        "products_active": products_active,
        "products_inactive": products_inactive,
        "out_of_stock": out_of_stock,
        # sales card
        "sales_total": sales_total,
        "sales_curr": sales_curr,
        "sales_pct": sales_pct,
        "sales_dir": sales_dir,
        # users card
        "users_total": users_total,
        "users_curr": users_curr,
        "users_pct": users_pct,
        "users_dir": users_dir,
        # orders card
        "orders_total": orders_total,
        "orders_curr": orders_curr,
        "orders_pct": orders_pct,
        "orders_dir": orders_dir,
        # pending card
        "pending_total": pending_total,
        "pending_curr": pending_curr,
        "pending_pct": pending_pct,
        "pending_dir": pending_dir,
        # avg check card
        "avg_check_curr": avg_check_curr,
        "avg_check_pct": avg_check_pct,
        "avg_check_dir": avg_check_dir,
    }
    return render(request, "staff_dashboard/dashboard.html", context)


# ======================================================================
# PRODUCTS LIST
# ======================================================================
@staff_required
def products(request: HttpRequest) -> HttpResponse:
    qs = Product.objects.select_related("category").order_by("-created_at")
    return render(request, "staff_dashboard/products.html", {"products": qs})


# ======================================================================
# PRODUCT FORM (ADD / EDIT)
# ======================================================================
@staff_required
def product_form(request: HttpRequest, pk: int | None = None) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk) if pk else None

    # POST
    if request.method == "POST":
        form = ProductAdminForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            saved = form.save()
            messages.success(request, f"Товар сохранён: {saved.name}")
            return redirect("staff_dashboard:products")
        messages.error(request, "Исправьте ошибки формы.")
    # GET
    else:
        form = ProductAdminForm(instance=product)

    return render(
        request,
        "staff_dashboard/product_form.html",
        {"form": form, "product": product, "mode": "edit" if product else "add"},
    )


# ======================================================================
# PRODUCT DELETE
# ======================================================================
@staff_required
def product_delete(request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk)

    if request.method != "POST":
        messages.error(request, "Удаление доступно только через POST.")
        return redirect("staff_dashboard:product_edit", pk=pk)

    name = product.name
    product.delete()
    messages.success(request, f"Товар удалён: {name}")
    return redirect("staff_dashboard:products")
