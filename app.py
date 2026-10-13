import os
import pandas as pd
import numpy as np
import yfinance as yf

# Lista de activos a monitorear (puedes agregar o quitar los que quieras, ej: CEDEARs con .BA)
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "SPY", "GGAL.BA", "YPF"]

def calcular_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analizar_mercado():
    resultados = []
    for ticker in TICKERS:
        try:
            df = yf.download(ticker, period="6mo", interval="1d", progress=False)
            if df.empty or len(df) < 50:
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['RSI'] = calcular_rsi(df['Close'], window=14)
            
            precio = float(df['Close'].iloc[-1])
            sma_50 = float(df['SMA_50'].iloc[-1])
            rsi = float(df['RSI'].iloc[-1])
            
            # Criterio estricto de momento alcista
            es_alcista = precio > sma_50 and 55 <= rsi <= 75
            
            resultados.append({
                "ticker": ticker,
                "precio": round(precio, 2),
                "sma_50": round(sma_50, 2),
                "rsi": round(rsi, 2),
                "estado": "ALCISTA 🚀" if es_alcista else "Neutral / Lateral ➖",
                "clase_badge": "badge-bull" if es_alcista else "badge-neutral"
            })
        except Exception as e:
            print(f"Error con {ticker}: {e}")
    return resultados

def generar_html(datos):
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panel de Acciones Alcistas</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 40px; }}
        .container {{ max-width: 900px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }}
        h1 {{ margin-top: 0; color: #38bdf8; font-size: 24px; }}
        p.subtitle {{ color: #94a3b8; margin-bottom: 25px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 14px 16px; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background-color: #0f172a; color: #cbd5e1; font-weight: 600; text-transform: uppercase; font-size: 12px; }}
        tr:hover {{ background-color: #273548; }}
        .badge-bull {{ background-color: #065f46; color: #34d399; padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 12px; }}
        .badge-neutral {{ background-color: #334155; color: #94a3b8; padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 12px; }}
        .footer {{ margin-top: 25px; text-align: right; font-size: 12px; color: #64748b; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Dashboard de Momento Alcista</h1>
        <p class="subtitle">Análisis técnico automatizado (Precio > SMA 50 & RSI 55-75)</p>
        <table>
            <thead>
                <tr>
                    <th>Activo</th>
                    <th>Precio Actual</th>
                    <th>SMA 50</th>
                    <th>RSI (14)</th>
                    <th>Estado de Mercado</th>
                </tr>
            </thead>
            <tbody>"""

    for item in datos:
        html_content += f"""
                <tr>
                    <td><strong>{item['ticker']}</strong></td>
                    <td>${item['precio']}</td>
                    <td>${item['sma_50']}</td>
                    <td>{item['rsi']}</td>
                    <td><span class="{item['clase_badge']}">{item['estado']}</span></td>
                </tr>"""

    html_content += f"""
            </tbody>
        </table>
        <div class="footer">Actualizado automáticamente mediante script local.</div>
    </div>
</body>
</html>
"""
    with open("dashboard_acciones.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("¡Listo! Archivo 'dashboard_acciones.html' generado con éxito.")

if __name__ == "__main__":
    print("Analizando mercado en segundo plano...")
    datos_mercado = analizar_mercado()
    generar_html(datos_mercado)