from ultralytics import YOLO
import cv2
from sort.sort import *
from util import get_bus, read_destination, write_csv, get_bus_line


results = {}

mot_tracker = Sort(max_age=30, min_hits=60)

# carrega os modelos
coco_model = YOLO('yolov8s.pt')
destination_detector = YOLO('./models/best.pt')

# carrega o video
cap = cv2.VideoCapture('./videos/sample3.mp4')

coco_bus_id = 5 # o n°5 corresponde ao id da classe ônibus no dataset COCO

# lê os frames
frame_nmr = -1
ret = True
while ret:
    frame_nmr += 1
    ret, frame = cap.read()
    if ret :
        results[frame_nmr] = {}

        # detecta cada ônibus no frame e salva as coordenadas da caixa delimitadora e a precisão
        detections = coco_model(frame)[0]
        detections_ = []
        for detection in detections.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = detection
            if int(class_id) == coco_bus_id:
                detections_.append([x1, y1, x2, y2, score])

        # rastreia cada ônibus
        track_ids = mot_tracker.update(np.asarray(detections_))

        # detecta os letreiros no frame
        destinations = destination_detector(frame)[0]
        for destination in destinations.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = destination

            # faz a correspondência entre letreiros e ônibus
            xbus1, ybus1, xbus2, ybus2, bus_id = get_bus(destination, track_ids)

            if bus_id != -1:

                # recorta o letreiro
                destination_crop = frame[int(y1):int(y2), int(x1): int(x2), :]

                # mostra o recorte
                # cv2.imshow('original_crop', destination_crop)
                # cv2.waitKey(0)

                # lê o texto contido no letreiro
                destination_text, destination_text_score = read_destination(destination_crop)

                if destination_text is not None and destination_text_score > 0.5 :
                    results[frame_nmr][bus_id] = {'bus': {'bbox': [xbus1, ybus1, xbus2, ybus2]},
                                                  'destination': {'bbox': [x1, y1, x2, y2],
                                                                    'text': destination_text,
                                                                    'bbox_score': score,
                                                                    'text_score': destination_text_score}}
               
                    # escreve os resultados no arquivo CSV
                    write_csv(results, './output/dados_lidos.csv')
                    get_bus_line()