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
  st.header("Locomotive Information Lookup")
  st.markdown(
      "Enter any locomotive number to view its 11-point tabulated summary and"
      " failure details[span_0](start_span)[span_0](end_span)."
  )

  col1, col2 = st.columns([2, 1])
  with col1:
    search_loco = st.text_input(
        "Enter Locomotive Number (e.g., 23873, 70105)",
        key="loco_search_input",
    ).strip()
  with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    find_btn = st.button("Find Info", type="primary")

  if find_btn or search_loco:
    if search_loco in st.session_state.loco_db:
      info = st.session_state.loco_db[search_loco]
      st.success(f"Locomotive **{search_loco}** found!")

      # Check if electric or diesel based on starting digit '2'
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
          "10. Dia (Wheel Diameter)": info.get("Wheel Dia", "N/A"),
          "11. FDCS or Non-FDCS": info.get("MPFDCS", "Non FDCS"),
      }

      st.subheader("📋 Locomotive Summary Table")
      df_summary = pd.DataFrame(
          list(summary_dict.items()), columns=["Parameter", "Details"]
      )
      st.table(df_summary)

      st.subheader(
          f"⚠️ Detailed Failure Information for Locomotive {search_loco}"
      )
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
          f"Locomotive '{search_loco}' not found in memory. Please update data"
          " via the 'Update Data' tab."
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
      "1. **Electric vs Diesel Check** (No Diesel + Electric MU) | 2."
      " **Traction Motor Match** (Electric only) | 3. **Control System Rule**"
      " (Non-FDCS requires Non-FDCS) | 4. **Wheel Diameter Difference (<"
      " 40mm)**"
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

      l1_is_electric = loco_1.startswith("2")
      l2_is_electric = loco_2.startswith("2")

      # Rule A: Diesel and Electric MU restriction
      if l1_is_electric != l2_is_electric:
        incompatible_reasons.append(
            "Locomotive Type Mismatch: MU formation between a Diesel"
            " locomotive and an Electric locomotive is strictly not possible."
        )
      else:
        # Rule B: Traction Motor Check (Electric locomotives only)
        if l1_is_electric:
          if l1.get("Traction Motor") != l2.get("Traction Motor"):
            incompatible_reasons.append(
                f"Traction Motor mismatch: Loco {loco_1} has"
                f" {l1.get('Traction Motor')} motors while Loco {loco_2} has"
                f" {l2.get('Traction Motor')} motors."
            )

        # Rule C: Control System Rule (Non-FDCS requires Non-FDCS)
        l1_non_fdcs = "Non FDCS" in str(l1.get("MPFDCS", ""))
        l2_non_fdcs = "Non FDCS" in str(l2.get("MPFDCS", ""))
        if l1_non_fdcs != l2_non_fdcs:
          incompatible_reasons.append(
              "Control System mismatch: A Non-FDCS locomotive can only form MU"
              f" with another Non-FDCS locomotive ({loco_1} is"
              f" {l1.get('MPFDCS')}, {loco_2} is {l2.get('MPFDCS')})."
          )

        # Rule D: Wheel Diameter Difference Check (< 40mm)
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
            f"Locomotives {loco_1} and {loco_2} successfully meet all type,"
            " control, and wheel-tolerance criteria for MU operation."
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
              f"🎉 Successfully updated! Previous data cleared. Loaded"
              f" **{len(new_loco_db)} locomotives** from the new PDF."
          )
        except Exception as e:
          st.error(f"❌ Error processing PDF file: {e}")
            
