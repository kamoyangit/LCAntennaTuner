import streamlit as st
import numpy as np

# --- SVG描画用関数 ---
def generate_circuit_svg(topology, series_comp, shunt_comp, series_val, shunt_val, r_load, x_load, tx_ratio, tx_direction):
    """
    回路構成と定数を受け取り、SVG形式の回路図文字列を返す関数
    """
    
    # SVG基本設定
    width = 620 
    height = 240
    line_color = "black"
    stroke_width = 2
    
    # --- 部品描画パーツ ---
    def draw_inductor_h(x, y): # 水平コイル
        return f"""
        <path d="M {x},{y} l 10,0 q 5,-15 10,0 t 10,0 t 10,0 t 10,0 l 10,0" 
              fill="none" stroke="{line_color}" stroke-width="{stroke_width}"/>
        """
    
    def draw_inductor_v(x, y): # 垂直コイル
        return f"""
        <path d="M {x},{y} l 0,10 q -15,5 0,10 t 0,10 t 0,10 t 0,10 l 0,10" 
              fill="none" stroke="{line_color}" stroke-width="{stroke_width}"/>
        """

    def draw_capacitor_h(x, y): # 水平コンデンサ
        return f"""
        <line x1="{x}" y1="{y}" x2="{x+25}" y2="{y}" stroke="{line_color}" stroke-width="{stroke_width}" />
        <line x1="{x+25}" y1="{y-10}" x2="{x+25}" y2="{y+10}" stroke="{line_color}" stroke-width="{stroke_width}" />
        <line x1="{x+35}" y1="{y-10}" x2="{x+35}" y2="{y+10}" stroke="{line_color}" stroke-width="{stroke_width}" />
        <line x1="{x+35}" y1="{y}" x2="{x+60}" y2="{y}" stroke="{line_color}" stroke-width="{stroke_width}" />
        """

    def draw_capacitor_v(x, y): # 垂直コンデンサ
        return f"""
        <line x1="{x}" y1="{y}" x2="{x}" y2="{y+25}" stroke="{line_color}" stroke-width="{stroke_width}" />
        <line x1="{x-10}" y1="{y+25}" x2="{x+10}" y2="{y+25}" stroke="{line_color}" stroke-width="{stroke_width}" />
        <line x1="{x-10}" y1="{y+35}" x2="{x+10}" y2="{y+35}" stroke="{line_color}" stroke-width="{stroke_width}" />
        <line x1="{x}" y1="{y+35}" x2="{x}" y2="{y+60}" stroke="{line_color}" stroke-width="{stroke_width}" />
        """

    def draw_source(x, y):
        return f"""
        <circle cx="{x}" cy="{y}" r="20" fill="white" stroke="{line_color}" stroke-width="{stroke_width}"/>
        <path d="M {x-10},{y} q 5,-10 10,0 t 10,0" fill="none" stroke="{line_color}" stroke-width="{stroke_width}"/>
        <line x1="{x}" y1="{y-20}" x2="{x}" y2="{y-50}" stroke="{line_color}" stroke-width="{stroke_width}" />
        <line x1="{x}" y1="{y+20}" x2="{x}" y2="{y+100}" stroke="{line_color}" stroke-width="{stroke_width}" />
        <text x="{x-30}" y="{y-60}" font-family="sans-serif" font-size="14" fill="blue">Source(50Ω)</text>
        """

    def draw_transformer(x, y):
        # トランスの簡易記号
        pri = f'<path d="M {x},{y-30} q 10,5 0,10 t 0,10 t 0,10 t 0,10 t 0,10" fill="none" stroke="{line_color}" stroke-width="{stroke_width}"/>'
        sec = f'<path d="M {x+20},{y-30} q -10,5 0,10 t 0,10 t 0,10 t 0,10 t 0,10" fill="none" stroke="{line_color}" stroke-width="{stroke_width}"/>'
        core = f'<line x1="{x+8}" y1="{y-25}" x2="{x+8}" y2="{y+25}" stroke="{line_color}" stroke-width="1" />' + \
               f'<line x1="{x+12}" y1="{y-25}" x2="{x+12}" y2="{y+25}" stroke="{line_color}" stroke-width="1" />'
        
        # 接続線 (上部は信号ライン y-50 まで伸ばす)
        conn_l = f'<line x1="{x}" y1="{y-30}" x2="{x}" y2="{y-50}" stroke="{line_color}" stroke-width="{stroke_width}" />' + \
                 f'<line x1="{x}" y1="{y+20}" x2="{x}" y2="{y+100}" stroke="{line_color}" stroke-width="{stroke_width}" />'
        conn_r = f'<line x1="{x+20}" y1="{y-30}" x2="{x+20}" y2="{y-50}" stroke="{line_color}" stroke-width="{stroke_width}" />' + \
                 f'<line x1="{x+20}" y1="{y+20}" x2="{x+20}" y2="{y+100}" stroke="{line_color}" stroke-width="{stroke_width}" />'

        if tx_direction == "down": 
            label = f"1 : {tx_ratio}"
        elif tx_direction == "up":
            label = f"{tx_ratio} : 1"
        else:
            label = "1:1"

        txt = f'<text x="{x+10}" y="{y-60}" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#880088">Trans</text>' + \
              f'<text x="{x+10}" y="{y+50}" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#880088">{label}</text>'

        return pri + sec + core + conn_l + conn_r + txt

    def draw_antenna(x, y):
        # 数値を丸めて表示
        r_disp = f"{r_load:.2f}"
        x_disp = f"{x_load:.2f}"
        
        return f"""
        <rect x="{x-15}" y="{y}" width="30" height="60" fill="white" stroke="{line_color}" stroke-width="{stroke_width}" />
        <text x="{x}" y="{y+35}" text-anchor="middle" font-family="sans-serif" font-size="12">Z_load</text>
        <line x1="{x}" y1="{y}" x2="{x}" y2="{y-50}" stroke="{line_color}" stroke-width="{stroke_width}" />
        <line x1="{x}" y1="{y+60}" x2="{x}" y2="{y+100}" stroke="{line_color}" stroke-width="{stroke_width}" />
        <text x="{x}" y="{y-60}" text-anchor="middle" font-family="sans-serif" font-size="14" fill="red">ANT</text>
        <text x="{x}" y="{y+130}" text-anchor="middle" font-family="sans-serif" font-size="12">R={r_disp}Ω</text>
        <text x="{x}" y="{y+145}" text-anchor="middle" font-family="sans-serif" font-size="12">X={x_disp}jΩ</text>
        """

    y_sig = 80
    y_gnd = 180
    x_src = 60
    x_trans = 450
    x_load_pos = 580

    svg_elements = []
    
    # GNDライン (共通)
    svg_elements.append(f'<line x1="{x_src}" y1="{y_gnd}" x2="{x_load_pos}" y2="{y_gnd}" stroke="{line_color}" stroke-width="{stroke_width}" />')
    svg_elements.append(draw_source(x_src, y_sig))

    lc_end_x = x_trans - 50 # LC回路の描画終了位置

    # --- LC回路部分の描画 ---
    if topology == "shunt_first": 
        node_x = x_src + 100
        svg_elements.append(f'<line x1="{x_src}" y1="{y_sig-50}" x2="{node_x}" y2="{y_sig-50}" stroke="{line_color}" stroke-width="{stroke_width}" />')
        svg_elements.append(f'<line x1="{node_x}" y1="{y_sig-50}" x2="{node_x}" y2="{y_sig}" stroke="{line_color}" stroke-width="{stroke_width}" />')
        if shunt_comp == "L":
            svg_elements.append(draw_inductor_v(node_x, y_sig))
            label_unit = "µH"
        else:
            svg_elements.append(draw_capacitor_v(node_x, y_sig))
            label_unit = "pF"
        svg_elements.append(f'<line x1="{node_x}" y1="{y_sig+60}" x2="{node_x}" y2="{y_gnd}" stroke="{line_color}" stroke-width="{stroke_width}" />')
        svg_elements.append(f'<text x="{node_x+10}" y="{y_sig+30}" font-family="sans-serif" font-size="12" fill="green">{shunt_comp}: {shunt_val:.1f}{label_unit}</text>')

        comp_x = node_x
        comp_y = y_sig - 50
        if series_comp == "L":
            svg_elements.append(draw_inductor_h(comp_x, comp_y))
            comp_len = 60
            label_unit = "µH"
        else:
            svg_elements.append(draw_capacitor_h(comp_x, comp_y))
            comp_len = 60
            label_unit = "pF"
        svg_elements.append(f'<text x="{comp_x+10}" y="{comp_y-10}" font-family="sans-serif" font-size="12" fill="green">{series_comp}: {series_val:.1f}{label_unit}</text>')
        
        # LC終端点までの線
        svg_elements.append(f'<line x1="{comp_x + comp_len}" y1="{comp_y}" x2="{lc_end_x}" y2="{comp_y}" stroke="{line_color}" stroke-width="{stroke_width}" />')

    else: 
        node_x = lc_end_x - 60 
        svg_elements.append(f'<line x1="{x_src}" y1="{y_sig-50}" x2="{x_src+40}" y2="{y_sig-50}" stroke="{line_color}" stroke-width="{stroke_width}" />')
        
        comp_x = x_src + 40
        comp_y = y_sig - 50
        if series_comp == "L":
            svg_elements.append(draw_inductor_h(comp_x, comp_y))
            comp_len = 60
            label_unit = "µH"
        else:
            svg_elements.append(draw_capacitor_h(comp_x, comp_y))
            comp_len = 60
            label_unit = "pF"
        svg_elements.append(f'<text x="{comp_x+10}" y="{comp_y-10}" font-family="sans-serif" font-size="12" fill="green">{series_comp}: {series_val:.1f}{label_unit}</text>')

        svg_elements.append(f'<line x1="{comp_x+comp_len}" y1="{comp_y}" x2="{node_x}" y2="{comp_y}" stroke="{line_color}" stroke-width="{stroke_width}" />')
        svg_elements.append(f'<line x1="{node_x}" y1="{comp_y}" x2="{node_x}" y2="{y_sig}" stroke="{line_color}" stroke-width="{stroke_width}" />')
        if shunt_comp == "L":
            svg_elements.append(draw_inductor_v(node_x, y_sig))
            label_unit = "µH"
        else:
            svg_elements.append(draw_capacitor_v(node_x, y_sig))
            label_unit = "pF"
        svg_elements.append(f'<line x1="{node_x}" y1="{y_sig+60}" x2="{node_x}" y2="{y_gnd}" stroke="{line_color}" stroke-width="{stroke_width}" />')
        svg_elements.append(f'<text x="{node_x+10}" y="{y_sig+30}" font-family="sans-serif" font-size="12" fill="green">{shunt_comp}: {shunt_val:.1f}{label_unit}</text>')

        # LC終端点までの線
        svg_elements.append(f'<line x1="{node_x}" y1="{comp_y}" x2="{lc_end_x}" y2="{comp_y}" stroke="{line_color}" stroke-width="{stroke_width}" />')

    # --- トランスと負荷への接続 ---
    if tx_ratio > 1:
        svg_elements.append(f'<line x1="{lc_end_x}" y1="{y_sig-50}" x2="{x_trans}" y2="{y_sig-50}" stroke="{line_color}" stroke-width="{stroke_width}" />')
        svg_elements.append(draw_transformer(x_trans, y_sig))
        svg_elements.append(f'<line x1="{x_trans+20}" y1="{y_sig-50}" x2="{x_load_pos}" y2="{y_sig-50}" stroke="{line_color}" stroke-width="{stroke_width}" />')
    else:
        svg_elements.append(f'<line x1="{lc_end_x}" y1="{y_sig-50}" x2="{x_load_pos}" y2="{y_sig-50}" stroke="{line_color}" stroke-width="{stroke_width}" />')

    svg_elements.append(draw_antenna(x_load_pos, y_sig))

    svg_code = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" style="background-color:#f9f9f9; border:1px solid #ddd; border-radius:5px;">' + "".join(svg_elements) + '</svg>'
    return svg_code

# --- 計算ロジック ---
def calculate_l_match(r_load, x_load, freq_mhz, power_w, z0=50):
    omega = 2 * np.pi * freq_mhz * 1e6
    results = {
        "topology": "", "topology_code": "", 
        "L_val": 0.0, "C_val": 0.0,
        "V_L_rms": 0.0, "V_L_peak": 0.0, "I_L_rms": 0.0, "I_L_peak": 0.0,
        "V_C_rms": 0.0, "V_C_peak": 0.0, "I_C_rms": 0.0, "I_C_peak": 0.0,
        "error": None,
        "series_comp": "", "shunt_comp": "", 
        "series_disp_val": 0.0, "shunt_disp_val": 0.0
    }

    v_in_rms = np.sqrt(power_w * z0)
    i_in_rms = np.sqrt(power_w / z0)

    if r_load <= 0:
        results["error"] = "整合後の抵抗値が正の値になりません。"
        return results

    i_out_rms = np.sqrt(power_w / r_load)
    v_out_complex = complex(r_load, x_load) * i_out_rms
    v_out_rms = abs(v_out_complex)
    
    # Case 1: Step-up
    if r_load < z0:
        term = (z0 / r_load) - 1
        if term < 0:
             results["error"] = "整合解が見つかりません。"
             return results
        Q_match = np.sqrt(term)
        Xs = Q_match * r_load - x_load
        X_total_series = Xs + x_load
        denominator = r_load**2 + X_total_series**2
        Bp = X_total_series / denominator 
        Xp = -1.0 / Bp
        
        results["topology"] = "並列素子(源側) - 直列素子(負荷側)"
        results["topology_code"] = "shunt_first"
        
        results["I_series"] = i_out_rms
        results["V_series"] = i_out_rms * abs(Xs)
        results["V_shunt"] = v_in_rms
        results["I_shunt"] = v_in_rms / abs(Xp)
        
        results["Xs"] = Xs
        results["Xp"] = Xp

    # Case 2: Step-down
    else: 
        z_load_mag2 = r_load**2 + x_load**2
        G_load = r_load / z_load_mag2
        B_load = -x_load / z_load_mag2
        term = (G_load / 50.0) - G_load**2
        
        if term < 0:
             if abs(term) < 1e-9: term = 0
             else:
                 results["error"] = "整合解が見つかりません。"
                 return results
        B_total = np.sqrt(term)
        Xs = B_total / (G_load**2 + B_total**2)
        B_add = B_total - B_load
        Xp = -1.0 / B_add if abs(B_add) > 1e-12 else 1e9
        
        results["topology"] = "直列素子(源側) - 並列素子(負荷側)"
        results["topology_code"] = "series_first"
        
        results["I_series"] = i_in_rms
        results["V_series"] = i_in_rms * abs(Xs)
        results["V_shunt"] = v_out_rms
        results["I_shunt"] = v_out_rms / abs(Xp)
        
        results["Xs"] = Xs
        results["Xp"] = Xp

    # L/C 判定
    def get_comp_data(X_val):
        if X_val > 0:
            return "L", X_val / omega * 1e6 # uH
        else:
            return "C", 1 / (omega * abs(X_val)) * 1e12 # pF

    s_type, s_val = get_comp_data(results["Xs"])
    results["series_comp"] = s_type
    results["series_disp_val"] = s_val
    
    p_type, p_val = get_comp_data(results["Xp"])
    results["shunt_comp"] = p_type
    results["shunt_disp_val"] = p_val

    # 集計
    if s_type == "L":
        results["L_val"] = s_val
        results["V_L_rms"] = results["V_series"]
        results["I_L_rms"] = results["I_series"]
    else:
        results["C_val"] = s_val
        results["V_C_rms"] = results["V_series"]
        results["I_C_rms"] = results["I_series"]
        
    if p_type == "L":
        results["L_val"] = p_val
        results["V_L_rms"] = results["V_shunt"]
        results["I_L_rms"] = results["I_shunt"]
    else:
        results["C_val"] = p_val
        results["V_C_rms"] = results["V_shunt"]
        results["I_C_rms"] = results["I_shunt"]

    # Peak
    results["V_L_peak"] = results["V_L_rms"] * np.sqrt(2)
    results["I_L_peak"] = results["I_L_rms"] * np.sqrt(2)
    results["V_C_peak"] = results["V_C_rms"] * np.sqrt(2)
    results["I_C_peak"] = results["I_C_rms"] * np.sqrt(2)

    return results

# --- Streamlit UI ---

st.set_page_config(page_title="LCアンテナチューナ計算機", layout="wide")

st.title("LC型アンテナチューナ 計算＆回路図")
st.markdown("インピーダンス変換トランス対応シミュレータ")

with st.sidebar:
    st.header("入力パラメータ")
    freq = st.number_input("周波数 (MHz)", min_value=0.1, value=40.68, step=0.1)
    power = st.number_input("送信電力 (W)", min_value=1, value=100, step=100)
    
    st.markdown("---")
    st.markdown("#### アンテナ(負荷)設定")
    r_load_in = st.number_input("アンテナ抵抗 R (Ω)", min_value=0.1, value=40.0, step=5.0)+0.001
    x_load_in = st.number_input("アンテナリアクタンス X (jΩ)", value=10.0, step=5.0)
    
    # --- VSWR計算の追加 ---
    z_ant = complex(r_load_in, x_load_in)
    gamma_val = abs((z_ant - 50) / (z_ant + 50))
    if gamma_val < 1.0:
        vswr_raw = (1 + gamma_val) / (1 - gamma_val)
        vswr_disp = f"{vswr_raw:.2f}"
    else:
        vswr_disp = "∞"
    st.markdown(f"**補正前 VSWR (50Ω系)**: `{vswr_disp}`")
    # ----------------------

    st.markdown("---")
    st.markdown("#### トランス(インピーダンス変換)")
    tx_ratio = st.number_input("インピーダンス比 (N)", min_value=1, value=1, step=1)
    tx_mode = st.radio("変換方向", ("なし (1:1)", "降圧 (Ant側が高い)", "昇圧 (Ant側が低い)"), index=0)
    
    if tx_ratio == 1 or tx_mode == "なし (1:1)":
        r_seen = r_load_in
        x_seen = x_load_in
        tx_direction_code = "bypass"
        ratio_disp = 1
    elif tx_mode == "降圧 (Ant側が高い)":
        r_seen = r_load_in / tx_ratio
        x_seen = x_load_in / tx_ratio
        tx_direction_code = "down"
        ratio_disp = tx_ratio
    else: 
        r_seen = r_load_in * tx_ratio
        x_seen = x_load_in * tx_ratio
        tx_direction_code = "up"
        ratio_disp = tx_ratio

    st.info(f"チューナ負荷:\n {r_seen:.1f} + j({x_seen:.1f}) Ω")

if st.button("計算実行"):
    res = calculate_l_match(r_seen, x_seen, freq, power)
    
    if res["error"]:
        st.error(res["error"])
    else:
        col_diag, col_data = st.columns([1.4, 1])
        
        with col_diag:
            st.subheader("回路図")
            svg_html = generate_circuit_svg(
                res["topology_code"], res["series_comp"], res["shunt_comp"],
                res["series_disp_val"], res["shunt_disp_val"],
                r_load_in, x_load_in, ratio_disp, tx_direction_code
            )
            st.markdown(svg_html, unsafe_allow_html=True)
            
            st.markdown("##### インピーダンス遷移")
            st.latex(r"Z_{ANT} = " + f"{r_load_in} + j({x_load_in}) \\Omega")
            if tx_ratio > 1:
                 st.latex(r"\downarrow \text{Transformer} (1:" + str(ratio_disp) + r") \downarrow")
                 st.latex(r"Z_{TunerInput} = " + f"{r_seen:.1f} + j({x_seen:.1f}) \\Omega")

        with col_data:
            st.subheader("計算結果 (チューナ部品)")
            
            # --- Inductor Section ---
            st.markdown("#### 🌀 インダクタ (L)")
            if res.get("L_val") > 0:
                st.metric("インダクタンス", f"{res['L_val']:.3f} µH")
                l_col1, l_col2 = st.columns(2)
                l_col1.metric("電圧 (Peak)", f"{res['V_L_peak']:.0f} V", help=f"RMS: {res['V_L_rms']:.1f}V")
                l_col2.metric("電流 (RMS)", f"{res['I_L_rms']:.2f} A", help=f"Peak: {res['I_L_peak']:.2f}A")
            else:
                st.info("使用しません")

            st.divider()

            # --- Capacitor Section ---
            st.markdown("#### ⚡ キャパシタ (C)")
            if res.get("C_val") > 0:
                st.metric("キャパシタンス", f"{res['C_val']:.1f} pF")
                c_col1, c_col2 = st.columns(2)
                c_col1.metric("電圧 (Peak)", f"{res['V_C_peak']:.0f} V", help=f"RMS: {res['V_C_rms']:.1f}V")
                c_col2.metric("電流 (RMS)", f"{res['I_C_rms']:.2f} A", help=f"Peak: {res['I_C_peak']:.2f}A")
            else:
                st.info("使用しません")