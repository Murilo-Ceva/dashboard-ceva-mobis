#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor HTTP para CEVA Dashboard
Serve arquivos estáticos e API de dados dinamicamente
"""

from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import pandas as pd
from pathlib import Path
from io import StringIO
import sys

class CEVARequestHandler(SimpleHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        """Roteia requisições GET para APIs"""
        
        # API: Retorna dados completos do dashboard
        if self.path == '/api/dashboard-data':
            self.serve_json_file('dashboard_data.json')
        
        # API: Retorna apenas TSP
        elif self.path == '/api/tsp-data':
            data = self.load_dashboard_data()
            if data and 'tsp' in data:
                self.send_json(data['tsp'])
            else:
                self.send_error(404, 'Dados não encontrados')
        
        # API: Retorna apenas Dealer
        elif self.path == '/api/dealer-data':
            data = self.load_dashboard_data()
            if data and 'dealer' in data:
                self.send_json(data['dealer'])
            else:
                self.send_error(404, 'Dados não encontrados')
        
        # API: Retorna apenas UF
        elif self.path == '/api/uf-data':
            data = self.load_dashboard_data()
            if data and 'uf' in data:
                self.send_json(data['uf'])
            else:
                self.send_error(404, 'Dados não encontrados')
        
        # API: Retorna apenas Dia
        elif self.path == '/api/dia-data':
            data = self.load_dashboard_data()
            if data and 'dia' in data:
                self.send_json(data['dia'])
            else:
                self.send_error(404, 'Dados não encontrados')
        
        # API: Retorna apenas Ocorrências
        elif self.path == '/api/ocorrencias-data':
            data = self.load_dashboard_data()
            if data and 'ocorrencias' in data:
                self.send_json(data['ocorrencias'])
            else:
                self.send_error(404, 'Dados não encontrados')
        
        # API: Retorna Resumo
        elif self.path == '/api/resumo-data':
            data = self.load_dashboard_data()
            if data and 'resumo' in data:
                self.send_json(data['resumo'])
            else:
                self.send_error(404, 'Dados não encontrados')
        
        else:
            super().do_GET()
    
    def do_POST(self):
        """Roteia requisições POST"""
        
        if self.path == '/api/upload-csv':
            self.handle_csv_upload()
        else:
            super().do_POST()
    
    def load_dashboard_data(self):
        """Carrega dados do JSON"""
        try:
            data_file = Path(__file__).parent / 'dashboard_data.json'
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
        return None
    
    def serve_json_file(self, filename):
        """Serve um arquivo JSON"""
        try:
            filepath = Path(__file__).parent / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.send_json(data)
            else:
                self.send_error(404, f'Arquivo {filename} não encontrado')
        except Exception as e:
            self.send_error(500, str(e))
    
    def send_json(self, data):
        """Envia resposta JSON"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def handle_csv_upload(self):
        """Processa upload de CSV"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')
            if 'boundary=' not in content_type:
                self.send_json({'success': False, 'error': 'Invalid multipart form'})
                return
            
            boundary = content_type.split('boundary=')[1].encode()
            parts = body.split(b'--' + boundary)
            
            csv_data = None
            for part in parts:
                if b'filename=' in part:
                    # Encontra o conteúdo do arquivo
                    try:
                        header_end = part.find(b'\r\n\r\n')
                        if header_end != -1:
                            csv_data = part[header_end + 4:-4].decode('utf-8', errors='ignore')
                    except:
                        pass
            
            if csv_data:
                # Processa CSV com pandas
                df = pd.read_csv(StringIO(csv_data), encoding='utf-8')
                
                # Reexecuta o parser
                sys.path.insert(0, str(Path(__file__).parent))
                from parse_base_otd import (
                    gerar_dados_tsp, gerar_dados_dealer, 
                    gerar_dados_uf, gerar_dados_dia, 
                    gerar_dados_ocorrencias, gerar_resumo_geral
                )
                
                # Calcula OTD
                df['no_prazo'] = df['Status'].str.contains('No Prazo', case=False, na=False)
                otd_geral = (df['no_prazo'].sum() / len(df) * 100) if len(df) > 0 else 0
                
                # Gera agregados
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
                
                self.send_json({
                    'success': True,
                    'message': f'✅ CSV processado! {len(df)} NFs importadas',
                    'data': dados['resumo']
                })
            else:
                self.send_json({'success': False, 'error': 'Nenhum arquivo encontrado'})
        
        except Exception as e:
            print(f"Erro no upload: {e}")
            self.send_json({'success': False, 'error': str(e)})

def run_server():
    server_address = ('', 8001)
    httpd = HTTPServer(server_address, CEVARequestHandler)
    print('🚀 Servidor CEVA Dashboard rodando em http://localhost:8000/')
    print('📊 Acesse: http://localhost:8000/mobis_dashboard.html')
    print('📊 API /api/dashboard-data - Dados completos')
    print('📊 API /api/tsp-data, /api/dealer-data, /api/uf-data, /api/dia-data')
    print('⏹️  Pressione Ctrl+C para parar\n')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
