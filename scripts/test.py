import os
import numpy as numpy
import cv2
from utils import extract_results


from paddleocr import PaddleOCR,draw_ocr

# custom_ocr = PaddleOCR(use_angle_cls=True,
#                 # rec_model_dir='/home/frinks3/amal/paddle_ocr/PaddleOCR/inference/en_PP-OCRv3_rec_custom_1000_epochs_freezed/',
#                 rec_model_dir='/home/frinks3/.paddleocr/whl/rec/en/en_PP-OCRv3_rec_infer/',
#                 det_model_dir='/home/frinks3/.paddleocr/whl/det/en/en_PP-OCRv3_det_infer', 
#                 rec_char_dict_path='/home/frinks3/amal/paddle_ocr/PaddleOCR/ppocr/utils/en_dict.txt',
#                 use_gpu=True,
#                 show_log=True, lang="en")

pre_ocr = PaddleOCR(use_angle_cls=True, lang="en")

img_path = "IMG_20230906_165406.jpg"
img = cv2.imread(img_path)
res = extract_results(pre_ocr.ocr(img))
print(res)

# from itertools import permutations

# def generate_all_combinations(s):
#     all_combinations = []
#     n = len(s)
    
#     for i in range(1, n + 1):
#         for subset in permutations(s, i):
#             all_combinations.append(''.join(subset))
            
#     return all_combinations

# # Example usage:
# reference_strings = res["texts"]
# print("len of mylist: ", len(reference_strings))
# all_variants = generate_all_combinations(reference_strings)
# print("len of all possible combinations: ", len(all_variants))
# # print(result)  # Output will be ['a', 'b', 'ab', 'ba']

# # Partial matching function
# def partial_match(target, patterns):
#     return any(pattern in target for pattern in patterns)

# # List of reference strings
# # reference_strings = ['abc', 'def', 'ghi']

# # # List of strings to generate combinations and permutations from
# # input_strings = ['a', 'b', 'c', 'd']

# import time
# x = time.time()
# results = {}
# for ref in reference_strings:
#     for variant in all_variants:
#         if partial_match(variant, [ref]):
#             if ref not in results:
#                 results[ref] = []
#             results[ref].append(variant)
# print("Time for matching: ", time.time() - x)
# print(len(results))
# print(results)
# # print(pre_ocr.ocr(img))