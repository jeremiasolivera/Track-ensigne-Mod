from django.shortcuts import render,redirect,get_object_or_404
import cv2
import os
import face_recognition
from .models import Paciente
from django.contrib.auth.decorators import login_required
from .form import PacienteForm
import time

@login_required
def extract_faces(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        patient_age = int(request.POST.get('patient_age'))
        patient_report = request.POST.get('patient_report')
        patient_name = request.POST.get('patient_name')  # Obtén el nombre del paciente del formulario
        imagesPath = "C:/Users/alexi/OneDrive/Escritorio/Programming/Track-ensigne-CRUDpatient/Track-ensigne-CRUDpatient/faces"

        if not os.path.exists(imagesPath):
            os.makedirs(imagesPath)
            print("Nueva carpeta: faces")

        image_path = os.path.join(imagesPath, f"{patient_name}.jpg")  # Usa el nombre del paciente como nombre de archivo
        with open(image_path, 'wb') as f:
            for chunk in image.chunks():
                f.write(chunk)
        paciente = Paciente(nombre=patient_name, imagen=image, edad=patient_age, informe_medico=patient_report)
        paciente.save()
        # Código para el procesamiento de imágenes y extracción de rostros
        faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        image = cv2.imread(image_path)
        
        faces = faceClassif.detectMultiScale(image, 1.1, 5)
        for (x, y, w, h) in faces:
            face = image[y:y + h, x:x + w]
            face = cv2.resize(face, (150, 150))
            new_face_filename = f"{patient_name}.jpg"  # Usa el nombre del paciente como nombre de archivo
            cv2.imwrite(os.path.join(imagesPath, new_face_filename), face)

        # return redirect('recognition')  # Redirige a la vista de reconocimiento

    return render(request, 'extract_faces.html')




@login_required
def recognition(request):
        imageFacesPath = "C:/Users/alexi/OneDrive/Escritorio/Programming/Track-ensigne-CRUDpatient/Track-ensigne-CRUDpatient/faces"

        facesEncodings = []
        facesNames = []
        for file_name in os.listdir(imageFacesPath):
            image = cv2.imread(os.path.join(imageFacesPath, file_name))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            f_coding = face_recognition.face_encodings(image, known_face_locations=[(0, 150, 150, 0)])[0]
            facesEncodings.append(f_coding)
            facesNames.append(file_name.split(".")[0])

        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        # Detector facial
        faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            orig = frame.copy()
            faces = faceClassif.detectMultiScale(frame, 1.1, 5)

            for (x, y, w, h) in faces:
                face = orig[y:y + h, x:x + w]
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                actual_face_encoding = face_recognition.face_encodings(face, known_face_locations=[(0, w, h, 0)])[0]
                result = face_recognition.compare_faces(facesEncodings, actual_face_encoding)
                if True in result:
                    index = result.index(True)
                    name = facesNames[index]
                    color = (125, 220, 0)
                else:
                    name = "Desconocido"
                    color = (50, 50, 255)

                cv2.rectangle(frame, (x, y + h), (x + w, y + h + 30), color, -1)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, name, (x, y + h + 25), 2, 1, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow("Frame", frame)
            k = cv2.waitKey(1)
            if k == 27:  # Presiona "ESC" para salir
                break
        
        cap.release()
        cv2.destroyAllWindows()

        # Devuelve los resultados a la plantilla
        context = {
            'result': result,  # Agrega los resultados del reconocimiento
        }
        return render(request, 'recognition.html', context)



@login_required
def patients_details(request):

    patients = Paciente.objects.all()

    context = {
        'patients': patients
    }

    return render(request, 'pages/detalles_pacientes.html', context)

@login_required
def patients_delete(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)

    if request.method == 'POST':
        try:
            paciente.delete()
            return redirect('pacientes')
        except Exception as e:
            print.error(request, "Ocurrió un error al eliminar paciente")

    return render(request, 'pages/eliminar_paciente.html', {'paciente':paciente})

@login_required
def patients_update(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)

    if request.method == 'POST':
        form = PacienteForm(request.POST,request.FILES, instance=paciente)  # Cambia "request.post" a "request.POST"

        if form.is_valid():
            form.save()
            return redirect('pacientes')
    else:
        form = PacienteForm(instance=paciente)

    return render(request, 'pages/actualizar_paciente.html', {'form': form})


















##########################################
#         Codigo funcionando
##########################################

@login_required
def restricted_site(request):
    if request.method == 'POST':

        time_desc_advertencia = int(request.POST.get('tiempo_desconocido'))
        print(time_desc_advertencia)
        # Ruta donde se encuentran las imágenes de referencia de rostros conocidos
        imageFacesPath = "C:/Users/alexi/OneDrive/Escritorio/Programming/Track-ensigne-CRUDpatient/Track-ensigne-CRUDpatient/faces"

        # Listas para almacenar las codificaciones de los rostros conocidos y sus nombres
        facesEncodings = []
        facesNames = []

        # Cargar las codificaciones de los rostros conocidos
        for file_name in os.listdir(imageFacesPath):
            image = cv2.imread(os.path.join(imageFacesPath, file_name))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Obtener la codificación del rostro
            f_coding = face_recognition.face_encodings(image, known_face_locations=[(0, 150, 150, 0)])[0]
            
            facesEncodings.append(f_coding)
            facesNames.append(file_name.split(".")[0])

        # Inicializar la cámara para la detección en tiempo real
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        # Detector facial
        faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        # Inicializar una bandera para indicar si se detectó un rostro desconocido
        desconocido_detectado = False
        conocido_detectado = False

        start_time = None

        while True:
            # Capturar un fotograma de la cámara
            ret, frame = cap.read()

            if not ret:
                break

            # Voltear el fotograma horizontalmente
            frame = cv2.flip(frame, 1)
            orig = frame.copy()

            # Detectar rostros en el fotograma
            faces = faceClassif.detectMultiScale(frame, 1.1, 5)

            for (x, y, w, h) in faces:
                face = orig[y:y + h, x:x + w]
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                
                # Obtener la codificación del rostro detectado
                actual_face_encoding = face_recognition.face_encodings(face, known_face_locations=[(0, w, h, 0)])[0]
                
                # Comparar la codificación del rostro detectado con las codificaciones de los rostros conocidos
                result = face_recognition.compare_faces(facesEncodings, actual_face_encoding)

                if True in result:
                    # Si se encuentra un rostro conocido, obtener su nombre
                    index = result.index(True)
                    name = facesNames[index]
                    color = (125, 220, 0)
                    # Reiniciar el contador de tiempo si se detecta un rostro conocido
                    start_time = None
                else:
                    # Si el rostro es desconocido, mostrar "Desconocido" y cambiar el color
                    name = "Desconocido"
                    color = (50, 50, 255)
                    # Iniciar el contador de tiempo si aún no se ha iniciado
                    if start_time is None:
                        start_time = time.time()
                    elif time.time() - start_time >= time_desc_advertencia and desconocido_detectado:
                        # Si se ha superado el tiempo límite de 10 segundos después de detectar un rostro desconocido, salir del bucle
                        desconocido_detectado = True
                        break
                    elif time.time() - start_time >= time_desc_advertencia and desconocido_detectado and conocido_detectado:
                        # Si se ha superado el tiempo límite de 10 segundos después de detectar un rostro desconocido, salir del bucle
                        desconocido_detectado = True
                        break
                    elif time.time() - start_time < time_desc_advertencia and not desconocido_detectado:
                        desconocido_detectado = True

                cv2.rectangle(frame, (x, y + h), (x + w, y + h + 30), color, -1)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, name, (x, y + h + 25), 2, 1, (255, 255, 255), 2, cv2.LINE_AA)

            # Mostrar el fotograma con los resultados
            cv2.imshow("Frame", frame)

            # Comprobar si se ha superado el tiempo límite de time_desc_advertencia segundos
            if start_time is not None and time.time() - start_time >= time_desc_advertencia:
                break

            # Esperar la tecla ESC para salir
            k = cv2.waitKey(1)
            if k == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

        # Devolver los resultados a la plantilla
        context = {
            'result': result,
            'desconocido_detectado': desconocido_detectado,  # Agregar los resultados del reconocimiento
        }

        # Renderizar la plantilla con los resultados
        return render(request, 'pages/sitio_restringido.html', context)
    else:
        return render(request, 'pages/sitio_restringido.html')