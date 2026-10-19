from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from core.Plus import Plus
import re
from django.db.models import F
from django.core.cache import cache
from django.conf import settings
from apps.sales.models import Sale, SalePaymentMethod
from core.models import Company, Branch 
from django.db.models import Count, Q, Sum, DecimalField
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.db.models.functions import Coalesce

@shared_task
def send_weekly_reports():
    companies = Company.objects.filter(
        activated=True
    ).only(
        "id",
        "company_name",
        "email_of_the_person_in_charge"
    )
    #here we will to get the start and end of the week
    today = timezone.localdate()
    this_monday = today - timedelta(days=today.weekday()) #monday of this week
    start_week = this_monday - timedelta(days=7) #monday of last week
    end_week = this_monday #range the report 

    #here we will to read all the company that exist in the system and we will to create his report of the week
    print('reportes email')
    for company in companies:
        print('entra a empresa ')
        generate_company_report.delay(company.id, start_week, end_week)

@shared_task
def generate_company_report(company_id, start_week, end_week):
    #get the company that we will to generate the report
    company = Company.objects.get(id=company_id)

    #------------------get all the sale of the last week------------------
    week_sales = Sale.objects.filter(
        company=company,
        creationDate__gte=start_week,
        creationDate__lt=end_week,
    )

    #information of the sale of the week
    sales = week_sales.aggregate(
        total_sales=Count("id"),
        pending=Count(
            "id",
            filter=Q(status="pending")
        ),
        paid=Count(
            "id",
            filter=Q(status="paid")
        ),
        cancelled=Count(
            "id",
            filter=Q(status="cancelled")
        ),
        accepted=Count(
            "id",
            filter=Q(status="accepted")
        ),
    )

    #here we will do the total of the sale 
    sales_money = week_sales.aggregate(
        generated=Coalesce(
            Sum("total"),
            0,
            output_field=DecimalField()
        ),
        paid=Coalesce(
            Sum("amount_paid"),
            0,
            output_field=DecimalField()
        ),
        pending=Coalesce(
            Sum("balance"),
            0,
            output_field=DecimalField()
        ),
    )

    #------------------here we will to get all the inside money and all the outside money------------------
    payments = SalePaymentMethod.objects.filter(
        company=company,
        date__gte=start_week,
        date__lt=end_week,
    )
    cashflow = payments.aggregate(
        # -------- Entradas por método --------
        cash=Coalesce(
            Sum("amount", filter=Q(method="cash", amount__gt=0)),
            0,
            output_field=DecimalField()
        ),
        card=Coalesce(
            Sum("amount", filter=Q(method="card", amount__gt=0)),
            0,
            output_field=DecimalField()
        ),
        transfer=Coalesce(
            Sum("amount", filter=Q(method="transfer", amount__gt=0)),
            0,
            output_field=DecimalField()
        ),
        terminal=Coalesce(
            Sum("amount", filter=Q(method="terminal", amount__gt=0)),
            0,
            output_field=DecimalField()
        ),
        change=Coalesce(
            Sum("amount", filter=Q(method="change")),
            0,
            output_field=DecimalField()
        ),

        # -------- Totales --------
        total_income=Coalesce(
            Sum("amount", filter=Q(amount__gt=0)),
            0,
            output_field=DecimalField()
        ),
        total_expense=Coalesce(
            Sum("amount", filter=Q(amount__lt=0)),
            0,
            output_field=DecimalField()
        ),
    )


    #here we will to calculate the balance
    cashflow["balance"] = (
        cashflow["total_income"] +
        cashflow["total_expense"]
    )

    #------------------information agenda of this week------------------
    #now we will to create a dictionary for the report 
    context = {
        "company": company.company_name if company.company_name else 'Your company',
        "week":{
            "start":start_week,
            "end":end_week,
        },
        "sales":sales,
        "sales_money":sales_money,
        "cashflow":cashflow
    }
    
    #here we will to render the email html 
    html_content = convert_infot_to_html(context)

    send_weekly_report_email.delay(
        company.email_of_the_person_in_charge,
        company.company_name,
        html_content
    )

def convert_infot_to_html(context):
    # 1. Extraer los objetos principales del contexto seguro (evitando KeyErrors)
    company = context.get("company")
    sales_money = context.get("sales_money") or {}
    sales = context.get("sales") or {}
    cashflow=context.get("cashflow", {})

    # Extraer fechas
    week = context.get("week", {})

    start_week = week.get("start")
    end_week = week.get("end")

    # Formatear fechas para el encabezado del correo
    start_str = start_week.strftime("%d %b") if start_week else ""
    end_str = end_week.strftime("%d %b, %Y") if end_week else ""

    # 2. Extraer y asegurar valores financieros (evitar None)
    money_generated = sales_money.get("generated") or 0
    money_paid = sales_money.get("paid") or 0
    money_pending = sales_money.get("pending") or 0

    # Formatear el dinero de manera externa para evitar conflictos de llaves en el f-string
    money_generated_str = f"${money_generated:,.2f}"
    money_paid_str = f"${money_paid:,.2f}"
    money_pending_str = f"${money_pending:,.2f}"

    # 3. Extraer cantidades de ventas
    total_sales = sales.get("total_sales") or 0
    sales_paid = sales.get("paid") or 0
    sales_pending = sales.get("pending") or 0

    #get the move of the money 
    cashFloat = cashflow.get("cash") or 0
    cardFloat = cashflow.get("card") or 0
    transferFloat = cashflow.get("transfer") or 0
    terminalFloat = cashflow.get("terminal") or 0
    changeFloat = cashflow.get("change") or 0
    total_incomeFloat = cashflow.get("total_income") or 0
    total_expenseFloat = cashflow.get("total_expense") or 0
    balanceFloat = cashflow.get("balance") or 0

    #this is for convert float to string
    cash = f"${cashFloat:,.2f}"
    card = f"${cardFloat:,.2f}"
    transfer = f"${transferFloat:,.2f}"
    terminal = f"${terminalFloat:,.2f}"
    change = f"${changeFloat:,.2f}"
    total_income = f"${total_incomeFloat:,.2f}"
    total_expense = f"${total_expenseFloat:,.2f}"
    balance = f"${balanceFloat:,.2f}"

    # 6. Construcción del HTML
    # Nota: Las llaves del CSS se duplican ({{ }}) para que Python no las confunda con variables
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reporte Semanal de Actividad</title>
        <style>
            body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
            table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
            img {{ -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }}
            table {{ border-collapse: collapse !important; }}
            body {{ height: 100% !important; margin: 0 !important; padding: 0 !important; width: 100% !important; background-color: #f4f6f9; font-family: 'Segoe UI', Helvetica, Arial, sans-serif; color: #333333; }}

            .email-container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }}
            .header {{ background: linear-gradient(135deg, #0f4c81 0%, #1d72b8 100%); padding: 32px 24px; text-align: center; }}
            .logo {{ max-width: 140px; height: auto; margin-bottom: 12px; }}
            .header h1 {{ color: #ffffff; margin: 0; font-size: 22px; font-weight: 600; letter-spacing: 0.5px; }}
            .header p {{ color: #e1f0fa; margin: 5px 0 0 0; font-size: 14px; }}

            .content {{ padding: 28px 24px; }}
            .welcome-text {{ font-size: 16px; line-height: 1.5; color: #4a5568; margin-top: 0; margin-bottom: 24px; }}
            .welcome-text strong {{ color: #0f4c81; }}

            .section-title {{ font-size: 16px; font-weight: 700; color: #0f4c81; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px; border-bottom: 2px solid #edf2f7; padding-bottom: 6px; }}
            
            .stat-table {{ width: 100%; margin-bottom: 24px; }}
            .stat-card {{ background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 14px; text-align: center; width: 31%; }}
            .stat-card-4 {{ background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px 8px; text-align: center; width: 23%; }}
            
            .stat-value {{ font-size: 20px; font-weight: 700; color: #1d72b8; margin-bottom: 2px; }}
            .stat-label {{ font-size: 11px; color: #64748b; text-transform: uppercase; font-weight: 600; }}
            
            .text-success {{ color: #10b981; }}
            .text-warning {{ color: #f59e0b; }}
            .text-danger {{ color: #ef4444; }}

            .financial-table {{ width: 100%; margin-bottom: 28px; background-color: #f8fafc; border-radius: 6px; border-collapse: separate !important; border: 1px solid #e2e8f0; }}
            .financial-table td {{ padding: 12px 16px; font-size: 14px; border-bottom: 1px solid #edf2f7; }}
            .financial-table tr:last-child td {{ border-bottom: none; }}
            .financial-label {{ color: #4a5568; font-weight: 500; }}
            .financial-value {{ text-align: right; font-weight: 600; color: #1e293b; }}
            .financial-total {{ background-color: #e0f2fe; }}
            .financial-total td {{ color: #0369a1; font-size: 15px; font-weight: 700; }}
            .debt-total {{ background-color: #ffedd5; }}
            .debt-total td {{ color: #c2410c; font-size: 15px; font-weight: 700; }}

            .btn-container {{ text-align: center; margin: 28px 0 12px 0; }}
            .btn {{ background-color: #1d72b8; color: #ffffff !important; padding: 12px 28px; text-decoration: none; font-weight: 600; font-size: 14px; border-radius: 5px; display: inline-block; }}

            .footer {{ background-color: #f1f5f9; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0; }}
            .footer p {{ margin: 0; font-size: 12px; color: #94a3b8; line-height: 1.5; }}
            .footer .powered-by {{ font-size: 13px; color: #64748b; font-weight: 600; margin-top: 6px; }}
            .footer a {{ color: #1d72b8; text-decoration: none; }}
        </style>
    </head>
    <body>

        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f4f6f9; padding: 20px 0;">
            <tr>
                <td>
                    <div class="email-container">
                        
                        <!-- ENCABEZADO -->
                        <div class="header">
                            <img src="https://denty.cloud/img/logo.webp?v=1.1" alt="Logo Denty" class="logo">
                            <h1>Resumen Semanal de Desempeño</h1>
                            <p>Período: {start_str} - {end_str}</p>
                        </div>

                        <!-- CONTENIDO -->
                        <div class="content">
                            <p class="welcome-text">
                                Hola, <strong>{company}</strong>.<br>
                                Aquí tienes el desglose y las métricas clave de la actividad de tu clínica correspondiente a la última semana.
                            </p>

                            <!-- SECCIÓN VENTAS (CANTIDADES) -->
                            <div class="section-title">Control de Ventas</div>
                            <table class="stat-table" cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td class="stat-card">
                                        <div class="stat-value">{total_sales}</div>
                                        <div class="stat-label">Totales</div>
                                    </td>
                                    <td width="3%">&nbsp;</td>
                                    <td class="stat-card">
                                        <div class="stat-value text-success">{sales_paid}</div>
                                        <div class="stat-label">Pagadas</div>
                                    </td>
                                    <td width="3%">&nbsp;</td>
                                    <td class="stat-card">
                                        <div class="stat-value text-warning">{sales_pending}</div>
                                        <div class="stat-label">Pendientes</div>
                                    </td>
                                </tr>
                            </table>


                            <!-- SECCIÓN FINANCIERA (DINERO) -->
                            <div class="section-title">Resumen Financiero</div>
                            <table class="financial-table" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td class="financial-label">Total de Ingresos</td>
                                    <td class="financial-value">{total_income}</td>
                                </tr>
                                <tr>
                                    <td class="financial-label">Total de gastos</td>
                                    <td class="financial-value text-success">{total_expense}</td>
                                </tr>
                                <tr class="financial-total">
                                    <td class="financial-label">Balance</td>
                                    <td class="financial-value">{balance}</td>
                                </tr>
                            </table>

                            <table class="stat-table" cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td class="stat-card-4">
                                        <div class="stat-value">{cash}</div>
                                        <div class="stat-label">Efectivo</div>
                                    </td>
                                    <td width="2%">&nbsp;</td>
                                    <td class="stat-card-4">
                                        <div class="stat-value">{card}</div>
                                        <div class="stat-label">Tarjetas</div>
                                    </td>
                                    <td width="2%">&nbsp;</td>
                                    <td class="stat-card-4">
                                        <div class="stat-value">{transfer}</div>
                                        <div class="stat-label">Transferencia</div>
                                    </td>
                                    <td width="2%">&nbsp;</td>
                                    <td class="stat-card-4">
                                        <div class="stat-value">{terminal}</div>
                                        <div class="stat-label">Terminal</div>
                                    </td>
                                    <td width="2%">&nbsp;</td>
                                    <td class="stat-card-4">
                                        <div class="stat-value text-danger">{change}</div>
                                        <div class="stat-label">Cambio</div>
                                    </td>
                                </tr>
                            </table>

                            <table class="financial-table" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td class="financial-label">Ingresos Totales Generados</td>
                                    <td class="financial-value">{money_generated_str}</td>
                                </tr>
                                <tr>
                                    <td class="financial-label">Monto Total Pagado</td>
                                    <td class="financial-value text-success">{money_paid_str}</td>
                                </tr>
                                <tr class="debt-total">
                                    <td class="financial-label">Balance Pendiente por Cobrar</td>
                                    <td class="financial-value">{money_pending_str}</td>
                                </tr>
                            </table>

                            <!-- SECCIÓN AGENDA / CITAS -->
                            <div class="section-title">Estado de la Agenda</div>
                            <table class="stat-table" cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td class="stat-card-4">
                                        <div class="stat-value">{total_app}</div>
                                        <div class="stat-label">Citas</div>
                                    </td>
                                    <td width="2%">&nbsp;</td>
                                    <td class="stat-card-4">
                                        <div class="stat-value text-success">{completed_app}</div>
                                        <div class="stat-label">Atendidas</div>
                                    </td>
                                    <td width="2%">&nbsp;</td>
                                    <td class="stat-card-4">
                                        <div class="stat-value text-warning">{pending_app}</div>
                                        <div class="stat-label">Pendientes</div>
                                    </td>
                                    <td width="2%">&nbsp;</td>
                                    <td class="stat-card-4">
                                        <div class="stat-value text-danger">{cancelled_app}</div>
                                        <div class="stat-label">Canceladas</div>
                                    </td>
                                </tr>
                            </table>
                            
                            {no_show_alert}

                            <!-- BOTÓN AL DASHBOARD -->
                            <div class="btn-container">
                                <a href="https://app.denty.cloud" class="btn" target="_blank">Ir al Dashboard Completo</a>
                            </div>
                        </div>

                        <!-- PIE DE PÁGINA -->
                        <div class="footer">
                            <p>Recibiste este correo automático porque estás registrado como administrador en nuestra plataforma.</p>
                            <p>Por favor, no respondas directamente a este mensaje.</p>
                            <div class="powered-by">powered by <a href="https://denty.cloud" target="_blank">denty.cloud</a></div>
                        </div>

                    </div>
                </td>
            </tr>
        </table>

    </body>
    </html>
    """
    return html_content

@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def send_weekly_report_email(email_to, company_name, html_content):
    subject = f"📊 Reporte semanal de {company_name}"


    email = EmailMultiAlternatives(
        subject=subject,
        body="Tu cliente de correo no soporta HTML, pero tienes una cita pendiente.",
        from_email="plus_recordatorios@gmail.com",
        to=[email_to],
    )

    email.attach_alternative(html_content, "text/html")
    email.send()