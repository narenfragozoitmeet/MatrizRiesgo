from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from io import BytesIO
from typing import List
from pydantic import BaseModel
from datetime import datetime

class RiskItem(BaseModel):
    categoria: str
    riesgo: str
    descripcion: str
    probabilidad: str
    impacto: str
    nivel_riesgo: str
    mitigacion: str

def generate_risk_matrix_excel(risks: List[RiskItem], document_name: str, summary: str) -> bytes:
    """Generate Excel file with risk matrix"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Matriz de Riesgos"
    
    header_fill = PatternFill(start_color="0A0A0A", end_color="0A0A0A", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    ws.merge_cells('A1:G1')
    title_cell = ws['A1']
    title_cell.value = f"MATRIZ DE RIESGOS LEGALES - {document_name}"
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = Alignment(horizontal='center', vertical='center')
    
    ws.merge_cells('A2:G2')
    date_cell = ws['A2']
    date_cell.value = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    date_cell.alignment = Alignment(horizontal='center')
    
    ws.append([])
    
    headers = ['Categoría', 'Riesgo', 'Descripción', 'Probabilidad', 'Impacto', 'Nivel de Riesgo', 'Mitigación']
    ws.append(headers)
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = border
    
    risk_colors = {
        'Crítico': 'DC2626',
        'Alto': 'EA580C',
        'Medio': 'EAB308',
        'Bajo': '16A34A'
    }
    
    for risk in risks:
        row_data = [
            risk.categoria,
            risk.riesgo,
            risk.descripcion,
            risk.probabilidad,
            risk.impacto,
            risk.nivel_riesgo,
            risk.mitigacion
        ]
        ws.append(row_data)
        
        current_row = ws.max_row
        
        for col_num in range(1, 8):
            cell = ws.cell(row=current_row, column=col_num)
            cell.border = border
            cell.alignment = Alignment(wrap_text=True, vertical='top')
        
        nivel_cell = ws.cell(row=current_row, column=6)
        nivel_color = risk_colors.get(risk.nivel_riesgo, 'A1A1AA')
        nivel_cell.fill = PatternFill(start_color=nivel_color, end_color=nivel_color, fill_type="solid")
        nivel_cell.font = Font(bold=True, color="FFFFFF")
        nivel_cell.alignment = Alignment(horizontal='center', vertical='center')
    
    ws.column_dimensions['A'].width = 18
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 40
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 15
    ws.column_dimensions['G'].width = 45
    
    ws.row_dimensions[1].height = 25
    ws.row_dimensions[4].height = 30
    
    summary_sheet = wb.create_sheet("Resumen Ejecutivo")
    summary_sheet.merge_cells('A1:E1')
    summary_title = summary_sheet['A1']
    summary_title.value = "RESUMEN EJECUTIVO"
    summary_title.font = Font(bold=True, size=14)
    summary_title.alignment = Alignment(horizontal='center')
    
    summary_sheet.append([])
    summary_sheet.merge_cells('A3:E10')
    summary_cell = summary_sheet['A3']
    summary_cell.value = summary
    summary_cell.alignment = Alignment(wrap_text=True, vertical='top')
    
    summary_sheet.append([])
    summary_sheet.append([])
    summary_sheet.append(['Estadísticas:'])
    summary_sheet.cell(row=12, column=1).font = Font(bold=True)
    summary_sheet.append([f'Total de riesgos identificados: {len(risks)}'])
    
    risk_levels = {}
    for risk in risks:
        risk_levels[risk.nivel_riesgo] = risk_levels.get(risk.nivel_riesgo, 0) + 1
    
    for level, count in risk_levels.items():
        summary_sheet.append([f'{level}: {count}'])
    
    summary_sheet.column_dimensions['A'].width = 80
    
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output.read()