# -*- coding: utf-8 -*-
import os
import io
import sys
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WEB_TRANS_MAP = {
    # Settings Modal Header & Tabs
    '设置': 'Configurações',
    '性能': 'Desempenho',
    '显示': 'Exibição',
    '声音': 'Áudio',
    '文件': 'Arquivos',
    '基础': 'Geral',
    '通知': 'Notificações',
    '问题反馈': 'Feedback',
    '诊断日志': 'Log de Diagnóstico',
    '恢复默认设置': 'Restaurar Padrões',
    '保存设置': 'Salvar Configurações',
    '取消': 'Cancelar',
    '确定': 'Confirmar',
    
    # Notification tab
    '本地安装通知设置': 'Notificações de Instalação Local',
    '开启检测第三方APK安全风险': 'Verificar segurança em APKs de terceiros',
    '文件推送通知': 'Notificações de Transferência de Arquivos',
    '开启后推荐本地缺失文件格式应用': 'Recomendar apps para formatos de arquivos não suportados',
    '应用通知设置': 'Notificações de Aplicativos',
    '加速器通知设置': 'Notificações do Acelerador',
    '开启加速器福利通知': 'Receber notificações de promoções do acelerador',
    '关闭后将无法接收免费加速福利通知': 'Ao desativar, você não receberá ofertas de aceleração grátis',
    
    # Performance tab
    '性能设置': 'Configurações de Desempenho',
    'CPU设置': 'Processador (CPU)',
    '内存设置': 'Memória RAM',
    '显卡渲染模式': 'Modo de Renderização Gráfica',
    '极速模式': 'Modo Desempenho',
    '流畅模式': 'Modo Fluido',
    '极致模式': 'Modo Ultra',
    '自定义': 'Personalizado',
    '推荐': 'Recomendado',
    '智能分配': 'Automático (Auto)',
    '显卡': 'Placa de Vídeo (GPU)',
    '显卡切换': 'Alternar GPU',
    '独显': 'GPU Dedicada',
    '集显': 'GPU Integrada',
    
    # Display tab
    '显示设置': 'Configurações de Exibição',
    '分辨率设置': 'Resolução da Tela',
    '默认分辨率': 'Resolução Padrão',
    '超宽屏': 'Ultrawide (21:9)',
    '平板模式': 'Modo Tablet (16:9)',
    '手机模式': 'Modo Celular (9:16)',
    'DPI设置': 'DPI / Densidade de Pixels',
    '帧率设置': 'Taxa de Quadros (FPS)',
    '高帧率模式': 'Modo Alto FPS (90/120 FPS)',
    '开启后可在支持的游戏中体验更高帧率': 'Permite rodar jogos compatíveis em até 120 FPS',
    
    # Audio tab
    '声音设置': 'Configurações de Áudio',
    '声音输出设备': 'Dispositivo de Saída (Alto-falantes)',
    '声音输入设备': 'Dispositivo de Entrada (Microfone)',
    '主音量': 'Volume Principal',
    '录屏声音设置': 'Áudio de Gravação',
    '录制系统声音': 'Gravar som do sistema',
    '录制麦克风声音': 'Gravar microfone',
    
    # File tab
    '文件设置': 'Configurações de Arquivos',
    '文件保存路径': 'Pasta de Arquivos',
    '截图保存路径': 'Pasta de Capturas de Tela (Prints)',
    '录屏保存路径': 'Pasta de Gravações de Vídeo',
    '更改路径': 'Alterar Pasta',
    '打开文件夹': 'Abrir Pasta',
    '打开目录': 'Abrir Pasta',
    '共享文件夹': 'Pasta Compartilhada PC/Android',
    
    # General / Basic tab
    '基础设置': 'Configurações Gerais',
    '开机自启': 'Iniciar com o Windows',
    '开机自动启动应用宝': 'Iniciar emulador automaticamente com o Windows',
    '退出设置': 'Ao Fechar o Aplicativo',
    '点击关闭按钮时': 'Ao clicar no botão fechar (X)',
    '最小化到系统托盘': 'Minimizar para a bandeja do sistema',
    '直接退出程序': 'Encerrar o aplicativo',
    '老板键': 'Boss Key (Tecla de Ocultar)',
    '按下快捷键可快速隐藏界面': 'Oculta a interface instantaneamente',
    '缓存清理': 'Limpeza de Cache e Disco',
    '清理应用缓存': 'Limpar arquivos temporários e liberar espaço',
    '立即清理': 'Limpar Agora',
    '检查更新': 'Verificar Atualizações',
    '当前已是最新版本': 'Você já está na versão mais recente',
    '关于': 'Sobre',
    '版本号': 'Versão',
    
    # Store UI / Sidebar
    '发现': 'Descobrir',
    '榜单': 'Rankings',
    '软件': 'Aplicativos',
    '游戏': 'Jogos',
    'AI专区': 'Área de IA',
    '我的': 'Biblioteca',
    '智能启动台': 'Inicializador',
    '立即登录': 'Entrar / Login',
    '登录': 'Entrar',
    '退出登录': 'Sair',
    '搜索': 'Pesquisar jogos e apps...',
    '王者荣耀': 'Pesquisar jogos...',
    '腾讯应用宝': 'Tencent MyApp',
    '今日为你推荐': 'Recomendações de Hoje',
    '平台动态': 'Novidades da Plataforma',
    '每日一推': 'Destaque do Dia',
    '每日书单': 'Recomendados',
    '全部': 'Todos',
    '下载': 'Baixar',
    '安装': 'Instalar',
    '打开': 'Abrir',
    '更新': 'Atualizar',
    '暂停': 'Pausar',
    '继续': 'Continuar',
    '已安装': 'Instalado',
    '应用宝电脑版': 'Tencent MyApp PC',
}

target_dirs = [
    os.path.expandvars(r'%APPDATA%\Tencent\Androws\offline-page'),
    r'C:\emu tenc\Androws\Application\5.10.7110.6414\offline-page'
]

# Sort by length descending to replace compound phrases first
sorted_terms = sorted(WEB_TRANS_MAP.keys(), key=len, reverse=True)

total_files_updated = 0

for base_dir in target_dirs:
    if not os.path.exists(base_dir): continue
    print(f"\nProcessing Web UI directory: {base_dir}")
    
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith(('.js', '.html', '.json')):
                file_p = os.path.join(root, f)
                bak_p = file_p + '.bak_orig'
                
                # Make backup if not exists
                if not os.path.exists(bak_p):
                    try:
                        with open(file_p, 'rb') as f_in, open(bak_p, 'wb') as f_bak:
                            f_bak.write(f_in.read())
                    except Exception as e:
                        pass
                
                try:
                    content = open(file_p, 'r', encoding='utf-8', errors='ignore').read()
                    orig_content = content
                    
                    for zh in sorted_terms:
                        pt = WEB_TRANS_MAP[zh]
                        if zh in content:
                            content = content.replace(zh, pt)
                            
                    if content != orig_content:
                        with open(file_p, 'w', encoding='utf-8') as f_out:
                            f_out.write(content)
                        print(f"  [TRANSLATED] {os.path.relpath(file_p, base_dir)}")
                        total_files_updated += 1
                except Exception as e:
                    print(f"  Error translating {file_p}:", e)

print(f"\nSUCCESS! Translated {total_files_updated} Web UI / Settings files to Portuguese!")
