import streamlit as st
import duckdb
import plotly.express as px

st.set_page_config(page_title="Airbnb Analytics", layout="wide")
st.title("🏠 Plateforme d'analyse Airbnb")
st.caption("Pipeline dbt + DuckDB — couches Bronze / Silver / Gold")

con = duckdb.connect("airbnb.duckdb", read_only=True)

def q(sql, params=None):
    return con.execute(sql, params or []).fetchdf()

# ---- Filtre dynamique ----
st.sidebar.header("Filtres")
room_types = q("SELECT DISTINCT room_type FROM sl_listings ORDER BY room_type")["room_type"].tolist()
selected = st.sidebar.multiselect("Type de logement", room_types, default=room_types)

# Sécurité : si rien n'est sélectionné, on prend tout
filtre = selected if selected else room_types
# Placeholders SQL pour le filtre (?, ?, ...)
ph = ",".join("?" for _ in filtre)

st.sidebar.markdown(f"**{len(filtre)}** type(s) sélectionné(s)")

# ---- 1. Logements et prix par type ----
st.subheader("1. Nombre de logements et prix moyen par type de logement")
df1 = q(f"""
    SELECT room_type,
           COUNT(*) AS nb_listings,
           ROUND(AVG(price), 2) AS avg_price
    FROM sl_listings
    WHERE room_type IN ({ph})
    GROUP BY room_type
    ORDER BY nb_listings DESC
""", filtre)
col1, col2 = st.columns(2)
with col1:
    fig = px.bar(df1, x="room_type", y="nb_listings", title="Nombre de logements")
    fig.update_layout(xaxis_title="Type de logement", yaxis_title="Nombre de logements")
    st.plotly_chart(fig, width="stretch")
with col2:
    fig = px.bar(df1, x="room_type", y="avg_price", title="Prix moyen (€)")
    fig.update_layout(xaxis_title="Type de logement", yaxis_title="Prix moyen")
    st.plotly_chart(fig, width="stretch")

# ---- 2. Top hôtes (filtré par type de logement) ----
st.subheader("2. Top 15 des hôtes par nombre de logements")
df2 = q(f"""
    SELECT h.host_name, h.is_superhost,
           COUNT(l.listing_id) AS nb_listings
    FROM sl_hosts h
    JOIN sl_listings l ON l.host_id = h.host_id
    WHERE l.room_type IN ({ph})
    GROUP BY h.host_name, h.is_superhost
    ORDER BY nb_listings DESC
    LIMIT 15
""", filtre)
fig = px.bar(df2, x="host_name", y="nb_listings", color="is_superhost",
             title="Les plus gros hôtes (couleur = superhôte)",
             labels={"host_name": "Hôte", "nb_listings": "Nombre de logements",
                     "is_superhost": "Superhôte"})
st.plotly_chart(fig, width="stretch")

# ---- 3. Avis dans le temps (filtré par type de logement) ----
st.subheader("3. Évolution du nombre d'avis dans le temps")
df3 = q(f"""
    SELECT date_trunc('month', r.review_date) AS month,
           COUNT(*) AS nb_reviews
    FROM sl_reviews r
    JOIN sl_listings l ON l.listing_id = r.listing_id
    WHERE l.room_type IN ({ph})
    GROUP BY 1
    ORDER BY 1
""", filtre)
fig = px.line(df3, x="month", y="nb_reviews", title="Nombre d'avis par mois")
fig.update_layout(xaxis_title="Période (par mois)", yaxis_title="Nombre d'avis")
st.plotly_chart(fig, width="stretch")

# ---- 4. Impact de la pleine lune (filtré par type de logement) ----
st.subheader("4. Impact de la pleine lune sur les avis")
df4 = q(f"""
    WITH moon AS (
        SELECT DISTINCT CAST(full_moon_date AS DATE) AS d
        FROM main_main.seed_full_moon_dates
    ),
    rf AS (
        SELECT r.review_date,
               (moon.d IS NOT NULL) AS is_full_moon,
               CASE WHEN r.sentiment = 'positive' THEN 1.0 ELSE 0.0 END AS is_positive
        FROM sl_reviews r
        JOIN sl_listings l ON l.listing_id = r.listing_id
        LEFT JOIN moon ON r.review_date = moon.d
        WHERE l.room_type IN ({ph})
    )
    SELECT CASE WHEN is_full_moon THEN 'Pleine lune' ELSE 'Nuit normale' END AS periode,
           COUNT(*) AS nb_reviews,
           COUNT(DISTINCT review_date) AS nb_nuits,
           ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT review_date), 1) AS avis_par_nuit,
           ROUND(AVG(is_positive) * 100, 1) AS pct_positif
    FROM rf
    GROUP BY 1
""", filtre)

if not df4.empty and len(df4) == 2:
    normale = df4[df4["periode"] == "Nuit normale"].iloc[0]
    lune = df4[df4["periode"] == "Pleine lune"].iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Avis/nuit (normale)", f"{normale['avis_par_nuit']:.1f}")
    c2.metric("Avis/nuit (pleine lune)", f"{lune['avis_par_nuit']:.1f}",
              delta=f"{lune['avis_par_nuit'] - normale['avis_par_nuit']:.1f}")
    c3.metric("Écart de positivité", f"{lune['pct_positif'] - normale['pct_positif']:.1f} pts")

col5, col6 = st.columns(2)
with col5:
    fig = px.bar(df4, x="periode", y="avis_par_nuit",
                 title="Avis par nuit (comparaison équitable)", color="periode")
    fig.update_layout(xaxis_title="", yaxis_title="Avis par nuit", showlegend=False)
    st.plotly_chart(fig, width="stretch")
with col6:
    fig = px.bar(df4, x="periode", y="pct_positif",
                 title="Taux de sentiment positif (%)", color="periode")
    fig.update_yaxes(range=[50, 60])
    fig.update_layout(xaxis_title="", yaxis_title="% d'avis positifs", showlegend=False)
    st.plotly_chart(fig, width="stretch")

df4_affichage = df4.rename(columns={
    "periode": "Période",
    "nb_reviews": "Nombre d'avis",
    "nb_nuits": "Nombre de nuits",
    "avis_par_nuit": "Avis par nuit",
    "pct_positif": "% d'avis positifs"
})
st.dataframe(df4_affichage, width="stretch")