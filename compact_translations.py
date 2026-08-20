# -*- coding: utf-8 -*-
import json
import io
import sys
import os
import struct
import re

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def elf_hash(s):
    if isinstance(s, str):
        s = s.encode('utf-8')
    h = 0
    for b in s:
        h = (h << 4) + b
        g = h & 0xf0000000
        if g:
            h ^= (g >> 24)
        h &= ~g
    return h

def parse_qm(filepath):
    data = open(filepath, 'rb').read()
    offset = 16
    sections = {}
    while offset < len(data):
        tag = data[offset]
        length = int.from_bytes(data[offset+1:offset+5], 'big')
        sections[tag] = data[offset+5:offset+5+length]
        offset += 5 + length
        
    contexts_data = sections.get(0x42, b'')
    msg_data = sections.get(0x69, b'')
    
    offsets = []
    for i in range(0, len(contexts_data), 8):
        h, off = struct.unpack('>II', contexts_data[i:i+8])
        offsets.append((h, off))
        
    messages = []
    for h, off in offsets:
        if off >= len(msg_data):
            continue
        p = off
        msg = {'hash': h, 'offset': off}
        while p < len(msg_data):
            tag = msg_data[p]
            p += 1
            if tag == 1: break
            tag_len = struct.unpack('>i', msg_data[p:p+4])[0]
            p += 4
            if tag_len < 0: val = b''
            else:
                val = msg_data[p:p+tag_len]
                p += tag_len
            if tag == 3: msg['translation'] = val.decode('utf-16be', 'replace') if val else ''
            elif tag == 6: msg['source'] = val.decode('utf-8', 'replace')
            elif tag == 7: msg['context'] = val.decode('utf-8', 'replace')
            elif tag == 8: msg['comment'] = val.decode('utf-8', 'replace')
        messages.append(msg)
    return messages

def build_qm(messages, locale='zh_CN'):
    header = bytes.fromhex('3cb86418caef9c95cd211cbf60a1bddd')
    locale_bytes = locale.encode('utf-8')
    sec_locale = b'\xa7' + struct.pack('>I', len(locale_bytes)) + locale_bytes
    
    entries = []
    for m in messages:
        src = m.get('source', '')
        ctx = m.get('context', '')
        trans = m.get('translation', '')
        comm = m.get('comment', '')
        h = elf_hash(src)
        entries.append((h, src, ctx, trans, comm))
        
    entries.sort(key=lambda x: x[0])
    
    msg_body = bytearray()
    contexts_body = bytearray()
    
    for h, src, ctx, trans, comm in entries:
        offset = len(msg_body)
        contexts_body += struct.pack('>II', h, offset)
        
        if trans:
            trans_bytes = trans.encode('utf-16be')
            msg_body += b'\x03' + struct.pack('>I', len(trans_bytes)) + trans_bytes
        else:
            msg_body += b'\x03\xff\xff\xff\xff'
            
        if comm:
            comm_bytes = comm.encode('utf-8')
            msg_body += b'\x08' + struct.pack('>I', len(comm_bytes)) + comm_bytes
        else:
            msg_body += b'\x08\x00\x00\x00\x00'
            
        src_bytes = src.encode('utf-8')
        msg_body += b'\x06' + struct.pack('>I', len(src_bytes)) + src_bytes
        
        ctx_bytes = ctx.encode('utf-8')
        msg_body += b'\x07' + struct.pack('>I', len(ctx_bytes)) + ctx_bytes
        
        msg_body += b'\x01'
        
    sec_contexts = b'\x42' + struct.pack('>I', len(contexts_body)) + bytes(contexts_body)
    sec_messages = b'\x69' + struct.pack('>I', len(msg_body)) + bytes(msg_body)
    
    return header + sec_locale + sec_contexts + sec_messages

# COMPACT & OPTIMIZED PT-BR Translations Dictionary
PT_BR_MAP = {
    # Buttons & Short actions
    "OK": "OK",
    "Ok": "OK",
    "Cancel": "Cancelar",
    "cancel": "Cancelar",
    "Exit": "Sair",
    "exit": "Sair",
    "Confirm": "Confirmar",
    "confirm": "Confirmar",
    "Confirm Exit": "Confirmar Saída",
    "Close": "Fechar",
    "close": "Fechar",
    "Save": "Salvar",
    "save": "Salvar",
    "Save File": "Salvar",
    "save as": "Salvar Como",
    "save to local": "Salvar no PC",
    "save setting": "Salvar",
    "Open": "Abrir",
    "open": "Abrir",
    "Open folder": "Abrir Pasta",
    "Help": "Ajuda",
    "help": "Ajuda",
    "gain help": "Ajuda",
    "Settings": "Config.",
    "settings": "Config.",
    "Back": "Voltar",
    "back": "Voltar",
    "Next": "Avançar",
    "next": "Avançar",
    "next step": "Avançar",
    "skip": "Pular",
    "Retry": "Tentar de Novo",
    "retry": "Tentar de Novo",
    "Refresh": "Atualizar",
    "refresh": "Atualizar",
    "refresh try": "Atualizar",
    "Restore": "Restaurar",
    "restore": "Restaurar",
    "Delete": "Excluir",
    "delete": "Excluir",
    "Clean": "Limpar",
    "clean": "Limpar",
    "Clean now": "Limpar",
    "Clean later": "Mais Tarde",
    "Restart": "Reiniciar",
    "restart": "Reiniciar",
    "Restart now": "Reiniciar",
    "restart right now": "Reiniciar",
    "confirm restart": "Reiniciar",
    "cancel  restart": "Cancelar",
    "Do not restart": "Mais Tarde",
    "restart later": "Mais Tarde",
    "I know": "OK",
    "I known": "OK",
    "Knew": "OK",
    "know it": "OK",
    "Login": "Entrar",
    "login": "Entrar",
    "Logout": "Sair",
    "logout": "Sair",
    "Install": "Instalar",
    "install": "Instalar",
    "Install now": "Instalar",
    "Exit Installing": "Cancelar",
    "Update": "Atualizar",
    "update": "Atualizar",
    "Update driver": "Atualizar Driver",
    "To update driver": "Atualizar Driver",
    "Download": "Baixar",
    "download": "Baixar",
    "Downloading": "Baixando...",
    "Transferring": "Transferindo...",
    "File list": "Arquivos",
    "Choose files": "Escolher",
    "Import": "Importar",
    "import": "Importar",
    "Importing...": "Importando...",
    "Export": "Exportar",
    "export": "Exportar",
    "Share": "Compartilhar",
    "share": "Compartilhar",
    "View": "Ver",
    "view": "Ver",
    "view log": "Ver Log",
    "Log has been generated": "Relatório gerado",
    "Generating log": "Gerando log...",
    "maximize": "Maximizar",
    "minimize": "Minimizar",
    "Pin": "Fixar Topo",
    "All": "Todos",
    "all": "Todos",
    "Search": "Buscar",
    "search": "Buscar",
    "hint": "Dica",
    "Hint": "Dica",
    "Warning": "Aviso",
    "warning": "Aviso",
    "Error": "Erro",
    "error": "Erro",
    "Success": "Sucesso",
    "success": "Sucesso",
    "Failed": "Falhou",
    "failed": "Falhou",
    "Finish": "Concluir",
    "finish": "Concluir",
    "Done": "Pronto",
    "done": "Pronto",
    "Default": "Padrão",
    "default": "Padrão",
    "Custom": "Personalizado",
    "custom": "Personalizado",
    "Auto": "Auto",
    "auto": "Auto",
    "None": "Nenhum",
    "none": "Nenhum",
    "More": "Mais",
    "more": "Mais",
    "Edit": "Editar",
    "edit": "Editar",
    "Add": "Adicionar",
    "add": "Adicionar",
    "add note": "Adicionar Nota",
    "Remove": "Remover",
    "remove": "Remover",
    "Clear": "Limpar",
    "clear": "Limpar",
    "go to clear": "Limpar",
    "Reset": "Redefinir",
    "reset": "Redefinir",
    "Apply": "Aplicar",
    "apply": "Aplicar",
    "Accept": "Aceitar",
    "Reject": "Recusar",
    "Title": "Título",
    "Description": "Nome",
    "TextLabel": "",
    "Form": "",
    "Frame": "",
    "CheckBox": "",
    "icon": "",
    "Toolbar": "Ferramentas",
    "Sidebar": "Guia",
    "toolbar guide": "Guia",
    "Beginner Guide": "Guia",
    "MiniWindow": "Mini Janela",
    "perf setting": "Desempenho",
    "file setting": "Arquivos",
    "close btn setting": "Ao Fechar",
    "vram usage strategy": "VRAM",
    "esc exit fullscreen": "Esc: Sair Tela Cheia",
    "do not show again": "Não exibir mais",
    "Partial failed": "Falha Parcial",
    "Transfer failed": "Falha",
    "Transfer success": "Concluído",
    "file has been deleted": "Arquivo movido",
    "Browse file via Virtual Disk": "Ver no Disco Virtual",
    "Device not supported": "Não Suportado",
    "display voice setting": "Áudio Gravação",
    "volume setting": "Volume",
    "Do you have below question": "Problemas encontrados?",
    "HideFps": "Ocultar FPS",
    "show display": "Exibir FPS no jogo",
    "Update available": "Atualização",
    
    # UI / Display
    "Hd": "HD",
    "Fps": "FPS",
    "DPI": "DPI",
    "cpu": "CPU",
    "CPU": "CPU",
    "Memory": "RAM",
    "Resolution": "Resolução",
    "Frame rate": "FPS",
    "High frame rate": "Alto FPS",
    "High FPS": "Alto FPS",
    "Display": "Exibição",
    "Display setting": "Exibição",
    "Display mode": "Modo Exibição",
    "Fullscreen": "Tela Cheia",
    "Full screen": "Tela Cheia",
    "Exit full screen": "Sair Tela Cheia",
    "Press F11 to exit full screen": "F11: Sair Tela Cheia",
    "Volume": "Volume",
    "Volume setting": "Volume",
    "Mute": "Mudo",
    "Screen record": "Gravação",
    "Screen recording": "Gravar Tela",
    "Screen recording is successful": "Gravação salva",
    "00:00:00": "00:00:00",
    "00: 00: 00": "00:00:00",
    "hh: mm: ss": "hh: mm: ss",
    "Screen shot": "Print",
    "Screenshot": "Print",
    "The screenshot was successful": "Print salvo",
    "screenshot file": "Print",
    "already copy to clipboard": "Copiado",
    "Vol:%1%\nVol+:Ctrl+Alt+Up\nVol-:Ctrl+Alt+Down": "Vol: %1%\n+: Ctrl+Alt+Up\n-: Ctrl+Alt+Down",
    
    # Compact Key mapping & Controls
    "Key mapping": "Teclas",
    "Key Mapping": "Teclas",
    "key setting": "Teclas",
    "Key setting": "Ajuste Tecla",
    "click button": "Clique",
    "shoot button": "Tiro (Esq.)",
    "scale button": "Zoom",
    "scale button wheel": "Scroll",
    "scale button key": "Teclado",
    "scale key setting": "Zoom",
    "slide button": "Deslizar",
    "slide button tip": "Gesto de deslizar",
    "skill button": "Habilidade",
    "macro button": "Macro",
    "mouse button": "Mira",
    "repeat button": "Combo",
    "observe button": "Visão",
    "Left joystick": "WASD",
    "Right joystick": "Analógico",
    "left joystick Setting": "WASD",
    "joyStick Item Setting": "Analógico",
    "joyStick resetPos": "Centralizar",
    "joyStick sensitivity": "Sensibilidade",
    "SteeringWheel Item Setting": "Direcional",
    "slide control": "Deslizar",
    "click control": "Toque",
    "Set combo count": "Qtd. Combo",
    "Click to delete this key": "Excluir tecla",
    "Click for more key settings": "Opções da tecla",
    "Right-click to add keys": "Clique direito para add",
    "Click or drag the sidebar into the interface to add keys": "Arraste da barra lateral para add teclas",
    "The key binding conflicts with another. Please reconfigure": "Tecla em uso! Escolha outra.",
    "Press keyboard or mouse button to set key value": "Pressione a tecla desejada",
    "Press the keyboard/mouse button to set the key": "Pressione tecla ou botão do mouse",
    "Press the handler button to set the key": "Pressione botão do controle",
    "Press handler button to set key value": "Pressione botão do controle",
    "Drag to the location you want to click": "Arraste para onde clicar",
    "Set interrupt button": "Tecla Cancelar",
    "show wheel radius": "Ver Raio",
    "release direction": "Direção",
    "release time": "Momento",
    "release range": "Raio",
    "release on key up": "Soltar Tecla",
    "wheel radius": "Raio",
    "wheel offset": "Offset",
    "show skill loc": "Posição Inicial",
    "cancel release": "Cancelar",
    "arrow": "Setas",
    "mouse": "Mouse",
    "Center": "Centro",
    "Color": "Cor",
    "Blue": "Azul",
    "Pink": "Rosa",
    "Green": "Verde",
    "Recommended to be within 5 words": "Até 5 palavras",
    "OperationTime": "Tempo (s)",
    "Master Keymap Community": "Comunidade",
    "preview window desc": "Prévia",
    "preview keys title": "Teclas na Prévia",
    "all keys title": "Todas Teclas",
    "preview empty hint": "Sem teclas.\nClique em [Editar] para adicionar.",
    "edit preview content": "Editar",
    "click to modify preview content": "Editar teclas exibidas",
    "exit edit preview": "Sair",
    "toggle preview desc": "Exibir Prévia",
    "toggle preview window": "Exibir Prévia",
    "preview window supports drag position": "A janela de prévia pode ser arrastada",
    "Adjust X-axis sensitivity": "Sensib. Eixo X",
    "Adjust Y-axis sensitivity": "Sensib. Eixo Y",
    "Lock/Unlock the camera view using the %1 key": "[%1] Travar/Destravar mira",
    "save on cloud": "Nuvem",
    "open and enjoy vpp": "Aprimorar imagem",
    
    # Environment & Diagnostics
    "Environmental repair": "Reparar Ambiente",
    "Environment detect": "Verificar Ambiente",
    "environment fixed": "Reparo Concluído",
    "environment repair failed": "Falha no Reparo",
    "Disable Hyper-V": "Desativar Hyper-V",
    "Disabling Hyper-V...": "Desativando...",
    "Disable now": "Desativar",
    "To disable Hyper-V": "Desativar Hyper-V",
    "Hyper-v is enabled": "Hyper-V Ativo",
    "Hyper-V has been successfully enabled": "Hyper-V Ativado",
    "repair": "Reparar",
    "Detected that you have enabled Hyper-V, configuration of the related environment is required before normal use, would you like to repair?": "Hyper-V detectado. Configuração necessária para emular. Reparar agora?",
    "Detected runtime environment as a virtual machine, there is a risk of information leakage, and usage is currently not supported.": "Ambiente de Máquina Virtual não suportado.",
    "Your graphics card driver version has been detected as outdated, which may cause the application to fail to install and launch. Please update your graphics card driver and then restart the application.": "Driver de vídeo desatualizado. Atualize para rodar sem erros.",
    "It has been detected that your graphics card driver is outdated, which may cause the application to blue screen upon startup. It is recommended that you update your graphics card driver and restart the application.": "Driver de vídeo desatualizado. Atualize para evitar travamentos.",
    "updating driver, Be patient and don't operate androws": "Atualizando driver... Aguarde.",
    "updating driver, Be patient and don't operate Game Assist": "Atualizando driver... Aguarde.",
    "Checking memory...": "Verificando RAM...",
    "Free Up Memory by Closing Other Apps": "Feche outros programas para liberar RAM",
    "Your device is low on memory. Close some running applications and retry.": "RAM insuficiente. Feche apps e tente de novo.",
    "Free memory:": "RAM Livre:",
    "Free vm memory: %1": "RAM Virtual: %1",
    "Recheck": "Verificar de Novo",
    "Failed to initialize game environment, please exit and try restart again.": "Falha ao iniciar jogo. Reinicie o emulador.",
    "It will take effect after restarting the computer. Do you want to restart it now?": "Efeito após reiniciar o PC. Reiniciar agora?",
    "An unknown application has been detected": "App de fonte desconhecida detectado.",
    "Has high risks": "App de alto risco detectado.",
    "Detecting runtime risks": "Verificando segurança...",
    "Detecting malicious plugins": "Verificando plugins...",
    "Detecting virus threats": "Verificando vírus...",
    "Security detection in progress": "Verificando segurança...",
    "%1 has passed security detection": "%1 verificado com sucesso",
    "Start virtual disk when Application starts": "Iniciar disco virtual com emulador",
    "Exit App Store Virtual Disk": "Ejetar Disco Virtual",
    "Tencent Mobile App Engine - Security Guard Center": "Centro de Segurança Android",
    "Mobile application engine services are provided by Tencent MyApp": "Subsistema Android Tencent",
    "Exited the Tencent Mobile Engine": "Subsistema Android finalizado.",
    "Exit the Tencent Mobile Engine": "Sair do Subsistema",
    "Exit the Tencent Mobile Engine?": "Deseja sair do Subsistema Android?",
    "Rolling out the Tencent Mobile Engine...": "Encerrando Subsistema...",
    "Exit Tencent Mobile Engine": "Sair do Subsistema",
    "Exit anyway": "Sair Mesmo Assim",
    "Exit %1": "Sair de %1",
    "Continue": "Continuar",
    "The installation is about to be completed. Please do not exit %1.": "Instalação em andamento. Não feche %1.",
    "%1(%2 apps) are about to be completed. Please do not exit Tencent MyApp.": "%1 (%2 apps) instalando. Não feche.",
    "create shortcut success": "Atalho criado",
    "Create a YYB shortcut to your desktop": "Criar atalho na Área de Trabalho",
    "Create a Game Assist shortcut to your desktop": "Criar atalho na Área de Trabalho",
    "Number of games remaining today": "Jogadas hoje: ",
    "The trial times have been used up, please try again tomorrow": "Tentativas esgotadas hoje. Volte amanhã.",
    "buy buy buy": "Obter Versão Completa",
    "%1Entering the game": "%1 entrando...",
    "Pull up the window to adjust the size": "Redimensione pelas bordas",
    "confirm  resize": "Confirmar",
    "cancel  resize": "Cancelar",
    "confirm window size, restart lite %1": "Confirmar e reiniciar %1",
    "query restart lite %1, confirm restart %2": "Reiniciar %1 para ajustar tamanho?",
    "Acceleration Center": "Acelerador",
    "Show Acceleration Center": "Exibir",
    "Exit Acceleration Center": "Fechar",
    "Wake up Xiaobao Assistant": "Assistente",
    "Xiaobao lost": "Não encontrado",
    "page lost please refresh": "Página indisponível. Atualize.",
    "Get apps": "Apps",
    "Target file: ": "Destino: ",
    "%1 is not supported on PC": "%1 não suportado no PC",
    "Current queue%1,It will take another %2 minutes": "Fila: %1. Tempo: %2 min",
    "Check apk file": "Ver APK",
    "The system environment has been fixed. Please continue use.": "Ambiente corrigido com sucesso.",
    "Tips for switching accounts": "Troca de Conta",
    "Switching the mini program login account will exit the yyb program you are currently running.": "Trocar de conta encerrará o app atual.",
    "Switching the mini program login account will exit the syzs program you are currently running.": "Trocar de conta encerrará os jogos em execução.",
    "Switching the mini program login account in tray hidden mode.": "Trocar de conta exigirá novo login.",
    "Notification Settings": "Notificações",
    "Notification settings": "Notificações",
    "open app notification with %1": "Notificações de [%1]",
    "user feedback": "Feedback",
    "receive a message": "Mensagem",
    "forum feedback": "Fórum",
    "Join the group for feedback": "Suporte",
    "Copy diagnostic information to clipboard": "Copiar Diagnóstico",
    "If you encounter any issues during use, please join our official channel. Our staff will assist you in resolving the problem.": "Dúvidas ou problemas? Acesse nosso suporte oficial.",
    "If you encounter any issues during use, Feel free to give us feedback or suggestions in the forum": "Dúvidas ou sugestões? Deixe seu feedback no fórum.",
    "AppletGame": "Jogos",
    "AppletApp": "Apps",
    "[%1] loading": "Carregando [%1]...",
    "(ErrorCode:%1)": "(Erro: %1)",
    "\"%1\" has no local app to open, we recommend these apps": "Sem app padrão para \"%1\". Recomendamos:",
    "\"%1\"": "\"%1\"",
    "%1": "%1",
    "75%": "75%",
    "Initializing configuration, please do not close the syzs emulator.": "Inicializando configurações... Não feche.",
    "Cleaning up memory, please wait patiently": "Limpando RAM... Aguarde.",
    "Application failed to start, please restart your computer and try again.ErrorCode:%1": "Falha ao iniciar. <b>Reinicie o PC</b>.<br/>Erro: %1",
    "This will cancel all files that have not started uploading": "Cancelar uploads pendentes?",
    "When enabled, the boss key will hide the application tray icon": "Ocultar ícone da bandeja com a Boss Key",
    "Current game switch to %1,will get better behavior.Do you want to restart to swicth?": "Alternar para motor %1 para gráficos melhores?",
    "%1 failed to start, please exit and try again.": "Falha ao iniciar %1. Tente de novo.",
    "Window size change detected, which may cause display blurring. It is recommended to restart the application": "Janela redimensionada. Reinicie para imagem nítida.",
    "Waiting for phone files...": "Aguardando arquivos do celular...",
    "When it is turned on, when the window is close to the edge of the screen, the window will be retracted inward; when the mouse moves to the edge of the retracted area, the window will appear downward.": "Ocultar janela na borda da tela automaticamente.",
    "Some setting value change need restart emulator and application": "Reinicie o ${product_name} para aplicar.",
    "%1 files transferred": "%1 arquivos recebidos",
    "Please return to the previous page and re-enter": "Volte e tente novamente.",
    "enable split screen you can browser info by two screens": "Tela dividida em 2 janelas.",
    "Confirm disconnect?": "Desconectar?",
    "Confirm cancel upload?": "Cancelar envio?",
    "%1 files failed": "%1 arquivos falharam",
    "Pausing this connection will resend when the phone leaves": "Requer novo pareamento do celular.",
    "To resolve this issue, follow these steps to free up space on the %1 drive": "Libere espaço na unidade %1.",
    "not enought space": "Disco Cheio",
    "Detected missing file directory of Tencent Mobile Application Engine": "Pasta de arquivos não encontrada.",
    "To ensure normal file transfer, the missing directory %1 has been created. Please view historical content in the original directory.": "Diretório %1 recriado para transferência.",
    "%1 File (*.%1);;All File (*)": "%1 (*.%1);;Todos (*)",
    "All File (*)": "Todos (*)",
    "PNG image (*.png)": "PNG (*.png)",
    "BMP image (*.bmp)": "BMP (*.bmp)",
    "JPEG image (*.jpg *.jpeg)": "JPEG (*.jpg *.jpeg)",
    "Chinese-English Translation": "Tradução",
    "Question search and answer": "Pesquisa",
    "ask xiao bao": "Assistente",
    "extract text": "OCR",
    "Activate environment components": "Ativando sistema...",
    "It has been detected that the window has been switched to a new display device.": "Monitor alterado. Reinicie para ajustar.",
    "restart the application for optimal display configuration": "Reinicie para calibrar exibição.",
    "%1 has not yet adapted this app, and there may be compatibility issues": "%1 em fase de adaptação para este app.",
    "Log has been generated. please check %1 file name %2": "Log salvo em %1 (%2)",
    "frame rate tips": "FPS alto demais pode causar travamentos.",
    "esc %1 fullscreen checkbox": "F11 e Esc saem da tela cheia em [%1]",
    "Some setting value change need restart Game Assist": "Reinicie o emulador para aplicar.",
    "multi app rate tips": "Vários apps abertos reduzem o FPS.",
    "Detected camera need permission": "Permissão de câmera necessária",
    "Detected no camera": "Sem câmera",
    "Detected location is not turned on": "Localização desativada",
    "To turn on": "Ativar",
    "It is detected that your camera permission is not turned on, which may cause some functions to not work properly It is recommended to enable it. After opening, please restart the application and %1. Open path: windows settings - privacy - location": "Câmera desativada no Windows. Ative em Configurações > Privacidade.",
    "Don't show again": "Não mostrar mais",
    
    # Direct Chinese
    "保存成功": "Salvo",
    "应用设置": "Config. App",
    "录屏同时录制声音": "Gravar áudio junto com a tela",
    "提示": "Aviso",
    "退出应用时提示": "Confirmar ao sair",
    "再等一会": "Aguardar",
    "按F11可以进入/退出全屏模式": "F11: Alternar Tela Cheia",
    "Android子系统正在启动中...": "Iniciando Android...",
    "应用正在启动中...": "Iniciando...",
    "恢复默认": "Padrão",
    "查看文件": "Ver Arquivos",
    "高画质": "HD",
    "调字体": "DPI",
    "帧率": "FPS",
    "置顶": "Fixar",
    "处理器": "CPU",
    "导入中...": "Importando...",
    "返回": "Voltar",
    "返回上一步": "Voltar",
    "确定": "OK",
    "取消": "Cancelar",
    "退出": "Sair",
    "下一步": "Avançar",
    "跳过": "Pular",
    "知道了": "OK",
    "我知道了": "OK",
    "立即重启": "Reiniciar",
    "暂不重启": "Mais Tarde",
    "立即清理": "Limpar",
    "暂不清理": "Mais Tarde",
    "全屏": "Tela Cheia",
    "帮助": "Ajuda",
    "获取帮助": "Ajuda",
    "打开": "Abrir",
    "打开文件": "Abrir",
    "保存文件": "Salvar",
    "关闭": "Fechar",
    "最小化": "Minimizar",
    "最大化": "Maximizar",
    "菜单": "Menu",
    "开始/暂停": "Iniciar / Pausar",
    "结束": "Fim",
    "部分失败": "Falha Parcial",
    "文件不在当前位置": "Arquivo movido",
    "正在初始化配置，请不要关闭腾讯手游助手。": "Inicializando... Não feche.",
    "清理中，请耐心等待": "Limpando RAM...",
    "打开后将在游戏中展示实时帧率": "Exibir FPS no jogo",
    "接收失败": "Falha",
    "接收成功": "Concluído",
    "性能设置": "Desempenho",
    "剩余虚拟内存: %1": "RAM Virtual: %1",
    "应用启动失败，请 <b>重启电脑</b> 后再次尝试。<br/>错误码：%1": "Falha ao iniciar. <b>Reinicie o PC</b>.<br/>Erro: %1",
    "稍后重启": "Mais Tarde",
    "点击关闭按钮设置": "Ao Fechar",
    "这将取消所有未开始上传的文件": "Cancelar uploads pendentes?",
    "打开虚拟磁盘查看文件": "Ver no Disco Virtual",
    "开启后启用老板键时将隐藏${product_name}托盘态": "Ocultar ícone com Boss Key",
    "小窗": "Mini Janela",
    "按下手柄按键设置键值": "Pressione botão do controle",
    "设备不支持运行": "Não Suportado",
    "屏幕声音设置": "Áudio Gravação",
    "体验过程中是否遇到以下问题？": "Problemas encontrados?",
    "取消帧率显示": "Ocultar FPS",
    "当前运行的游戏切换到%1引擎能体验更好的显示效果，是否重启完成切换？": "Alternar motor para %1?",
    "施法时机": "Momento",
    "视角键": "Visão",
    "指引": "Guia",
    "歌名": "Música",
    "歌手": "Artista",
    "文件设置": "Arquivos",
    "%1启动失败，请退出重试。": "Falha ao iniciar %1. Tente de novo.",
    "立即开启": "Ativar",
    "有更新": "Atualização",
    "使用Esc退出全屏": "Esc: Sair Tela Cheia",
    "不再显示": "Não mostrar mais",
    "显存使用策略": "VRAM",
    "文件助手/截图录屏设置": "Arquivos & Gravação",
    "检测到窗口尺寸有较大变化，可能会导致显示模糊的问题，建议重启应用": "Janela redimensionada. Reinicie para nitidez.",
    "海量应用、游戏库一键畅玩": "Jogos e Apps Android no PC",
    "新手引导": "Guia",
    "等待接收手机文件...": "Aguardando arquivos...",
    "开启后，当窗口靠近屏幕的边缘时，窗口会向内收起；当鼠标移至收起的区域边缘，窗口会向下出现": "Ocultar janela na borda da tela.",
    "施法半径": "Raio",
    "部分设置选项需要重启${product_name}和已打开的应用才能生效": "Reinicie o ${product_name} para aplicar.",
    "%1个文件接收成功": "%1 arquivos recebidos",
    "请返回上一级页面重新进入": "Volte e tente de novo.",
    "将录屏和截图存储到该路径": "Salvar prints e vídeos neste caminho",
    "自动释放": "Auto Disparo",
    "开启后可体验应用分屏，双屏浏览信息": "Tela dividida.",
    "蓝色": "Azul",
    "粉色": "Rosa",
    "绿色": "Verde",
    "正中心": "Centro",
    "颜色": "Cor",
    "备注": "Nome",
    "建议5字以内": "Até 5 letras",
    "按键设置": "Ajuste Tecla",
    "操作时间(s)": "Tempo (s)",
    "缩放键设置": "Zoom",
    "所有键位": "Todas",
    "预览窗": "Prévia",
    "预览窗键位": "Teclas Prévia",
    "修改展示内容": "Editar",
    "点击退出修改": "Sair",
    "点击修改预览窗内的展示内容": "Editar teclas exibidas",
    "显示/隐藏预览窗": "Exibir Prévia",
    "预览窗支持拖拽位置": "A janela pode ser arrastada",
    "暂未添加键位\n点击【修改展示内容】添加键位": "Sem teclas.\nClique em [Editar] para add.",
    "键位冲突，请重新设置": "Conflito! Escolha outra.",
    "点击可删除该键位": "Excluir tecla",
    "点击可进行更多按键设置": "Opções",
    "按下键盘或鼠标按键设置键值": "Pressione a tecla",
    "按下键盘/鼠标按键设置按键": "Pressione a tecla",
    "按下手柄按键设置按键": "Pressione botão do controle",
    "拖动到需要点击的位置": "Arraste para a tela",
    "设置打断按键": "Tecla Cancelar",
    "查看轮盘半径": "Ver Raio",
    "施法方向控制": "Direção",
    "轮盘半径": "Raio",
    "方向键": "Setas",
    "鼠标": "Mouse",
    "取消施法": "Cancelar",
    "查看技能起始位置": "Posição",
    "轮盘偏移": "Offset",
    "滑动控制": "Deslizar",
    "点击控制": "Toque",
    "方向键设置": "Direcional",
    "左摇杆设置": "WASD",
    "右摇杆设置": "Analógico",
    "复位": "Centralizar",
    "灵敏度": "Sensib.",
    "调整X轴灵敏度": "Sensib. X",
    "调整Y轴灵敏度": "Sensib. Y",
    "设置连击次数": "Qtd. Combo",
    "单击键": "Clique",
    "左键射击": "Tiro",
    "缩放键": "Zoom",
    "进行滑动操作": "Deslizar",
    "自由滑动": "Deslizar",
    "技能键": "Habilidade",
    "一键宏": "Macro",
    "鼠标模式": "Mira",
    "滚轮": "Scroll",
    "按键": "Teclas",
    "侧边栏点击/拖拽至界面内增加键位": "Arraste para add teclas",
    "点击鼠标右键，添加键位": "Clique direito para add",
    "使用 %1 解锁/锁定鼠标,控制视角移动": "[%1] Travar/Destravar mira",
    "打开即可体验画质增强功能": "Aprimorar imagem",
    "检测到窗口已切换至新显示设备，因显示设置差异可能导致布局错乱，重启应用可自动修复布局。": "Monitor alterado. Reinicie para ajustar.",
    "建议重启应用以达最佳显示配置": "Reinicie para calibrar exibição.",
    "%1暂未适配该应用，可能存在兼容性问题": "%1 em adaptação.",
    "超出硬件条件的帧率设置会带来资源浪费、卡顿": "FPS alto demais pode causar travamentos.",
    "开启后【%1】可同时使用F11和Esc退出全屏": "F11 e Esc saem da tela cheia em [%1]",
    "部分设置选项需要重启腾讯手游助手和已打开的应用才能生效": "Reinicie o emulador para aplicar.",
    "启动多款应用时，帧率表现可能会受到影响": "Muitos apps reduzem o FPS.",
    "打开【%1】内的通知提醒": "Notificações de [%1]",
    "诊断日志已生成，请前往%1查看，文件名:%2": "Log salvo em %1 (%2)",
    "打开目录": "Abrir",
    "音量设置": "Volume",
    "应用退出设置": "Ao Sair",
    "录屏声音设置": "Áudio Gravação",
    "恢复默认设置": "Padrão",
    "游戏模式": "Modo Jogo",
    "某些应用和Windows功能需要访问你的位置才能正常工作。在此处关闭此设置可能会限制桌面应用和Windows可以执行的操作。": "Apps precisam de localização.",
    "允许应用访问你的位置信息": "Permitir localização",
    "开启定位功能": "Ativar Localização",
    "去开启": "Ativar",
    "定位提示": "Localização",
    "允许桌面应用访问你的相机": "Permitir câmera",
    "开启摄像头功能": "Ativar Câmera",
    "某些应用和Windows功能需要访问相机才能正常工作。在此处关闭此设置可能会限制桌面应用和Windows可以执行的操作。": "Apps precisam de câmera.",
    "摄像头提示": "Câmera",
    "检查内存中...": "Verificando RAM...",
    "请关闭其它应用以释放内存": "Feche apps para liberar RAM",
    "运行内存不足，请关闭其它应用后重试。": "RAM insuficiente. Feche apps.",
    "初始化游戏环境失败，请退出并重启游戏。": "Falha ao iniciar. Reinicie.",
    "剩余内存：": "RAM Livre: ",
    "检测到您的显卡驱动版本过旧，可能导致应用启动蓝屏，建议您更新显卡驱动后重新启动应用。": "Driver de vídeo antigo. Atualize.",
    "重新检查": "Verificar de Novo",
    "%1个文件接收失败": "%1 arquivos falharam",
    "断开本次连接后，从手机上传文件需重新扫码": "Requer novo pareamento.",
    "确认要断开本次连接？": "Desconectar?",
    "文件列表": "Arquivos",
    "确认取消上传？": "Cancelar envio?",
    "接收中": "Recebendo...",
    "去清理": "Limpar",
    "空间不足": "Disco Cheio",
    "磁盘空间已满，文件可能无法正常下载，请清理%1盘后使用": "Libere espaço em %1.",
    "为保证文件正常传输，已新建缺失目录%1，历史内容请于原目录下查看": "Diretório %1 recriado.",
    "检测到腾讯应用宝文件管理目录缺失": "Pasta não encontrada.",
    "录屏成功": "Gravação salva",
    "截图成功": "Print salvo",
    "选择文件": "Escolher",
    "截图已保存至剪贴板": "Copiado",
    "检测到你的摄像头权限未打开，可能导致部分功能无法正常使用，建议开启。开启后，请重启应用和%1。开启路径：windows设置-隐私-位置": "Câmera desativada no Windows.",
    "音量:%1%\n增大音量:Ctrl+Alt+Up\n减小音量:Ctrl+Alt+Down": "Vol: %1%\n+: Ctrl+Alt+Up\n-: Ctrl+Alt+Down",
    "腾讯移动应用引擎服务由应用宝提供": "Subsistema Android Tencent",
    "激活环境组件": "Ativando...",
    "不再提示": "Não mostrar mais",
    "登录": "Entrar",
    "存云端": "Nuvem",
    "切换后将退出当前小游戏/小程序": "Trocar de conta fechará o app.",
    "切换账号，会退出您当前正在运行的小程序和小游戏，同时切换您的手助平台账号与小游戏/小程序账号。": "Trocar conta encerrará os jogos.",
    "腾讯移动应用引擎在锁屏时已断开, 正在为你重新启动": "Subsistema pausado no bloqueio. Reiniciando...",
    "安全系统启动中...": "Iniciando segurança...",
    "本游戏由腾讯安全保护运行": "Protegido por Tencent Shield",
    "若您在使用过程中遇到问题，欢迎在论坛反馈问题或提供建议。": "Feedback no fórum.",
    "若您在使用过程中遇到问题，可以加入腾讯应用宝电脑版官方频道进行反馈，工作人员将会为您解决问题。": "Suporte oficial.",
    "应用宝": "Emulador",
    "暂不开启": "Agora Não",
    "关": "Desligado",
    "开": "Ligado",
    "未知": "Desconhecido",
    "设置": "Config.",
    "允许应用访问你的相机": "Permitir câmera",
    "允许桌面应用访问你的位置信息": "Permitir localização",
}

def clean_key(s):
    if not s: return ""
    return re.sub(r'[\r\n\t]+', ' ', s).strip()

def translate_string(ctx, src, trans, comm):
    if src in PT_BR_MAP:
        return PT_BR_MAP[src]
    if trans in PT_BR_MAP:
        return PT_BR_MAP[trans]
    c_src = clean_key(src)
    if c_src in PT_BR_MAP:
        return PT_BR_MAP[c_src]
    c_trans = clean_key(trans)
    if c_trans in PT_BR_MAP:
        return PT_BR_MAP[c_trans]
    if "检测到你的系统位置权限未打开" in src or "检测到你的系统位置权限未打开" in trans:
        return "Localização desativada no Windows. Ative em Configurações > Privacidade."
    if "某些应用和Windows功能需要访问你的位置" in src or "某些应用和Windows功能需要访问你的位置" in trans:
        return "Apps precisam de acesso à localização."
    if "如果你允许访问,则可以使用此页面上的设置" in src or "如果你允许访问,则可以使用此页面上的设置" in trans:
        return "Permite consultar dados de localização e clima."
    if "某些应用和Windows功能需要访问相机" in src or "某些应用和Windows功能需要访问相机" in trans:
        return "Apps precisam de acesso à câmera."
    if "如果你允许访问,你可以使用此页面上的设置" in src or "如果你允许访问,你可以使用此页面上的设置" in trans:
        return "Permite aos apps usar a câmera."
    if "检测到您的设备内存不足" in src or "检测到您的设备内存不足" in trans:
        return "Pouca memória RAM livre. Limpe a memória para melhor fluidez."
    if "Hyper-V failed to enable" in src or "Hyper-V开启失败" in trans:
        return "<p style='text-align: left; font-size: 14px; color: black;'>Falha no Hyper-V (%1). Clique no botão para tentar de novo.</p>"
    if "退出将不能体验游戏快感" in src or "退出将不能体验游戏快感" in trans:
        return "Deseja sair do emulador?"
    if src in ["Form", "TextLabel", "CheckBox", "Frame", "icon", "qt_demo_android_emulator", "Title", "Accept", "Reject", "content content content content"]:
        return ""
    if re.match(r'^[0-9\.\:\%\-\s]+$', src):
        return src
    if src == '"%1"' or src == '%1' or src == 'C:\\':
        return src
    if src and not any(ord(c) > 0x4e00 for c in src):
        return src
    return trans

if __name__ == '__main__':
    app_root = r'C:\emu tenc\Androws\Application'
    component_root = r'C:\emu tenc\AndrowsData\Component\Androws'

    i18n_targets = []
    for item in os.listdir(app_root):
        full_p = os.path.join(app_root, item, 'i18n')
        if os.path.isdir(full_p):
            i18n_targets.append(full_p)

    if os.path.isdir(os.path.join(component_root, 'i18n')):
        i18n_targets.append(os.path.join(component_root, 'i18n'))

    for i18n_dir in i18n_targets:
        print(f"\nProcessing directory: {i18n_dir}")
        for mod in os.listdir(i18n_dir):
            mod_dir = os.path.join(i18n_dir, mod)
            if not os.path.isdir(mod_dir): continue
            qm_path = os.path.join(mod_dir, 'zh_cn.qm')
            bak_path = os.path.join(mod_dir, 'zh_cn.qm.bak_orig')
            source_qm = bak_path if os.path.exists(bak_path) else qm_path
            if not os.path.exists(source_qm): continue
            
            msgs = parse_qm(source_qm)
            translated_msgs = []
            for m in msgs:
                ctx = m.get('context', '')
                src = m.get('source', '')
                trans = m.get('translation', '')
                comm = m.get('comment', '')
                pt = translate_string(ctx, src, trans, comm)
                new_m = dict(m)
                new_m['translation'] = pt
                translated_msgs.append(new_m)
                
            compiled = build_qm(translated_msgs, locale='pt_BR')
            with open(qm_path, 'wb') as f_out:
                f_out.write(compiled)
            print(f"  [COMPACT COMPILED] {mod}: {len(translated_msgs)} strings, {len(compiled)} bytes -> {qm_path}")

    # Update qt.conf
    for ver in ['5.10.7110.6414', '5.10.7110.6413']:
        qc = os.path.join(app_root, ver, 'qt.conf')
        if os.path.exists(qc):
            content = """[Paths]
Data = .
[Platforms]
WindowsArguments = fontengine=freetype,dpiawareness=1
"""
            with open(qc, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {qc} with DPI awareness")

    print("\nALL LABELS OPTIMIZED AND FONT SCALING ADJUSTED!")
