import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('data.db')

# Création d'un curseur
c = conn.cursor()

# Ajout de la colonne email
c.execute("ALTER TABLE users ADD COLUMN email TEXT")

# Validation des modifications
conn.commit()

# Fermeture de la connexion
conn.close()
