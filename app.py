# app.py
# Streamlit web app: Commission & Incentive Calculator
# Salesman includes:
# - 4 categories (IRU / Fiber Lease / Build / DC Grid)
# - Commission Rules reference table
# - Commission Table with tick-to-delete + clear all buttons
# - Bonus tiers (auto sum) with robust column normalization
#
# Project Manager + Delivery Team are replaced with your provided full logic (tiers + weighted KPI)

import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Commission & Incentive Calculator", layout="centered")
st.title("Commission & Incentive Calculator")


def clamp_0_1(x: float) -> float:
    return max(0.0, min(1.0, x))


# =========================================================
# Role selector
# =========================================================
role = st.selectbox("Role", ["Salesman", "Project Manager", "Delivery Team"])
st.divider()

# =========================================================
# SALESMAN
# =========================================================
if role == "Salesman":
    st.subheader("Sales Incentive")

    currency = st.selectbox("Currency", ["USD", "RM"], key="sm_currency")

    # =========================
    # Session storage
    # =========================
    if "sales_rows" not in st.session_state:
        st.session_state.sales_rows = []

    # Default tier headers (friendly names)
    # Bonus % is stored as "percent" (e.g. 0.2 means 0.2%)
    if "sales_bonus_tiers" not in st.session_state:
        st.session_state.sales_bonus_tiers = pd.DataFrame(
            [
                {"Min Total Contract Value (inclusive)": 0, "Bonus % on Total": 0.0},
                {"Min Total Contract Value (inclusive)": 1_000_000, "Bonus % on Total": 0.2},
                {"Min Total Contract Value (inclusive)": 5_000_000, "Bonus % on Total": 0.5},
                {"Min Total Contract Value (inclusive)": 10_000_000, "Bonus % on Total": 0.8},
                {"Min Total Contract Value (inclusive)": 15_000_000, "Bonus % on Total": 1.0},
            ]
        )

    def normalize_tier_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize possible tier column names (in case user renamed headers in the editor).
        Output columns will be:
          - Min Total Contract Value
          - Bonus %
        """
        rename_map = {
            "Min Total Contract Value": "Min Total Contract Value",
            "Min Total Contract Value (inclusive)": "Min Total Contract Value",
            "Min Total Contract Value (Inclusive)": "Min Total Contract Value",
            "Bonus %": "Bonus %",
            "Bonus % on Total": "Bonus %",
            "Bonus % On Total": "Bonus %",
        }
        out = df.copy()
        out.columns = [c.strip() for c in out.columns]
        out = out.rename(columns=rename_map)

        if "Min Total Contract Value" in out.columns:
            out["Min Total Contract Value"] = pd.to_numeric(out["Min Total Contract Value"], errors="coerce").fillna(0.0)
        if "Bonus %" in out.columns:
            out["Bonus %"] = pd.to_numeric(out["Bonus %"], errors="coerce").fillna(0.0)

        return out

    # =========================
    # Reference: Commission Rules Table (for all 4 categories)
    # =========================
    with st.expander("📌 Commission Rules (Reference Table)", expanded=True):
        st.caption("Reference only. The calculator below uses these formulas.")
        rules_df = pd.DataFrame(
            [
                {
                    "Category": "IRU",
                    "Rate Rule": "Base 3% + 0.1% per extra pair (pairs > 1)",
                    "Commission Formula": "Contract Value × Rate",
                },
                {
                    "Category": "Fiber Lease",
                    "Rate Rule": "Base 2% + 0.1% per extra pair (pairs > 1)",
                    "Commission Formula": "Contract Value × Rate",
                },
                {
                    "Category": "Build to Own",
                    "Rate Rule": "<5M=1.2%; 5–15M linearly 1.5%→3.0%; >15M=3.0%; +0.2% if 50% prepaid",
                    "Commission Formula": "Contract Value × Rate",
                },
                {
                    "Category": "DC Grid",
                    "Rate Rule": "Existing=3%; New=4%; Hyperscaler=5%",
                    "Commission Formula": "Contract Value × Rate",
                },
            ]
        )
        st.dataframe(rules_df, use_container_width=True, hide_index=True)

    st.divider()

    # =========================
    # INPUT SECTION (4 categories)
    # =========================
    st.markdown("### Add Commission Item (each category has its own date)")

    # ---------- IRU ----------
    with st.expander("1) IRU", expanded=True):
        iru_date = st.date_input("Deal date (IRU)", value=date.today(), key="iru_date")
        c1, c2, c3, c4 = st.columns([2, 2, 1, 1])

        with c1:
            iru_customer = st.text_input("Customer", key="iru_c")
        with c2:
            iru_value = st.number_input(
                f"Contract Value ({currency})",
                min_value=0.0,
                value=0.0,
                step=10000.0,
                key="iru_v",
            )
        with c3:
            iru_pairs = st.number_input("Pairs", min_value=0, value=0, step=1, key="iru_p")
        with c4:
            if st.button("Add IRU", key="add_iru"):
                base = 0.03
                new_pairs = max(int(iru_pairs) - 1, 0)
                rate = base + (new_pairs * 0.001)  # +0.1% per extra pair
                commission = float(iru_value) * rate

                st.session_state.sales_rows.append(
                    {
                        "Date": str(iru_date),
                        "Category": "IRU",
                        "Customer": (iru_customer or "").strip(),
                        "Contract Value": float(iru_value),
                        "Pairs": int(iru_pairs),
                        "Rate %": round(rate * 100, 3),
                        "Commission": float(commission),
                        "Currency": currency,
                    }
                )
                st.rerun()

    # ---------- FIBER LEASE ----------
    with st.expander("2) Fiber Lease", expanded=True):
        lease_date = st.date_input("Deal date (Lease)", value=date.today(), key="lease_date")
        c1, c2, c3, c4 = st.columns([2, 2, 1, 1])

        with c1:
            l_customer = st.text_input("Customer", key="l_c")
        with c2:
            l_value = st.number_input(
                f"Contract Value ({currency})",
                min_value=0.0,
                value=0.0,
                step=10000.0,
                key="l_v",
            )
        with c3:
            l_pairs = st.number_input("Pairs", min_value=0, value=0, step=1, key="l_p")
        with c4:
            if st.button("Add Lease", key="add_lease"):
                base = 0.02
                new_pairs = max(int(l_pairs) - 1, 0)
                rate = base + (new_pairs * 0.001)  # +0.1% per extra pair
                commission = float(l_value) * rate

                st.session_state.sales_rows.append(
                    {
                        "Date": str(lease_date),
                        "Category": "Fiber Lease",
                        "Customer": (l_customer or "").strip(),
                        "Contract Value": float(l_value),
                        "Pairs": int(l_pairs),
                        "Rate %": round(rate * 100, 3),
                        "Commission": float(commission),
                        "Currency": currency,
                    }
                )
                st.rerun()

    # ---------- BUILD ----------
    with st.expander("3) Build to Own", expanded=True):
        build_date = st.date_input("Deal date (Build)", value=date.today(), key="build_date")
        c1, c2, c3, c4 = st.columns([2, 2, 1, 1])

        with c1:
            b_customer = st.text_input("Customer", key="b_c")
        with c2:
            b_value = st.number_input(
                f"Contract Value ({currency})",
                min_value=0.0,
                value=0.0,
                step=10000.0,
                key="b_v",
            )
        with c3:
            prepay = st.checkbox("50% prepaid (+0.2%)", key="b_prepay")
        with c4:
            if st.button("Add Build", key="add_build"):
                v = float(b_value)

                if v < 5_000_000:
                    base = 0.012
                elif v <= 15_000_000:
                    t = (v - 5_000_000) / 10_000_000
                    base = 0.015 + (0.03 - 0.015) * clamp_0_1(t)
                else:
                    base = 0.03

                if prepay:
                    base += 0.002

                commission = v * base

                st.session_state.sales_rows.append(
                    {
                        "Date": str(build_date),
                        "Category": "Build",
                        "Customer": (b_customer or "").strip(),
                        "Contract Value": float(b_value),
                        "Pairs": "",
                        "Rate %": round(base * 100, 3),
                        "Commission": float(commission),
                        "Currency": currency,
                    }
                )
                st.rerun()

    # ---------- DC GRID ----------
    with st.expander("4) DC Grid", expanded=True):
        dc_date = st.date_input("Deal date (DC Grid)", value=date.today(), key="dc_date")
        c1, c2, c3, c4 = st.columns([2, 2, 1, 1])

        with c1:
            d_customer = st.text_input("Customer", key="d_c")
        with c2:
            d_value = st.number_input(
                f"Contract Value ({currency})",
                min_value=0.0,
                value=0.0,
                step=10000.0,
                key="d_v",
            )
        with c3:
            d_type = st.selectbox("Type", ["Existing 3%", "New 4%", "Hyperscaler 5%"], key="d_type")
        with c4:
            if st.button("Add DC", key="add_dc"):
                if "3" in d_type:
                    rate = 0.03
                elif "4" in d_type:
                    rate = 0.04
                else:
                    rate = 0.05

                commission = float(d_value) * rate

                st.session_state.sales_rows.append(
                    {
                        "Date": str(dc_date),
                        "Category": "DC Grid",
                        "Customer": (d_customer or "").strip(),
                        "Contract Value": float(d_value),
                        "Pairs": "",
                        "Rate %": round(rate * 100, 3),
                        "Commission": float(commission),
                        "Currency": currency,
                    }
                )
                st.rerun()

    st.divider()

    # =========================
    # COMMISSION TABLE (Saved Deals) - tick + delete selected + clear all
    # =========================
    st.markdown("## Commission Table (Saved Deals)")

    if st.session_state.sales_rows:
        df_all = pd.DataFrame(st.session_state.sales_rows)
        df_view = df_all[df_all["Currency"] == currency].reset_index(drop=True).copy()

        if df_view.empty:
            st.info("No data for this currency yet.")
        else:
            df_view.insert(0, "No.", range(1, len(df_view) + 1))
            df_view.insert(1, "🗑 Delete?", False)

            st.caption("Tick rows to delete, then click 'Delete ticked rows'.")

            edited = st.data_editor(
                df_view,
                use_container_width=True,
                hide_index=True,
                key=f"sales_table_editor_{currency}",
                disabled=[
                    "No.", "Date", "Category", "Customer", "Contract Value",
                    "Pairs", "Rate %", "Commission", "Currency"
                ],
            )

            total_value = float(df_view["Contract Value"].sum())
            total_comm = float(df_view["Commission"].sum())
            st.write(f"Total Contract Value: {total_value:,.2f} {currency}")
            st.write(f"Total Commission: {total_comm:,.2f} {currency}")

            col1, col2, col3 = st.columns([1.2, 1.2, 1.6])

            with col1:
                if st.button("🗑 Delete ticked rows", key=f"btn_delete_ticked_{currency}"):
                    ticked_nos = edited.loc[edited["🗑 Delete?"] == True, "No."].tolist()

                    if not ticked_nos:
                        st.warning("No rows ticked.")
                    else:
                        cur_rows = [r for r in st.session_state.sales_rows if r["Currency"] == currency]
                        other_rows = [r for r in st.session_state.sales_rows if r["Currency"] != currency]

                        keep_cur = []
                        for i, r in enumerate(cur_rows):
                            row_no = i + 1
                            if row_no not in ticked_nos:
                                keep_cur.append(r)

                        st.session_state.sales_rows = other_rows + keep_cur
                        st.rerun()

            with col2:
                if st.button(f"🧹 Clear ALL ({currency})", key=f"btn_clear_currency_{currency}"):
                    st.session_state.sales_rows = [r for r in st.session_state.sales_rows if r["Currency"] != currency]
                    st.rerun()

            with col3:
                if st.button("🔥 Clear ALL (ALL currencies)", key="btn_clear_all_currencies"):
                    st.session_state.sales_rows = []
                    st.rerun()
    else:
        st.info("No data yet. Add a deal in any category.")

    st.divider()

    # =========================
    # FINAL BONUS AUTO SUM
    # =========================
    st.markdown("## FINAL BONUS (Auto Sum)")
    st.caption("Bonus is based on TOTAL contract value (same currency). Bonus % is percent (e.g. 0.2 means 0.2%).")

    st.session_state.sales_bonus_tiers = st.data_editor(
        st.session_state.sales_bonus_tiers,
        use_container_width=True,
        hide_index=True,
        key="bonus_tiers_editor",
    )

    tiers_norm = normalize_tier_df(st.session_state.sales_bonus_tiers)
    required_cols = {"Min Total Contract Value", "Bonus %"}
    if not required_cols.issubset(set(tiers_norm.columns)):
        st.error(
            "Bonus tiers must contain columns like:\n"
            "- Min Total Contract Value (inclusive)\n"
            "- Bonus % on Total\n\n"
            f"Current columns: {tiers_norm.columns.tolist()}"
        )
        st.stop()

    df_all = pd.DataFrame(st.session_state.sales_rows) if st.session_state.sales_rows else pd.DataFrame()
    df = df_all[df_all["Currency"] == currency] if not df_all.empty else pd.DataFrame()

    if df.empty:
        st.info("Add at least 1 row in this currency to calculate bonus.")
    else:
        total_value = float(df["Contract Value"].sum())
        total_comm = float(df["Commission"].sum())

        tiers = tiers_norm.sort_values("Min Total Contract Value")

        bonus_rate = 0.0
        for _, r in tiers.iterrows():
            if total_value >= float(r["Min Total Contract Value"]):
                bonus_rate = float(r["Bonus %"]) / 100.0

        bonus = total_value * bonus_rate
        total_incentive = total_comm + bonus

        st.write(f"Bonus Rate: **{bonus_rate*100:.2f}%**")
        st.write(f"Bonus Amount: **{bonus:,.2f} {currency}**")
        st.success(
            f"✅ TOTAL incentive = Commission {total_comm:,.2f} {currency} "
            f"+ Bonus {bonus:,.2f} {currency} = **{total_incentive:,.2f} {currency}**"
        )

# =========================================================
# PROJECT MANAGER (your provided full block)
# =========================================================
elif role == "Project Manager":
    st.subheader("Project Manager Incentive (On-time Projects + KPI Bonus)")
    currency = st.selectbox("Currency", ["RM", "USD"], key="pm_currency")

    def clamp_0_100(x: float) -> float:
        return max(0.0, min(100.0, x))

    st.markdown("## Part A — On-time Delivery Bonus (Tiered)")
    st.caption("Enter number of projects delivered on time. Bonus is calculated by editable tiers.")

    ontime_projects = st.number_input(
        "Number of projects delivered on time",
        min_value=0,
        value=0,
        step=1,
        key="pm_ontime_projects",
    )

    st.markdown("### Tier setup (editable)")
    tiers_default = pd.DataFrame(
        [
            {"Tier": "Tier 1", "From #": 1, "To #": 3, "Rate per project": 500.0},
            {"Tier": "Tier 2", "From #": 4, "To #": 6, "Rate per project": 700.0},
            {"Tier": "Tier 3", "From #": 7, "To #": 9999, "Rate per project": 900.0},
        ]
    )
    tiers = st.data_editor(tiers_default, use_container_width=True, hide_index=True, key="pm_tiers_editor")

    part_a_bonus = 0.0
    breakdown_rows = []
    tiers_sorted = tiers.sort_values("From #")

    for _, t in tiers_sorted.iterrows():
        start = int(t["From #"])
        end = int(t["To #"])
        rate = float(t["Rate per project"])

        if ontime_projects < start:
            continue

        tier_count = min(ontime_projects, end) - start + 1
        tier_count = max(tier_count, 0)

        tier_pay = tier_count * rate
        part_a_bonus += tier_pay

        breakdown_rows.append(
            {
                "Tier": str(t["Tier"]),
                "Projects counted": tier_count,
                "Rate per project": f"{rate:,.2f} {currency}",
                "Tier payout": f"{tier_pay:,.2f} {currency}",
            }
        )

    st.write("### Tier breakdown")
    st.dataframe(pd.DataFrame(breakdown_rows), use_container_width=True)
    st.success(f"Part A On-time bonus: {part_a_bonus:,.2f} {currency}")

    st.divider()

    st.markdown("## Part B — KPI Bonus (based on basic salary)")
    st.caption(
        "KPI is weighted to 100%. "
        "Bonus months rule: KPI < 50% = 1.00 month; KPI 50–100% scales up to 6.00 months."
    )

    basic_salary = st.number_input(
        f"Basic salary per month ({currency})",
        min_value=0.0,
        value=8000.0,
        step=100.0,
        key="pm_basic_salary",
    )

    st.markdown("#### 1) On-time completion — 40%")
    milestone_on_schedule_pct = st.number_input(
        "% of milestones achieved on schedule (0–100)",
        min_value=0.0,
        max_value=100.0,
        value=90.0,
        step=1.0,
        key="pm_milestone_pct",
    )
    delay_days = st.number_input(
        "Final completion delay (days)",
        min_value=0.0,
        value=0.0,
        step=1.0,
        key="pm_delay_days",
    )

    milestone_score = clamp_0_100(milestone_on_schedule_pct)
    timeline_score = clamp_0_100(100.0 - 5.0 * delay_days)
    ontime_header_score = (milestone_score + timeline_score) / 2.0
    st.write(f"On-time completion score: **{ontime_header_score:.2f}/100**")
    st.divider()

    st.markdown("#### 2) Delivery quality — 20%")
    otdr_fail = st.checkbox("OTDR test fail happened (tick if YES)", key="pm_otdr_fail")
    no_major_defect_60 = st.checkbox("No major defect within 60 days", key="pm_no_major_defect_60")

    quality_score = 100.0
    if otdr_fail:
        quality_score -= 50.0
    if not no_major_defect_60:
        quality_score -= 50.0
    quality_score = clamp_0_100(quality_score)
    st.write(f"Delivery quality score: **{quality_score:.2f}/100**")
    st.divider()

    st.markdown("#### 3) Customer acceptance & activation — 15%")
    activation_no_dispute = st.checkbox("Activation without dispute", key="pm_activation_no_dispute")
    no_sla_penalty_60 = st.checkbox("No SLA penalty within 60 days after activation", key="pm_no_sla_penalty_60")

    cust_score = ((100.0 if activation_no_dispute else 0.0) + (100.0 if no_sla_penalty_60 else 0.0)) / 2.0
    st.write(f"Customer acceptance & activation score: **{cust_score:.2f}/100**")
    st.divider()

    st.markdown("#### 4) Compliance & safety — 15%")
    no_authority_penalty = st.checkbox("No authority penalty", key="pm_no_authority_penalty")
    no_safety_incident = st.checkbox("No safety incident", key="pm_no_safety_incident")

    comp_score = ((100.0 if no_authority_penalty else 0.0) + (100.0 if no_safety_incident else 0.0)) / 2.0
    st.write(f"Compliance & safety score: **{comp_score:.2f}/100**")
    st.divider()

    st.markdown("#### 5) Internal coordination & reporting — 10%")
    weekly_reporting = st.checkbox("Weekly reporting discipline", key="pm_weekly_reporting")
    accurate_tracking = st.checkbox("Accurate tracking of material & labour usage report", key="pm_accurate_tracking")

    internal_score = ((100.0 if weekly_reporting else 0.0) + (100.0 if accurate_tracking else 0.0)) / 2.0
    st.write(f"Internal coordination & reporting score: **{internal_score:.2f}/100**")
    st.divider()

    KPI_total = (
        ontime_header_score * 0.40
        + quality_score * 0.20
        + cust_score * 0.15
        + comp_score * 0.15
        + internal_score * 0.10
    )
    kpi_score = KPI_total / 100.0

    st.markdown("### KPI Result")
    st.write(f"**Overall KPI score:** **{KPI_total:.2f}%**")

    if kpi_score < 0.5:
        bonus_months = 1.0
    else:
        bonus_months = 1.0 + 5.0 * ((kpi_score - 0.5) / 0.5)

    bonus_months = min(bonus_months, 6.0)
    bonus_months = round(bonus_months, 2)

    st.write(f"**Bonus months (1.00 to 6.00):** **{bonus_months:.2f} months**")

    part_b_bonus = basic_salary * bonus_months * kpi_score
    st.success(f"Part B KPI bonus payout: {part_b_bonus:,.2f} {currency}")

    st.divider()

    total_pm_incentive = part_a_bonus + part_b_bonus
    st.success(f"✅ Total Project Manager incentive: {total_pm_incentive:,.2f} {currency}")

# =========================================================
# DELIVERY TEAM (your provided full block)
# =========================================================
else:
    st.subheader("Delivery Team Incentive (On-time • Budget • Safety • Quality)")
    currency = st.selectbox("Currency", ["RM", "USD"], key="dt_currency")

    st.caption("Reward delivery team for completing projects on time, within budget, safely, and with quality.")

    basic_salary = st.number_input(
        f"Basic salary per month ({currency})",
        min_value=0.0,
        value=3500.0,
        step=50.0,
        key="dt_basic_salary",
    )

    def clamp_0_100(x: float) -> float:
        return max(0.0, min(100.0, x))

    st.markdown("#### 1) On-time delivery — 35%")
    milestone_on_schedule_pct = st.number_input(
        "% milestones completed on schedule (0–100)",
        min_value=0.0,
        max_value=100.0,
        value=90.0,
        step=1.0,
        key="dt_milestone_pct",
    )
    delay_days = st.number_input(
        "Delay days vs baseline (0 if on time)",
        min_value=0.0,
        value=0.0,
        step=1.0,
        key="dt_delay_days",
    )
    no_missed_critical = st.checkbox("No missed critical milestone", key="dt_no_missed_critical")

    milestone_score = clamp_0_100(milestone_on_schedule_pct)
    delay_score = clamp_0_100(100.0 - 5.0 * delay_days)
    critical_score = 100.0 if no_missed_critical else 0.0

    ontime_score = (milestone_score + delay_score + critical_score) / 3.0
    st.write(f"On-time delivery score: **{ontime_score:.1f}/100**")
    st.divider()

    st.markdown("#### 2) Budget / cost control — 25%")
    st.caption("Variance % = (Actual - Budget) / Budget × 100. Positive means over budget.")
    cost_variance_pct = st.number_input(
        "Cost variance % (positive = over budget, 0 = on budget)",
        value=0.0,
        step=0.5,
        key="dt_cost_variance_pct",
    )
    material_wastage_ok = st.checkbox("Material wastage within limit", key="dt_material_wastage_ok")
    vo_approved_only = st.checkbox("Only approved variation orders (no unapproved extra work)", key="dt_vo_approved_only")

    if cost_variance_pct <= 0:
        variance_score = 100.0
    else:
        variance_score = clamp_0_100(100.0 - 10.0 * cost_variance_pct)

    wastage_score = 100.0 if material_wastage_ok else 0.0
    vo_score = 100.0 if vo_approved_only else 0.0

    budget_score = (variance_score + wastage_score + vo_score) / 3.0
    st.write(f"Budget / cost control score: **{budget_score:.1f}/100**")
    st.divider()

    st.markdown("#### 3) Quality workmanship — 20%")
    otdr_fail = st.checkbox("OTDR test fail happened (tick if YES)", key="dt_otdr_fail")
    no_major_defect_60 = st.checkbox("No major defect within 60 days", key="dt_no_major_defect_60")
    rework_due_to_team = st.checkbox("Rework required due to workmanship (tick if YES)", key="dt_rework_due_to_team")

    quality_score = 100.0
    if otdr_fail:
        quality_score -= 40.0
    if rework_due_to_team:
        quality_score -= 40.0
    if not no_major_defect_60:
        quality_score -= 20.0
    quality_score = clamp_0_100(quality_score)

    st.write(f"Quality workmanship score: **{quality_score:.1f}/100**")
    st.divider()

    st.markdown("#### 4) Safety & compliance — 15%")
    no_safety_incident = st.checkbox("No safety incident", key="dt_no_safety_incident")
    no_authority_penalty = st.checkbox("No authority penalty / permit violation", key="dt_no_authority_penalty")

    safety_score = ((100.0 if no_safety_incident else 0.0) + (100.0 if no_authority_penalty else 0.0)) / 2.0
    st.write(f"Safety & compliance score: **{safety_score:.1f}/100**")
    st.divider()

    st.markdown("#### 5) Reporting & coordination — 5%")
    weekly_reporting = st.checkbox("Weekly reporting discipline", key="dt_weekly_reporting")
    accurate_tracking = st.checkbox("Accurate material & labour usage tracking", key="dt_accurate_tracking")

    reporting_score = ((100.0 if weekly_reporting else 0.0) + (100.0 if accurate_tracking else 0.0)) / 2.0
    st.write(f"Reporting & coordination score: **{reporting_score:.1f}/100**")
    st.divider()

    KPI_total = (
        ontime_score * 0.35
        + budget_score * 0.25
        + quality_score * 0.20
        + safety_score * 0.15
        + reporting_score * 0.05
    )
    kpi_score = KPI_total / 100.0

    st.markdown("### KPI Result")
    st.write(f"**Overall KPI score:** **{KPI_total:.1f}%**")

    if kpi_score < 0.5:
        bonus_months = 1.0
    else:
        bonus_months = 1.0 + 5.0 * ((kpi_score - 0.5) / 0.5)

    bonus_months = min(bonus_months, 6.0)
    bonus_months = round(bonus_months, 2)

    st.write(f"**Bonus months (1.00 to 6.00):** **{bonus_months:.2f} months**")

    delivery_bonus = basic_salary * bonus_months * kpi_score
    st.success(f"Delivery Team KPI bonus payout: {delivery_bonus:,.2f} {currency}")

    st.divider()
    st.success(f"✅ Total Delivery Team incentive: {delivery_bonus:,.2f} {currency}")