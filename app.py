import io
from datetime import datetime
import pandas as pd
import pypdf
import streamlit as st

st.set_page_config(
    page_title="DLS Itarsi Loco Manager",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Minimal styling: center align text, fix heading cut-offs, clean mobile padding
st.markdown(
    """
    <style>
    .stApp { text-align: center; }
    h1, h2, h3, p, label, .stTextInput, .stButton, div[data-baseweb="tab"] { text-align: center !important; }
    .block-container { 
        padding-top: 1rem !important; 
        padding-bottom: 2rem !important; 
        max-width: 600px !important;
    }
    /* Center align input fields and tables */
    .stTextInput > div > div > input { text-align: center; }
    table { margin-left: auto; margin-right: auto; text-align: left; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("### 🚂 DLS Itarsi - Loco Portal")

# Initialize session state database so updated PDFs persist across tabs
if "loco_db" not in st.session_state:
  st.session_state.loco_db = {
      "23873": {
          "Loco No": "23873",
          "Loco Type": "WAG5H Hitachi (Electric)",
          "Traction Motor": "Hitachi",
          "Minor Schedule Date": "IB (12-Jul-26)",
          "Major Schedule Date": "TOH (15-Feb-28)",
          "Commissioning Date": "20-Apr-94",
          "Overage Date": "20-Apr-29",
          "Shed Arrival Date": "02-May-26",
          "Wheel Dia": "50/44",
          "MPFDCS": "Laxven V3 (FDCS)",
      },
      "24453": {
          "Loco No": "24453",
          "Loco Type": "WAG5H Hitachi (Electric)",
          "Traction Motor": "Hitachi",
          "Minor Schedule Date": "IA (30-Jun-26)",
          "Major Schedule Date": "IOH (17-Jan-27)",
          "Commissioning Date": "10-Oct-96",
          "Overage Date": "10-Oct-31",
          "Shed Arrival Date": "12-Sep-26",
          "Wheel Dia": "62/68",
          "MPFDCS": "Laxven V3 (FDCS)",
      },
      "70105": {
          "Loco No": "70105",
          "Loco Type": "WDG4 (Diesel)",
          "Traction Motor": "N/A",
          "Minor Schedule Date": "45D",
          "Major Schedule Date": "180D",
          "Commissioning Date": "10-Jan-15",
          "Overage Date": "10-Jan-35",
          "Shed Arrival Date": "10-Sep-26",
          "Wheel Dia": "75/75",
          "MPFDCS": "Non FDCS",
      },
  }

if "failure_db" not in st.session_state:
  st.session_state.failure_db = [
      {
          "Date": "2026-04-03",
          "Loco No": "23892",
          "Failure Cause": (
              "QOP-1 permanently dropped due to TM 3 Interpole IR zero"
          ),
          "Components Involved": "Traction Motor",
          "Section": "RTM/WR",
          "Responsibility": "Defective material",
      },
      {
          "Date": "2026-05-02",
          "Loco No": "23722",
          "Failure Cause": (
              "Smoke came from HTC & message from DDS that battery charger"
              " output fail"
          ),
          "Components Involved": "SIV / CHBA",
          "Section": "JBP/WCR",
          "Responsibility": "Bad Workmanship (Firm)",
      },
      {
          "Date": "2026-07-03",
          "Loco No": "23584 + 23873",
          "Failure Cause": (
              "DJ not hold with message of Low/No OHE due to rain water leakage"
              " from roof resulting in PT transformer winding open circuited"
          ),
          "Components Involved": "Roof Equipment / PT Transformer",
          "Section": "BNU/JBP/WCR",
          "Responsibility": "Bad Workmanship",
      },
  ]

# --- MAIN APP TABS ---
tab1, tab2, tab3, tab4 = st.tabs(
    ["1. Loco Info", "2. Failure Info", "3. MU Compatibility", "4. Update Data"]
)

# ================= TAB 1: LOCO INFO =================
with tab1:
  st.subheader("Locomotive Information Lookup")
  st.write("Enter a locomotive number to view summary and failure details.")

  search_loco = st.text_input(
      "Loco Number (e.g., 23873, 70105)", key="loco_search_input"
  ).strip()
  find_btn = st.button("Find Info", type="primary")

  if find_btn or search_loco:
    if search_loco in st.session_state.loco_db:
      info = st.session_state.loco_db[search_loco]
      st.success(f"Locomotive **{search_loco}** found!")

      is_electric = search_loco.startswith("2")

      failure_dates = []
      matched_failures = []
      for f in st.session_state.failure_db:
        if search_loco in str(f.get("Loco No", "")) or search_loco in str(
            f.get("Failure Cause", "")
        ):
          failure_dates.append(str(f.get("Date", "N/A")))
          matched_failures.append(f)

      failure_date_str = (
          ", ".join(failure_dates)
          if failure_dates
          else "Not involved in recorded failures"
      )
      motor_type_display = (
          info.get("Traction Motor", "Hitachi") if is_electric else "N/A"
      )

      summary_dict = {
          "1. Loco Number": search_loco,
          "2. Loco Type": info.get(
              "Loco Type", "Electric Loco" if is_electric else "Diesel Loco"
          ),
          "3. Loco Motor Type": motor_type_display,
          "4. Minor Schedule Date": info.get(
              "Minor Schedule Date", "IA / IB / IC"
          ),
          "5. Major Schedule Date": info.get(
              "Major Schedule Date", "TOH / IOH"
          ),
          "6. Commissioning Date": info.get("Commissioning Date", "N/A"),
          "7. Overage Date": info.get("Overage Date", "N/A"),
          "8. Shed Arrival Date": info.get("Shed Arrival Date", "N/A"),
          "9. Failure Date": failure_date_str,
          "10. Wheel Diameter (Dia)": info.get("Wheel Dia", "N/A"),
          "11. FDCS or Non-FDCS": info.get("MPFDCS", "Non FDCS"),
      }

      st.markdown("**Locomotive Summary Table**")
      df_summary = pd.DataFrame(
          list(summary_dict.items()), columns=["Parameter", "Details"]
      )
      st.table(df_summary)

      st.markdown(f"**Detailed Failure Records for {search_loco}**")
      if matched_failures:
        df_loco_failures = pd.DataFrame(matched_failures)
        st.dataframe(df_loco_failures, use_container_width=True)
      else:
        st.info(f"No failure records found matching Locomotive {search_loco}.")

    else:
      st.error(
          f"Locomotive '{search_loco}' not found in memory. Please update data"
          " via the 'Update Data' tab."
      )

  st.markdown("---")
  st.caption(f"Loaded Locomotives in memory: {len(st.session_state.loco_db)} units")


# ================= TAB 2: FAILURE INFO =================
with tab2:
  st.subheader("Failure & ICMS History")
  st.write("Chronological breakdown of locomotive failures.")

  df_failures = pd.DataFrame(st.session_state.failure_db)
  if "Date" in df_failures.columns:
    df_failures["Date"] = pd.to_datetime(
        df_failures["Date"], errors="coerce"
    )
    df_failures = df_failures.sort_values(by="Date", ascending=False)
    df_failures["Date"] = df_failures["Date"].dt.strftime("%Y-%m-%d")

  st.dataframe(df_failures, use_container_width=True)


# ================= TAB 3: MU COMPATIBILITY =================
with tab3:
  st.subheader("MU Compatibility Checker")
  st.write("Check MU compatibility based on rules.")

  loco_1 = st.text_input("Locomotive 1", value="23873", key="mu_l1").strip()
  loco_2 = st.text_input("Locomotive 2", value="24453", key="mu_l2").strip()

  if st.button("Check Compatibility", type="primary"):
    if (
        loco_1 not in st.session_state.loco_db
        or loco_2 not in st.session_state.loco_db
    ):
      st.error(
          "One or both locomotive numbers are not found in memory. Please check"
          " numbers or update data."
      )
    else:
      l1 = st.session_state.loco_db[loco_1]
      l2 = st.session_state.loco_db[loco_2]

      incompatible_reasons = []

      l1_is_electric = loco_1.startswith("2")
      l2_is_electric = loco_2.startswith("2")

      if l1_is_electric != l2_is_electric:
        incompatible_reasons.append(
            "Locomotive Type Mismatch: MU between Diesel and Electric is not"
            " possible."
        )
      else:
        if l1_is_electric:
          if l1.get("Traction Motor") != l2.get("Traction Motor"):
            incompatible_reasons.append(
                f"Traction Motor mismatch: Loco {loco_1} has"
                f" {l1.get('Traction Motor')} motors while Loco {loco_2} has"
                f" {l2.get('Traction Motor')} motors."
            )

        l1_non_fdcs = "Non FDCS" in str(l1.get("MPFDCS", ""))
        l2_non_fdcs = "Non FDCS" in str(l2.get("MPFDCS", ""))
        if l1_non_fdcs != l2_non_fdcs:
          incompatible_reasons.append(
              "Control System mismatch: A Non-FDCS locomotive requires another"
              " Non-FDCS locomotive."
          )

        try:
          d1_str = l1.get("Wheel Dia", "75/75")
          d2_str = l2.get("Wheel Dia", "75/75")
          l1_d1, l1_d2 = map(int, d1_str.split("/"))
          l2_d1, l2_d2 = map(int, d2_str.split("/"))

          diff1 = abs(l1_d1 - l2_d1)
          diff2 = abs(l1_d2 - l2_d2)

          if diff1 >= 40 or diff2 >= 40:
            incompatible_reasons.append(
                f"Wheel diameter difference exceeded limit (>= 40mm): Cab 1 diff"
                f" is {diff1}mm, Cab 2 diff is {diff2}mm."
            )
        except Exception:
          pass

      if len(incompatible_reasons) == 0:
        st.markdown(
            '<div style="padding: 12px; background-color: #d4edda; color:'
            ' #155724; border-radius: 5px; font-weight: bold; margin-top:'
            ' 10px;">✅ Yes, MU Compatible</div>',
            unsafe_allow_html=True,
        )
      else:
        st.markdown(
            '<div style="padding: 12px; background-color: #f8d7da; color:'
            ' #721c24; border-radius: 5px; font-weight: bold; margin-top:'
            ' 10px;">❌ MU formation not possible</div>',
            unsafe_allow_html=True,
        )
        for reason in incompatible_reasons:
          st.markdown(f"- {reason}")


# ================= TAB 4: UPDATE DATA =================
with tab4:
  st.subheader("Update Data from PDF")
  st.write("Upload the latest Loco Position PDF file to refresh records.")

  uploaded_pdf = st.file_uploader(
      "Choose PDF file", type=["pdf"], key="tab4_uploader"
  )

  if uploaded_pdf is not None:
    if st.button("Process & Overwrite", type="primary"):
      with st.spinner("Parsing new PDF records..."):
        try:
          file_bytes = uploaded_pdf.getvalue()
          reader = pypdf.PdfReader(io.BytesIO(file_bytes))

          new_loco_db = {}
          for page in reader.pages:
            text = page.extract_text()
            lines = text.split("\n")

            for line in lines:
              parts = line.split()
              for part in parts:
                if part.isdigit() and len(part) == 5:
                  loco_no = part
                  wheel_dia = "N/A"
                  for p in parts:
                    if "/" in p and any(c.isdigit() for c in p):
                      wheel_dia = p
                      break

                  t_motor = "Hitachi" if "HITACHI" in text else "Taochi"
                  mpfdcs = "Non FDCS"
                  if "Medha V3" in line:
                    mpfdcs = "Medha V3"
                  elif "Medha V2" in line:
                    mpfdcs = "Medha V2"
                  elif "Laxven V3" in line:
                    mpfdcs = "Laxven V3"
                  elif "FDCS" in line:
                    mpfdcs = "FDCS"

                  if loco_no not in new_loco_db:
                    new_loco_db[loco_no] = {
                        "Loco No": loco_no,
                        "Loco Type": (
                            "Electric Loco"
                            if loco_no.startswith("2")
                            else "Diesel Loco"
                        ),
                        "Traction Motor": t_motor,
                        "MPFDCS": mpfdcs,
                        "Wheel Dia": (
                            wheel_dia if wheel_dia != "N/A" else "75/75"
                        ),
                        "Raw Details": line,
                    }

          st.session_state.loco_db = new_loco_db
          st.success(
              f"🎉 Successfully updated! Loaded {len(new_loco_db)} locomotives."
          )
        except Exception as e:
          st.error(f"❌ Error processing PDF: {e}")
