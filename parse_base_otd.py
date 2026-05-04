#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser avançado para BASE OTD
Gera dados agregados para TODAS as páginas do dashboard
"""

import pandas as pd
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def parse_base_otd(csv_file):
    """Lê BASE OTD e retorna DataFrame com ajustes"""
    
    # Lê com encoding latin-1
    df = pd.read_csv(csv_file, encoding='latin-1')
    
    # Limpa nomes de colunas (remove espaços)
    df.columns = df.columns.str.strip()
    
    # Converte Status para booleano
    df['no_prazo'] = df['Status'].str.contains('No Prazo', case=False, na=False)
    
    # Calcula OTD
    total_nfs = len(df)
    nfs_prazo = df['no_prazo'].sum()
    otd_geral = (nfs_prazo / total_nfs * 100) if total_nfs > 0 else 0
    
    print(f"✓ CSV lido: {total_nfs} NFs")
    print(f"✓ No Prazo: {nfs_prazo} ({otd_geral:.1f}%)")
    
    return df, otd_geral

def gerar_dados_tsp(df):
    """Agrega dados por TRANSPORTADORA"""
    
    grupos = df.groupby('TRANSPORTADORA').agg({
        'no_prazo': 'sum',
        'NF': 'count',
        'Qtde. Volumes': 'sum'
    }).rename(columns={'NF': 'total_nfs'})
    
    grupos['fora_prazo'] = grupos['total_nfs'] - grupos['no_prazo']
    grupos['otd'] = (grupos['no_prazo'] / grupos['total_nfs'] * 100).round(1)
    
    result = []
    for tsp_nome, row in grupos.iterrows():
        result.append({
            'tsp': tsp_nome.strip() if isinstance(tsp_nome, str) else tsp_nome,
            'no_prazo': int(row['no_prazo']),
            'fora': int(row['fora_prazo']),
            'total': int(row['total_nfs']),
            'volumes': int(row['Qtde. Volumes']),
            'otd': float(row['otd'])
        })
    
    print(f"\n✓ {len(result)} Transportadoras processadas")
    for r in sorted(result, key=lambda x: x['otd'], reverse=True):
        print(f"  {r['tsp']}: {r['otd']}% ({r['no_prazo']}/{r['total']})")
    
    return result

def gerar_dados_dealer(df):
    """Agrega dados por DEALER"""
    
    grupos = df.groupby('DEALER').agg({
        'no_prazo': 'sum',
        'NF': 'count',
        'UF Destino': 'first',
        'TRANSPORTADORA': 'first'
    }).rename(columns={'NF': 'total_nfs'})
    
    grupos['fora_prazo'] = grupos['total_nfs'] - grupos['no_prazo']
    grupos['otd'] = (grupos['no_prazo'] / grupos['total_nfs'] * 100).round(1)
    
    result = []
    for dealer_id, row in grupos.iterrows():
        if pd.isna(dealer_id) or dealer_id == '#N/D':
            continue
        result.append({
            'dealer_id': str(int(dealer_id)) if not pd.isna(dealer_id) else 'N/A',
            'no_prazo': int(row['no_prazo']),
            'fora': int(row['fora_prazo']),
            'total': int(row['total_nfs']),
            'uf': str(row['UF Destino']).strip() if not pd.isna(row['UF Destino']) else 'XX',
            'tsp': str(row['TRANSPORTADORA']).strip() if not pd.isna(row['TRANSPORTADORA']) else 'N/A',
            'otd': float(row['otd'])
        })
    
    print(f"✓ {len(result)} Dealers processados")
    return sorted(result, key=lambda x: x['otd'], reverse=True)[:50]  # Top 50

def gerar_dados_uf(df):
    """Agrega dados por UF"""
    
    grupos = df.groupby('UF Destino').agg({
        'no_prazo': 'sum',
        'NF': 'count',
        'Qtde. Volumes': 'sum'
    }).rename(columns={'NF': 'total_nfs'})
    
    grupos['fora_prazo'] = grupos['total_nfs'] - grupos['no_prazo']
    grupos['otd'] = (grupos['no_prazo'] / grupos['total_nfs'] * 100).round(1)
    
    result = []
    for uf, row in grupos.iterrows():
        result.append({
            'uf': str(uf).strip(),
            'no_prazo': int(row['no_prazo']),
            'fora': int(row['fora_prazo']),
            'total': int(row['total_nfs']),
            'volumes': int(row['Qtde. Volumes']),
            'otd': float(row['otd'])
        })
    
    print(f"✓ {len(result)} UFs processadas")
    return sorted(result, key=lambda x: x['otd'], reverse=True)

def gerar_dados_dia(df):
    """Agrega dados por Dia"""
    
    grupos = df.groupby('Dia_Previsao').agg({
        'no_prazo': 'sum',
        'NF': 'count'
    }).rename(columns={'NF': 'total_nfs'})
    
    grupos['fora_prazo'] = grupos['total_nfs'] - grupos['no_prazo']
    grupos['otd'] = (grupos['no_prazo'] / grupos['total_nfs'] * 100).round(1)
    
    result = []
    for dia, row in grupos.iterrows():
        if pd.isna(dia):
            continue
        result.append({
            'dia': int(dia),
            'no_prazo': int(row['no_prazo']),
            'fora': int(row['fora_prazo']),
            'total': int(row['total_nfs']),
            'otd': float(row['otd'])
        })
    
    print(f"✓ {len(result)} Dias processados")
    return sorted(result, key=lambda x: x['dia'])

def gerar_dados_ocorrencias(df):
    """Agrega dados de Ocorrências"""
    
    # Filtra NFs com ocorrências
    df_ocorr = df[df['Ocorrência Entrega'].notna() & (df['Ocorrência Entrega'] != '')]
    
    grupos = df_ocorr['Ocorrência Entrega'].value_counts()
    
    result = []
    for ocorrencia, count in grupos.items():
        result.append({
            'ocorrencia': str(ocorrencia).strip(),
            'count': int(count)
        })
    
    print(f"✓ {len(result)} Tipos de Ocorrência")
    for r in result[:10]:
        print(f"  {r['ocorrencia']}: {r['count']}")
    
    return result

def gerar_resumo_geral(df, otd_geral):
    """Gera resumo geral"""
    
    total_nfs = len(df)
    no_prazo = df['no_prazo'].sum()
    fora_prazo = total_nfs - no_prazo
    volumes_total = df['Qtde. Volumes'].sum()
    
    return {
        'total_nfs': int(total_nfs),
        'no_prazo': int(no_prazo),
        'fora_prazo': int(fora_prazo),
        'volumes': int(volumes_total),
        'otd': round(otd_geral, 1),
        'data_processamento': datetime.now().strftime('%d/%m/%Y %H:%M')
    }

if __name__ == '__main__':
    csv_path = Path(__file__).parent / 'BASE OTD.csv'
    
    if not csv_path.exists():
        print(f"❌ Arquivo não encontrado: {csv_path}")
        exit(1)
    
    print(f"📖 Lendo BASE OTD...")
    print("-" * 60)
    
    # Processa CSV
    df, otd_geral = parse_base_otd(csv_path)
    
    # Gera todos os agregados
    print("\n🔄 Gerando agregados...")
    print("-" * 60)
    
    dados = {
        'resumo': gerar_resumo_geral(df, otd_geral),
        'tsp': gerar_dados_tsp(df),
        'dealer': gerar_dados_dealer(df),
        'uf': gerar_dados_uf(df),
        'dia': gerar_dados_dia(df),
        'ocorrencias': gerar_dados_ocorrencias(df)
    }
    
    # Salva JSON
    output_file = Path(__file__).parent / 'dashboard_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"✅ Dados salvos em: {output_file}")
    print("=" * 60)
    print(f"\n📊 Resumo Geral:")
    for k, v in dados['resumo'].items():
        print(f"  {k}: {v}")
