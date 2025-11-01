"""
Implementación de Inversión de Dependencias (Dependency Injection)
para la generación de reportes en diferentes formatos.

Interfaz base y dos implementaciones concretas: PDF y Excel.
"""
from abc import ABC, abstractmethod
from django.http import HttpResponse
from django.db.models import QuerySet
from datetime import date
import logging

logger = logging.getLogger(__name__)


class ReportGenerator(ABC):
    """
    Interfaz base para generadores de reportes (Inversión de Dependencias).
    Define el contrato que deben implementar todas las clases de generación de reportes.
    """
    
    @abstractmethod
    def generate(self, queryset: QuerySet, filename: str, **kwargs) -> HttpResponse:
        """
        Genera un reporte a partir de un queryset.
        
        Args:
            queryset: QuerySet de transacciones a incluir en el reporte
            filename: Nombre del archivo para el reporte
            **kwargs: Argumentos adicionales específicos de cada implementación
        
        Returns:
            HttpResponse con el reporte generado
        """
        pass
    
    @abstractmethod
    def get_content_type(self) -> str:
        """
        Retorna el content type MIME del formato de reporte.
        
        Returns:
            String con el content type (ej: 'application/pdf', 'application/vnd.ms-excel')
        """
        pass


class PDFReportGenerator(ReportGenerator):
    """
    Implementación concreta para generar reportes en formato PDF.
    Usa reportlab para generar PDFs.
    """
    
    def generate(self, queryset: QuerySet, filename: str, **kwargs) -> HttpResponse:
        """Genera un reporte en formato PDF."""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from io import BytesIO
            from django.utils import timezone
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            
            # Estilos
            styles = getSampleStyleSheet()
            
            # Título
            title = Paragraph("Reporte de Transacciones Financieras", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 0.2*inch))
            
            # Información de fecha
            date_info = Paragraph(f"Generado el: {timezone.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal'])
            elements.append(date_info)
            elements.append(Spacer(1, 0.2*inch))
            
            # Encabezados de tabla
            data = [['Fecha', 'Tipo', 'Descripción', 'Monto', 'Categoría']]
            
            # Datos de transacciones
            total_income = 0
            total_expenses = 0
            
            for transaction in queryset:
                row = [
                    transaction.date.strftime('%d/%m/%Y'),
                    transaction.get_transaction_type_display(),
                    transaction.description[:30] if transaction.description else '-',
                    f"${transaction.amount:.2f}",
                    transaction.category.name if transaction.category else '-'
                ]
                data.append(row)
                
                if transaction.transaction_type == 'income':
                    total_income += float(transaction.amount)
                else:
                    total_expenses += float(transaction.amount)
            
            # Agregar totales
            data.append(['', '', 'TOTAL INGRESOS', f"${total_income:.2f}", ''])
            data.append(['', '', 'TOTAL GASTOS', f"${total_expenses:.2f}", ''])
            data.append(['', '', 'BALANCE', f"${total_income - total_expenses:.2f}", ''])
            
            # Crear tabla
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -4), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            
            elements.append(table)
            
            # Generar PDF
            doc.build(elements)
            buffer.seek(0)
            
            response = HttpResponse(buffer.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
            return response
            
        except ImportError:
            logger.error("reportlab no está instalado. Instalar con: pip install reportlab")
            return HttpResponse(
                "Error: reportlab no está instalado. Instalar con: pip install reportlab",
                status=500
            )
        except Exception as e:
            logger.error(f"Error al generar PDF: {str(e)}")
            return HttpResponse(f"Error al generar PDF: {str(e)}", status=500)
    
    def get_content_type(self) -> str:
        return 'application/pdf'


class ExcelReportGenerator(ReportGenerator):
    """
    Implementación concreta para generar reportes en formato Excel.
    Usa openpyxl o pandas para generar archivos Excel.
    """
    
    def generate(self, queryset: QuerySet, filename: str, **kwargs) -> HttpResponse:
        """Genera un reporte en formato Excel."""
        try:
            import pandas as pd
            from io import BytesIO
            from django.utils import timezone
            
            # Preparar datos
            data = []
            total_income = 0
            total_expenses = 0
            
            for transaction in queryset:
                row = {
                    'Fecha': transaction.date.strftime('%d/%m/%Y'),
                    'Tipo': transaction.get_transaction_type_display(),
                    'Descripción': transaction.description or '-',
                    'Monto': float(transaction.amount),
                    'Categoría': transaction.category.name if transaction.category else '-',
                }
                data.append(row)
                
                if transaction.transaction_type == 'income':
                    total_income += float(transaction.amount)
                else:
                    total_expenses += float(transaction.amount)
            
            # Crear DataFrame
            df = pd.DataFrame(data)
            
            # Agregar fila de totales
            totals_row = pd.DataFrame([{
                'Fecha': '',
                'Tipo': '',
                'Descripción': 'TOTAL INGRESOS',
                'Monto': total_income,
                'Categoría': ''
            }])
            df = pd.concat([df, totals_row], ignore_index=True)
            
            totals_row = pd.DataFrame([{
                'Fecha': '',
                'Tipo': '',
                'Descripción': 'TOTAL GASTOS',
                'Monto': total_expenses,
                'Categoría': ''
            }])
            df = pd.concat([df, totals_row], ignore_index=True)
            
            totals_row = pd.DataFrame([{
                'Fecha': '',
                'Tipo': '',
                'Descripción': 'BALANCE',
                'Monto': total_income - total_expenses,
                'Categoría': ''
            }])
            df = pd.concat([df, totals_row], ignore_index=True)
            
            # Generar Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Transacciones')
                
                # Obtener la hoja para formatear
                worksheet = writer.sheets['Transacciones']
                
                # Ajustar ancho de columnas
                worksheet.column_dimensions['A'].width = 12
                worksheet.column_dimensions['B'].width = 12
                worksheet.column_dimensions['C'].width = 40
                worksheet.column_dimensions['D'].width = 15
                worksheet.column_dimensions['E'].width = 20
            
            output.seek(0)
            
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
            return response
            
        except ImportError:
            logger.error("pandas/openpyxl no están instalados. Instalar con: pip install pandas openpyxl")
            return HttpResponse(
                "Error: pandas/openpyxl no están instalados",
                status=500
            )
        except Exception as e:
            logger.error(f"Error al generar Excel: {str(e)}")
            return HttpResponse(f"Error al generar Excel: {str(e)}", status=500)
    
    def get_content_type(self) -> str:
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


class ReportGeneratorFactory:
    """
    Factory para obtener la instancia correcta del generador de reportes.
    Implementa el patrón Factory para la Inversión de Dependencias.
    """
    
    @staticmethod
    def get_generator(format_type: str) -> ReportGenerator:
        """
        Retorna una instancia del generador de reportes según el formato.
        
        Args:
            format_type: Tipo de formato ('pdf' o 'excel')
        
        Returns:
            Instancia de ReportGenerator
        
        Raises:
            ValueError: Si el formato no es soportado
        """
        format_type = format_type.lower()
        
        if format_type == 'pdf':
            return PDFReportGenerator()
        elif format_type == 'excel':
            return ExcelReportGenerator()
        else:
            raise ValueError(f"Formato no soportado: {format_type}")

