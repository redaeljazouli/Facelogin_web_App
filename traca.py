import pickle
import face_recognition

# Supposons que vous ayez ces images pour chaque personne
images = {
    "reda": "moi.jpg",
    "basma": "basma.jpg",
    "mohamed": "baba.jpg",
    
    # ...
}

encoded_faces = {}
for person, img_path in images.items():
    img = face_recognition.load_image_file(img_path)
    face_encoding = face_recognition.face_encodings(img)[0]
    encoded_faces[person] = face_encoding

# Enregistre les encodages de visage dans un fichier
with open('encodings.pkl', 'wb') as f:
    pickle.dump(encoded_faces, f)
