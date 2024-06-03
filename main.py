#!/usr/bin/python3

from utils import db

def chercher_borne(conn, type_charge):
    """
    Affiche la liste des bornes correspondants au type de recharge de user.

    :param conn: Connexion à la base de données
    :param type_charge: Type de recharge du user
    """
    cur = conn.cursor()
    cur.execute(""" 
        SELECT DISTINCT B.numero_bornebase, L.ville_location, 
                        L.adresse_location, ROUND(B.prixActuel_borne,2) As Prix
        FROM Bornes B JOIN Locations L ON B.numero_bornebase = L.numero_bornebase 
        WHERE B.typeRecharge_typebornebase = ? """,[type_charge])
    rows = cur.fetchall()
    for row in rows:
        print(row)
    
def select_prix_borne(conn):
    """
    Affiche la liste des bornes avec leur prix et adresse.

    :param conn: Connexion à la base de données
    """
    cur = conn.cursor()
    cur.execute("""
                SELECT B.numero_bornebase, L.ville_location, 
                        L.adresse_location, B.prixActuel_borne
                FROM Bornes B JOIN Locations L ON B.numero_bornebase = L.numero_bornebase
                """)

    rows = cur.fetchall()

    for row in rows:
        print(row)

def select_adress_prix_type2(conn):
    """
    Affiche la liste des bornes de type 2.

    :param conn: Connexion à la base de données
    """
    cur = conn.cursor()
    cur.execute("""
                SELECT L.ville_location, L.adresse_location, 
                        B.numero_bornebase, B.prixActuel_borne
                FROM Bornes B, Locations L
                WHERE B.numero_bornebase = L.numero_bornebase AND B.typeRecharge_typebornebase = 'Type 2'
                """)

    rows = cur.fetchall()

    for row in rows:
        print(row)
        
def select_contact_borne(conn, borne):
    """
    Affiche le nom de l'entreprise et son contact
    pour maintenir la borne passée en argument.

    :param conn: Connexion à la base de données
    """
    cur = conn.cursor()
    cur.execute("""
                SELECT E.nom_entreprise, B.courriel_entreprise, 
                        B.numTel_entreprise
                FROM BorneBases E JOIN Entreprises B USING (nom_entreprise)
                WHERE E.numero_bornebase = ? """, [borne])

    rows = cur.fetchall()

    for row in rows:
        print(row)

def select_prix_borne(conn, nomVoiture, modele):
    """
    Affiche la liste des bornes avec leur prix et adresse correspondant 
    à la voiture de l'utilisateur et son type de recharge.
    Si la voiture n'existe pas dans la base de données, 
    demande la couleur et le type de recharge de la voiture.
    Met à jour la base de données avec les nouvelles valeurs.
    
    :param conn: Connexion à la base de données
    """
    cur = conn.cursor()
    
    # vérifier si nomVoiture et modele existent dans la base de données
    cur.execute("""
                SELECT COUNT(*)
                FROM Voitures
                WHERE marque_voiture = ? AND modele_voiture = ? """, (nomVoiture, modele))
    
    if cur.fetchone()[0] > 0:  # si nomVoiture et modele existent dans la base de données
        cur.execute("""
                    SELECT B.numero_bornebase, L.ville_location, 
                            L.adresse_location, B.prixActuel_borne
                    FROM RechargeBases R JOIN Bornes B USING (numero_bornebase) 
                        JOIN Locations L USING (numero_bornebase)
                    WHERE R.marque_voiture = ? AND R.modele_voiture = ? """, (nomVoiture, modele))
    else:                       # si nomVoiture et modele n'existent pas dans la base de données
        couleur = input("Votre voiture n'existe pas dans notre BD.\nVeuillez taper la couleur de votre voiture: ")
        typeRecharge = str(input("Veuillez taper le type de recharge: "))
        print(typeRecharge)
        cur.execute("""
                    SELECT B.numero_bornebase, L.ville_location, 
                            L.adresse_location, B.prixActuel_borne
                    FROM Bornes B JOIN Locations L ON B.numero_bornebase = L.numero_bornebase
                    WHERE B.typeRecharge_typebornebase = ? """, (typeRecharge,))
        
        rows = cur.fetchall()
        for row in rows:
            print(row) 

        # puis insérer les nouvelles valeurs dans la table Voitures et RechargeBases
        cur.execute("""
                    INSERT INTO Voitures (marque_voiture, modele_voiture, couleur_voiture)
                    VALUES (?, ?, ?) """, (nomVoiture, modele, couleur))
        cur.execute("""
                    SELECT numero_bornebase
                    FROM Bornes
                    WHERE typeRecharge_typebornebase = ? """, (typeRecharge,))
        rows = cur.fetchall()
        for row in rows:
            cur.execute("""
                        INSERT INTO RechargeBases (marque_voiture, modele_voiture, numero_bornebase)
                        VALUES (?, ?, ?) """, (nomVoiture, modele, row[0]))
        
        conn.commit()
    rows = cur.fetchall()

    for row in rows:
        print(row)      
        
def update_location(conn, numero_bornebase, adresse_location,ville):
    """
    Met à jour l'adresse de la location de la borne.

    :param conn: Connexion à la base de données
    :param ville: Nouvelle ville de la location
    :param numero_bornebase: Numéro de la borne
    :param adresse_location: Nouvelle adresse de la location
    """
    cur = conn.cursor()
    cur.execute("""
                UPDATE Locations
                SET adresse_location = ? , ville_location = ?
                WHERE numero_bornebase = ? """, (adresse_location, ville, numero_bornebase))
    conn.commit()   
       
def supprimer_borne(conn, numero_bornebase):
    """
    Supprime la borne passée en argument à cause de maintenance.

    :param conn: Connexion à la base de données
    :param numero_bornebase: Numéro de la borne
    """
    cur = conn.cursor()
    cur.execute("""
                DELETE FROM RechargeBases
                WHERE numero_bornebase = ? """, [numero_bornebase])
    cur.execute(""" 
                DELETE FROM Locations
                WHERE numero_bornebase = ? """, [numero_bornebase])
    cur.execute("""
                DELETE FROM BorneBases
                WHERE numero_bornebase = ? """, [numero_bornebase])
    conn.commit()     

def main():
    # Nom de la BD à créer
    db_file = "database/database.db"

    # Créer une connexion a la BD
    conn = db.creer_connexion(db_file)
   
    # créer une fonction power pour calculer la puissance (table view Bornes)
    # car il y a pas de fonction power dans SQLite
    conn.create_function("power", 2, lambda x, y: x**y)
    
    # Remplir la BD
    print("1. On crée la bd et on l'initialise avec des premières valeurs.")
    db.mise_a_jour_bd(conn, "database/Bornes_creation.sql")
    db.mise_a_jour_bd(conn, "database/Bornes_inserts_ok.sql")
    #db.mise_a_jour_bd(conn, "database/Bornes_inserts_nok.sql")
   
    # Lire la BD
    # Interaction avec la BD
    while True:
        print("Menu principal:")
        print("1. Liste des bornes avec leur prix et adresse.")
        print("2. Liste des bornes de type 2.")
        print("3. Bornes correspondants au type de recharge de user.")
        print("4. Nom de l'entreprise, son adresse mail et numéro de télé pour maintenir la borne passée en argument.")
        print("5. Liste des bornes avec leur prix et adresse correspondant à la voiture de l'utilisateur et son type de recharge.")
        print("6. Mettre à jour l'adresse de la location de la borne.")
        print("7. Supprimer la borne passée en argument à cause de maintenance.")
        print("8. Quitter.")
        choix = input("Entrez votre choix: ")
        if choix == "1":
            select_prix_borne(conn)
        elif choix == "2":  
            select_adress_prix_type2(conn)
        elif choix == "3":
            type_charge = input("Entrez le type de recharge: ")
            chercher_borne(conn, type_charge)
        elif choix == "4":
            borne = input("Entrez le numéro de la borne: ")
            select_contact_borne(conn, borne)
        elif choix == "5":
            nomVoiture = input("Entrez le nom de la voiture: ")
            modele = input("Entrez le modèle de la voiture: ")
            select_prix_borne(conn, nomVoiture, modele)    
        elif choix == "6":
            borne = input("Entrez le numéro de la borne: ")
            ville = input("Entrez la nouvelle ville: ")
            adresse = input("Entrez la nouvelle adresse: ")
            update_location(conn, borne, adresse, ville)
        elif choix == "7":
            borne = input("Entrez le numéro de la borne: ")
            supprimer_borne(conn, borne)
        elif choix == "8":
            break
        else:
            print("Choix invalide.")
        print("\n")
    
    #conn.set_trace_callback(print)

if __name__ == "__main__":
    main()
