# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import plotly.express as px

# --- Configuration de la page ---
st.set_page_config(page_title="Le Capital", layout="wide", page_icon="dcg.jpg")

# --- Chargement des données ---
@st.cache_data
def load_data1():
    df = pd.read_csv("data/capital.csv", decimal=",")
    # Conversion de "Réussi" en numérique si besoin
    return df

def load_data2():
    df2 = pd.read_csv("data/parties.csv")
    # Conversion de "Réussi" en numérique si besoin
    return df2


df = load_data1()
df2 = load_data2()

st.title("🎯 Darts Club des Gones - Capital")
st.markdown("Visualisez vos performances et les statistiques globales des soirées ! (voir menu à gauche)")

#df2["Points"]=5-df2["Classement_final"]
df2["Session"]=df2["Date"].apply(lambda x: "Rentrée 2025" if x < "2025-11-01" else "Automne 2025" if x < "2025-12-18" else "Hiver 2026" if x < "2026-02-26" else "Mars 2026")
finales = pd.DataFrame({
    "Session": ["Mars 2026","Hiver 2026", "Rentrée 2025", "Automne 2025"],
    "Finale": ["2026-04-29","2026-02-25","2025-10-29","2025-12-17"]
})
#finales["Finale"] = pd.to_datetime(finales["Finale"])
#finales=finales.rename(columns={"Date":"Finale"})
df2=df2.merge(finales, on="Session", how="left")
df2["Points"]=df2.apply(lambda x: (5 - x["Classement_final"])*2 if x["Date"]==x["Finale"] else 5-x["Classement_final"],axis=1)

nb_parties=df2["Joueur"].value_counts()
joueurs_gardes=nb_parties[nb_parties >= 15].index
df_dix=df[df["Joueur"].isin(joueurs_gardes)]
df2_dix=df2[df2["Joueur"].isin(joueurs_gardes)]


if "session_radio_tab2" not in st.session_state:
    st.session_state["session_radio_tab2"] = "Automne 2025"
# --- Filtres ---

st.sidebar.title("Navigateur")
choice = st.sidebar.radio("Sélectionnez une section", ["Général", 
                                                      "Par joueur","Par contrat","Soirées","Tableau récap","Divers","Lancer une partie" ]) 
#st.sidebar.header("🧮 Filtres")
#joueurs_sel = st.sidebar.multiselect("Sélectionnez les joueurs :", sorted(df["Joueur"].unique()), default=df["Joueur"].unique())
#contrats_sel = st.sidebar.multiselect("Sélectionnez les contrats :", sorted(df["Contrat"].unique()), default=df["Contrat"].unique())

#df_filtered = df[df["Joueur"].isin(joueurs_sel) & df["Contrat"].isin(contrats_sel)]

#df_final = df[df["Contrat"]=="25"]

if choice=="Général":

    tab1,tab2=st.tabs(["Statistiques globales", "Classement"])

    with tab1 :
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

        st.subheader("Réparition des scores en fonction du classement final")

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=df2, x="Classement_final", y="Score_final", ax=ax)
        ax.axhline(score_moyen, color="red", linestyle="--", linewidth=2, label=f"Moyenne ({score_moyen:.1f})")
        ax.set_xlabel("Classement final", fontsize=12)
        ax.set_ylabel("Score final", fontsize=12)
        ax.legend()
        st.pyplot(fig)

        
        st.subheader("Réparition des scores en fonction de la cible")

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=df2, x="Cible", y="Score_final", ax=ax)
        ax.axhline(score_moyen, color="red", linestyle="--", linewidth=2, label=f"Moyenne ({score_moyen:.1f})")
        ax.set_xlabel("Cible", fontsize=12)
        ax.set_ylabel("Score final", fontsize=12)
        ax.legend()
        st.pyplot(fig)

        st.subheader("Réparition des scores en fonction de la partie")

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=df2, x="Phase", y="Score_final", ax=ax)
        ax.axhline(score_moyen, color="red", linestyle="--", linewidth=2, label=f"Moyenne ({score_moyen:.1f})")
        ax.set_xlabel("Partie", fontsize=12)
        ax.set_ylabel("Score final", fontsize=12)
        ax.legend()
        st.pyplot(fig)

        st.subheader("Réparition des scores de l'ordre de passage")

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=df2, x="Ordre", y="Score_final", ax=ax)
        ax.axhline(score_moyen, color="red", linestyle="--", linewidth=2, label=f"Moyenne ({score_moyen:.1f})")
        ax.set_xlabel("Ordre", fontsize=12)
        ax.set_ylabel("Score final", fontsize=12)
        ax.legend()
        st.pyplot(fig)


    with tab2 :
        session = st.selectbox("Session", ["Mars 2026", "Hiver 2026", "Automne 2025", "Rentrée 2025"])
        df2clas=df2[df2["Session"] == session]
        Classement=(
            df2clas.groupby(["Joueur"])["Points"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        Classement.index=range(1, len(Classement)+1)
        st.table(Classement)

elif choice=="Par joueur":
    tab1, tab2= st.tabs(["Analyse par joueur", "Meilleurs joueurs"])
    with tab1 :
        st.subheader("Analyse par joueur")
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
        score_moyenpartie=df_filtered["Score_Après"].mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("Taux de réussite global des contrats (nombres inclus)", f"{taux_reussite2:.1%}")
        col2.metric("Score final moyen", f"{score_moyen2:.0f}")
        col3.metric("Score moyen au cours de la partie", f"{score_moyenpartie:.0f}")

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

    with tab2 :
            df_reussi = (
            df_dix.groupby(["Joueur"])["Réussi"]
            .mean()
            .reset_index()
            .sort_values(["Réussi"], ascending=[False])
             )
            df_moy = (
            df2_dix.groupby(["Joueur"])["Score_final"]
            .mean()
            .reset_index()
            .sort_values(["Score_final"], ascending=[False])
            )
            df_partie = (
            df_dix.groupby(["Joueur"])["Score_Après"]
            .mean()
            .reset_index()
            .sort_values(["Score_Après"], ascending=[False])
            .rename(columns={"Score_Après": "Score moyen"})
            )
            st.subheader("Top 10 des moyennes de score final")
            st.table(df_moy.head(10))
            st.subheader("Top 10 en réussite des contrats (nombres compris)")
            st.table(df_reussi.head(10))
            st.subheader("Top 10 en score moyen au cours de la partie")
            st.table(df_partie.head(10))
            

elif choice=="Par contrat":
    tab1, tab2= st.tabs(["Contrats spéciaux", "Nombres"])

    with tab1:
        contrat = st.selectbox("Contrat",df[df["Type_Contrat"].isin(["Spécial", "Points"])]["Contrat"].unique())
        df_filtered = df_dix[df_dix["Contrat"]==contrat]
        df_filtered22 = df[df["Contrat"]==contrat]
        st.header("Scores les plus communs par contrat")
        col1, col2, col3 = st.columns(3)
        col1met=df_filtered22[df_filtered22["Gain"]>0]["Gain"].mean()
        col1.metric("Gain moyen", f"{col1met:.1f}")
        df_filteredgain=df_filtered22[df_filtered22["Gain"]>0]
        scores_freq = (
            df_filteredgain["Gain"]
            .value_counts()
            .reset_index()
            .rename(columns={"Gain": "Gain", "count": "Occurrences"})
            .sort_values("Occurrences", ascending=False)
        )
        col2met = scores_freq["Gain"].iloc[0]
        col2.metric("Score le plus réalisé", f"{col2met:.0f}")
        col3met = scores_freq["Gain"].max()
        col3.metric("Plus gros score", f"{col3met:.0f}")
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=scores_freq.head(20), x="Gain", y="Occurrences", ax=ax, order=scores_freq["Gain"].head(20))
        for container in ax.containers:
            ax.bar_label(container, fmt="%d", label_type="edge", padding=3)
        ax.set_title("Les scores les plus réalisés", fontsize=14)
        ax.set_xlabel("Score", fontsize=12)
        ax.set_ylabel("Nombre d'occurrences", fontsize=12)
        st.pyplot(fig)

        if contrat=="Capital":
            st.subheader("Meilleurs moyennes au capital")
            taux_par_joueur = (
            df_filtered.groupby(["Joueur"])["Gain"]
            .mean()
            .reset_index()
            .sort_values(["Gain"], ascending=[False])
            )
            st.table(taux_par_joueur.head(20))

        else :
            st.subheader("Meilleurs joueurs pour ce contrat")
            taux_par_joueur = (
            df_filtered.groupby(["Joueur"])["Réussi"]
            .mean()
            .reset_index()
            .sort_values(["Réussi"], ascending=[False])
            )
            st.table(taux_par_joueur.head(10))
    with tab2:
        dftab2=df_dix[df_dix["Type_Contrat"]=="Nombre"]
        dftab22=df[df["Type_Contrat"]=="Nombre"]
        dftab2.loc[dftab2["Nb"].astype(float) < 0, "Nb"] = 0
        dftab22.loc[dftab22["Nb"].astype(float) < 0, "Nb"] = 0
        col1, col2 = st.columns(2)
        col1met=dftab22["Réussi"].mean()
        col1.metric("Taux de réussite global aux nombres", f"{col1met:.1%}")
        col2met=dftab22["Nb"].mean()
        col2.metric("Score moyen", f"{col2met:.2f}")
        st.subheader("Nombre les plus touchés")
        nb_nombres = (
            dftab22.groupby(["Contrat"])["Nb"]
            .mean()
            .reset_index()
            .rename(columns={"Contrat": "Nombre", "Nb": "mean"})
            .sort_values("mean", ascending=False)
        )
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=nb_nombres, x="Nombre", y="mean", ax=ax, order=[20,19,18,17,16,15,14,13])
        for container in ax.containers:
            ax.bar_label(container, fmt="%.2f", label_type="edge", padding=3)
        ax.set_xlabel("Nombres", fontsize=12)
        ax.set_ylabel("Moyenne", fontsize=12)
        st.pyplot(fig)
        st.subheader("Meilleurs joueurs sur les nombres (% validation)")
        taux_par_joueur = (
        dftab22.groupby(["Joueur"])["Réussi"]
        .mean()
        .reset_index()
        .sort_values(["Réussi"], ascending=[False])
        )
        taux_par_joueur22 = (
        dftab2.groupby(["Joueur"])["Réussi"]
        .mean()
        .reset_index()
        .sort_values(["Réussi"], ascending=[False])
        )
        st.table(taux_par_joueur22.head(10))
        st.subheader("Meilleurs joueurs sur les nombres (moyenne)")
        taux_par_joueur2 = (
        dftab2.groupby(["Joueur"])["Nb"]
        .mean()
        .reset_index()
        .sort_values(["Nb"], ascending=[False])
        )
        st.table(taux_par_joueur2.head(10))

        joueur_sel = st.selectbox("Stats par joueur :", sorted(df["Joueur"].unique()))
        df_filt=dftab22[dftab22["Joueur"]==joueur_sel]
        nb_nombres_par_joueur = (
            df_filt.groupby(["Contrat"])["Nb"]
            .mean()
            .reset_index()
            .rename(columns={"Contrat": "Nombre", "Nb": "mean"})
            .sort_values("mean", ascending=False)
        )
        score_moyen=nb_nombres_par_joueur["mean"].mean()
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=nb_nombres_par_joueur, x="Nombre", y="mean", ax=ax, order=[20,19,18,17,16,15,14,13])
        ax.axhline(score_moyen, color="red", linestyle="--", linewidth=2, label=f"Moyenne ({score_moyen:.1f})")
        for container in ax.containers:
            ax.bar_label(container, fmt="%.2f", label_type="edge", padding=3)
        ax.set_xlabel("Nombres", fontsize=12)
        ax.set_ylabel("Moyenne", fontsize=12)
        st.pyplot(fig)

        taux_par_joueur2 = (
                    dftab2.groupby(["Joueur", "Contrat"])["Nb"]
                    .mean()
                    .reset_index()
                    .sort_values(["Nb"], ascending=[False])
                    )

        for i in range(20,12,-1):
                    st.subheader(f"Meilleurs joueurs au {i}")
                    dfnb=taux_par_joueur2[taux_par_joueur2["Contrat"]==str(i)]
                    st.table(dfnb.head(10))


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

    st.subheader("Evolution des performances")
    fig, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(df_soiree["Score_moyen"], marker="o", linewidth=2, color="m")
    ax1.set_ylabel("Score moyen", color="m")
    ax1.set_xlabel("Date")

    ax2=ax1.twinx()
    ax2.plot(df_soiree["Taux de réussite"], marker="x", linewidth=2, color="y")
    ax2.set_ylabel("Taux de réussite", color="y")
    fig.tight_layout()
    st.pyplot(fig)

elif choice=="Tableau récap":
    df["Division"] = (df["Réussi"] == 0).astype(int)
    df_divisions = (
        df.groupby(["Partie_ID", "Joueur"])["Division"]
        .sum()
        .reset_index()
        .rename(columns={"Division": "Nb_Divisions"})
        .sort_values("Nb_Divisions", ascending=True)
    )
    df_divpartie=(
        df_divisions.groupby("Partie_ID")["Nb_Divisions"]
        .sum()

    )
    st.header("🏆 Tableau récapitualitif")
    st.subheader("Statistiques depuis le 8 Octobre 2025")
    
    # On identifie les finales gagnées (Phase 'F' et Classement 1)
    for i in range(1, 6):
        df2[f"{i}e"] = (df2["Classement_final"] == i).astype(int)
    df2["Soleil"]=((df2["Phase"]=="F") & (df2["Classement_final"]==1)).astype(int)
    df2["Est_Finale"]=(df2["Phase"]=="F").astype(int)
    
    stats_parties=df2.groupby("Joueur").agg(
        Parties=("Partie_ID", "nunique"),
        Finales=("Est_Finale", "sum"),
        Soleils=("Soleil", "sum"),
        Victoires=("1e", "sum"),
        Deuxième=("2e", "sum"),
        Troisième=("3e", "sum"),
        Quatrième=("4e", "sum"),
        Cinquième=("5e", "sum"),
        Score_Moyen_Final=("Score_final", "mean")
    )
    
    # 2. Calcul des stats basées sur les contrats (df)
    stats_contrats = df.groupby("Joueur").agg(
        Réussite=("Réussi", "mean"),
        Score_Moyen_Tour=("Score_Après", "mean")
    )
    
    # 3. Fusion des deux tableaux
    recap = pd.concat([stats_parties, stats_contrats], axis=1).reset_index()
    
    # 4. Nettoyage et formatage
    recap["Réussite"] = (recap["Réussite"] * 100).round(1)
    recap["Score_Moyen_Final"] = recap["Score_Moyen_Final"].round(1)
    recap["Score_Moyen_Tour"] = recap["Score_Moyen_Tour"].round(1)
    
    # On renomme pour le style
    recap = recap.rename(columns={
        "Soleils": "☀️ Soleils",
        "Finales": "📅 Nb Finales",
        "Victoires": "1er",
        "Deuxième": "2e",
        "Troisième": "3e",
        "Quatrième": "4e",
        "Cinquième": "5e",
        "Réussite": "% Réussite"
    })
    
    # 5. Affichage interactif
    st.dataframe(
        recap.sort_values("☀️ Soleils", ascending=False), 
        use_container_width=True,
        hide_index=True,
        column_config={
            "% Réussite": st.column_config.NumberColumn(format="%.1f%%"),
            "☀️ Soleils": st.column_config.NumberColumn(help="Nombre de victoires en grande finale"),
        }
    )
        


    #st.dataframe(df_divpartie)
    
    #st.table(df_divisions.head(10))
elif choice=="Divers":

    tab1, tab2,tab3,tab4= st.tabs(["Classement Elo", "Face à Face","Magnum","Gibolins"])

    with tab1 :
        
        def calcul_elo(df2,elo_base=1500):
        
            joueurs=df2['Joueur'].unique()
            elo_dict={joueur:elo_base for joueur in joueurs}
            nb_parties={joueur: 0 for joueur in df2['Joueur'].unique()}
            historique = []
            for partie_id in df2['Partie_ID'].unique():
                partie=df2[df2['Partie_ID'] == partie_id]
                joueurs_partie=partie['Joueur'].tolist()
                classements_partie=partie['Classement_final'].tolist()
                changements={joueurs: 0 for joueurs in joueurs_partie}
                nb_joueurs=len(joueurs_partie)
                k_dict={}
                for nb in joueurs_partie:
                    n=nb_parties[nb]
                    if n<15:
                        k_dict[nb]=50
                    elif n<40:
                        k_dict[nb]=30
                    else :
                        k_dict[nb]=20


                for i in range(nb_joueurs):
                    for j in range(i+1,nb_joueurs):
                        j1=joueurs_partie[i]
                        j2=joueurs_partie[j]
                        elo_j1=elo_dict[j1]
                        elo_j2=elo_dict[j2]

                        proba_j1=(1/(1+10 ** ((elo_j2-elo_j1)/400)))
                        proba_j2=1-proba_j1
                        if classements_partie[i]<classements_partie[j]:
                            s_j1=1
                            s_j2=0 
                        elif classements_partie[i]>classements_partie[j]:
                            s_j1=0
                            s_j2=1
                        else:                
                            s_j1,s_j2=0.5,0.5  

                        gain_j1=((k_dict[j1])/(nb_joueurs-1))*(s_j1-proba_j1)
                        gain_j2=((k_dict[j2])/(nb_joueurs-1))*(s_j2-proba_j2)

                        changements[j1]=changements[j1]+gain_j1
                        changements[j2]=changements[j2]+gain_j2
                

                for j in joueurs_partie:
                    nb_parties[j]=nb_parties[j]+1
                    elo_dict[j]=elo_dict[j]+changements[j]
                    historique.append({'Partie_ID': partie_id, 'Joueur': j, 'Elo': elo_dict[j]})

            return elo_dict, pd.DataFrame(historique),nb_parties
        dicoo,historique,nb_parties=calcul_elo(df2)

        

        df_elo=pd.DataFrame(list(dicoo.items()), columns=['Joueur', 'Elo'])
        df_matchs=pd.DataFrame(list(nb_parties.items()), columns=['Joueur', 'Matchs'])
        df_ranking=pd.merge(df_elo, df_matchs, on='Joueur')
        df_affiche=df_ranking[df_ranking["Matchs"]>15].sort_values('Elo', ascending=False).copy()
        df_affiche.index=range(1, len(df_affiche)+1)

        derniere_date=df2["Date"].max()
        historique_date=pd.merge(historique, df2[["Partie_ID","Date","Phase"]], on='Partie_ID')
        df_last=historique_date[historique_date['Date']==derniere_date]
        df_avant=historique_date[historique_date['Date']<derniere_date]
    
        evolution={}
        for joueur in df_last['Joueur'].unique():
            histo_joueur_avant=df_avant[df_avant['Joueur'] == joueur]
            elo_depart=histo_joueur_avant.iloc[-1]['Elo'] if not histo_joueur_avant.empty else 1500
            elo_fin=df_last[df_last['Joueur'] == joueur].iloc[-1]['Elo']
            evolution[joueur]=round(elo_fin-elo_depart, 0).astype(int)

        df_affiche['Dernière Soirée']=df_affiche['Joueur'].map(evolution).fillna(0)

        def generer_tendance(delta):
            if delta > 0: return f"▲ +{delta}"
            if delta < 0: return f"▼ {delta}"
            return "—"
        
        df_affiche["Dernière Soirée"]=round(df_affiche["Dernière Soirée"],0).astype(int)
        df_affiche['Evolution']=df_affiche['Dernière Soirée'].apply(generer_tendance)
        df_affiche['Elo']=round(df_affiche['Elo'],0).astype(int)

        def style_tendance(val):
            if '▲' in str(val): color = '#28a745'
            elif '▼' in str(val): color = '#dc3545'
            else: color = '#6c757d' # Gris
            return f'color: {color}; font-weight: bold'
        
        top_player=df_affiche.sort_values('Elo', ascending=False).iloc[0]
        st.subheader("Classement Elo du Capital")
        st.subheader(f"👑 Leader : {top_player['Joueur']}")
        
        st.divider()

        st.subheader("🏆 Classement Actuel")
        st.info("Elo de départ : 1500 - Joueurs avec 15+ parties affichés")
        st.dataframe(df_affiche[['Joueur', 'Elo', 'Evolution']].style.applymap(style_tendance, subset=['Evolution']),use_container_width=True,hide_index=True)
        
        st.divider()

        st.subheader("Evolution de l'Elo du top 5 actuel")


        historique_date['Date'] = pd.to_datetime(historique_date['Date'])
        ordre_phases = ['P1', 'P2', 'P3', 'DF', 'F']
        historique_date['Phase'] = pd.Categorical(historique_date['Phase'], categories=ordre_phases, ordered=True)
        historique_date = historique_date.sort_values(['Date', 'Phase'])
        historique_date['Session']=historique_date['Date'].dt.strftime('%Y-%m-%d') + " (" + historique_date['Phase'].astype(str) + ")"
        top_joueurs=df_affiche.head(5)['Joueur'].tolist()
        df_top=historique_date[historique_date['Joueur'].isin(top_joueurs)].copy()
        df_top=df_top.sort_values(['Date', 'Phase'])
        df_pivot=df_top.pivot_table(index='Session', columns='Joueur', values='Elo', sort=False)
        df_pivot=df_pivot.ffill()
        fig=plt.figure(figsize=(20, 10))
        for joueur in top_joueurs:
            if joueur in df_pivot.columns:
                plt.plot(df_pivot.index, df_pivot[joueur], label=joueur, linewidth=2, marker='o', markersize=4)

        #plt.title(f"Évolution d'Elo du top 5 actuel", fontsize=16, fontweight='bold')
        plt.xticks(rotation=45, ha='right', fontsize=8)
        plt.ylabel("Points Elo", fontsize=20)
        plt.tick_params(axis='both', which='major', labelsize=18)
        plt.legend(title="Top Joueurs", loc='center left', bbox_to_anchor=(1, 0.5),fontsize=20,title_fontsize=20)
        plt.grid(True, linestyle='--', alpha=0.4)
        ax = plt.gca() # Récupère l'axe actuel
        # On      force l'affichage de 10 graduations maximum sur l'axe X
        ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=20))
        
        plt.tight_layout()
        #plt.savefig("evolution_par_phase.png")
        st.pyplot(fig)

        st.divider()

        st.header("Comparer la progression de différents joueurs")
    

        joueurs=df2['Joueur'].unique().tolist()
        selection=st.multiselect("Choisir les joueurs à comparer :",joueurs)
        
        if selection:
    
            historique_date['Date'] = pd.to_datetime(historique_date['Date'])
            ordre_phases = ['P1', 'P2', 'P3', 'DF', 'F']
            historique_date['Phase'] = pd.Categorical(historique_date['Phase'], categories=ordre_phases, ordered=True)
            historique_date = historique_date.sort_values(['Date', 'Phase'])
            historique_date['Session']=historique_date['Date'].dt.strftime('%Y-%m-%d') + " (" + historique_date['Phase'].astype(str) + ")"
            df_top=historique_date[historique_date['Joueur'].isin(selection)].copy()
            df_top=df_top.sort_values(['Date', 'Phase'])
            df_pivot=df_top.pivot_table(index='Session', columns='Joueur', values='Elo', sort=False)
            df_pivot=df_pivot.ffill()
            fig2=plt.figure(figsize=(20, 10))
            for joueur in selection:
                if joueur in df_pivot.columns:
                    plt.plot(df_pivot.index, df_pivot[joueur], label=joueur, linewidth=2, marker='o', markersize=4)

            #plt.title(f"Évolution d'Elo du top 5 actuel", fontsize=16, fontweight='bold')
            plt.xticks(rotation=45, ha='right', fontsize=8)
            plt.ylabel("Points Elo", fontsize=20)
            plt.tick_params(axis='both', which='major', labelsize=18)
            plt.legend(title="Top Joueurs", loc='center left', bbox_to_anchor=(1, 0.5),fontsize=20,title_fontsize=20)
            plt.grid(True, linestyle='--', alpha=0.4)
            ax2 = plt.gca() # Récupère l'axe actuel
            # On      force l'affichage de 10 graduations maximum sur l'axe X
            ax2.xaxis.set_major_locator(ticker.MaxNLocator(nbins=20))
            
            plt.tight_layout()
            #plt.savefig("evolution_par_phase.png")
            st.pyplot(fig2)

    with tab3 :

        ordre_contrats=df["Contrat"].unique().tolist()
        df["Division"] = (df["Réussi"] == 0).astype(int)
        df_divisions = (
            df.groupby(["Partie_ID", "Joueur"])["Division"]
            .sum()
            .reset_index()
            .rename(columns={"Division": "Nb_Divisions"})
            .sort_values("Nb_Divisions", ascending=True)
        )
        df_divpartie=(
            df_divisions.groupby("Partie_ID")["Nb_Divisions"]
            .sum()

        )
        magnum=list(df_divisions[df_divisions["Nb_Divisions"]==0]["Joueur"])
        if magnum:
            st.header(f"🍾 **Ils ont réussi le Magnum :** {', '.join(magnum)}")
        else:
            st.header("Aucun Magnum pour le moment. Gardez la foi ! 🎯")
        
        df_div=df[(df["Réussi"] == 0) & (~df["Joueur"].isin(magnum))]
        
        test1 = (df_div.sort_values("Tour")
                    .groupby(["Partie_ID", "Joueur"])
                    .first() 
                    .reset_index())
        
        test1['Contrat']=pd.Categorical(test1['Contrat'], categories=ordre_contrats, ordered=True)

        if not test1.empty:
            st.subheader("📊 Répartition des premières divisions")
            stats_graph=test1['Contrat'].value_counts().reset_index()
            stats_graph.columns=['Contrat', 'Premières divisions']
            stats_graph['Contrat']=stats_graph['Contrat'].astype(str)
            stats_graph['Contrat']=pd.Categorical(stats_graph['Contrat'], categories=ordre_contrats, ordered=True)
            stats_graph=stats_graph.sort_values('Contrat')

            fig = px.bar(
                stats_graph, 
                x='Contrat', 
                y='Premières divisions',
                labels={'Nombre de chutes': 'Nombre de 1ères divisions'},
            )
            
            fig.update_layout(
            xaxis_type='category', 
            xaxis_title="Nom du Contrat",
            yaxis_title="Nombre de 1ères divisions",
            xaxis_tickmode='linear' 
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("Pas assez de données pour le graphique.")
        
    

        records_personnels=test1.sort_values('Contrat', ascending=False).drop_duplicates('Joueur')

        for contrat in reversed(ordre_contrats):
            joueurs_record=records_personnels[records_personnels['Contrat']==contrat]['Joueur'].tolist()
            nb_arrets_total=len(test1[test1['Contrat']==contrat])
            
            if nb_arrets_total>0:
                st.subheader(f"📝 Contrat **{contrat}** — {nb_arrets_total} premières divisions au total")
                if joueurs_record:
                    st.write("🏅 **Record personnel pour :**")
                    for j in joueurs_record:
                            st.write(f"- {j}")
                else:
                    st.write("*(Personne n'a ce contrat comme record personnel)*")
    with tab2:
        df2=df2[["Partie_ID","Joueur","Classement_final","Phase"]]

        df_hth=pd.merge(df2,df2,on="Partie_ID")
        df_hth=df_hth[df_hth["Joueur_x"]!=df_hth["Joueur_y"]]
        df_hth["Battu"]=df_hth["Classement_final_x"]<df_hth["Classement_final_y"]
        mat=df_hth.groupby(["Joueur_x",'Joueur_y'])["Battu"].agg(["sum","count"]).reset_index()
        mat.columns=['Joueur_1','Joueur_2','Victoires_J1','Total_Matchs']
        mat['Victoires_J2']=mat['Total_Matchs']-mat['Victoires_J1']
        mat=mat[mat['Joueur_1']<mat['Joueur_2']]
        mat=mat[['Joueur_1','Joueur_2','Victoires_J1','Victoires_J2','Total_Matchs']].sort_values(by='Total_Matchs', ascending=False)
        st.subheader("Les confrontations les plus fréquentes")
        st.dataframe(mat.head(10))
        st.subheader("Chercher les face à face pour un joueur particulier :")
        joujou=st.selectbox("Joueur", sorted(df2["Joueur"].unique()))
        if joujou:
            hthj=df_hth.groupby(["Joueur_x",'Joueur_y'])["Battu"].agg(["sum","count"]).reset_index()
            hthj.columns=['Joueur','Adversaire','Victoires','Matchs']
            hthj['Défaites']=hthj['Matchs']-hthj['Victoires']
            hthj=hthj[['Joueur','Adversaire','Victoires','Défaites','Matchs']].sort_values(by='Matchs', ascending=False)
            hthj=hthj[hthj["Joueur"]==joujou]
            st.dataframe(hthj)
    with tab4:
        liste_gibolins=[i*111 for i in range(1,9)]
        df["Gibolins"]=df["Score_Après"].isin(liste_gibolins)
        df_gibolins=(
            df.groupby(["Joueur"])["Gibolins"]
            .sum()
            .reset_index()
            .sort_values("Gibolins", ascending=False)
        )
        df_gibolins.index=range(1, len(df_gibolins)+1)
        st.subheader("Joueurs ayant réalisé des gibolins (tous compris)")
        st.dataframe(df_gibolins[df_gibolins["Gibolins"]>0])


elif choice=="Lancer une partie" :
    
    # Configuration de la page
    st.title("🎯 Saisie de Partie en Direct")
    
    # 1. Liste des contrats dans l'ordre (selon tes règles)
    CONTRATS = [
        "Capital", "20", "Suite", "19", "Côté", "18", "Couleurs", 
        "17", "57", "16", "Peluche", "15", "Triple", "14", "Double", "13", "Bulle"
    ]
    
    # 2. Initialisation de la partie (Session State)
    if "game_active" not in st.session_state:
        st.session_state.game_active = False
        st.session_state.current_tour = 0
        st.session_state.scores = {}
    
    # --- Formulaire de début de partie ---
    if not st.session_state.game_active:
        st.subheader("Nouvelle Partie")
        joueurs_input = st.text_input("Noms des joueurs (séparés par une virgule)", "Ely, Manon, Aurel")
        if st.button("Lancer la partie 🚀"):
            liste_joueurs = [j.strip() for j in joueurs_input.split(",")]
            st.session_state.scores = {j: 0 for j in liste_joueurs}
            st.session_state.game_active = True
            st.session_state.current_tour = 0
            st.rerun()
    
    # --- Interface de jeu ---
    else:
        tour_idx = st.session_state.current_tour
        if tour_idx < len(CONTRATS):
            contrat_actuel = CONTRATS[tour_idx]
            st.header(#f"Tour {tour_idx + 1} : {contrat_actuel}")
                      f"Contrat actuel : **{contrat_actuel}**")
            
            # Affichage des scores actuels
            cols_score = st.columns(len(st.session_state.scores))
            for i, (joueur, score) in enumerate(st.session_state.scores.items()):
                cols_score[i].metric(joueur, f"{score} pts")
    
            st.divider()
    
            # Zone de saisie pour chaque joueur
            st.subheader("Saisie des résultats")
            form_scores = {}
            cols_input = st.columns(len(st.session_state.scores))
            
            for i, joueur in enumerate(st.session_state.scores.keys()):
                with cols_input[i]:
                    st.write(f"**{joueur}**")
                    points = st.number_input("Points marqués", min_value=0, step=1, key=f"pts_{joueur}_{tour_idx}")
                    form_scores[joueur] = {"points": points}
    
            if st.button("Valider le tour ✅"):
                for joueur, result in form_scores.items():
                    old_score = st.session_state.scores[joueur]
                    
                    if result["points"]>0:
                        # Si réussi, on ajoute les points traditionnels
                        st.session_state.scores[joueur] += result["points"]
                    else:
                        # Si raté, on divise par 2 (arrondi en dessous)
                        st.session_state.scores[joueur] = old_score // 2
                
                st.session_state.current_tour += 1
                st.rerun()
    
        else:
            st.balloons()
            st.success("Partie terminée !")
            st.table(pd.DataFrame(st.session_state.scores.items(), columns=["Joueur", "Score Final"]).sort_values("Score Final", ascending=False))
            
            if st.button("Recommencer une partie"):
                st.session_state.game_active = False
                st.rerun()
    
        if st.button("Annuler la partie ❌"):
            st.session_state.game_active = False
            st.rerun()
    
    #st.subheader("📋 Données")
    #st.dataframe(df2)
