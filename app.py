# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuration de la page ---
st.set_page_config(page_title="🎯 Le Capital", layout="wide", page_icon="dcg.jpg")

# --- Chargement des données ---
@st.cache_data
def load_data1():
    df = pd.read_csv("data/capital.csv")
    # Conversion de "Réussi" en numérique si besoin
    return df

def load_data2():
    df2 = pd.read_csv("data/parties.csv")
    # Conversion de "Réussi" en numérique si besoin
    return df2


df = load_data1()
df2 = load_data2()

st.title("🎯 Darts Club des Gones - Capital")
st.markdown("Visualisez vos performances et les statistiques globales des soirées !")

# --- Filtres ---

st.sidebar.title("Navigateur")
choice = st.sidebar.radio("Sélectionnez une section", ["Général", 
                                                      "Par joueur","Par contrat","Soirées","Données" ]) 
#st.sidebar.header("🧮 Filtres")
#joueurs_sel = st.sidebar.multiselect("Sélectionnez les joueurs :", sorted(df["Joueur"].unique()), default=df["Joueur"].unique())
#contrats_sel = st.sidebar.multiselect("Sélectionnez les contrats :", sorted(df["Contrat"].unique()), default=df["Contrat"].unique())

#df_filtered = df[df["Joueur"].isin(joueurs_sel) & df["Contrat"].isin(contrats_sel)]

#df_final = df[df["Contrat"]=="25"]

if choice=="Général":

    # --- Statistiques globales ---
    st.subheader("📈 Statistiques globales")
    taux_reussite = df["Réussi"].mean()
    score_moyen = df2["Score_final"].mean()
    score_vainqueur=df2[df2["Classement_final"]==1]["Score_final"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Taux de réussite global des contrats (nombres inclus)", f"{taux_reussite:.1%}")
    col2.metric("Score final moyen", f"{score_moyen:.0f}")
    col3.metric("Score final moyen pour un vainqueur", f"{score_vainqueur:.0f}")

    # --- Taux de réussite par contrat ---
    st.subheader("🎯 Taux de réussite par contrat")
    taux_par_contrat = (
        df.groupby("Contrat")["Réussi"]
        .mean()
        .reset_index()
        .sort_values("Réussi", ascending=False)
    )

    fig, ax = plt.subplots(figsize=(10, 4))
    bars=ax.bar(taux_par_contrat["Contrat"], taux_par_contrat["Réussi"], color="skyblue")
    ax.set_ylabel("Taux de réussite")
    ax.set_xlabel("Contrat")
    ax.set_ylim(0, 1)
    plt.xticks(rotation=45)
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,  # position horizontale (milieu de la barre)
            height + 0.02,                      # position verticale (au-dessus)
            f"{height:.1%}",                    # texte (format pourcentage)
            ha="center", va="bottom", fontsize=9
        )

    st.pyplot(fig)

elif choice=="Par joueur":

    st.subheader("🏅 Analyse par joueur")
    df25=df.copy()
    df25.loc[df25["Tour"] > 17, "Tour"] = 17
    taux_joueur = (
        df.groupby(["Joueur", "Contrat"])["Réussi"]
        .mean()
        .reset_index()
        .sort_values(["Joueur", "Réussi"], ascending=[True, False])
    )
    score_moyen_apres = (
        df25.groupby(["Tour","Joueur", "Contrat"])["Score_Après"]
        .mean()
        .reset_index()
        .sort_values(["Tour","Joueur", "Score_Après"], ascending=[True,True, False])
    )

    joueur_sel = st.selectbox("Choisir un joueur :", sorted(df["Joueur"].unique()))
    df_filtered = df[df["Joueur"]==joueur_sel]
    #df_final = df_filtered[df_filtered["Contrat"]=="25"]
    df_filtered2 = df2[df2["Joueur"]==joueur_sel]
    data_joueur = taux_joueur[taux_joueur["Joueur"] == joueur_sel]
    taux_reussite2=df_filtered["Réussi"].mean()
    score_moyen2=df_filtered2["Score_final"].mean()

    col1, col2 = st.columns(2)
    col1.metric("Taux de réussite global des contrats (nombres inclus)", f"{taux_reussite2:.1%}")
    col2.metric("Score final moyen", f"{score_moyen2:.0f}")

    st.subheader("Réussite par contrat")
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    bars=ax2.bar(data_joueur["Contrat"], data_joueur["Réussi"], color="orange")
    ax2.set_ylabel("Taux de réussite")
    ax2.set_xlabel("Contrat")
    ax2.set_ylim(0, 1)
    plt.xticks(rotation=45)
    for bar in bars:
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2,  # position horizontale (milieu de la barre)
            height + 0.02,                      # position verticale (au-dessus)
            f"{height:.1%}",                    # texte (format pourcentage)
            ha="center", va="bottom", fontsize=9
        )

    st.pyplot(fig2)

    data_joueur2=score_moyen_apres[score_moyen_apres["Joueur"]==joueur_sel]
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    ax3.plot(data_joueur2["Contrat"], data_joueur2["Score_Après"], marker="o", linewidth=2)
    ax3.set_title("Évolution du score moyen au cours de la partie")
    ax3.set_xlabel("Contrat")
    ax3.set_ylabel("Score moyen")
    plt.xticks(rotation=45)
    st.pyplot(fig3)

    st.subheader("Historique des parties")
    joueur=df2[df2["Joueur"]==joueur_sel]
    st.dataframe(joueur)

elif choice=="Par contrat":
    tab1, tab2= st.tabs(["Contrats spéciaux", "Nombres"])

    with tab1:
        contrat = st.selectbox("Contrats", (df[df["Type_Contrat"]=="Spécial" | df["Type_Contrat"]=="Points"]["Contrat"].unique()))
        df_filtered = df[df["Contrat"]==contrat]
        st.header("Scores les plus communs par contrat")
        col1, col2 = st.columns(2)
        col1met=df_filtered["Gain"].mean()
        col1.metric("Gain moyen", f"{col1met:.1%}")
        
        scores_freq = (
        df_filtered["Gain"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "Score", "Score": "Occurrences"})
        .sort_values("count")
        )
        col2met=scores_freq["Gain"][0]
        col2.metric("Score le plus réalisé", f"{col2met:.0f}")
        fig, ax = plt.subplots(figsize=(10, 5))

        sns.barplot(data=scores_freq.head(20), x="Gain", y="count", ax=ax)
        ax.set_title("Les scores les plus réalisés")
        ax.set_xlabel("Score")
        ax.set_ylabel("Nombre d'occurrences")
        st.pyplot(fig)
        st.subheader("Meilleurs joueurs par contrat blablabla")
        taux_par_joueur = (
        df_filtered.groupby(["Joueur", "Contrat"])["Réussi"]
        .mean()
        .reset_index()
        .sort_values(["Réussi"], ascending=[False])
        )
        st.table(taux_par_joueur.head(5))
    with tab2:
        st.header("Nombre les plus réussis ou marqués ?")
        st.subheader("Meilleurs joueurs par nombre blablabla")

elif choice=="Soirées":
    st.subheader("📅 Résumé des soirées")
    taux_par_soiree=(
        df.groupby("Date")["Réussi"].mean()

    )
    Vainqueurs=df2[(df2["Phase"] =="F") & (df2["Classement_final"]==1)].set_index("Date")["Joueur"]
    df_soiree=(
        df2.groupby("Date")
        .agg(
            Nombre_joueurs=("Joueur","nunique"),
            Score_moyen=("Score_final","mean")
        )
        )
    df_soiree["Taux de réussite"] = taux_par_soiree.values*100
    df_soiree["Vainqueur"]=Vainqueurs
    styled_df = (
    df_soiree.style
    .format({
        "Taux de réussite": "{:.1f}%",
        "Score_moyen": "{:.1f}"
    })
    #.bar(subset=["Taux de réussite"], color="#4CAF50")
    #.bar(subset=["Score_moyen"], color="#4CAF50")
    #.background_gradient(subset=["Score_moyen"], cmap="Blues")
)

    st.table(styled_df)


elif choice=="Données" :
    # --- Données brutes ---
    st.subheader("📋 Données")
    st.dataframe(df)
