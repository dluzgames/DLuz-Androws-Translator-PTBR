# 🎮 DLuz Tradutor & Customizador PT-BR — Tencent Androws Emulator

[![GitHub Release](https://img.shields.io/github/v/release/dluzgames/DLuz-Androws-Translator-PTBR?color=red&logo=github)](https://github.com/dluzgames/DLuz-Androws-Translator-PTBR/releases/latest)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue?logo=windows)](https://github.com/dluzgames/DLuz-Androws-Translator-PTBR)
[![Language](https://img.shields.io/badge/Language-Portugu%C3%AAs%20(Brasil)-green)](https://github.com/dluzgames/DLuz-Androws-Translator-PTBR)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

Ferramenta oficial e automatizada de **tradução completa para Português (PT-BR)**, **calibração de fontes/DPI**, **personalização visual com logo DLuz Games** e **injeção de mapeamento profissional de controles (Keymaps)** para o emulador oficial **Tencent Androws (Tencent MyApp PC)**.

---

## 🌟 Principais Recursos

- 🇧🇷 **100% em Português do Brasil:** Traduz todos os módulos Qt nativos (`Androws`, `AndrowsStore`, `Assistant`) e telas do aplicativo.
- ⚙️ **Painel de Configurações & Loja Traduzidos:** Tradução completa das abas *Desempenho*, *Exibição*, *Áudio*, *Arquivos*, *Geral* e *Notificações*.
- 🔍 **Calibração de DPI & Fontes:** Ajuste fino no `qt.conf` para renderização nítida sem estouro de texto em monitores Full HD, 2K e 4K.
- 🎯 **Mapeamento de Teclas Pré-Configurado (Keymaps Pro):**
  - **Call of Duty Mobile:** Modos *Multijogador (MP)* e *Battle Royale (BR)* configurados com trava de mira no `~` (abaixo do Esc) / `Ctrl`, clique direito para mirar (ADS) e clique esquerdo para atirar.
  - **Free Fire:** Movimento no WASD, troca rápida de armas (1 e 2), uso de kits (4), granadas/gelo (G), mochila (Tab) e mapa (M).
- 🎨 **Identidade Visual Personalizada:** Troca automática do logo do emulador e atalhos na Área de Trabalho com a marca oficial **DLuz Games**.
- 🚀 **1-Clique e Compatibilidade Automática:** Detecta automaticamente a instalação do emulador e funciona em atualizações novas e futuras.

---

## 📥 Download e Instalação Rápida

1. Acesse a aba **[Releases](https://github.com/dluzgames/DLuz-Androws-Translator-PTBR/releases/latest)** e baixe o executável:
   - **`DLuz_Tradutor_Tencent_Androws_PTBR.exe`**
2. Feche o emulador se estiver aberto.
3. Dê um **duplo clique** no arquivo `DLuz_Tradutor_Tencent_Androws_PTBR.exe`.
4. O instalador detectará a pasta do emulador e aplicará a tradução, ajustes de DPI, controles e logo em menos de 5 segundos.
5. Pronto! Abra o emulador pelos novos atalhos na sua Área de Trabalho.

---

## 🛠️ Como Compilar a Partir do Código Fonte

Requisitos:
- **Python 3.10+**
- **PyInstaller**: `pip install pyinstaller pillow`

Para compilar o binário autônomo:
```bash
git clone https://github.com/dluzgames/DLuz-Androws-Translator-PTBR.git
cd DLuz-Androws-Translator-PTBR
python -m PyInstaller --onefile --noconfirm --name "DLuz_Tradutor_Tencent_Androws_PTBR" --icon "dluz_logo.ico" dluz_androws_installer.py
```

O executável gerado estará na pasta `dist/`.

---

## 👨‍💻 Desenvolvido por

**DLuz Games**  
- 🌐 **Site Oficial:** [dluzgames.com.br](https://dluzgames.com.br)  
- 🛍️ **Loja DLuz:** [loja.dluz.com.br](https://loja.dluz.com.br)  
- 📺 **YouTube:** [Joga DLuz](https://youtube.com/@jogadluz) | [DLuz Games](https://youtube.com/@dluzgames)  
- 💬 **Discord:** [Comunidade DLuz Games](https://discord.gg/dluz)

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT - consulte o arquivo [LICENSE](LICENSE) para obter detalhes.
