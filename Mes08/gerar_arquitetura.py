# ==============================================================================
# UNIVERSIDADE ESTADUAL DE FEIRA DE SANTANA (UEFS)
# Projeto de Iniciação Tecnológica (PIBITI/CNPq)
# Plano de Trabalho: Cinto Vestível com IoT para Monitoramento de Idosos
# Orientador: Prof. Dr. Germano Pinto Guedes
# Bolsista: Felipe Amorim do Carmo Silva
# ==============================================================================
# ARQUIVO: Mes08/gerar_arquitetura.py
# DESCRIÇÃO: Gera o diagrama arquitetural completo do estado atual do projeto
#            (Meses 01 a 08 concluídos e convergência para os Meses 09 a 12).
# ==============================================================================

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
CAMINHO_SAIDA = os.path.join(DIRETORIO_ATUAL, "arquitetura_atual_projeto.png")


def desenhar_bloco(ax, x, y, w, h, titulo, linhas_texto, cor_fundo, cor_borda, cor_titulo="#0F172A"):
    caixa = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.010,rounding_size=0.018",
        facecolor=cor_fundo, edgecolor=cor_borda, linewidth=1.6, zorder=2
    )
    ax.add_patch(caixa)

    altura_header = 0.040
    header = FancyBboxPatch(
        (x, y + h - altura_header), w, altura_header,
        boxstyle="round,pad=0.006,rounding_size=0.015",
        facecolor=cor_borda, edgecolor=cor_borda, linewidth=1.0, zorder=3
    )
    ax.add_patch(header)

    ax.text(
        x + w / 2, y + h - altura_header / 2, titulo,
        ha="center", va="center", fontsize=8.6, fontweight="bold",
        color="white", zorder=4
    )

    texto_completo = "\n".join(linhas_texto)
    ax.text(
        x + w / 2, y + (h - altura_header) / 2, texto_completo,
        ha="center", va="center", fontsize=7.8, color=cor_titulo,
        linespacing=1.30, zorder=4
    )


def desenhar_seta(ax, x1, y1, x2, y2, label="", cor="#334155"):
    seta = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>,head_length=6.5,head_width=4.2",
        color=cor, linewidth=1.7, zorder=5
    )
    ax.add_patch(seta)
    if label:
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        ax.text(
            mx, my + 0.015, label,
            ha="center", va="bottom", fontsize=7.3, fontweight="bold",
            color=cor,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.92),
            zorder=6
        )


def gerar_diagrama():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans"],
    })

    fig, ax = plt.subplots(figsize=(14.5, 9.5), dpi=300)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Título geral do diagrama
    ax.text(
        0.5, 0.970,
        "ARQUITETURA ATUAL DO PROJETO — CINTO VESTÍVEL COM IoT E APRENDIZADO DE MÁQUINA",
        ha="center", va="center", fontsize=12.5, fontweight="bold", color="#0F172A"
    )
    ax.text(
        0.5, 0.942,
        "Estado Consolidado no Mês 08: Frente Embarcada IoT (Meses 01, 02, 03 e 06) + Frente de Ciência de Dados e ML (Meses 04, 05, 07 e 08)",
        ha="center", va="center", fontsize=9.2, color="#475569"
    )

    # ==========================================================================
    # CAMADA 1: FRENTE DE HARDWARE EMBARCADO E TELEMETRIA IoT (SUPERIOR)
    # ==========================================================================
    container_hw = FancyBboxPatch(
        (0.02, 0.635), 0.945, 0.280,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        facecolor="#F8FAFC", edgecolor="#1E40AF", linewidth=1.4, linestyle="--", zorder=1
    )
    ax.add_patch(container_hw)
    ax.text(
        0.035, 0.896,
        "FRENTE 1 — PROTÓTIPO FÍSICO, AQUISIÇÃO I2C E TELEMETRIA EM NUVEM (CONCLUÍDO — MESES 01, 02, 03 E 06)",
        ha="left", va="center", fontsize=9.1, fontweight="bold", color="#1E3A8A"
    )

    desenhar_bloco(
        ax, 0.032, 0.655, 0.198, 0.215,
        "1. Sensor MPU-9250 (Mês 01/02)",
        [
            "• Acelerômetro Triaxial (ax, ay, az)",
            "• Conversor ADC 16 bits (1 kHz)",
            "• Filtro DLPF interno (Integrador)",
            "• Calibração de Offset em repouso",
            "• Escala na Bancada: ±2 g por eixo",
            "  (Teto vetorial √12 ≈ 3,464 g)"
        ],
        cor_fundo="#EFF6FF", cor_borda="#1D4ED8"
    )

    desenhar_bloco(
        ax, 0.270, 0.655, 0.215, 0.215,
        "2. ESP32 — Firmware C++ (Mês 02/06)",
        [
            "• Leitura I2C (GPIO 8/9) a 50 Hz (20 ms)",
            "• Cálculo: SVM = √(ax² + ay² + az²)",
            "• Buffer em SRAM: bufferSVM[250]",
            "  (Evita perda durante envio Wi-Fi)",
            "• Empacotamento a cada 5.000 ms",
            "  (~220 amostras contínuas / lote)"
        ],
        cor_fundo="#EFF6FF", cor_borda="#1D4ED8"
    )

    desenhar_bloco(
        ax, 0.525, 0.655, 0.195, 0.215,
        "3. Google Firebase RTDB (Mês 03/06)",
        [
            "• Conexão Wi-Fi / HTTPS (BearSSL)",
            "• Nó: /Sensores/Historico",
            "• Operação assíncrona pushJSON",
            "• 24 Lotes recebidos (100% entrega)",
            "• Persistência JSON em nuvem para",
            "  auditoria e extração remota"
        ],
        cor_fundo="#EFF6FF", cor_borda="#1D4ED8"
    )

    desenhar_bloco(
        ax, 0.760, 0.655, 0.190, 0.215,
        "4. Validação de Bancada (Mês 06)",
        [
            "• Scripts: extrairCsv.py e",
            "  analise_bancada_mes6.py",
            "• Dataset: 5.283 amostras (105,6 s)",
            "• 4 Regimes: Repouso (1,06 g), Marcha,",
            "  ADL Vigorosa e Queda Aguda",
            "• Vale 0,086 g e Pico 3,464 g"
        ],
        cor_fundo="#DBEAFE", cor_borda="#1E3A8A"
    )

    desenhar_seta(ax, 0.230, 0.762, 0.270, 0.762, "I2C 50 Hz")
    desenhar_seta(ax, 0.485, 0.762, 0.525, 0.762, "Wi-Fi 5s")
    desenhar_seta(ax, 0.720, 0.762, 0.760, 0.762, "REST JSON")

    # ==========================================================================
    # CAMADA 2: FRENTE DE PROCESSAMENTO DE SINAIS E ML (INTERMEDIÁRIA)
    # ==========================================================================
    container_ml = FancyBboxPatch(
        (0.02, 0.315), 0.945, 0.280,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        facecolor="#F0FDF4", edgecolor="#15803D", linewidth=1.4, linestyle="--", zorder=1
    )
    ax.add_patch(container_ml)
    ax.text(
        0.035, 0.576,
        "FRENTE 2 — PIPELINE DE PROCESSAMENTO DIGITAL DE SINAIS (DSP) E MACHINE LEARNING (CONCLUÍDO — MESES 04, 05, 07 E 08)",
        ha="left", va="center", fontsize=9.1, fontweight="bold", color="#14532D"
    )

    desenhar_bloco(
        ax, 0.032, 0.335, 0.198, 0.215,
        "5. Base SisFall & EDA (Mês 04)",
        [
            "• 4.505 ensaios (200 Hz, ±16 g)",
            "• 2.707 ADLs (Jovens SA + Idosos SE)",
            "• 1.798 Quedas simuladas",
            "• Conversão: a[g] = AD / 256,0",
            "• Leitor híbrido (.txt / .csv) em",
            "  analise_sisfall.py"
        ],
        cor_fundo="#ECFDF5", cor_borda="#15803D"
    )

    desenhar_bloco(
        ax, 0.270, 0.335, 0.215, 0.215,
        "6. Filtro Butterworth & Unificação (Mês 05)",
        [
            "• Passa-Baixa 4ª Ordem (fc = 5,0 Hz)",
            "• Atenuação de -80 dB/década",
            "• Fase zero bidirecional (filtfilt)",
            "• Remoção de ruído de impacto calcâneo",
            "• Base unificada: 15.858.929 linhas",
            "  (dataset_sisfall_unificado.csv)"
        ],
        cor_fundo="#ECFDF5", cor_borda="#15803D"
    )

    desenhar_bloco(
        ax, 0.525, 0.335, 0.195, 0.215,
        "7. Extração de Atributos (Mês 07)",
        [
            "• Janela de 2,0 s (400 amostras)",
            "  centrada no pico dinâmico",
            "• 16 Features temporais leves:",
            "  SVM_Min, SVM_Max, SVM_PtP,",
            "  SVM_Std, Energy, SMA, Skew,",
            "  Kurt e dispersões por eixo"
        ],
        cor_fundo="#ECFDF5", cor_borda="#15803D"
    )

    desenhar_bloco(
        ax, 0.760, 0.335, 0.190, 0.215,
        "8. Validação 10-Fold (Mês 07/08)",
        [
            "• Stratified 10-Fold Cross-Validation",
            "• SVM (RBF, C=10): Acc 99,71%,",
            "  F1-Score 99,64% (2 FP / 2.707 ADLs)",
            "• Random Forest (100 árv.): Acc",
            "  99,49%, F1-Score 99,36% (4 FP)",
            "• Meta superada (> 90% F1-Score)"
        ],
        cor_fundo="#DCFCE7", cor_borda="#166534"
    )

    desenhar_seta(ax, 0.230, 0.442, 0.270, 0.442, "AD / 256")
    desenhar_seta(ax, 0.485, 0.442, 0.525, 0.442, "Sinal Limpo")
    desenhar_seta(ax, 0.720, 0.442, 0.760, 0.442, "16 Features")

    # ==========================================================================
    # CAMADA 3: CONVERGÊNCIA E PRÓXIMAS ETAPAS (INFERIOR — MESES 09 A 12)
    # ==========================================================================
    container_conv = FancyBboxPatch(
        (0.02, 0.025), 0.945, 0.210,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        facecolor="#FFFBEB", edgecolor="#B45309", linewidth=1.5, zorder=1
    )
    ax.add_patch(container_conv)
    ax.text(
        0.035, 0.214,
        "ETAPA DE CONVERGÊNCIA — INTEGRAÇÃO EMBARCADA TINYML E VALIDAÇÃO NO CINTO VESTÍVEL (PRÓXIMOS PASSOS — MESES 09 A 12)",
        ha="left", va="center", fontsize=9.1, fontweight="bold", color="#92400E"
    )

    desenhar_bloco(
        ax, 0.035, 0.042, 0.435, 0.148,
        "9. Ajustes de Escala e Embarque TinyML no ESP32 (Meses 09 e 10)",
        [
            "• Ajuste do registrador ACCEL_CONFIG do MPU-9250 para ±8 g / ±16 g (superando o teto de 3,464 g visto no Mês 06)",
            "• Portabilidade do classificador validado no Mês 08 (regras da Random Forest / hiperplano SVM em C++) para a Flash",
            "• Cálculo embarcado das 16 features sobre o buffer de 2,0 s e inferência local em tempo real no microcontrolador"
        ],
        cor_fundo="#FEF3C7", cor_borda="#B45309"
    )

    desenhar_bloco(
        ax, 0.520, 0.042, 0.430, 0.148,
        "10. Integração no Cinto Vestível, Alertas e Escrita Final (Meses 10 a 12)",
        [
            "• Encapsulamento do conjunto ESP32 + MPU-9250 + Bateria LiPo 3,7 V no cinto posicionado junto à cintura",
            "• Transmissão imediata de alerta prioritário ao Firebase RTDB e sinalização local ao detectar queda (Classe 1)",
            "• Aferição da latência de resposta e elaboração do Relatório Técnico Final PIBITI/CNPq e artigo científico"
        ],
        cor_fundo="#FEF3C7", cor_borda="#B45309"
    )

    desenhar_seta(ax, 0.470, 0.116, 0.520, 0.116, "Cinto Integrado", cor="#92400E")

    # ==========================================================================
    # CONECTORES ORTOGONAIS LIMPOS (SEM CRUZAR NENHUM BLOCO OU TEXTO)
    # ==========================================================================
    # 1. Trilha azul: sai à direita do Bloco 4 (x=0.950, y=0.762), desce pelo canal externo direito (x=0.984)
    #    até o corredor horizontal (y=0.285), caminha até x=0.250 e aponta para o topo da Etapa de Convergência (y=0.235)
    ax.plot([0.950, 0.984, 0.984, 0.250], [0.762, 0.762, 0.285, 0.285], color="#1E3A8A", linewidth=1.8, linestyle="-", zorder=5)
    seta_hw = FancyArrowPatch(
        (0.250, 0.285), (0.250, 0.235),
        arrowstyle="-|>,head_length=6.5,head_width=4.5",
        color="#1E3A8A", linewidth=1.8, zorder=5
    )
    ax.add_patch(seta_hw)
    ax.text(
        0.250, 0.289,
        "Insumos da Frente 1: Hardware + Buffer 50 Hz + Diagnóstico de Escala (Mês 06)",
        ha="center", va="bottom", fontsize=7.6, fontweight="bold", color="#1E3A8A",
        bbox=dict(boxstyle="round,pad=0.2", fc="#EFF6FF", ec="#1E3A8A", lw=0.9), zorder=6
    )

    # 2. Trilha verde: sai da base do Bloco 8 (x=0.855, y=0.335), desce até y=0.268,
    #    caminha até x=0.720 e aponta para o topo da Etapa de Convergência (y=0.235)
    ax.plot([0.855, 0.855, 0.720], [0.335, 0.268, 0.268], color="#166534", linewidth=1.8, linestyle="-", zorder=5)
    seta_ml = FancyArrowPatch(
        (0.720, 0.268), (0.720, 0.235),
        arrowstyle="-|>,head_length=6.5,head_width=4.5",
        color="#166534", linewidth=1.8, zorder=5
    )
    ax.add_patch(seta_ml)
    ax.text(
        0.720, 0.272,
        "Insumos da Frente 2: 16 Features + Modelos SVM (99,64% F1) e RF (99,36% F1) (Mês 08)",
        ha="center", va="bottom", fontsize=7.6, fontweight="bold", color="#166534",
        bbox=dict(boxstyle="round,pad=0.2", fc="#DCFCE7", ec="#166534", lw=0.9), zorder=6
    )

    plt.tight_layout(pad=0.4)
    plt.savefig(CAMINHO_SAIDA, dpi=300)
    plt.close(fig)
    print(f"[OK] Diagrama de arquitetura salvo em: {CAMINHO_SAIDA}")


if __name__ == "__main__":
    gerar_diagrama()
