import io
from datetime import datetime
import pandas as pd
import pypdf
import streamlit as st

st.set_page_config(
    page_title="Diesel Loco Shed Itarsi - Loco Manager", layout="wide"
)

st.title(
    "🚂 Diesel Loco Shed Itarsi - Locomotive Information & MU Compatibility"
    " Portal"
)

# Initialize session state database so updated PDFs persist across tabs
if "loco_db" not in st.session_state:
  st.session_state.loco_db = {
      "23873": {
          "Loco No": "23873",
          "Loco Type": "WAG5H Hitachi",
          "MPFDCS": "Laxven V3 (FDCS)",
          "Traction Motor": "Hitachi",
          "Wheel Dia": "50/44",
          "Shed Arrival Date": "02-May-26",
          "Commissioning Date": "20-Apr-94",
          "Overage Date": "20-Apr-29",
          "Major Schedule Due": "TOH 15-Feb-28",
          "Minor Schedule Done": "IB 12-Jul-26",
          "ARNO/SIV": "AAL",
      },
      "24453": {
          "Loco No": "24453",
          "Loco Type": "WAG5H Hitachi",
          "MPFDCS": "Laxven V3 (FDCS)",
          "Traction Motor": "Hitachi",
          "Wheel Dia": "62/68",
          "Shed Arrival Date": "12-Sep-26",
          "Commissioning Date": "10-Oct-96",
          "Overage Date": "10-Oct-31",
          "Major Schedule Due": "IOH 17-Jan-27",
          "Minor Schedule Done": "IA 30-Jun-26",
          "ARNO/SIV": "ARNO",
      },
      "23944": {
          "Loco No": "23944",
          "Loco Type": "WAG5H Hitachi",
          "MPFDCS": "Medha V3 (FDCS)",
          "Traction Motor": "Hitachi",
          "Wheel Dia": "79/79",
          "Shed Arrival Date": "12-Sep-26",
          "Commissioning Date": "31-Dec-94",
          "Overage Date": "31-Dec-29",
          "Major Schedule Due": "IOH 30-Jun-28",
          "Minor Schedule Done": "IA 17-Sep-26",
          "ARNO/SIV": "ARNO",
      },
      "24426": {
          "Loco No": "24426",
          "Loco Type": "WAG5H Hitachi",
          "MPFDCS": "Non FDCS",
          "Traction Motor": "Hitachi",
          "Wheel Dia": "83/82",
          "Shed Arrival Date": "11-Aug-25",
          "Commissioning Date": "27-Mar-96",
          "Overage Date": "27-Mar-31",
          "Major Schedule Due": "IOH 18-Oct-26 (Overdue)",
          "Minor Schedule Done": "IC 14-Jul-26",
          "ARNO/SIV": "AAL",
      },
      "23584": {
          "Loco No": "23584",
          "Loco Type": "WAG5T",
          "MPFDCS": "Non FDCS",
          "Traction Motor": "Taochi",
          "Wheel Dia": "75/75",
          "Shed Arrival Date": "13-Sep-26",
          "Commissioning Date": "13-Sep-91",
          "Overage Date": "13-Sep-26",
          "Major Schedule Due": "Overdue",
          "Minor Schedule Done": "IA",
          "ARNO/SIV": "ARNO",
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
          "Date": "2026-04-11",
          "Loco No": "23960",
          "Failure Cause": (
              'ICDJ with message "DJ tripped via QCVAR" due to suspected SCU'
              " unit defective"
          ),
          "Components Involved": "FDCS / MPFDCS",
          "Section": "BPL/WCR",
          "Responsibility": "Defective Material",
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
          "Date": "2026-06-01",
          "Loco No": "24411",
          "Failure Cause": "QOP-2 dropping, TM6 armature circuit IR zero",
          "Components Involved": "Traction Motor",
          "Section": "BKA/BPL/WCR",
          "Responsibility": "Defective material",
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
      {
          "Date": "2026-08-21",
          "Loco No": "23812",
          "Failure Cause": (
              "QOP-1 repeatedly dropping due to TM no. 1 carbon brush holder"
              " spring broken"
          ),
          "Components Involved": "Traction Motor",
          "Section": "KMI/R/SECR",
          "Responsibility": "Defective Material",
      },
      {
          "Date": "2026-09-23",
          "Loco No": "23601 + 23613",
          "Failure Cause": "Rheostatic braking not working",
          "Components Involved": "Rheostatic Brakes / Control Circuit",
          "Section": "PGT/SR",
          "Responsibility": "Under Investigation",
      },
  ]

# --- MAIN APP TABS ---
tab1, tab2, tab3, tab4 = st.tabs(
    ["1. Loco Info", "2. Failure Info", "3. MU Compatibility", "4. Update Data"]
)

# ================= TAB 1: LOCO INFO =================
with tab1:
  st.header("Locomotive Information Lookup")
  st.markdown(
      "Enter any locomotive number from the shed position records to view its"
      " specifications."
  )

  col1, col2 = st.columns([2, 1])
  with col1:
    search_loco = st.text_input(
        "Enter Locomotive Number (e.g., 23873, 24453, 23944)",
        key="loco_search_input",
    ).strip()
  with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    find_btn = st.button("Find Info", type="primary")

  if find_btn or search_loco:
    if search_loco in st.session_state.loco_db:
      info = st.session_state.loco_db[search_loco]
      st.success(f"Locomotive **{search_loco}** found!")

      # 1. General Specifications Table
      st.subheader("📋 General Specifications")
      df_info = pd.DataFrame(list(info.items()), columns=["Parameter", "Value"])
      st.table(df_info)

      # 2. Detailed Failure Information (Displayed separately below)
      st.subheader(
          f"⚠️ Detailed Failure Information for Locomotive {search_loco}"
      )
      matched_failures = []
      for f in st.session_state.failure_db:
        if search_loco in str(f.get("Loco No", "")) or search_loco in str(
            f.get("Failure Cause", "")
        ):
          matched_failures.append(f)

      if matched_failures:
        df_loco_failures = pd.DataFrame(matched_failures)
        st.dataframe(df_loco_failures, use_container_width=True)
      else:
        st.info(
            f"No failure records found matching Locomotive {search_loco} in the"
            " failure database."
        )

    else:
      st.error(
          f"Locomotive '{search_loco}' not found in current memory. Please"
          " update data via the 'Update Data' tab."
      )

  st.markdown("---")
  st.subheader("Total Locomotives Currently in Memory")
  st.info(f"Loaded Locomotives: **{len(st.session_state.loco_db)} units**")


# ================= TAB 2: FAILURE INFO =================
with tab2:
  st.header("Locomotive Failure & ICMS History")
  st.markdown(
      "Chronological (date-wise) breakdown of locomotive failures, failure"
      " causes, and components involved[span_1](start_span)[span_1](end_span)."
  )

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
  st.header("Multiple Unit (MU) Compatibility Checker")
  st.markdown("Verify MU compatibility between two locomotives based on:")
  st.markdown(
      "1. **Traction Motor Type** | 2. **Control System (FDCS / Conventional)**"
      " | 3. **Wheel Diameter Difference (< 40mm)**"
  )

  col1, col2 = st.columns(2)
  with col1:
    loco_1 = st.text_input(
        "Locomotive Number 1", value="23873", key="mu_l1"
    ).strip()
  with col2:
    loco_2 = st.text_input(
        "Locomotive Number 2", value="24453", key="mu_l2"
    ).strip()

  if st.button("Check MU Compatibility", type="primary"):
    if (
        loco_1 not in st.session_state.loco_db
        or loco_2 not in st.session_state.loco_db
    ):
      st.error(
          "One or both locomotive numbers are not found in memory. Please check"
          " the numbers or update data."
      )
    else:
      l1 = st.session_state.loco_db[loco_1]
      l2 = st.session_state.loco_db[loco_2]

      incompatible_reasons = []

      # Rule 1: Traction Motor Type Check
      if l1.get("Traction Motor") != l2.get("Traction Motor"):
        incompatible_reasons.append(
            f"Traction Motor mismatch: Loco {loco_1} has"
            f" {l1.get('Traction Motor')} motors while Loco {loco_2} has"
            f" {l2.get('Traction Motor')} motors."
        )

      # Rule 2: Control Type Check (FDCS vs Conventional)
      l1_fdcs = "FDCS" in str(l1.get("MPFDCS", ""))
      l2_fdcs = "FDCS" in str(l2.get("MPFDCS", ""))
      if l1_fdcs != l2_fdcs:
        incompatible_reasons.append(
            f"Control system mismatch: Loco {loco_1} is {l1.get('MPFDCS')} while"
            f" Loco {loco_2} is {l2.get('MPFDCS')}."
        )

      # Rule 3: Wheel Diameter Difference Check (< 40mm)
      try:
        d1_str = l1.get("Wheel Dia", "75/75")
        d2_str = l2.get("Wheel Dia", "75/75")
        l1_d1, l1_d2 = map(int, d1_str.split("/"))
        l2_d1, l2_d2 = map(int, d2_str.split("/"))

        diff1 = abs(l1_d1 - l2_d1)
        diff2 = abs(l1_d2 - l2_d2)

        if diff1 >= 40 or diff2 >= 40:
          incompatible_reasons.append(
              f"Wheel diameter difference limit exceeded (>= 40mm): Cab 1"
              f" difference is {diff1}mm, Cab 2 difference is {diff2}mm."
          )
      except Exception:
        pass

      # Display Result
      if len(incompatible_reasons) == 0:
        st.markdown(
            '<div style="padding: 15px; background-color: #d4edda; color:'
            ' #155724; border-radius: 5px; font-weight: bold; font-size:'
            ' 18px;">✅ Yes, MU Compatible</div>',
            unsafe_allow_html=True,
        )
        st.info(
            f"Locomotives {loco_1} and {loco_2} successfully meet all"
            " electrical, control, and mechanical wheel-tolerance criteria"
            " for MU operation."
        )
      else:
        st.markdown(
            '<div style="padding: 15px; background-color: #f8d7da; color:'
            ' #721c24; border-radius: 5px; font-weight: bold; font-size:'
            ' 18px;">❌ MU formation not possible</div>',
            unsafe_allow_html=True,
        )
        st.error("Reasons for incompatibility:")
        for reason in incompatible_reasons:
          st.markdown(f"- {reason}")


# ================= TAB 4: UPDATE DATA =================
with tab4:
  st.header("Update Data from PDF")
  st.markdown(
      "Upload the latest `Loco Position of Diesel Loco Shed Itarsi.pdf` file"
      " from your phone[span_2](start_span)[span_2](end_span). **Note:** Uploading a new file will"
      " completely clear the previous data and parse all fresh records from"
      " the uploaded PDF."
  )

  uploaded_pdf = st.file_uploader(
      "Choose Loco Position PDF file", type=["pdf"], key="tab4_uploader"
  )

  if uploaded_pdf is not None:
    if st.button("Process & Overwrite Database", type="primary"):
      with st.spinner(
          "Clearing old database and parsing new PDF records..."
      ):
        try:
          file_bytes = uploaded_pdf.getvalue()
          reader = pypdf.PdfReader(io.BytesIO(file_bytes))

          new_loco_db = {}
          for page_num, page in enumerate(reader.pages):
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
                            "WAG5H Hitachi"
                            if t_motor == "Hitachi"
                            else "WAG5 Taochi"
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
              f"🎉 Successfully updated! Previous data cleared. Loaded"
              f" **{len(new_loco_db)} locomotives** from the new PDF."
          )
        except Exception as e:
          st.error(f"❌ Error processing PDF file: {e}")
            
