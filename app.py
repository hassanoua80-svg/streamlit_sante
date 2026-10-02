import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(
    page_title="Dashboard – Rendez-vous de soins",
    page_icon="🏥",
    layout="wide"
)

DATA_PATH = Path(__file__).parent / "rendez_vous_soins_2026.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(DATA_PATH, engine="openpyxl")

    # Nettoyage des types
    df["Date rendez-vous"] = pd.to_datetime(
        df["Date rendez-vous"], errors="coerce"
    )

    numeric_cols = [
        "Délai RDV (jours)",
        "Attente sur place (min)",
        "Consultation (min)",
        "Satisfaction /5",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Suppression des doublons d'identifiant
    df = df.drop_duplicates(subset=["ID rendez-vous"]).copy()

    # Les mesures d'attente, consultation et satisfaction sont naturellement
    # manquantes pour les rendez-vous non honorés : on ne les remplace pas par 0.
    return df


df = load_data()

st.title("🏥 Tableau de bord – Organisation des rendez-vous de soins")
st.caption(
    "Réseau de cliniques fictif · janvier–août 2026 · 800 rendez-vous. "
    "Données administratives créées pour un exercice de formation."
)

# ------------------------- Filtres -------------------------
st.sidebar.header("🔎 Filtres")

min_date = df["Date rendez-vous"].min().date()
max_date = df["Date rendez-vous"].max().date()

date_range = st.sidebar.date_input(
    "Période",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

villes = st.sidebar.multiselect(
    "Ville",
    sorted(df["Ville"].dropna().unique()),
    default=sorted(df["Ville"].dropna().unique()),
)

services = st.sidebar.multiselect(
    "Service",
    sorted(df["Service"].dropna().unique()),
    default=sorted(df["Service"].dropna().unique()),
)

statuts = st.sidebar.multiselect(
    "Statut",
    sorted(df["Statut"].dropna().unique()),
    default=sorted(df["Statut"].dropna().unique()),
)

mask = (
    df["Date rendez-vous"].dt.date.between(start_date, end_date)
    & df["Ville"].isin(villes)
    & df["Service"].isin(services)
    & df["Statut"].isin(statuts)
)

data = df.loc[mask].copy()

if data.empty:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    st.stop()

# ------------------------- KPI -------------------------
total = len(data)
honores = int((data["Statut"] == "Honoré").sum())
absents = int((data["Statut"] == "Absent").sum())
annules = int((data["Statut"] == "Annulé").sum())

taux_honores = honores / total * 100
taux_absents = absents / total * 100
attente_moy = data.loc[
    data["Statut"] == "Honoré", "Attente sur place (min)"
].mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Rendez-vous", f"{total:,}".replace(",", " "))
c2.metric("Taux honorés", f"{taux_honores:.1f} %")
c3.metric("Taux d'absence", f"{taux_absents:.1f} %")
c4.metric(
    "Attente moyenne",
    "—" if pd.isna(attente_moy) else f"{attente_moy:.1f} min"
)

st.divider()

tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "❓ Les 6 questions", "🧾 Données"])

# ------------------------- Dashboard -------------------------
with tab1:
    left, right = st.columns(2)

    with left:
        st.subheader("Volume de rendez-vous par service")
        service_volume = (
            data.groupby("Service")
            .size()
            .sort_values(ascending=True)
        )
        fig, ax = plt.subplots(figsize=(7, 4))
        service_volume.plot(kind="barh", ax=ax)
        ax.set_xlabel("Nombre de rendez-vous")
        ax.set_ylabel("Service")
        ax.set_title("Volume des rendez-vous")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with right:
        st.subheader("Répartition des statuts par service")
        status_pct = (
            pd.crosstab(data["Service"], data["Statut"], normalize="index")
            .mul(100)
            .reindex(columns=["Honoré", "Absent", "Annulé"], fill_value=0)
        )

        fig, ax = plt.subplots(figsize=(7, 4))
        status_pct.plot(kind="bar", ax=ax)
        ax.set_ylabel("Pourcentage (%)")
        ax.set_xlabel("Service")
        ax.set_title("Honorés, absents et annulés")
        ax.set_ylim(0, 100)
        ax.tick_params(axis="x", rotation=35)
        ax.legend(title="Statut")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    st.subheader("Évolution mensuelle du volume et des absences")
    monthly = (
        data.assign(Mois=data["Date rendez-vous"].dt.to_period("M").astype(str))
        .groupby("Mois")
        .agg(
            volume=("ID rendez-vous", "size"),
            absences=("Statut", lambda s: (s == "Absent").sum()),
        )
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(monthly["Mois"], monthly["volume"], marker="o", label="Volume")
    ax.plot(monthly["Mois"], monthly["absences"], marker="o", label="Absences")
    ax.set_xlabel("Mois")
    ax.set_ylabel("Nombre")
    ax.set_title("Volume et absences par mois")
    ax.legend()
    ax.grid(alpha=0.25)
    plt.xticks(rotation=35)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Attente moyenne sur place par ville – rendez-vous honorés")
    honored = data[data["Statut"] == "Honoré"].copy()
    wait_city = (
        honored.groupby("Ville")["Attente sur place (min)"]
        .mean()
        .sort_values(ascending=False)
    )

    if wait_city.empty:
        st.info("Pas de rendez-vous honoré dans les filtres sélectionnés.")
    else:
        fig, ax = plt.subplots(figsize=(10, 4))
        wait_city.sort_values().plot(kind="barh", ax=ax)
        ax.set_xlabel("Attente moyenne (minutes)")
        ax.set_ylabel("Ville")
        ax.set_title("Attente moyenne par ville")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

# ------------------------- Six questions -------------------------
with tab2:
    st.header("Réponses aux six questions du Mode d'emploi")

    st.subheader("1. Quel service reçoit le plus de rendez-vous ?")
    q1 = data.groupby("Service").size().sort_values(ascending=False)
    top_service = q1.index[0]
    st.write(
        f"**Réponse : {top_service}**, avec **{int(q1.iloc[0])} rendez-vous** "
        f"sur la période filtrée."
    )
    st.dataframe(q1.rename("Nombre de rendez-vous"), use_container_width=True)

    st.subheader("2. Quel est le taux de rendez-vous honorés, absents et annulés par service ?")
    q2 = (
        pd.crosstab(data["Service"], data["Statut"], normalize="index")
        .mul(100)
        .round(1)
        .reindex(columns=["Honoré", "Absent", "Annulé"], fill_value=0)
    )
    st.dataframe(q2.style.format("{:.1f} %"), use_container_width=True)
    st.caption(
        "Dénominateur : nombre total de rendez-vous prévus dans chaque service. "
        "Cette définition suit le Mode d'emploi."
    )

    st.subheader("3. Quels services ont les délais de rendez-vous les plus longs ?")
    q3 = (
        data.groupby("Service")["Délai RDV (jours)"]
        .agg(["mean", "median", "max"])
        .sort_values("mean", ascending=False)
        .round(1)
        .rename(columns={
            "mean": "Moyenne (jours)",
            "median": "Médiane (jours)",
            "max": "Maximum (jours)"
        })
    )
    st.dataframe(q3, use_container_width=True)
    st.write(
        f"Le délai moyen le plus élevé est observé en **{q3.index[0]}** "
        f"({q3.iloc[0, 0]:.1f} jours)."
    )

    st.subheader("4. Parmi les visites honorées, comment l'attente varie-t-elle selon la ville ?")
    q4 = (
        data[data["Statut"] == "Honoré"]
        .groupby("Ville")["Attente sur place (min)"]
        .agg(["count", "mean", "median"])
        .sort_values("mean", ascending=False)
        .round(1)
        .rename(columns={
            "count": "Visites honorées",
            "mean": "Attente moyenne (min)",
            "median": "Médiane (min)"
        })
    )
    st.dataframe(q4, use_container_width=True)
    st.caption(
        "Cette comparaison porte uniquement sur les rendez-vous honorés. "
        "Elle décrit une différence entre villes et ne prouve pas sa cause."
    )

    st.subheader("5. Comment le volume et les absences évoluent-ils par mois ?")
    q5 = (
        data.assign(Mois=data["Date rendez-vous"].dt.to_period("M").astype(str))
        .groupby("Mois")
        .agg(
            Volume=("ID rendez-vous", "size"),
            Absences=("Statut", lambda s: (s == "Absent").sum()),
        )
    )
    q5["Taux d'absence (%)"] = (q5["Absences"] / q5["Volume"] * 100).round(1)
    st.dataframe(q5, use_container_width=True)

    if len(q5) > 0:
        peak_month = q5["Taux d'absence (%)"].idxmax()
        peak_rate = q5.loc[peak_month, "Taux d'absence (%)"]
        st.write(
            f"Le mois avec le taux d'absence le plus élevé dans la sélection est "
            f"**{peak_month} ({peak_rate:.1f} %)**."
        )

    st.subheader("6. Quelle amélioration de l'organisation proposeriez-vous ?")

    # Proposition basée sur l'ensemble du fichier, sans prétendre démontrer une causalité.
    overall_absence = (df["Statut"] == "Absent").mean() * 100
    channel_abs = (
        pd.crosstab(df["Canal réservation"], df["Statut"], normalize="index")
        .mul(100)
    )
    web_abs = channel_abs.loc["Site web", "Absent"]
    month_all = (
        df.assign(Mois=df["Date rendez-vous"].dt.to_period("M").astype(str))
        .groupby("Mois")
        .agg(
            volume=("ID rendez-vous", "size"),
            absences=("Statut", lambda s: (s == "Absent").sum()),
        )
    )
    month_all["taux"] = month_all["absences"] / month_all["volume"] * 100
    worst_month = month_all["taux"].idxmax()
    worst_month_rate = month_all.loc[worst_month, "taux"]

    st.markdown(
        f"""
**Proposition : renforcer la confirmation et les rappels des rendez-vous**, 
en ciblant en priorité les réservations faites via le site web et les périodes
où les absences augmentent.

Dans le fichier complet, le taux d'absence est de **{overall_absence:.1f} %**.
Le **site web** présente un taux d'absence de **{web_abs:.1f} %**, contre
**{channel_abs.loc["WhatsApp", "Absent"]:.1f} %** sur WhatsApp. Le mois de
**{worst_month}** atteint **{worst_month_rate:.1f} %** d'absences.

Ces écarts justifient un test organisationnel de rappels/confirmation,
mais ils ne démontrent pas à eux seuls que le canal de réservation est la
cause des absences.
"""
    )

    st.subheader("📝 Deux résultats importants à retenir")
    full_service = df.groupby("Service").size().sort_values(ascending=False)
    full_delay = (
        df.groupby("Service")["Délai RDV (jours)"].mean().sort_values(ascending=False)
    )
    full_wait = (
        df[df["Statut"] == "Honoré"]
        .groupby("Ville")["Attente sur place (min)"]
        .mean()
        .sort_values(ascending=False)
    )

    st.markdown(
        f"""
1. **Médecine générale** représente le plus gros volume avec
**{full_service["Médecine générale"]} rendez-vous sur 800**. Cela signifie que
toute amélioration sur ce service peut avoir un impact opérationnel important.

2. **Cardiologie** a le délai moyen de rendez-vous le plus long
(**{full_delay["Cardiologie"]:.1f} jours**) et **Casablanca** a l'attente moyenne
la plus élevée parmi les visites honorées (**{full_wait["Casablanca"]:.1f} min**).
Ces résultats permettent de cibler l'analyse de capacité et d'organisation.
"""
    )

# ------------------------- Data -------------------------
with tab3:
    st.subheader("Données filtrées")
    st.dataframe(data, use_container_width=True, height=500)

    missing = data.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if not missing.empty:
        st.info(
            "Valeurs manquantes : elles concernent surtout l'attente, la durée "
            "de consultation et la satisfaction pour les rendez-vous non honorés. "
            "Elles sont conservées comme valeurs manquantes et non transformées en 0."
        )
        st.dataframe(missing.rename("Valeurs manquantes"), use_container_width=True)

st.divider()
st.caption(
    "Source : fichier pédagogique « Organisation des rendez-vous de soins ». "
    "Les données sont fictives et ne concernent aucun patient réel."
)
