import os
import numpy as np
import cv2

def extract_results(res, threshold=0.80):
    res = res[0]
    boxes = [line[0] for line in res] if res is not None else []
    txts = [line[1][0] for line in res] if res is not None else []
    scores = [float(line[1][1]) for line in res] if res is not None else []
    final_results = {"boxes":[], "texts":[], "scores":[]}
    for index, score in enumerate(scores):
        if score > threshold:
            final_results["boxes"].append(boxes[index])
            final_results["texts"].append(txts[index])
            final_results["scores"].append(score)
    return final_results


def infer(model, img, threshold=0.8):    # Loading model
    if isinstance(img, str):
        img = cv2.imread(img)
    # Inferencing
    results = model.ocr(img)
    print(results)
    # Extrating results
    res_dict = extract_results(res=results, threshold=threshold)
    return res_dict



from itertools import permutations
import cv2

# # Your OCR output and reference strings go here
# texts_detected = ["sometext", "you", "got", "text"]  # Replace with your OCR output
# bounding_boxes = [(0, 0, 20, 20), (25, 0, 45, 20), (50, 0, 70, 20), (75, 0, 95, 20)]  # Replace with your bounding box coordinates
# reference_strings = ["sometext", "yougot", "text"]  # Replace with your list of reference strings

def match_strings(texts_detected, bounding_boxes, reference_strings):

    # Initialize list to hold matched bounding boxes
    matched_dets = dict()

    if len(texts_detected)==0:
        return matched_dets
    
    # First, check for direct matches between reference strings and detected text
    remaining_references = []
    for ref in reference_strings:
        found = False
        for idx, detected_text in enumerate(texts_detected):
            if clean_string(ref) in clean_string(detected_text):
                matched_dets[ref] = [bounding_boxes[idx]]
                found = True
                break
        if not found:
            remaining_references.append(ref)

    if len(remaining_references)!=0:
        # Generate all possible permutations
        all_permutations = list(permutations(texts_detected))
        # print(all_permutations)

        # Loop through all remaining permutations and concatenate them
        for perm in all_permutations:
            concatenated_text = ''.join(perm)
            # print(concatenated_text)

            # Loop through all remaining reference strings to check for a match
            for ref in remaining_references:
                match_pos = clean_string(concatenated_text).find(clean_string(ref))

                # If match found, find which original text caused the match and append its bounding box
                if match_pos != -1:
                    match_pos_1 = match_pos + len(clean_string(ref)) 
                    start_pos = 0
                    for text in perm:
                        end_pos = start_pos + len(clean_string(text))
                        if (start_pos <= match_pos < end_pos) or (match_pos <= start_pos < match_pos_1):
                            # matched_boxes.append(bounding_boxes[texts_detected.index(text)])
                            # Adding all the detecting that are matching
                            if ref not in matched_dets.keys():
                                matched_dets[ref] = [bounding_boxes[texts_detected.index(text)]]
                            else:
                                matched_dets[ref].append(bounding_boxes[texts_detected.index(text)])
                        start_pos = end_pos 
    return matched_dets


def draw_boxes_and_text(image, bounding_boxes, texts):
    # Validate inputs
    if len(bounding_boxes) != len(texts):
        raise ValueError("The number of bounding boxes must match the number of texts")

    # Loop over each bounding box and corresponding text
    for box, text in zip(bounding_boxes, texts):
        # Draw rectangle
        box = [[int(val) for val in sub] for sub in box]
        image = drawbox(box, image)      
        # Draw text
        cv2.putText(image, text, box[0], cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
    return image


def drawbox(box, image):
    # Draw lines between each pair of points
    # print(box[0], type(box[0]), tuple(box[0]))
    cv2.line(image, tuple(box[0]), tuple(box[1]), (0, 255, 0), 3)
    cv2.line(image, tuple(box[1]), tuple(box[2]), (0, 255, 0), 3)
    cv2.line(image, tuple(box[2]), tuple(box[3]), (0, 255, 0), 3)
    cv2.line(image, tuple(box[3]), tuple(box[0]), (0, 255, 0), 3)
    return image


def Visualize(image, results):
    # Font settings
    font = cv2.FONT_HERSHEY_SIMPLEX  # Font type
    font_scale = 2.5                 # Font scale
    font_color = (0, 0, 255)     # White
    font_thickness = 3               # Thickness of the font lines
    
    for txt, boxes in results.items():

        write_pt = [int(val) for val in boxes[0][0]]
        for box in boxes:
            box = [[int(val) for val in sub] for sub in box]
            image = drawbox(box, image)
        print("Text to write: ", txt)
        # Add text to image
        cv2.putText(image, txt, write_pt, font, font_scale, font_color, font_thickness)
    return image


def clean_string(input_str):
    # Remove non-alphanumeric characters and convert to lowercase
    cleaned_str = ''.join(char.lower() for char in input_str if char.isalnum())
    
    return cleaned_str


# # Annotate the image with the matched bounding boxes
# image = cv2.imread('your_image_path.jpg')  # Replace with your image path

# for bbox in matched_boxes:
#     top_left, top_right, bottom_right, bottom_left = bbox  # Assuming each bounding box is a tuple of 4 points
#     cv2.rectangle(image, (top_left[0], top_left[1]), (bottom_right[0], bottom_right[1]), (0, 255, 0), 2)

# cv2.imwrite('annotated_image.jpg', image)  # This saves the annotated image
