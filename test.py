import face_recognition

# Charge une image
image = face_recognition.load_image_file("./static/face/unknown/test.jpg")

# Extrayez les encodages du visage de l'image
face_encodings = face_recognition.face_encodings(image)

# Imprime les encodages du visage
for encoding in face_encodings:
    print(encoding)
