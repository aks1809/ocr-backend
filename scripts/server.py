import os
import numpy as np
import cv2
from paddleocr import PaddleOCR, draw_ocr
from utils import *
import socketio
from dotenv import load_dotenv
import sys
import json

# Loading parameters
load_dotenv()

# Params
GLOBAL_SWITCH = [False]
REFERENCE_NAME = [None]
REFERENCE_TXT = [None]
IMAGE_NAME = [None]
IMAGE_BASE = os.getenv("BASE_PATH")

sio = socketio.Client()

try:
    sio.connect(os.getenv("BASE_URL"))
except Exception as e:
    print('Socket is unable to connect to the BASE_URL!!!')


@sio.on('input')
def on_message(data):
    print("input called", data)
    GLOBAL_SWITCH[0] = True
    IMAGE_NAME[0] = data["input_1_image"]
    REFERENCE_NAME[0] = data["input_2_image"]
    REFERENCE_TXT[0] = data["input_2_text"]


###################################
# Model loading
try:
    model = PaddleOCR(use_angle_cls=True,
                      rec_model_dir='./en_PP-OCRv3_rec_infer',
                      det_model_dir='./en_PP-OCRv3_det_infer',
                      rec_char_dict_path='./en_dict.txt',
                      show_log=True, lang="en")  # ,  det_algorithm='EAST')
    print("[INFO] Model Loaded")
except Exception as e:
    print(e)
    print("[INFO] Error While Loading the model")


# Main Fucntion
def main():
    while True:
        try:
            if GLOBAL_SWITCH[0] == False:
                continue
            # Checking if refernce txt is available
            if REFERENCE_TXT[0] == "":
                ref_img = cv2.imread(f'{IMAGE_BASE}/{REFERENCE_NAME[0]}')
                ref_result = infer(
                    model=model, img=ref_img, threshold=0.8)
                txt_2_compare, ref_bboxes = ref_result["texts"], ref_result["boxes"]
                # Saving the refernce image
                ref_image_res = draw_boxes_and_text(image=ref_img, bounding_boxes=ref_bboxes, texts=txt_2_compare)
                cv2.imwrite(f"{IMAGE_BASE}/{REFERENCE_NAME[0]}_result.png", ref_image_res)

            else:
                txt_2_compare = REFERENCE_TXT
            print("txt_2_compare", txt_2_compare)
            # Getting results from image
            img = cv2.imread(f'{IMAGE_BASE}/{IMAGE_NAME[0]}')
            # img = cv2.imread("IMG_20230905_132552_678.jpg")
            results = infer(model=model, img=img, threshold=0.8)
            # comparing reference image and getting matched txts
            matched_detections = match_strings(
                texts_detected=results["texts"], bounding_boxes=results["boxes"], reference_strings=txt_2_compare)
            # Visualise results
            final_image = draw_boxes_and_text(image=img, bounding_boxes=results["boxes"], texts=results["texts"])
            # final_image = Visualize(image=img, results=matched_detections)
            # saving image
            cv2.imwrite(
                f"{IMAGE_BASE}/{IMAGE_NAME[0]}_result.png", final_image)
            # cv2.imwrite(f"result.png", final_image)
            print(matched_detections)
            detected_texts = list(matched_detections.keys())
            res_dict = {
                "image_path": f"{IMAGE_NAME[0]}_result.png",
                "ref_image_path": f"{REFERENCE_NAME[0]}_result.png" if REFERENCE_NAME[0] is not None else None,
                "texts": ",".join(detected_texts) if len(detected_texts) != 0 else None
            }

            res_json = json.dumps(res_dict, indent=2)
            print(res_json)
            sio.emit("output", res_json)
            GLOBAL_SWITCH[0] = False
            IMAGE_NAME[0] = None
            REFERENCE_NAME[0] = None
            REFERENCE_TXT[0] = None

        except Exception as e:
            print(e)
            print("INFO: Error in main")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            GLOBAL_SWITCH[0] = False
            IMAGE_NAME[0] = None
            REFERENCE_NAME[0] = None
            REFERENCE_TXT[0] = None
            pass


if __name__ == "__main__":
    main()
