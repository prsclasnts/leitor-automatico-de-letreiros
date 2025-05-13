import easyocr

# Inicializa o leitor OCR
reader = easyocr.Reader(['pt'], gpu=False)


def write_csv(results, output_path):
    """
    Escreve o resultados em um arquivo CSV.

    Args:
        results (dict): Dicionário contendo os resultados.
        output_path (str): Caminho para o arquivo CSV de saída.
    """
    with open(output_path, 'w') as f:
        f.write('{},{},{},{},{}\n'.format('frame', 'id_onibus', 'texto_lido', 'precisao_letreiro',
                                                'precisao_texto'))

        for frame_nmr in results.keys():
            for bus_id in results[frame_nmr].keys():
                # print(results[frame_nmr][bus_id])
                if 'bus' in results[frame_nmr][bus_id].keys() and \
                   'destination' in results[frame_nmr][bus_id].keys() and \
                   'text' in results[frame_nmr][bus_id]['destination'].keys():
                    f.write('{},{},{},{},{}\n'.format(frame_nmr,
                                                            bus_id,
                                                            results[frame_nmr][bus_id]['destination']['text'],
                                                            results[frame_nmr][bus_id]['destination']['bbox_score'],
                                                            results[frame_nmr][bus_id]['destination']['text_score'])
                            )
        f.close()



def read_destination(destination_crop):
    """
    Lê o texto contido no letreiro do recorte de imagem recebido.

    Args:
        license_plate_crop (PIL.Image.Image): Recorte de imagem contendo o letreiro.

    Retorna:
        tuple: Tupla contendo o texto lido e o valor de precisão.
    """

    detections = reader.readtext(destination_crop)
    print('## Iniciou Leitura ##')
    readIt = False
    for detection in detections:
        bbox, text, score = detection
        text = text.upper().replace(' ', '')
        readIt = True

        if readIt:
            print('## Texto Lido ##')
        return text, score
    

    return None, None


def get_bus(destination, vehicle_track_ids):
    """
    Recupera as coordenadas do veículo e ID baseados nas coordenadas do letreiro.

    Args:
        destination (tuple): Uma tupla contendo as coordenadas do letreiro (x1, y1, x2, y2, score, class_id).
        vehicle_track_ids (list): Lista do IDs dos veículos e suas coordenadas correpondentes.

    Retorna:
        tuple: Tupla contendos as coordenadas do veículo (x1, y1, x2, y2) and ID.
    """
    x1, y1, x2, y2, score, class_id = destination

    foundIt = False
    for j in range(len(vehicle_track_ids)):
        xcar1, ycar1, xcar2, ycar2, car_id = vehicle_track_ids[j]

        if x1 > xcar1 and y1 > ycar1 and x2 < xcar2 and y2 < ycar2:
            car_indx = j
            foundIt = True
            break

    if foundIt:
        return vehicle_track_ids[car_indx]

    return -1, -1, -1, -1, -1
