import html
import math
from dataclasses import dataclass

import streamlit as st
from streamlit.components.v1 import html as st_html


st.set_page_config(
    page_title="미분: 속도와 가속도 시각화",
    page_icon=".",
    layout="wide",
    initial_sidebar_state="collapsed",
)


CUSTOM_CSS = """
<style>
    .block-container {
        max-width: 1280px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.35rem;
    }
    .section-title {
        font-size: 1.25rem;
        font-weight: 760;
        margin: 0.4rem 0 0.1rem;
    }
    .subtle {
        color: #5d6673;
        font-size: 0.95rem;
        line-height: 1.45;
    }
    .formula-box {
        border: 1px solid #d8dee8;
        background: #f7f9fc;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-top: 0.35rem;
    }
    .stButton > button {
        min-height: 2.7rem;
        border-radius: 8px;
        font-weight: 700;
    }
</style>
"""


@dataclass(frozen=True)
class MotionSettings:
    a: float
    b: float
    c: float
    t_min: float
    t_max: float
    t_current: float
    frame_count: int


def fmt(value: float) -> str:
    if abs(value) < 1e-10:
        value = 0.0
    if abs(value - round(value)) < 1e-10:
        return str(int(round(value)))
    return f"{value:.3f}".rstrip("0").rstrip(".")


def signed_term(coef: float, variable: str, first: bool = False) -> str:
    if abs(coef) < 1e-10:
        return ""
    sign = "-" if coef < 0 else "+"
    abs_coef = abs(coef)
    coef_text = "" if abs(abs_coef - 1) < 1e-10 and variable else fmt(abs_coef)
    term = f"{coef_text}{variable}" if variable else fmt(abs_coef)
    if first:
        return f"-{term}" if coef < 0 else term
    return f" {sign} {term}"


def polynomial_label(a: float, b: float, c: float) -> str:
    parts = [
        signed_term(a, "t^2", first=True),
        signed_term(b, "t"),
        signed_term(c, ""),
    ]
    joined = "".join(part for part in parts if part)
    return joined or "0"


def position(t: float, settings: MotionSettings) -> float:
    return settings.a * t * t + settings.b * t + settings.c


def velocity(t: float, settings: MotionSettings) -> float:
    return 2 * settings.a * t + settings.b


def acceleration(settings: MotionSettings) -> float:
    return 2 * settings.a


def sample_motion(settings: MotionSettings):
    if settings.frame_count <= 1:
        return [(settings.t_min, position(settings.t_min, settings), velocity(settings.t_min, settings))]
    step = (settings.t_max - settings.t_min) / (settings.frame_count - 1)
    return [
        (settings.t_min + i * step, position(settings.t_min + i * step, settings), velocity(settings.t_min + i * step, settings))
        for i in range(settings.frame_count)
    ]


def padded_range(values, extra=0.12):
    lo = min(values)
    hi = max(values)
    if math.isclose(lo, hi):
        return lo - 5, hi + 5
    pad = (hi - lo) * extra
    return lo - pad, hi + pad


def extrema_summary(settings: MotionSettings):
    candidates = [settings.t_min, settings.t_max]
    if abs(settings.a) > 1e-10:
        vertex_t = -settings.b / (2 * settings.a)
        if settings.t_min <= vertex_t <= settings.t_max:
            candidates.append(vertex_t)

    rows = []
    for t in sorted(set(round(t, 12) for t in candidates)):
        rows.append((t, position(t, settings), velocity(t, settings)))

    min_position = min(rows, key=lambda row: row[1])
    max_position = max(rows, key=lambda row: row[1])

    v_start = velocity(settings.t_min, settings)
    v_end = velocity(settings.t_max, settings)
    min_velocity = (settings.t_min, v_start) if v_start <= v_end else (settings.t_max, v_end)
    max_velocity = (settings.t_max, v_end) if v_end >= v_start else (settings.t_min, v_start)
    return rows, min_position, max_position, min_velocity, max_velocity


def build_animation_html(settings: MotionSettings) -> str:
    samples = sample_motion(settings)
    ts = [row[0] for row in samples]
    xs = [row[1] for row in samples]
    vs = [row[2] for row in samples]
    x_lo, x_hi = padded_range(xs + [settings.c])
    t_lo, t_hi = padded_range(ts, 0.03)
    y_lo, y_hi = padded_range(xs, 0.15)
    current_x = position(settings.t_current, settings)

    data_rows = [
        {"t": round(t, 5), "x": round(x, 5), "v": round(v, 5)}
        for t, x, v in zip(ts, xs, vs)
    ]
    escaped_label = html.escape(f"x(t) = {polynomial_label(settings.a, settings.b, settings.c)}")

    return f"""
    <div id="motion-app">
      <style>
        #motion-app {{
          --ink: #14213d;
          --muted: #667085;
          --grid: #e4e7ec;
          --accent: #e11d48;
          --blue: #2563eb;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          color: var(--ink);
        }}
        #motion-app .toolbar {{
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
          align-items: center;
          margin: 0 0 12px;
        }}
        #motion-app button {{
          border: 1px solid #cbd5e1;
          background: white;
          border-radius: 8px;
          padding: 10px 14px;
          font-weight: 760;
          cursor: pointer;
          min-width: 126px;
        }}
        #motion-app button.primary {{
          background: #111827;
          border-color: #111827;
          color: white;
        }}
        #motion-app .readout {{
          color: var(--muted);
          font-size: 14px;
          margin-left: auto;
        }}
        #motion-app .grid {{
          display: grid;
          grid-template-columns: minmax(320px, 0.95fr) minmax(420px, 1.35fr);
          gap: 16px;
        }}
        #motion-app .panel {{
          border: 1px solid #d8dee8;
          border-radius: 8px;
          background: #fff;
          padding: 12px;
        }}
        #motion-app .panel-title {{
          display: flex;
          justify-content: space-between;
          gap: 12px;
          align-items: baseline;
          font-weight: 800;
          margin-bottom: 8px;
        }}
        #motion-app .panel-title span {{
          color: var(--muted);
          font-size: 13px;
          font-weight: 600;
        }}
        #motion-app svg {{
          width: 100%;
          height: auto;
          display: block;
        }}
        #motion-app .axis {{
          stroke: #334155;
          stroke-width: 3;
        }}
        #motion-app .grid-line {{
          stroke: var(--grid);
          stroke-width: 1;
        }}
        #motion-app .curve {{
          fill: none;
          stroke: var(--blue);
          stroke-width: 4;
        }}
        #motion-app .point {{
          fill: var(--accent);
          stroke: white;
          stroke-width: 3;
        }}
        #motion-app .label {{
          fill: #344054;
          font-size: 13px;
          font-weight: 650;
        }}
        #motion-app .small {{
          fill: #667085;
          font-size: 12px;
        }}
        @media (max-width: 860px) {{
          #motion-app .grid {{
            grid-template-columns: 1fr;
          }}
          #motion-app .readout {{
            width: 100%;
            margin-left: 0;
          }}
          #motion-app button {{
            flex: 1 1 145px;
          }}
        }}
      </style>
      <div class="toolbar">
        <button id="playLine">Play 수직선</button>
        <button id="playPlane">Play 좌표평면</button>
        <button id="playBoth" class="primary">Play Both</button>
        <button id="pauseAll">Pause</button>
        <div class="readout" id="readout">{escaped_label}</div>
      </div>
      <div class="grid">
        <div class="panel">
          <div class="panel-title">수직선 위의 위치 <span>점의 좌우 이동</span></div>
          <svg id="lineSvg" viewBox="0 0 560 250" role="img" aria-label="수직선 위치 애니메이션">
            <line class="axis" x1="36" y1="124" x2="524" y2="124"></line>
            <g id="lineTicks"></g>
            <circle id="linePoint" class="point" cx="0" cy="124" r="11"></circle>
            <text id="lineLabel" class="label" x="0" y="92" text-anchor="middle"></text>
            <text class="small" x="280" y="222" text-anchor="middle">위치 x</text>
          </svg>
        </div>
        <div class="panel">
          <div class="panel-title">좌표평면의 그래프 y=x(t) <span>시간에 따른 위치</span></div>
          <svg id="planeSvg" viewBox="0 0 680 390" role="img" aria-label="좌표평면 운동 애니메이션">
            <g id="planeGrid"></g>
            <path id="curve" class="curve"></path>
            <circle id="planePoint" class="point" cx="0" cy="0" r="9"></circle>
            <text id="planeLabel" class="label" x="0" y="0" text-anchor="middle"></text>
            <text class="small" x="340" y="374" text-anchor="middle">시간 t</text>
            <text class="small" transform="translate(18 195) rotate(-90)" text-anchor="middle">위치 x(t)</text>
          </svg>
        </div>
      </div>
      <script>
        const rows = {data_rows};
        const xLo = {x_lo};
        const xHi = {x_hi};
        const tLo = {t_lo};
        const tHi = {t_hi};
        const yLo = {y_lo};
        const yHi = {y_hi};
        const initialT = {settings.t_current};
        const initialX = {current_x};
        const line = {{
          left: 42, right: 518, y: 124,
          scale: (x) => 42 + (x - xLo) / (xHi - xLo) * (518 - 42)
        }};
        const plane = {{
          left: 54, right: 650, top: 24, bottom: 340,
          sx: (t) => 54 + (t - tLo) / (tHi - tLo) * (650 - 54),
          sy: (x) => 340 - (x - yLo) / (yHi - yLo) * (340 - 24)
        }};
        const state = {{ lineTimer: null, planeTimer: null, lineIndex: 0, planeIndex: 0 }};

        function fmt(n) {{
          const clean = Math.abs(n) < 1e-10 ? 0 : n;
          return Number.isInteger(Math.round(clean * 1000) / 1000)
            ? String(Math.round(clean))
            : String(Math.round(clean * 1000) / 1000);
        }}

        function nearestIndex(t) {{
          let best = 0;
          let bestDist = Infinity;
          rows.forEach((row, i) => {{
            const dist = Math.abs(row.t - t);
            if (dist < bestDist) {{ best = i; bestDist = dist; }}
          }});
          return best;
        }}

        function drawTicks() {{
          const lineTicks = document.getElementById("lineTicks");
          const planeGrid = document.getElementById("planeGrid");
          lineTicks.innerHTML = "";
          planeGrid.innerHTML = "";

          for (let i = 0; i <= 8; i++) {{
            const xValue = xLo + (xHi - xLo) * i / 8;
            const px = line.scale(xValue);
            lineTicks.insertAdjacentHTML("beforeend", `
              <line class="grid-line" x1="${{px}}" y1="112" x2="${{px}}" y2="136"></line>
              <text class="small" x="${{px}}" y="158" text-anchor="middle">${{fmt(xValue)}}</text>
            `);
          }}

          for (let i = 0; i <= 6; i++) {{
            const t = tLo + (tHi - tLo) * i / 6;
            const px = plane.sx(t);
            planeGrid.insertAdjacentHTML("beforeend", `
              <line class="grid-line" x1="${{px}}" y1="${{plane.top}}" x2="${{px}}" y2="${{plane.bottom}}"></line>
              <text class="small" x="${{px}}" y="358" text-anchor="middle">${{fmt(t)}}</text>
            `);
          }}
          for (let i = 0; i <= 5; i++) {{
            const y = yLo + (yHi - yLo) * i / 5;
            const py = plane.sy(y);
            planeGrid.insertAdjacentHTML("beforeend", `
              <line class="grid-line" x1="${{plane.left}}" y1="${{py}}" x2="${{plane.right}}" y2="${{py}}"></line>
              <text class="small" x="46" y="${{py + 4}}" text-anchor="end">${{fmt(y)}}</text>
            `);
          }}
          const zeroX = plane.sx(0);
          const zeroY = plane.sy(0);
          if (tLo <= 0 && 0 <= tHi) {{
            planeGrid.insertAdjacentHTML("beforeend", `<line class="axis" x1="${{zeroX}}" y1="${{plane.top}}" x2="${{zeroX}}" y2="${{plane.bottom}}"></line>`);
          }}
          if (yLo <= 0 && 0 <= yHi) {{
            planeGrid.insertAdjacentHTML("beforeend", `<line class="axis" x1="${{plane.left}}" y1="${{zeroY}}" x2="${{plane.right}}" y2="${{zeroY}}"></line>`);
          }}
        }}

        function drawCurve() {{
          const d = rows.map((row, i) => `${{i === 0 ? "M" : "L"}} ${{plane.sx(row.t)}} ${{plane.sy(row.x)}}`).join(" ");
          document.getElementById("curve").setAttribute("d", d);
        }}

        function setLinePoint(row) {{
          const px = line.scale(row.x);
          document.getElementById("linePoint").setAttribute("cx", px);
          const label = document.getElementById("lineLabel");
          label.setAttribute("x", px);
          label.textContent = `t=${{fmt(row.t)}}, x=${{fmt(row.x)}}`;
        }}

        function setPlanePoint(row) {{
          const px = plane.sx(row.t);
          const py = plane.sy(row.x);
          document.getElementById("planePoint").setAttribute("cx", px);
          document.getElementById("planePoint").setAttribute("cy", py);
          const label = document.getElementById("planeLabel");
          label.setAttribute("x", px);
          label.setAttribute("y", Math.max(18, py - 16));
          label.textContent = `(${{fmt(row.t)}}, ${{fmt(row.x)}})`;
        }}

        function updateReadout(row) {{
          document.getElementById("readout").textContent = `t=${{fmt(row.t)}} | x=${{fmt(row.x)}} | v=${{fmt(row.v)}}`;
        }}

        function play(which) {{
          const timerName = which === "line" ? "lineTimer" : "planeTimer";
          const indexName = which === "line" ? "lineIndex" : "planeIndex";
          if (state[timerName]) clearInterval(state[timerName]);
          state[indexName] = 0;
          state[timerName] = setInterval(() => {{
            const row = rows[state[indexName]];
            if (which === "line") setLinePoint(row);
            if (which === "plane") setPlanePoint(row);
            updateReadout(row);
            state[indexName] += 1;
            if (state[indexName] >= rows.length) clearInterval(state[timerName]);
          }}, 35);
        }}

        function pauseAll() {{
          if (state.lineTimer) clearInterval(state.lineTimer);
          if (state.planeTimer) clearInterval(state.planeTimer);
        }}

        drawTicks();
        drawCurve();
        const initialRow = rows[nearestIndex(initialT)] || {{ t: initialT, x: initialX, v: 0 }};
        setLinePoint(initialRow);
        setPlanePoint(initialRow);
        updateReadout(initialRow);

        document.getElementById("playLine").addEventListener("click", () => play("line"));
        document.getElementById("playPlane").addEventListener("click", () => play("plane"));
        document.getElementById("playBoth").addEventListener("click", () => {{ play("line"); play("plane"); }});
        document.getElementById("pauseAll").addEventListener("click", pauseAll);
      </script>
    </div>
    """


def render_details(settings: MotionSettings):
    current_x = position(settings.t_current, settings)
    current_v = velocity(settings.t_current, settings)
    current_a = acceleration(settings)
    rows, min_pos, max_pos, min_vel, max_vel = extrema_summary(settings)

    metric_cols = st.columns(4)
    metric_cols[0].metric("현재 위치 x(t)", fmt(current_x))
    metric_cols[1].metric("현재 속도 v(t)", fmt(current_v))
    metric_cols[2].metric("가속도 a(t)", fmt(current_a))
    metric_cols[3].metric("운동 방향", "오른쪽" if current_v > 0 else "왼쪽" if current_v < 0 else "순간 정지")

    info_cols = st.columns([1.2, 1, 1])
    with info_cols[0]:
        st.markdown("**식 정리**")
        st.markdown(
            f"""
            <div class="formula-box">
                x(t) = {polynomial_label(settings.a, settings.b, settings.c)}<br>
                v(t) = x'(t) = {polynomial_label(0, 2 * settings.a, settings.b)}<br>
                a(t) = v'(t) = {fmt(current_a)}
            </div>
            """,
            unsafe_allow_html=True,
        )
    with info_cols[1]:
        st.markdown("**위치의 최솟값과 최댓값**")
        st.write(f"최소 위치: x={fmt(min_pos[1])}, t={fmt(min_pos[0])}")
        st.write(f"최대 위치: x={fmt(max_pos[1])}, t={fmt(max_pos[0])}")
    with info_cols[2]:
        st.markdown("**속도의 최솟값과 최댓값**")
        st.write(f"최소 속도: v={fmt(min_vel[1])}, t={fmt(min_vel[0])}")
        st.write(f"최대 속도: v={fmt(max_vel[1])}, t={fmt(max_vel[0])}")

    st.markdown("**확인 지점**")
    st.dataframe(
        [
            {"시간 t": fmt(t), "위치 x(t)": fmt(x), "속도 v(t)": fmt(v)}
            for t, x, v in rows
        ],
        use_container_width=True,
        hide_index=True,
    )


st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
st.title("미분 I: 속도와 가속도")
st.caption("이차함수 x(t)의 값을 수직선 위 위치와 좌표평면의 점으로 동시에 확인하는 수업용 도구")

with st.container(border=True):
    st.markdown('<div class="section-title">이차함수와 시간 범위 설정</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtle">상단에서 x(t)=at^2+bt+c를 정하고, 아래에서 같은 운동을 두 표현으로 비교합니다.</div>',
        unsafe_allow_html=True,
    )
    coef_cols = st.columns([1, 1, 1, 0.9])
    a = coef_cols[0].number_input("t^2의 계수 a", value=1.0, step=0.5, format="%.3f")
    b = coef_cols[1].number_input("t의 계수 b", value=-4.0, step=0.5, format="%.3f")
    c = coef_cols[2].number_input("상수항 c", value=3.0, step=0.5, format="%.3f")
    frame_count = coef_cols[3].slider("애니메이션 정밀도", 40, 160, 90, 10)

    range_cols = st.columns([1, 1, 2])
    t_min = range_cols[0].number_input("시작 시간", value=0.0, step=0.5, format="%.2f")
    t_max = range_cols[1].number_input("끝 시간", value=6.0, step=0.5, format="%.2f")
    if t_max <= t_min:
        st.warning("끝 시간은 시작 시간보다 커야 합니다. 끝 시간을 자동으로 조정했습니다.")
        t_max = t_min + 1
    t_current = range_cols[2].slider("현재 시간 t", float(t_min), float(t_max), float(t_min), 0.05)

settings = MotionSettings(a, b, c, float(t_min), float(t_max), float(t_current), int(frame_count))

st.markdown(
    f"""
    <div class="formula-box">
        <strong>현재 함수</strong>&nbsp;&nbsp; x(t) = {polynomial_label(a, b, c)}
        &nbsp;&nbsp; | &nbsp;&nbsp;
        <strong>속도</strong>&nbsp;&nbsp; v(t) = {polynomial_label(0, 2 * a, b)}
        &nbsp;&nbsp; | &nbsp;&nbsp;
        <strong>가속도</strong>&nbsp;&nbsp; {fmt(acceleration(settings))}
    </div>
    """,
    unsafe_allow_html=True,
)

st_html(build_animation_html(settings), height=650, scrolling=False)

with st.container(border=True):
    st.markdown('<div class="section-title">세부정보</div>', unsafe_allow_html=True)
    render_details(settings)
