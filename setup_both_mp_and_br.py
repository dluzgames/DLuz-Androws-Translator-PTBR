# -*- coding: utf-8 -*-
import sqlite3
import os
import io
import sys
import json
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = os.path.expandvars(r'%APPDATA%\Tencent\Androws\db\Configs.db')
con = sqlite3.connect(db_path, timeout=15.0)
cur = con.cursor()
cur.execute("PRAGMA busy_timeout = 8000;")

# 1. Drop triggers temporarily
triggers = cur.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger'").fetchall()
for tname, tsql in triggers:
    cur.execute(f"DROP TRIGGER IF EXISTS {tname}")
con.commit()

# 2. XML templates
from translate_keymap_xml_clean import DESC_MAP, translate_xml_content

mp_row = cur.execute("SELECT value0 FROM key_map_configs_cache_official WHERE key = 'offcial_keymap_data2.com.activision.callofduty.shooter.145.145'").fetchone()
mp_xml = mp_row[0] if mp_row and mp_row[0] else ""
mp_xml_pt = translate_xml_content(mp_xml)

br_row = cur.execute("SELECT value0 FROM key_map_configs_cache_official WHERE key = 'offcial_keymap_data2.com.activision.callofduty.shooter.146.146'").fetchone()
br_xml = br_row[0] if br_row and br_row[0] else ""
br_xml_pt = translate_xml_content(br_xml)

sol_mp_id = "1787152993686"
sol_mp_official = "1752061764155"
sol_br_id = "1787153423079"
sol_br_official = "1752061764139"

# 3. Combined official config XML with BOTH MP (145) and BR (146)
offcial_cfg_xml = """<Item ApkName="com.activision.callofduty.shooter">
  <KeyMapMode ModeID="145" Name="MP - 16:9" Desciption="Multijogador" Thumbnail="https://static.sj.qq.com/xy/yyb_official_website/vTee3TEK.png" ListImage="" PreviewImage="" Level="0" GroupList="">
    <KeyMapSolution SolutionID="145" SolutionName="MP - 16:9" Version="15634" />
    <KeyMapSolution SolutionID="1752061764155" SolutionName="Multijogador (MP)" Version="15634" />
    <KeyMapSolution SolutionID="1787152993686" SolutionName="MP - 16:9" Version="15634" />
  </KeyMapMode>
  <KeyMapMode ModeID="146" Name="BR - 16:9" Desciption="Battle Royale" Thumbnail="https://static.sj.qq.com/xy/yyb_official_website/vTee3TEK.png" ListImage="" PreviewImage="" Level="0" GroupList="">
    <KeyMapSolution SolutionID="146" SolutionName="BR - 16:9" Version="12417" />
    <KeyMapSolution SolutionID="1752061764139" SolutionName="Battle Royale (BR)" Version="12417" />
    <KeyMapSolution SolutionID="1787153423079" SolutionName="BR - 16:9" Version="12417" />
    <KeyMapSolution SolutionID="1765593240066" SolutionName="DMZ" Version="12417" />
  </KeyMapMode>
</Item>"""

# 4. Mode JSON for MP (145)
mode_145_json = json.dumps({
    "lastSolutionId": sol_mp_id,
    "lastSolutionIdType": {"id": sol_mp_id, "type": 0},
    "modeId": 145,
    "solutions": {
        sol_mp_official: {
            "inputType": 1,
            "solutionId": sol_mp_official,
            "solutionName": "Multijogador (MP)",
            "sourceDesc": {"last_badge_version_id": "15634", "solutionId": "145", "sourceType": 1, "versionId": "15634"}
        },
        sol_mp_id: {
            "inputType": 1,
            "solutionId": sol_mp_id,
            "solutionName": "MP - 16:9"
        }
    }
}, ensure_ascii=False)

# Mode JSON for BR (146)
mode_146_json = json.dumps({
    "lastSolutionId": sol_br_id,
    "lastSolutionIdType": {"id": sol_br_id, "type": 0},
    "modeId": 146,
    "solutions": {
        sol_br_official: {
            "inputType": 1,
            "solutionId": sol_br_official,
            "solutionName": "Battle Royale (BR)",
            "sourceDesc": {"last_badge_version_id": "12417", "solutionId": "146", "sourceType": 1, "versionId": "12417"}
        },
        sol_br_id: {
            "inputType": 1,
            "solutionId": sol_br_id,
            "solutionName": "BR - 16:9"
        },
        "1765593240066": {
            "inputType": 1,
            "solutionId": "1765593240066",
            "solutionName": "DMZ"
        }
    }
}, ensure_ascii=False)

# 5. Insert both modes and their solutions into database
cur.execute("INSERT OR REPLACE INTO key_map_configs_cache_official (key, value0, value1, value2, value3, value4) VALUES ('lastmodeid.unlogin.com.activision.callofduty.shooter', '145', NULL, NULL, NULL, NULL)")
cur.execute("INSERT OR REPLACE INTO key_map_configs_cache_official (key, value0, value1, value2, value3, value4) VALUES ('recentlyused_mode.com.activision.callofduty.shooter', '{\"145\":1787153394,\"146\":1787154006}', NULL, NULL, NULL, NULL)")
cur.execute("INSERT OR REPLACE INTO key_map_configs_cache_official (key, value0, value1, value2, value3, value4) VALUES ('offcial_config2.com.activision.callofduty.shooter', NULL, ?, ?, NULL, NULL)", (offcial_cfg_xml, offcial_cfg_xml))

cur.execute("INSERT OR REPLACE INTO key_map_configs_cache_official (key, value0, value1, value2, value3, value4) VALUES ('keymap_mode.unlogin.com.activision.callofduty.shooter.145', ?, NULL, NULL, NULL, NULL)", (mode_145_json,))
cur.execute("INSERT OR REPLACE INTO key_map_configs_cache_official (key, value0, value1, value2, value3, value4) VALUES ('keymap_mode.unlogin.com.activision.callofduty.shooter.146', ?, NULL, NULL, NULL, NULL)", (mode_146_json,))

# Populate MP solutions
cur.execute("INSERT OR REPLACE INTO key_map_configs_cache_official (key, value0, value1, value2, value3, value4) VALUES ('offcial_keymap_data2.com.activision.callofduty.shooter.145.145', ?, '15634', NULL, NULL, NULL)", (mp_xml_pt,))
cur.execute("INSERT OR REPLACE INTO key_map_configs_cache_official (key, value0, value1, value2, value3, value4) VALUES ('offcial_keymap_data2.com.activision.callofduty.shooter.145.566632', ?, '17179', NULL, NULL, NULL)", (mp_xml_pt,))
cur.execute("INSERT OR REPLACE INTO key_map_configs_cache_official (key, value0, value1, value2, value3, value4) VALUES ('keymap_data.unlogin.com.activision.callofduty.shooter.145.1787152993686', ?, NULL, NULL, NULL, NULL)", (mp_xml_pt,))
cur.execute("INSERT OR REPLACE INTO key_map_configs_cache_official (key, value0, value1, value2, value3, value4) VALUES ('keymap_data.unlogin.com.activision.callofduty.shooter.145.1752061764155', ?, NULL, NULL, NULL, NULL)", (mp_xml_pt,))

# Populate BR solutions
cur.execute("INSERT OR REPLACE INTO key_map_configs_cache_official (key, value0, value1, value2, value3, value4) VALUES ('offcial_keymap_data2.com.activision.callofduty.shooter.146.146', ?, '12417', NULL, NULL, NULL)", (br_xml_pt,))
cur.execute("INSERT OR REPLACE INTO key_map_configs_cache_official (key, value0, value1, value2, value3, value4) VALUES ('offcial_keymap_data2.com.activision.callofduty.shooter.146.566635', ?, '17175', NULL, NULL, NULL)", (br_xml_pt,))
cur.execute("INSERT OR REPLACE INTO key_map_configs_cache_official (key, value0, value1, value2, value3, value4) VALUES ('keymap_data.unlogin.com.activision.callofduty.shooter.146.1752061764139', ?, NULL, NULL, NULL, NULL)", (br_xml_pt,))
cur.execute("INSERT OR REPLACE INTO key_map_configs_cache_official (key, value0, value1, value2, value3, value4) VALUES ('keymap_data.unlogin.com.activision.callofduty.shooter.146.1787153423079', ?, NULL, NULL, NULL, NULL)", (br_xml_pt,))

# Ensure visual overlay
cur.execute("""
INSERT OR REPLACE INTO key_map_aux_setting 
(pkg_name, tips, remark, opacity, mode_map, preview_window, preview_window_opacity, color_area, animation, preview_window_conflict, enable_animation, last_known_visibility_mode)
VALUES ('com.activision.callofduty.shooter', 1, 1, 0.8, NULL, 0, NULL, 1, 1, 0, 1, 1)
""")

# Recreate triggers
for tname, tsql in triggers:
    if tsql:
        try: cur.execute(tsql)
        except: pass

con.commit()
try: cur.execute("PRAGMA wal_checkpoint(PASSIVE);")
except: pass
con.close()

print("BOTH MP and BR modes are now simultaneously active and switchable!")
