#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser para converter CSV Indicador Visão CEVA para formato JSON usável no dashboard
"""

import csv
import json
import sys
from pathlib import Path

def parse_ceva_csv(csv_file):
    """
    Lê CSV com encoding latin-1 e extrai dados de transportadoras
    Estrutura: Header em linhas 0-4, dados a partir da linha 5
    """
    
    with open(csv_file, 'r', encoding='latin-1') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    # Headers estão nas primeiras 5 linhas
    # Dados começam na linha 5 (índice 5)
    
    tsp_data = []
    
    # Procura pelas linhas de transportadora
    # Formato: cada linha tem: [?, ?, ?, ?, ID, NOME_TSP, ...]
    for i in range(5, len(rows)):
        row = rows[i]
        
        # Verifica se é uma linha com dados (começa com ID numérico)
        if len(row) < 7:
            continue
            
        try:
            row_id = row[4].strip() if row[4] else None
            tsp_name = row[5].strip() if row[5] else None
            
            if not tsp_name or tsp_name == '':
                continue
            
            # Coluna 6: Entregue no Prazo (Volume - Padrão Mobis)
            # Coluna 7: Entregue Fora do Prazo (Volume - Padrão Mobis)
            # Coluna 8: Total (Volume - Padrão Mobis)
            # Coluna 9: OTD % (Volume - Padrão Mobis)
            
            try:
                no_prazo = int(row[6].replace(',', '').replace('.', '').strip() or 0)
            except (ValueError, IndexError):
                no_prazo = 0
            
            try:
                fora = int(row[7].replace(',', '').replace('.', '').strip() or 0)
            except (ValueError, IndexError):
                fora = 0
            
            try:
                total = int(row[8].replace(',', '').replace('.', '').strip() or 0)
            except (ValueError, IndexError):
                total = no_prazo + fora if no_prazo + fora > 0 else 0
            
            # OTD % está na coluna 9, é um percentual
            try:
                otd_str = row[9].replace('%', '').strip()
                otd = float(otd_str) if otd_str else 0.0
            except (ValueError, IndexError):
                otd = 0.0
            
            if total > 0:  # Só inclui se tem dados
                tsp_data.append({
                    'tsp': tsp_name,
                    'no_prazo': no_prazo,
                    'fora': fora,
                    'total': total,
                    'otd': round(otd, 1)
                })
                print(f"✓ {tsp_name}: {no_prazo} no prazo, {fora} fora, OTD {otd}%")
        
        except Exception as e:
            continue
    
    return tsp_data

def generate_js_code(tsp_data):
    """Gera código JavaScript para inserir no dashboard"""
    
    js_code = "// Dados parseados do CSV\n"
    js_code += "const tspData = [\n"
    
    for tsp in tsp_data:
        js_code += f"  {{tsp:'{tsp['tsp']}', no_prazo:{tsp['no_prazo']}, fora:{tsp['fora']}, total:{tsp['total']}, otd:{tsp['otd']}}},\n"
    
    js_code += "];\n"
    
    return js_code

if __name__ == '__main__':
    csv_path = Path(__file__).parent / '(M) Indicador Visão Mobis V1.csv'
    
    if not csv_path.exists():
        print(f"❌ Arquivo não encontrado: {csv_path}")
        sys.exit(1)
    
    print(f"📖 Lendo: {csv_path}")
    print("-" * 60)
    
    tsp_data = parse_ceva_csv(csv_path)
    
    print("-" * 60)
    print(f"✅ Total de transportadoras encontradas: {len(tsp_data)}")
    
    # Gera JSON
    json_output = json.dumps(tsp_data, ensure_ascii=False, indent=2)
    json_file = Path(__file__).parent / 'tsp_data.json'
    
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(json_output)
    
    print(f"💾 JSON salvo em: {json_file}")
    
    # Gera JavaScript
    js_code = generate_js_code(tsp_data)
    js_file = Path(__file__).parent / 'tsp_data.js'
    
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    print(f"💾 JavaScript salvo em: {js_file}")
    
    print("\n📋 Dados extraídos:")
    print(json_output)
