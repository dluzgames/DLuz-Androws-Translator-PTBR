# -*- coding: utf-8 -*-
"""
===================================================================
     DLUZ GAMES - TRADUTOR & CUSTOMIZADOR PT-BR (TENCENT ANDROWS)
===================================================================
• Tradução 100% PT-BR de todos os módulos Qt e Web/Configurações
• Troca automática do Logo do Emulador pelo Logo Oficial DLuz
• Injeção de Controles Pro (Call of Duty Mobile e Free Fire)
• Calibração de DPI e Escala de Fontes
• Criação de Atalhos na Área de Trabalho com o Logo DLuz
===================================================================
"""

import os
import sys
import io
import struct
import re
import sqlite3
import time
import subprocess
import base64
import ctypes
import shutil

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

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
        if off >= len(msg_data): continue
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

def build_qm(messages, locale='pt_BR'):
    header = bytes.fromhex('3cb86418caef9c95cd211cbf60a1bddd')
    locale_bytes = locale.encode('utf-8')
    sec_locale = bytes([0xa7]) + struct.pack('>I', len(locale_bytes)) + locale_bytes
    
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
            msg_body += bytes([0x03]) + struct.pack('>I', len(trans_bytes)) + trans_bytes
        else:
            msg_body += bytes([0x03, 0xff, 0xff, 0xff, 0xff])
            
        if comm:
            comm_bytes = comm.encode('utf-8')
            msg_body += bytes([0x08]) + struct.pack('>I', len(comm_bytes)) + comm_bytes
        else:
            msg_body += bytes([0x08, 0x00, 0x00, 0x00, 0x00])
            
        src_bytes = src.encode('utf-8')
        msg_body += bytes([0x06]) + struct.pack('>I', len(src_bytes)) + src_bytes
        
        ctx_bytes = ctx.encode('utf-8')
        msg_body += bytes([0x07]) + struct.pack('>I', len(ctx_bytes)) + ctx_bytes
        
        msg_body += bytes([0x01])
        
    sec_contexts = bytes([0x42]) + struct.pack('>I', len(contexts_body)) + bytes(contexts_body)
    sec_messages = bytes([0x69]) + struct.pack('>I', len(msg_body)) + bytes(msg_body)
    
    return header + sec_locale + sec_contexts + sec_messages

from compact_translations import PT_BR_MAP, translate_string
from translate_keymap_xml_clean import DESC_MAP, translate_xml_content
from translate_offline_page import WEB_TRANS_MAP

def print_banner():
    print(r"""
======================================================================
  ██████╗ ██╗     ██╗   ██╗███████╗     ██████╗  █████╗ ███╗   ███╗███████╗███████╗
  ██╔══██╗██║     ██║   ██║╚══███╔╝    ██╔════╝ ██╔══██╗████╗ ████║██╔════╝██╔════╝
  ██║  ██║██║     ██║   ██║  ███╔╝     ██║  ███╗███████║██╔████╔██║█████╗  ███████╗
  ██║  ██║██║     ██║   ██║ ███╔╝      ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝  ╚════██║
  ██████╔╝███████╗╚██████╔╝███████╗    ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗███████║
  ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝     ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝
             TRADUTOR & CUSTOMIZADOR OFICIAL PT-BR COM LOGO DLUZ
                          Tencent Androws Emulator
======================================================================
    """)

def find_androws_roots():
    candidates = [
        r"C:\emu tenc",
        r"C:\Program Files\Tencent\Androws",
        r"C:\Program Files (x86)\Tencent\Androws",
        r"D:\emu tenc",
        r"E:\emu tenc",
        os.path.expandvars(r"%LOCALAPPDATA%\Tencent\Androws"),
        os.path.expandvars(r"%APPDATA%\Tencent\Androws")
    ]
    valid = []
    for c in candidates:
        if os.path.exists(os.path.join(c, 'Androws', 'Application')) or os.path.exists(os.path.join(c, 'Application')):
            valid.append(c)
    return valid

def main():
    print_banner()
    
    roots = find_androws_roots()
    if not roots:
        print("[!] Nenhuma pasta padrao encontrada.")
        custom = input("Digite o caminho onde o emulador esta instalado (ex: C:\\emu tenc): ").strip()
        if custom and os.path.exists(custom):
            roots = [custom]
        else:
            print("[X] Caminho invalido! Encerrando...")
            time.sleep(3)
            return

    target_root = roots[0]
    print(f"[*] Emulador detectado em: {target_root}\n")
    
    app_root = os.path.join(target_root, 'Androws', 'Application') if os.path.exists(os.path.join(target_root, 'Androws', 'Application')) else os.path.join(target_root, 'Application')
    comp_root = os.path.join(target_root, 'AndrowsData', 'Component', 'Androws')
    
    # 1. Injetar Logo da DLuz
    print("[1/6] Injetando Logo Oficial da DLuz Games no emulador...")
    scratch_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    ico_local = os.path.join(scratch_dir, 'dluz_logo.ico')
    png_local = os.path.join(scratch_dir, 'dluz_logo_64.png')
    
    # If compiled as standalone EXE with PyInstaller, use resource or create from assets
    root_ico = os.path.join(app_root, 'apk.ico')
    if os.path.exists(ico_local):
        try:
            shutil.copy2(ico_local, root_ico)
            print("  [✔] Icone principal do aplicativo atualizado!")
        except: pass
        
    # 2. Translate Qt QM files across all versions and apply icons
    print("[2/6] Traduzindo modulos Qt do emulador (Androws, Store, Assistant)...")
    i18n_targets = []
    if os.path.exists(app_root):
        for item in os.listdir(app_root):
            full_p = os.path.join(app_root, item, 'i18n')
            if os.path.isdir(full_p):
                i18n_targets.append((full_p, os.path.join(app_root, item)))
                
    if os.path.isdir(os.path.join(comp_root, 'i18n')):
        i18n_targets.append((os.path.join(comp_root, 'i18n'), comp_root))
        
    for i18n_dir, ver_dir in i18n_targets:
        print(f"  -> Processando pasta: {os.path.basename(ver_dir)}...")
        for mod in os.listdir(i18n_dir):
            mod_dir = os.path.join(i18n_dir, mod)
            if not os.path.isdir(mod_dir): continue
            qm_path = os.path.join(mod_dir, 'zh_cn.qm')
            bak_path = os.path.join(mod_dir, 'zh_cn.qm.bak_orig')
            
            if os.path.exists(qm_path) and not os.path.exists(bak_path):
                try:
                    with open(qm_path, 'rb') as f_in, open(bak_path, 'wb') as f_bak:
                        f_bak.write(f_in.read())
                except: pass
                
            source_qm = bak_path if os.path.exists(bak_path) else qm_path
            if not os.path.exists(source_qm): continue
            
            try:
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
                print(f"     [OK] Modulo {mod}: {len(translated_msgs)} textos traduzidos.")
            except Exception as e:
                print(f"     [X] Erro ao traduzir {mod}: {e}")
                
        # Apply qt.conf DPI fix
        qc = os.path.join(ver_dir, 'qt.conf')
        if os.path.exists(qc):
            try:
                with open(qc, 'w', encoding='utf-8') as f:
                    f.write("[Paths]\nData = .\n[Platforms]\nWindowsArguments = fontengine=freetype,dpiawareness=1\n")
            except: pass
            
        # Apply DLuz logo to version resources
        res_icon = os.path.join(ver_dir, 'resources', 'icon')
        if os.path.exists(res_icon) and os.path.exists(ico_local):
            for icon_name in ['androws_logo.ico', 'apk.ico']:
                ip = os.path.join(res_icon, icon_name)
                try: shutil.copy2(ico_local, ip)
                except: pass
            if os.path.exists(png_local):
                png_p = os.path.join(res_icon, 'androws_round_logo.png')
                try: shutil.copy2(png_local, png_p)
                except: pass
            
        off_fav = os.path.join(ver_dir, 'offline-page', 'favicon.ico')
        if os.path.exists(os.path.dirname(off_fav)) and os.path.exists(ico_local):
            try: shutil.copy2(ico_local, off_fav)
            except: pass

    print("[✔] Modulos Qt traduzidos e Logos aplicados!\n")
    
    # 3. Translate Web UI / Settings / Offline-page
    print("[3/6] Traduzindo interface Web, Loja e Painel de Configuracoes...")
    web_targets = [
        os.path.expandvars(r'%APPDATA%\Tencent\Androws\offline-page'),
        os.path.join(app_root, '5.10.7110.6414', 'offline-page') if os.path.exists(app_root) else ''
    ]
    
    sorted_terms = sorted(WEB_TRANS_MAP.keys(), key=len, reverse=True)
    web_files_count = 0
    for w_dir in web_targets:
        if not w_dir or not os.path.exists(w_dir): continue
        for root, dirs, files in os.walk(w_dir):
            for f in files:
                if f.endswith(('.js', '.html', '.json')):
                    file_p = os.path.join(root, f)
                    bak_p = file_p + '.bak_orig'
                    if not os.path.exists(bak_p):
                        try:
                            with open(file_p, 'rb') as f_in, open(bak_p, 'wb') as f_bak:
                                f_bak.write(f_in.read())
                        except: pass
                    try:
                        content = open(file_p, 'r', encoding='utf-8', errors='ignore').read()
                        orig = content
                        for zh in sorted_terms:
                            pt = WEB_TRANS_MAP[zh]
                            if zh in content:
                                content = content.replace(zh, pt)
                        if content != orig:
                            with open(file_p, 'w', encoding='utf-8') as f_out:
                                f_out.write(content)
                            web_files_count += 1
                    except: pass
    print(f"[✔] {web_files_count} arquivos de interface e configuracoes traduzidos!\n")
    
    # 4. Injetar Keymaps (Call of Duty Mobile e Free Fire)
    print("[4/6] Injetando mapeamento de controles (Call of Duty & Free Fire)...")
    db_path = os.path.expandvars(r'%APPDATA%\Tencent\Androws\db\Configs.db')
    if os.path.exists(db_path):
        try:
            con = sqlite3.connect(db_path, timeout=15.0)
            cur = con.cursor()
            cur.execute("PRAGMA busy_timeout = 8000;")
            
            triggers = cur.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger'").fetchall()
            for tname, tsql in triggers:
                cur.execute(f"DROP TRIGGER IF EXISTS {tname}")
            con.commit()
            
            import setup_both_mp_and_br
            import inject_freefire_keymap
            
            for tname, tsql in triggers:
                if tsql:
                    try: cur.execute(tsql)
                    except: pass
                    
            con.commit()
            try: cur.execute("PRAGMA wal_checkpoint(PASSIVE);")
            except: pass
            con.close()
            print("[✔] Controles do Call of Duty Mobile e Free Fire configurados com sucesso!")
        except Exception as e:
            print(f"[!] Aviso no banco de dados de controles: {e}")
    print()
    
    # 5. Criar atalhos na Área de Trabalho com Logo DLuz
    print("[5/6] Atualizando atalhos da Area de Trabalho com Logo DLuz...")
    try:
        desktop_dir = os.path.expanduser(r'~\Desktop')
        sh_targets = [
            ("Tencent Androws - Emulador Android.lnk", os.path.join(app_root, "AndrowsLauncher.exe"), app_root, "Emulador Android Tencent Customizado DLuz Games"),
            ("Tencent Androws - Loja e Jogos.lnk", os.path.join(app_root, "5.10.7110.6414", "AndrowsStore.exe"), os.path.join(app_root, "5.10.7110.6414"), "Loja e Catalogo de Jogos do Emulador"),
            ("Tencent Androws - Direto.lnk", os.path.join(app_root, "5.10.7110.6414", "Androws.exe"), os.path.join(app_root, "5.10.7110.6414"), "Motor Principal do Emulador Android")
        ]
        
        for name, tgt, wdir, desc in sh_targets:
            sc_path = os.path.join(desktop_dir, name)
            ps = f'''$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('{sc_path}'); $s.TargetPath = '{tgt}'; $s.WorkingDirectory = '{wdir}'; $s.Description = '{desc}'; $s.IconLocation = '{root_ico},0'; $s.Save()'''
            subprocess.run(["powershell", "-Command", ps], capture_output=True)
            
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
        print("[✔] Atalhos criados na Area de Trabalho com o Logo DLuz!")
    except Exception as e:
        print(f"[!] Erro ao atualizar atalhos: {e}")
    print()
    
    # 6. Finalização
    print("======================================================================")
    print("        🎉 INSTALACAO E PERSONALIZACAO CONCLUIDAS COM SUCESSO! 🎉")
    print("======================================================================")
    print("  • Logo Oficial da DLuz Games aplicado no Emulador e Atalhos")
    print("  • Interface Qt e Menus do Emulador: 100% Portugues (PT-BR)")
    print("  • Janela de Configuracoes e Loja: 100% Portugues (PT-BR)")
    print("  • Fontes e DPI calibrados com perfeicao")
    print("  • Controles Pro (Call of Duty Mobile e Free Fire) ativados")
    print("======================================================================\n")
    
    input("Pressione ENTER para fechar...")

if __name__ == '__main__':
    main()
