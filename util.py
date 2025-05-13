import easyocr
import pandas as pd
from fuzzywuzzy import fuzz

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


def get_bus_line():

    # 1. Carregar os dados do arquivo CSV de entrada
    input_csv = 'output/dados_lidos.csv'  # Substitua pelo seu arquivo de entrada
    output_csv = 'output/linhas_identificadas.csv'  # Arquivo de saída

    # Carrega o DataFrame do CSV (supondo colunas: id_onibus, precisao_letreiro, texto_lido, precisao_texto)
    df = pd.read_csv(input_csv)

    # 2. Lista de linhas válidas (exemplo - você pode carregar de outro CSV ou banco de dados)
    linhas_validas = [
        '223 Açucena',
        '223 Unifap',
        '124 Amazonas',
        '124 Zerão',
        '441 Brasil Novo',
        '441 Universidade',
        '105 Fortaleza',
        '105 Centro',
        '453 Infraero II',
        '453 Zerão',
        '431 Macapaba',
        '431 Garden Shopping',
        'Macapá - Santana',
        'Via coração',
        '214 Marabaixo',
        '214 Universidade',
        '611 Renascer',
        '611 Unifap',
        '510 Terra Nova',
        '510 Garden',
        '131 Universidade',
        '131 Jardim',
        '112 Zerão',
        '112 São Camilo'
    ]

    # 3. Função para encontrar a melhor correspondência usando fuzzy matching
    def encontrar_linha(texto_lido, linhas_validas, limiar=80):
        melhor_correspondencia = None
        maior_pontuacao = 0
        texto_lido = str(texto_lido).upper().strip()  # Padroniza o texto (evita NaN)

        for linha in linhas_validas:
            pontuacao = fuzz.ratio(texto_lido, linha.upper())
            if pontuacao > maior_pontuacao and pontuacao >= limiar:
                maior_pontuacao = pontuacao
                melhor_correspondencia = linha
        return melhor_correspondencia if melhor_correspondencia else "NÃO IDENTIFICADO"

    # 4. Aplica a função para identificar a linha
    df['linha_identificada'] = df['texto_lido'].apply(
        lambda x: encontrar_linha(x, linhas_validas, limiar=80)
    )

    # 5. Salva o resultado em um novo CSV
    df.to_csv(output_csv, index=False, encoding='utf-8')

    print(f"Processamento concluído! Resultados salvos em: {output_csv}")
