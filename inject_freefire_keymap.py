import sqlite3
import os
import io
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = os.path.expandvars(r'%APPDATA%\Tencent\Androws\db\Configs.db')
print(f"Connecting to {db_path}...")

ff_xml = """<KeyMapSolution SolutionID="{\"id\":\"1787152146654\",\"type\":0}" SolutionName="Free Fire Padrão Pro" InputType="1" SilentUpdate="0">
  <KeyMapping ItemName="Right Click" Point_X="0.855000" Point_Y="0.520000" Description="Mirar" Remark="" MiniVisiable="true" MiniDisable="false" ShowOnLockAsciiCode="192" AsciiCode="-2" />
  <KeyMapping ItemName="Space" Point_X="0.940000" Point_Y="0.760000" Description="Pular" Remark="" MiniVisiable="true" MiniDisable="false" LocationType="0" ColorType="0" AsciiCode="32" />
  <KeyMapping ItemName="C" Point_X="0.900000" Point_Y="0.860000" Description="Agachar" Remark="" MiniVisiable="true" MiniDisable="false" LocationType="0" ColorType="0" AsciiCode="67" />
  <KeyMapping ItemName="Z" Point_X="0.960000" Point_Y="0.910000" Description="Deitar" Remark="" MiniVisiable="true" MiniDisable="false" LocationType="0" ColorType="0" AsciiCode="90" />
  <KeyMapping ItemName="R" Point_X="0.920000" Point_Y="0.250000" Description="Recarregar" Remark="" MiniVisiable="true" MiniDisable="false" LocationType="0" ColorType="0" AsciiCode="82" />
  <KeyMapping ItemName="1" Point_X="0.750000" Point_Y="0.120000" Description="Arma 1" Remark="" MiniVisiable="true" MiniDisable="false" LocationType="0" ColorType="0" AsciiCode="49" />
  <KeyMapping ItemName="2" Point_X="0.840000" Point_Y="0.120000" Description="Arma 2" Remark="" MiniVisiable="true" MiniDisable="false" LocationType="0" ColorType="0" AsciiCode="50" />
  <KeyMapping ItemName="3" Point_X="0.930000" Point_Y="0.120000" Description="Pistola / Soco" Remark="" MiniVisiable="true" MiniDisable="false" LocationType="0" ColorType="0" AsciiCode="51" />
  <KeyMapping ItemName="4" Point_X="0.150000" Point_Y="0.500000" Description="Kit Médico" Remark="" MiniVisiable="true" MiniDisable="false" LocationType="0" ColorType="0" AsciiCode="52" />
  <KeyMapping ItemName="5" Point_X="0.380000" Point_Y="0.850000" Description="Granada / Gel" Remark="" MiniVisiable="true" MiniDisable="false" LocationType="0" ColorType="0" AsciiCode="53" />
  <KeyMapping ItemName="G" Point_X="0.380000" Point_Y="0.850000" Description="Granada / Gel" Remark="" MiniVisiable="true" MiniDisable="false" LocationType="0" ColorType="0" AsciiCode="71" />
  <KeyMapping ItemName="E" Point_X="0.800000" Point_Y="0.650000" Description="Habilidade" Remark="" MiniVisiable="true" MiniDisable="false" LocationType="0" ColorType="0" AsciiCode="69" />
  <KeyMapping ItemName="F" Point_X="0.720000" Point_Y="0.300000" Description="Loot 1 / Usar" Remark="" MiniVisiable="true" MiniDisable="false" LocationType="0" ColorType="0" AsciiCode="70" />
  <KeyMapping ItemName="G" Point_X="0.720000" Point_Y="0.370000" Description="Loot 2" Remark="" MiniVisiable="true" MiniDisable="false" LocationType="0" ColorType="0" AsciiCode="71" />
  <KeyMapping ItemName="H" Point_X="0.720000" Point_Y="0.440000" Description="Loot 3" Remark="" MiniVisiable="true" MiniDisable="false" LocationType="0" ColorType="0" AsciiCode="72" />
  <KeyMapping ItemName="Shift" Point_X="0.220000" Point_Y="0.560000" Description="Correr" Remark="" MiniVisiable="true" MiniDisable="false" LocationType="0" ColorType="0" AsciiCode="16" />
  <KeyMapping ItemName="Tab" Point_X="0.080000" Point_Y="0.850000" Description="Mochila" Remark="" MiniVisiable="true" MiniDisable="false" LocationType="0" ColorType="0" AsciiCode="9" />
  <KeyMapping ItemName="M" Point_X="0.080000" Point_Y="0.120000" Description="Mapa" Remark="" MiniVisiable="true" MiniDisable="false" LocationType="0" ColorType="0" AsciiCode="77" />
  <KeyMapping ItemName="F1" Point_X="0.500000" Point_Y="0.500000" Description="Trava de Mira" Remark="" MiniVisiable="true" MiniDisable="false" LocationType="0" ColorType="0" AsciiCode="112" />
  <KeyMappingEx ItemName="WASD" Point_X="0.165000" Point_Y="0.745000" Description="Movimento" Remark="" MiniVisiable="true" MiniDisable="false" HideTipsAlways="0" LocationType="0" ColorType="0" WidthRatio="0.000000" HeightRatio="0.000000" Type="CrossKey" UP_AsciiCode="87" DOWN_AsciiCode="83" LEFT_AsciiCode="65" RIGHT_AsciiCode="68" Offset="0.070000" ShiftOffset="0.100000" Speed="0.000000" />
  <KeyMappingEx ItemName="Botão Esquerdo" Point_X="0.885000" Point_Y="0.725000" Description="Atirar" Remark="" MiniVisiable="true" MiniDisable="false" AutoActive="1" LocationType="0" ColorType="0" WidthRatio="0.000000" HeightRatio="0.000000" Type="LClick" LOCK_AsciiCode="192" />
  <KeyMappingEx ItemName="~" Point_X="0.550000" Point_Y="0.500000" Description="Controle de Câmera" Remark="" MiniVisiable="true" MiniDisable="false" HideTipsAlways="0" AutoActive="1" Raw="1" LocationType="0" ColorType="0" WidthRatio="0.000000" HeightRatio="0.000000" Type="RClick" Offset="0.450000" LOCK_AsciiCode="192" AsciiCode="192" MouseResetTime="500" Sensi_X="1.000000" Sensi_Y="1.000000" />
</KeyMapSolution>"""

mode_json = """{
    "lastSolutionId": "1787152146654",
    "lastSolutionIdType": {
        "id": "1787152146654",
        "type": 0
    },
    "modeId": 84307,
    "solutions": {
        "1787152146654": {
            "inputType": 1,
            "solutionId": "1787152146654",
            "solutionName": "Free Fire Padrão Pro",
            "sourceDesc": {
                "last_badge_version_id": "193565",
                "solutionId": "84307",
                "sourceType": 1,
                "versionId": "193565"
            }
        }
    }
}"""

con = sqlite3.connect(db_path, timeout=10.0)
cur = con.cursor()
cur.execute("PRAGMA busy_timeout = 5000;")

# Update Free Fire entries
cur.execute("INSERT OR REPLACE INTO key_map_configs_cache_official (id, key, value0, value1, value2, value3, value4) VALUES (64, 'lastmodeid.unlogin.com.dts.freefireth', '84307', NULL, NULL, NULL, NULL)")
cur.execute("INSERT OR REPLACE INTO key_map_configs_cache_official (id, key, value0, value1, value2, value3, value4) VALUES (65, 'keymap_mode.unlogin.com.dts.freefireth.84307', ?, NULL, NULL, NULL, NULL)", (mode_json,))
cur.execute("INSERT OR REPLACE INTO key_map_configs_cache_official (id, key, value0, value1, value2, value3, value4) VALUES (67, 'offcial_keymap_data2.com.dts.freefireth.84307.193565', ?, '193565', NULL, NULL, NULL)", (ff_xml,))
cur.execute("INSERT OR REPLACE INTO key_map_configs_cache_official (id, key, value0, value1, value2, value3, value4) VALUES (69, 'keymap_data.unlogin.com.dts.freefireth.84307.1787152146654', ?, NULL, NULL, NULL, NULL)", (ff_xml,))

# Enable on screen key overlay
cur.execute("""
INSERT OR REPLACE INTO key_map_aux_setting 
(pkg_name, tips, remark, opacity, mode_map, preview_window, preview_window_opacity, color_area, animation, preview_window_conflict, enable_animation, last_known_visibility_mode)
VALUES ('com.dts.freefireth', 1, 1, 0.8, NULL, 0, NULL, 1, 1, 0, 1, 1)
""")

con.commit()
con.close()
print("\nFree Fire key mapping injected and activated successfully in Configs.db!")
