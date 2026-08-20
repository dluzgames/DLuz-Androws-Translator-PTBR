# -*- coding: utf-8 -*-
import sqlite3
import os
import io
import sys
import re

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DESC_MAP = {
    '2级背包': 'Mochila Nv2',
    '3级背包': 'Mochila Nv3',
    'CD上一首': 'Música Ant.',
    'CD下一首': 'Próx. Música',
    '上': 'Cima',
    '上潜': 'Subir',
    '上潜中': 'Subindo',
    '上车': 'Entrar',
    '上飞': 'Voar Cima',
    '上飞（躲猫猫）': 'Voar Cima',
    '下': 'Baixo',
    '下潜': 'Mergulhar',
    '下潜中': 'Mergulhando',
    '下蹲': 'Agachar',
    '下车': 'Sair Veículo',
    '下飞': 'Voar Baixo',
    '下飞（躲猫猫）': 'Voar Baixo',
    '义肢使用': 'Usar Prótese',
    '乘车': 'Entrar Veículo',
    '乘车(驾驶位有人)': 'Passageiro',
    '了断（恶魔岛）': 'Executar',
    '使用核弹': 'Bomba Nuclear',
    '信号': 'Marcar',
    '假身（躲猫猫）': 'Clone',
    '关背包': 'Fechar Mochila',
    '关闭CD': 'Parar Música',
    '关闭地图': 'Fechar Mapa',
    '关闭快递': 'Fechar Loot',
    '关闭捡物': 'Fechar Loot',
    '关闭捡物（打开背包时）': 'Fechar Loot',
    '关闭设置': 'Fechar Config.',
    '关闭购物机': 'Fechar Loja',
    '关闭躲猫猫介绍': 'Fechar Guia',
    '刀': 'Faca',
    '切换位置': 'Trocar Assento',
    '切换手雷': 'Trocar Granada',
    '切换技能（出生地）': 'Trocar Skill',
    '切换技能（复活专机）': 'Trocar Skill',
    '刹车': 'Freio',
    '刹车按住（无人机）': 'Freio Drone',
    '刹车（无人机）': 'Freio Drone',
    '加速跑': 'Correr',
    '升级技能': 'Evoluir Skill',
    '单发/连发': 'Modo Disparo',
    '单发/...': 'Modo Disparo',
    '取消': 'Cancelar',
    '取消下蹲': 'Levantar',
    '取消丢雷': 'Cancelar Granada',
    '取消僵尸雷': 'Cancelar Granada',
    '取消瞄准': 'Sair da Mira',
    '取消瞄准（坦克）': 'Sair Mira Tanque',
    '取消离开': 'Cancelar Saída',
    '取消趴下': 'Levantar',
    '取消释放弓箭/盾牌': 'Cancelar',
    '右': 'Direita',
    '右键': 'Botão Dir.',
    '右键开镜': 'Mirar',
    '吃药': 'Curar',
    '商店（吃鸡模式）': 'Loja',
    '喷气芯片喷气': 'Jetpack',
    '喷气芯片喷气中': 'Jetpack Ativo',
    '地图': 'Mapa',
    '坦克夜视': 'Visão Noturna',
    '坦克的干扰弹': 'Flares Tanque',
    '塔克马载具机枪': 'Metralhadora',
    '塔克马载具机枪下': 'Sair Metralhadora',
    '塔克马载具跳': 'Pular Veículo',
    '塔克马静音': 'Silencioso',
    '夜视仪关': 'Visão Noturna Off',
    '夜视仪开': 'Visão Noturna On',
    '字母键': 'Atalho',
    '字母键划线': 'Gesto',
    '安装炸弹': 'Plantar Bomba',
    '导弹齐射': 'Mísseis',
    '射击': 'Atirar',
    '小空投': 'AirDrop',
    '左': 'Esquerda',
    '左键': 'Botão Esq.',
    '开伞': 'Paraquedas',
    '开关门': 'Porta',
    '开启/关闭广播': 'Voz Geral',
    '开启/关闭语音': 'Mic On/Off',
    '开启/静音广播': 'Mutar Voz',
    '开启功能': 'Ativar',
    '开火': 'Atirar',
    '开车': 'Dirigir',
    '开车第一种模式': 'Dirigir',
    '异变围城扳手': 'Chave Inglesa',
    '弓箭': 'Arco',
    '引爆': 'Detonar',
    '引爆c4': 'Detonar C4',
    '弹跳': 'Salto Alto',
    '影刃': 'Lâmina Sombria',
    '快速挥刀': 'Ataque Faca',
    '快速说话': 'Chat Rápido',
    '快速说话(第一句)': 'Chat 1',
    '快速说话(第二句)': 'Chat 2',
    '急救包': 'Kit Médico',
    '感应弹': 'Sensor',
    '战斗机加速': 'Acelerar Jato',
    '战斗机加速/特殊载具跳跃': 'Acelerar/Pular',
    '战斗机加速/刹车': 'Acelerar/Freio',
    '战斗机导弹': 'Míssil Jato',
    '战斗机机关枪': 'Metralhadora Jato',
    '战斗机的刹车': 'Freio Jato',
    '战斗机的干扰弹': 'Flares Jato',
    '战绩面板': 'Placar',
    '手榴弹': 'Granada',
    '手雷': 'Granada',
    '打开CD': 'Tocar Música',
    '打开地图': 'Mapa',
    '打开地图时取消标记': 'Desmarcar',
    '打开礼物': 'Presente',
    '打开空投': 'AirDrop',
    '打开设置': 'Config.',
    '打开...': 'Abrir',
    '点开...': 'Abrir',
    '扔回丢雷': 'Rebater Granada',
    '扫描': 'Escanear',
    '技能': 'Habilidade',
    '抬头按住（摩托）': 'Empinar Moto',
    '抬头（摩托）': 'Empinar Moto',
    '拆弹': 'Desarmar',
    '拳套加速': 'Soco Veloz',
    '拾取防爆装置': 'Troféu',
    '捡东西鼠标滚轮': 'Loot Scroll',
    '捡快递/空投': 'Loot/AirDrop',
    '捡物': 'Loot',
    '捡物(打开背包时)': 'Loot',
    '拾物': 'Loot',
    '换1号武器': 'Arma 1',
    '换2号武器': 'Arma 2',
    '换位置': 'Trocar Lugar',
    '换弹': 'Recarregar',
    '换形（躲猫猫）': 'Transformar',
    '换武器': 'Trocar Arma',
    '换背包': 'Trocar Mochila',
    '摄像头（躲猫猫）': 'Câmera',
    '救人': 'Socorrer',
    '救援...': 'Socorrer',
    '新地图吃药': 'Curar',
    '新地图道具1': 'Item 1',
    '新地图道具2': 'Item 2',
    '新地图道具3': 'Item 3',
    '新年手雷': 'Granada Festiva',
    '新空投确认': 'Confirmar Drop',
    '新空投翻页': 'Página Drop',
    '无畏战士': 'Juggernaut',
    '普通护甲': 'Colete Nv1',
    '暂停CD': 'Pausar Som',
    '暴风雨': 'Tempestade',
    '止痛针': 'Analgésico',
    '止血凝胶': 'Bandagem',
    '歼灭者': 'Aniquilador',
    '毒气弹': 'Gás Tóxico',
    '求助': 'Pedir Ajuda',
    '油门': 'Acelerar',
    '滑雪板': 'Snowboard',
    '滑雪板跳': 'Pulo Snowboard',
    '滚轮切枪': 'Scroll: Arma',
    '滚轮滑动': 'Scroll',
    '滚轮点击': 'Scroll Clique',
    '滚轮缩放': 'Scroll: Zoom',
    '点开快递包': 'Abrir Loot',
    '点开快递（捡物存在）': 'Abrir Loot',
    '点开快递（点开捡物存在）': 'Abrir Loot',
    '点开捡物': 'Abrir Loot',
    '点开捡物/快递': 'Abrir Loot',
    '点开捡物（打开背包时）': 'Abrir Loot',
    '点开捡物（捡快递、背包存在）': 'Abrir Loot',
    '点开捡物（捡快递存在）': 'Abrir Loot',
    '烟雾弹': 'Fumaça',
    '爬楼梯（团队模式）': 'Subir Escada',
    '特级护甲': 'Colete Nv3',
    '直升机炮手': 'Artilheiro',
    '直升飞机的攻击': 'Ataque Heli',
    '盾牌': 'Escudo',
    '盾牌炮塔': 'Torreta',
    '盾牌炮塔拿起': 'Pegar Torreta',
    '瞄准': 'Mirar',
    '离开小蜜蜂': 'Sair Drone',
    '离开机甲': 'Sair Mecha',
    '移动': 'Mover',
    '空对地导弹': 'Míssil Predator',
    '空投（一击必杀）': 'AirDrop Pro',
    '空格': 'Espaço',
    '第1/3人称切换': '1ª/3ª Pessoa',
    '第1/...': '1ª/3ª Pessoa',
    '第一种开车模式': 'Dirigir 1',
    '第一种开车模式_按着': 'Dirigir 1',
    '单车...': 'Dirigir',
    '缆绳': 'Tirolesa',
    '缆绳中': 'Na Tirolesa',
    '缆车（恶魔岛）': 'Teleférico',
    '翻滚': 'Rolar',
    '背包': 'Mochila',
    '蜜蜂侵入': 'Hack Drone',
    '蜜蜂扫描': 'Scan Drone',
    '蜜蜂第一视角': 'Drone 1ª Pes.',
    '蜜蜂第三视角': 'Drone 3ª Pes.',
    '表情': 'Emote',
    '视角': 'Olhar',
    '语音按住': 'Falar (Mic)',
    '购物机上一个': 'Loja Ant.',
    '购物机下一个': 'Loja Próx.',
    '购物机确认': 'Comprar',
    '足球': 'Chutar Bola',
    '趴下': 'Deitar',
    '跳伞（单人）': 'Salto Solo',
    '跳伞（四人）': 'Salto Esquadrão',
    '跳跃': 'Pular',
    '返回设置': 'Voltar',
    '进入机甲': 'Entrar Mecha',
    '连环闪光弹': 'Flash Quádrupla',
    '选择手雷解锁鼠标（爆破模式）': 'Escolher Granada',
    '锁定（躲猫猫）': 'Travar',
    '闪光弹': 'Flash',
    '闪光弹（躲猫猫）': 'Flash',
    '防弹插板': 'Placa Blindada',
    '防弹衣': 'Colete',
    '防空炮出': 'Sair Antiaérea',
    '防空炮进': 'Entrar Antiaérea',
    '集束炸弹': 'Ataque Aéreo',
    '雪人手雷': 'Granada Boneco',
    '震爆弹': 'Concussão',
    '飞机的干扰弹': 'Flares',
    '飞机雷': 'Bomba Aérea',
    '高级护甲': 'Colete Nv2',
    '鸣笛': 'Buzinar',
    '鸣笛中': 'Buzinando',
    '鼠标左键': 'Botão Esq.',
    '鼠标滚轮': 'Scroll',
    '枪1': 'Arma 1',
    '枪2': 'Arma 2',
    '枪3': 'Arma 3',
    '枪4': 'Arma 4',
    '组合键': 'Combos',
    '这里空空如也...': 'Nenhum combo configurado...',
    '按Ctrl+J显示/隐藏预览窗': 'Ctrl+J: Exibir/Ocultar Prévia',
    '按%1显示/隐藏预览窗': '%1: Exibir/Ocultar Prévia',
    '团队竞技模式': 'Multijogador (MP)',
    '使命战场模式': 'Battle Royale (BR)',
    '官方默认方案': 'Padrão Oficial',
    '默认模式': 'Modo Padrão',
}

def translate_xml_content(text):
    if not text: return text
    
    def repl_desc(m):
        orig = m.group(1)
        pt = DESC_MAP.get(orig, orig)
        return f'Description="{pt}"'
        
    def repl_item(m):
        orig = m.group(1)
        pt = DESC_MAP.get(orig, orig)
        return f'ItemName="{pt}"'
        
    def repl_sol(m):
        orig = m.group(1)
        pt = DESC_MAP.get(orig, orig)
        return f'SolutionName="{pt}"'
        
    res = re.sub(r'Description="([^"]+)"', repl_desc, text)
    res = re.sub(r'ItemName="([^"]+)"', repl_item, res)
    res = re.sub(r'SolutionName="([^"]+)"', repl_sol, res)
    return res

if __name__ == '__main__':
    db_path = os.path.expandvars(r'%APPDATA%\Tencent\Androws\db\Configs.db')
    con = sqlite3.connect(db_path, timeout=10.0)
    cur = con.cursor()
    cur.execute("PRAGMA busy_timeout = 5000;")

    # 1. Fetch trigger DDLs
    triggers = cur.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger'").fetchall()
    print(f"Dropping {len(triggers)} triggers temporarily...")
    for tname, tsql in triggers:
        cur.execute(f"DROP TRIGGER IF EXISTS {tname}")

    # 2. Update all rows in key_map_configs_cache_official
    rows = cur.execute("SELECT id, key, value0, value1, value2 FROM key_map_configs_cache_official").fetchall()
    print(f"Updating {len(rows)} keymap cache rows...")
    updated_cache = 0
    for r in rows:
        rid, rkey, v0, v1, v2 = r
        new_v0 = translate_xml_content(v0) if v0 else v0
        new_v1 = translate_xml_content(v1) if v1 else v1
        new_v2 = translate_xml_content(v2) if v2 else v2
        if new_v0 != v0 or new_v1 != v1 or new_v2 != v2:
            cur.execute("UPDATE key_map_configs_cache_official SET value0 = ?, value1 = ?, value2 = ? WHERE id = ?", (new_v0, new_v1, new_v2, rid))
            updated_cache += 1

    # 3. Update configs table
    cfg_rows = cur.execute("SELECT id, key, value FROM configs").fetchall()
    print(f"Updating {len(cfg_rows)} rows in configs table...")
    updated_cfg = 0
    for r in cfg_rows:
        rid, rkey, val = r
        if val:
            new_val = translate_xml_content(val)
            if new_val != val:
                cur.execute("UPDATE configs SET value = ? WHERE id = ?", (new_val, rid))
                updated_cfg += 1

    # 4. Recreate triggers
    print(f"Recreating {len(triggers)} triggers...")
    for tname, tsql in triggers:
        if tsql:
            cur.execute(tsql)

    cur.execute("PRAGMA wal_checkpoint(FULL);")
    con.commit()
    con.close()
    print(f"\nSUCCESS! Updated {updated_cache} keymap cache entries and {updated_cfg} configs entries to Portuguese!")
