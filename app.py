import streamlit as st
import pandas as pd
import pypdf
import io
from datetime import datetime

st.set_page_config(page_title="Diesel Loco Shed Itarsi - Loco Manager", layout="wide")

st.title("🚂 Diesel Loco Shed Itarsi - Locomotive Information & MU Compatibility Portal")

# --- PDF UPLOADER AT THE BOTTOM / SIDEBAR CONTAINER ---
st.sidebar.markdown("---")
st.sidebar.subheader("📂 Data Management")
uploaded_file = st.sidebar.file_uploader(
    "Upload Updated Loco Position PDF", type=["pdf"]
)


# Helper function to extract and parse data from the PDF
@st.cache_data
def parse_loco_pdf(file_bytes):
    loco_data = {}
    failure_data = []

    reader = pypdf.PdfReader(io.BytesIO(file_bytes))

    # Parse locomotive tables across pages (WAG5 Taochi & Hitachi, HHP, Alco)
    for page_num in range(len(reader.pages)):
        text = reader.pages[page_num].extract_text()
        lines = text.split("\n")

        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                # Detect locomotive numbers (e.g. 5-digit numbers like 23873, 24453, etc.)
                potential_loco = parts[1] if parts[0].isdigit() else parts[0]
                if (
                    potential_loco.isdigit()
                    and len(potential_loco) == 5
                    and potential_loco not in loco_data
                ):
                    # Determine Loco Type and Motor from context
                    loco_type = (
                        "WAG5H Hitachi"
                        if "Hitachi" in text or "23609" in text
                        else "WAG5"
                    )
                    if "WAG5 TAOCHI" in text:
                        loco_type = "WAG5 Taochi"
                    elif "WDG4" in text:
                        loco_type = "WDG4"
                    elif "WDG4D" in text:
                        loco_type = "WDG4D"

                    # Check MPFDCS / FDCS status
                    mpfdcs = (
                        "Non FDCS"
                        if "Non FDCS" in line
                        else ("Medha V3" if "Medha V3" in line else "FDCS/V2")
                    )
                    if "FDCS" in line:
                        mpfdcs = "FDCS"

                    # Extract wheel diameters if present (e.g. 50/44)
                    wheel_dia = "N/A"
                    for p in parts:
                        if "/" in p and any(char.isdigit() for char in p):
                            wheel_dia = p
                            break

                    loco_data[potential_loco] = {
                        "Loco No": potential_loco,
                        "Loco Type": loco_type,
                        "Raw Line": line,
                        "MPFDCS": mpfdcs,
                        "Traction Motor": (
                            "Taochi" if "Taocchi" in text else "Hitachi"
                        ),
                        "Wheel Dia": wheel_dia,
                        "Details": line,
                    }

        # Parse failure records (ICMS failure tables)
        for line in lines:
            if any(
                month in line
                for month in [
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                ]
            ) and (
                "ELSI" in line
                or "ELFG" in line
                or "DLFG" in line
                or "ELTG" in line
            ):
                failure_data.append(
                    {
                        "Failure Record": line,
                    }
                )

    return loco_data, failure_data


# Default sample database if no file uploaded yet
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    loco_db, failure_db = parse_loco_pdf(bytes_data)
    st.sidebar.success("PDF successfully uploaded and processed!")
else:
    # Built-in baseline records for demonstration based on Shed records
    loco_db = {
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

# Comprehensive Failure Database (Date-wise)
failure_db = [
    {
        "Date": "2026-04-03",
        "Loco No": "23892",
        "Failure Cause": "QOP-1 permanently dropped due to TM 3 Interpole IR zero",
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
        "Failure Cause": "QOP-1 repeatedly dropping due to TM no. 1 carbon brush holder spring broken",
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
tab1, tab2, tab3 = st.tabs(
    ["1. Loco Info", "2. Failure Info", "3. MU Compatibility"]
)

# ================= TAB 1: LOCO INFO =================
with tab1:
    st.header("Locomotive Information Lookup")
    st.markdown(
        "Enter a locomotive number to retrieve its complete specification and"
        " schedule status."
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        search_loco = st.text_input(
            "Enter Locomotive Number (e.g. 23873, 24453, 23944)"
        ).strip()
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        find_btn = st.button("Find Info", type="primary")

    if find_btn or search_loco:
        if search_loco in loco_db:
            info = loco_db[search_loco]
            st.success(f"Locomotive **{search_loco}** found successfully!")

            # Display as a clean tabulated table / dataframe
            df_info = pd.DataFrame(list(info.items()), columns=["Parameter", "Value"])
            st.table(df_info)
        else:
            st.error(
                f"Locomotive number '{search_loco}' not found in current"
                " database. Please check the number or upload an updated PDF."
            )

    st.markdown("---")
    st.subheader("Quick Directory of Available Locomotives in Memory")
    available_locos = list(loco_db.keys())
    st.write(", ".join(available_locos))


# ================= TAB 2: FAILURE INFO =================
with tab2:
    st.header("Locomotive Failure & ICMS History")
    st.markdown(
        "Chronological (date-wise) record of locomotive failures, causes, and"
        " components involved."
    )

    # Convert failure db to DataFrame and sort date-wise
    df_failures = pd.DataFrame(failure_db)
    df_failures["Date"] = pd.to_datetime(df_failures["Date"])
    df_failures = df_failures.sort_values(by="Date", ascending=False)
    df_failures["Date"] = df_failures["Date"].dt.strftime("%Y-%m-%d")

    # Display as tabulated view
    st.dataframe(df_failures, use_container_width=True)


# ================= TAB 3: MU COMPATIBILITY =================
with tab3:
    st.header("Multiple Unit (MU) Compatibility Checker")
    st.markdown(
        "Verify if two locomotives can be coupled in Multiple Unit (MU) based"
        " on:"
    )
    st.markdown(
        "1. **Traction Motor Type Match** | 2. **Control System Type (FDCS vs"
        " Conventional)** | 3. **Wheel Diameter Difference (< 40mm)**"
    )

    col1, col2 = st.columns(2)
    with col1:
        loco_1 = st.text_input(
            "Locomotive Number 1 (e.g., 23873)", value="23873"
        ).strip()
    with col2:
        loco_2 = st.text_input(
            "Locomotive Number 2 (e.g., 24453)", value="24453"
        ).strip()

    if st.button("Check MU Compatibility", type="primary"):
        if loco_1 not in loco_db or loco_2 not in loco_db:
            st.error(
                "One or both locomotive numbers are not present in the"
                " database. Please check the numbers."
            )
        else:
            l1 = loco_db[loco_1]
            l2 = loco_db[loco_2]

            incompatible_reasons = []

            # Rule 1: Traction Motor Type Check
            if l1["Traction Motor"] != l2["Traction Motor"]:
                incompatible_reasons.append(
                    f"Traction Motor mismatch: Loco {loco_1} has"
                    f" {l1['Traction Motor']} motors while Loco {loco_2} has"
                    f" {l2['Traction Motor']} motors."
                )

            # Rule 2: Control Type Check (FDCS vs Conventional)
            l1_fdcs = "FDCS" in l1["MPFDCS"]
            l2_fdcs = "FDCS" in l2["MPFDCS"]
            if l1_fdcs != l2_fdcs:
                incompatible_reasons.append(
                    f"Control architecture mismatch: Loco {loco_1} is"
                    f" {l1['MPFDCS']} while Loco {loco_2} is {l2['MPFDCS']}."
                )

            # Rule 3: Wheel Diameter Difference Check (< 40mm)
            try:
                l1_d1, l1_d2 = map(int, l1["Wheel Dia"].split("/"))
                l2_d1, l2_d2 = map(int, l2["Wheel Dia"].split("/"))

                diff1 = abs(l1_d1 - l2_d1)
                diff2 = abs(l1_d2 - l2_d2)

                if diff1 >= 40 or diff2 >= 40:
                    incompatible_reasons.append(
                        f"Wheel diameter difference exceeded limit (>= 40mm):"
                        f" Cab 1 diff is {diff1}mm, Cab 2 diff is {diff2}mm."
                    )
            except Exception:
                pass  # Skip if wheel diameter format is non-numeric

            # Display Result
            if len(incompatible_reasons) == 0:
                st.markdown(
                    '<div style="padding: 15px; background-color: #d4edda; color: #155724; border-radius: 5px; font-weight: bold; font-size: 18px;">✅ Yes, MU Compatible</div>',
                    unsafe_allow_html=True,
                )
                st.info(
                    f"Locomotives {loco_1} and {loco_2} successfully meet all"
                    " electrical, control, and mechanical wheel-tolerance"
                    " criteria for MU operation."
                )
            else:
                st.markdown(
                    '<div style="padding: 15px; background-color: #f8d7da; color: #721c24; border-radius: 5px; font-weight: bold; font-size: 18px;">❌ MU formation not possible</div>',
                    unsafe_allow_html=True,
                )
                st.error("Reasons for incompatibility:")
                for reason in incompatible_reasons:
                    st.markdown(f"- {reason}")

# --- BOTTOM FOOTER / PDF UPDATE NOTICE ---
st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Tip:** Use the file uploader above to load a newly generated Loco"
    " Position PDF. The application will dynamically parse updated records"
    " instantly."
)
