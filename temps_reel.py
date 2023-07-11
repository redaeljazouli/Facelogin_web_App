import cv2
import face_recognition
import numpy as np

# je charge mes visages encodés et leurs noms à partir d'un fichier avec pickle
import pickle
with open('encodings.pkl', 'rb') as f:
    encoded_faces = pickle.load(f)

# Capture la vidéo de la caméra
video_capture = cv2.VideoCapture(0)

while True:
    # Capture un seul cadre de vidéo
    ret, frame = video_capture.read()

    # Trouve toutes les faces dans le cadre de la vidéo actuelle
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Voir si le visage correspond à ceux connus
        matches = face_recognition.compare_faces(list(encoded_faces.values()), face_encoding)

        name = "Visage non reconnu"

        if True in matches:
            first_match_index = matches.index(True)
            name = list(encoded_faces.keys())[first_match_index]

        # Dessine une boite autour du visage
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Dessine un label avec le nom sous la face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Affiche le résultat
    cv2.imshow('Video', frame)

    # Quitte sur 'q'
    if cv2.waitKey(4) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
