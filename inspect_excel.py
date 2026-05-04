import pandas as pd
from pathlib import Path
path = Path(r'c:\Users\AnjosM\Downloads\Dashboard - CEVA\(M) Indicador Visão Mobis V1.2 2.xlsx')
output = []
output.append(f'exists {path.exists()}')
xls = pd.ExcelFile(path)
output.append('sheets ' + str(xls.sheet_names))
for sheet in xls.sheet_names[:5]:
    df = pd.read_excel(path, sheet_name=sheet)
    output.append(f'SHEET {sheet} shape {df.shape}')
    output.append('cols ' + str(df.columns.tolist()))
    output.append('head ' + str(df.head(5).to_dict('records')))
with open(r'c:\Users\AnjosM\Downloads\Dashboard - CEVA\excel_inspect.txt','w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print('done')
