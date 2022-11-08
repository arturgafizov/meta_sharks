from datetime import datetime
from pathlib import Path

import xlwt
from django.http import HttpResponse


class ExcelFileOperation:

    date_format = '%d.%m.%Y'

    def __init__(self, filename: str, titles: list[tuple], data: dict, date_format: str = None):
        self.filename = Path(filename)
        self.filename.parent.mkdir(exist_ok=True, parents=True)
        self.filename.touch(exist_ok=True)
        self.date_format = date_format or self.date_format
        self.titles = titles
        self.data = data

    def get_filename(self) -> str:
        """If you need to generate a filename dynamically, override this method"""
        return self.filename

    def xcl_response(self):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{datetime.now()}-{self.get_filename()}"'
        return response

    def xcl_export(self):
        header_font = xlwt.Font()
        header_font.name = 'Arial'
        header_font.bold = True

        header_style = xlwt.XFStyle()
        header_style.font = header_font

        response = self.xcl_response()
        self.wb = xlwt.Workbook(encoding='UTF-8')
        self.ws = self.wb.add_sheet("Python Sheet 1", cell_overwrite_ok=True)

        for ind, val in enumerate(self.titles):
            self.ws.write(0, ind, val[0].capitalize(), header_style)
            self.ws.col(ind).width = val[1]
        row_nom = 0
        row_nom_gr = 0
        for key, val in self.data.items():
            for item in val:
                if key == 'directions':
                    row_nom += 1
                    self.ws.write(row_nom, 0, str(item), header_style)
                if key == 'groups_date':
                    row_nom_gr += 1
                    self.ws.write(row_nom_gr, 1, str(item), header_style)
        self.wb.save(response)
        self.wb.save(f'{self.filename}')
        return response
