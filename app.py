# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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

    tab1, tab2= st.tabs(["Magnum", "Face à Face"])

    with tab1 :

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
