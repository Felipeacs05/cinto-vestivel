# ==============================================================================
# UNIVERSIDADE ESTADUAL DE FEIRA DE SANTANA (UEFS)
# Projeto de Iniciação Tecnológica (PIBITI/CNPq)
# Plano de Trabalho: Cinto Vestível com IoT para Monitoramento de Idosos
# Orientador: Prof. Dr. Germano Pinto Guedes
# Bolsista: Felipe Amorim do Carmo Silva
# ==============================================================================
# ARQUIVO: Mes06/analise_bancada_mes6.py
# DESCRIÇÃO: Script automatizado de processamento e visualização científica dos
#            dados reais coletados na bancada física (ESP32 + MPU-9250) via
#            Firebase Realtime Database. Lê o arquivo 'dados_esp32_completos.csv',
#            calcula estatísticas descritivas por regime cinemático, detecta
#            automaticamente vales de queda livre (< 0,5 g) e picos de impacto
#            (> 3,0 g), e gera o gráfico 'validacao_bancada_M6.png'.
# ==============================================================================

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Garante que os caminhos funcionem rodando da raiz ou de dentro da pasta Mes06/
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
CAMINHO_CSV = os.path.join(DIRETORIO_ATUAL, "dados_esp32_completos.csv")
CAMINHO_FIGURA = os.path.join(DIRETORIO_ATUAL, "validacao_bancada_M6.png")

# Taxa de amostragem nominal configurada no firmware do ESP32 (50 Hz -> dt = 0.02 s)
FS_HZ = 50.0
DT_S = 1.0 / FS_HZ


def analisar_e_gerar_grafico():
    if not os.path.exists(CAMINHO_CSV):
        raise FileNotFoundError(
            f"Arquivo '{CAMINHO_CSV}' não encontrado. Execute 'extrairCsv.py' primeiro."
        )

    # 1. Carregamento do dataset real exportado do Firebase
    df = pd.read_csv(CAMINHO_CSV)
    svm = df["SVM"].values.astype(float)
    n_amostras = len(svm)
    n_lotes = df["ID_Lote"].nunique()
    tempo = np.arange(n_amostras) * DT_S

    print("=" * 78)
    print("RELATÓRIO AUTOMÁTICO DE BANCADA — MÊS 06 (ESP32 + MPU-9250 + FIREBASE RTDB)")
    print("=" * 78)
    print(f"Total de Amostras Coletadas : {n_amostras} amostras (@ {FS_HZ:.0f} Hz)")
    print(f"Total de Lotes no Firebase  : {n_lotes} lotes JSON")
    print(f"Duração Total do Ensaio     : {tempo[-1]:.2f} segundos")
    print("-" * 78)

    # 2. Segmentação dos 4 regimes cinemáticos do protocolo experimental de bancada
    # Nota: os primeiros 4,4 s correspondem à acomodação manual inicial do sensor na mesa
    regimes = [
        ("1. Repouso Estático (Estável)", 4.40, 26.60),
        ("2. Oscilação Suave (Caminhada)", 26.60, 53.00),
        ("3. Movimentação Vigorosa (ADL)", 53.00, 75.00),
        ("4. Queda e Choques Agudos", 75.00, tempo[-1] + DT_S),
    ]

    print(
        f"{'Regime Dinâmico':<32} | {'Intervalo (s)':<15} | {'N':<5} | "
        f"{'Média (g)':<9} | {'DP (g)':<7} | {'Mín (g)':<7} | {'Máx (g)':<7}"
    )
    print("-" * 78)

    for nome, t_ini, t_fim in regimes:
        mascara = (tempo >= t_ini) & (tempo < t_fim)
        seg = svm[mascara]
        print(
            f"{nome:<32} | {t_ini:5.2f} - {min(t_fim, tempo[-1]):6.2f}s | {len(seg):<5} | "
            f"{np.mean(seg):<9.3f} | {np.std(seg):<7.3f} | {np.min(seg):<7.3f} | {np.max(seg):<7.3f}"
        )

    print("-" * 78)
    print(
        f"{'Consolidado Global':<32} | {0.0:5.2f} - {tempo[-1]:6.2f}s | {n_amostras:<5} | "
        f"{np.mean(svm):<9.3f} | {np.std(svm):<7.3f} | {np.min(svm):<7.3f} | {np.max(svm):<7.3f}"
    )
    print("=" * 78)

    # 3. Geração automática da figura científica com 2 painéis
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans"],
        "axes.edgecolor": "#333333",
        "axes.linewidth": 0.8,
    })

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8.2), dpi=300)
    fig.patch.set_facecolor("white")

    # --- PAINEL SUPERIOR: Série Temporal Completa (0 a 105,66 s) ---
    ax1.axvspan(0, 26.6, color="#E8F5E9", alpha=0.65, label="1. Repouso Estático (~1,06 g)")
    ax1.axvspan(26.6, 53.0, color="#E3F2FD", alpha=0.65, label="2. Oscilação Suave / Caminhada (0,48 g – 1,94 g)")
    ax1.axvspan(53.0, 75.0, color="#FFF3E0", alpha=0.65, label="3. Movimentação Vigorosa / ADL (até 2,65 g)")
    ax1.axvspan(75.0, tempo[-1], color="#FFEBEE", alpha=0.65, label="4. Ensaios de Queda Livre e Impacto Agudo (até 3,46 g)")

    ax1.plot(
        tempo, svm, color="#1565C0", linewidth=0.95,
        label=f"Magnitude Inercial Resultante SVM ({n_amostras} amostras @ 50 Hz)"
    )
    ax1.axhline(3.0, color="#D32F2F", linestyle="--", linewidth=1.2, label="Limiar Heurístico de Impacto (3,0 g)")
    ax1.axhline(1.0, color="#2E7D32", linestyle=":", linewidth=1.0, label="Gravidade Basal Nominal (1,0 g)")

    # Destaca automaticamente os picos que superaram 3,0 g
    idx_picos = np.where(svm >= 3.0)[0]
    if len(idx_picos) > 0:
        ax1.scatter(
            tempo[idx_picos], svm[idx_picos], color="#B71C1C", s=28, zorder=5,
            label="Picos de Impacto Retidos e Enviados ao Firebase (3,46 g)"
        )

    ax1.set_title(
        f"Validação Experimental de Bancada (ESP32 + MPU-9250) — Série Contínua Sincronizada no Firebase RTDB ({n_lotes} Lotes)",
        fontsize=11.5, fontweight="bold", pad=10
    )
    ax1.set_xlabel("Tempo de Ensaio Contínuo (segundos)", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Magnitude SVM (g)", fontsize=10, fontweight="bold")
    ax1.set_xlim(0, tempo[-1])
    ax1.set_ylim(0, 3.95)
    ax1.grid(True, linestyle=":", alpha=0.5)
    ax1.legend(loc="upper left", fontsize=8.2, ncol=2, framealpha=0.92)

    # --- PAINEL INFERIOR: Zoom na Janela de Quedas e Impactos (74 s a 105,66 s) ---
    t_zoom_ini = 74.0
    mascara_zoom = tempo >= t_zoom_ini
    t_z = tempo[mascara_zoom]
    svm_z = svm[mascara_zoom]

    ax2.plot(
        t_z, svm_z, color="#0D47A1", linewidth=1.15, marker="o", markersize=2.2,
        label="Amostras Individuais (20 ms / 50 Hz)"
    )
    ax2.axhline(3.4641, color="#B71C1C", linestyle="-.", linewidth=1.1,
                label="Teto Físico de Saturação Triaxial ±2 g (√(2²+2²+2²) = 3,464 g)")
    ax2.axhline(3.0, color="#D32F2F", linestyle="--", linewidth=1.1, label="Limiar Crítico de Impacto (3,0 g)")
    ax2.axhline(0.6, color="#F57C00", linestyle="--", linewidth=1.1, label="Limiar de Alívio Gravitacional / Queda Livre (< 0,6 g)")
    ax2.axhline(1.0, color="#2E7D32", linestyle=":", linewidth=0.9)

    # Anotação automática do menor vale de queda livre e do maior pico de impacto
    idx_min_global = int(np.argmin(svm_z))
    t_min_val, svm_min_val = t_z[idx_min_global], svm_z[idx_min_global]
    ax2.scatter([t_min_val], [svm_min_val], color="#E65100", s=55, zorder=6)
    ax2.annotate(
        f"Vale de Queda Livre\n({svm_min_val:.3f} g @ {t_min_val:.2f} s)",
        xy=(t_min_val, svm_min_val),
        xytext=(t_min_val - 6.8, svm_min_val + 0.42),
        arrowprops=dict(arrowstyle="->", color="#E65100", lw=1.2),
        fontsize=8.5, fontweight="bold", color="#E65100",
        bbox=dict(boxstyle="round,pad=0.25", fc="#FFF3E0", ec="#E65100", lw=0.8)
    )

    idx_max_global = int(np.argmax(svm_z))
    t_max_val, svm_max_val = t_z[idx_max_global], svm_z[idx_max_global]
    ax2.scatter([t_max_val], [svm_max_val], color="#B71C1C", s=55, zorder=6)
    ax2.annotate(
        f"Pico de Colisão / Saturação\n({svm_max_val:.3f} g @ {t_max_val:.2f} s)",
        xy=(t_max_val, svm_max_val),
        xytext=(t_max_val - 7.5, svm_max_val - 0.78),
        arrowprops=dict(arrowstyle="->", color="#B71C1C", lw=1.2),
        fontsize=8.5, fontweight="bold", color="#B71C1C",
        bbox=dict(boxstyle="round,pad=0.25", fc="#FFEBEE", ec="#B71C1C", lw=0.8)
    )

    ax2.set_title(
        "Detalhamento da Fase de Impactos (t = 74,0 s a 105,7 s) — Assinatura de Queda Livre Seguida de Pico de Colisão",
        fontsize=11.0, fontweight="bold", pad=10
    )
    ax2.set_xlabel("Tempo (segundos)", fontsize=10, fontweight="bold")
    ax2.set_ylabel("Magnitude SVM (g)", fontsize=10, fontweight="bold")
    ax2.set_xlim(t_zoom_ini, tempo[-1])
    ax2.set_ylim(0, 3.95)
    ax2.grid(True, linestyle=":", alpha=0.5)
    ax2.legend(loc="upper right", fontsize=8.2, framealpha=0.92)

    plt.tight_layout(pad=1.8)
    plt.savefig(CAMINHO_FIGURA, dpi=300)
    plt.close(fig)
    print(f"\n[OK] Gráfico científico gerado automaticamente em: {CAMINHO_FIGURA}")


if __name__ == "__main__":
    analisar_e_gerar_grafico()
