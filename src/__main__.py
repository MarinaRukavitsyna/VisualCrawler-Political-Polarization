import face_recognition
import os
import sys
import pandas as pd

'''
    reading all images within the directory
    base images are supposed to have only SINGLE FACE in them
    :var directory the given dir
    :var local folder name that includes images
    :return array|null
'''


def read_all_known_images(directory, local_folder='/Images/'):
    images = os.listdir(directory + local_folder)
    full_image_path = {}
    for image in images:
        full_image_path[image] = directory + local_folder + image

    return full_image_path


'''
    reading csv file that includes name, token and tag of each entity
    :var directory the given dir
    :return dataFrame including class tagger data
'''


def read_tagger(directory):
    data = pd.read_csv(directory, sep='\t')
    return data


'''
    detects an unknown image out of a list of already tagged photos
    for each encoding i.e. face it suggests one tag or NOT_FOUND
    :var array list of known image paths coming from a certain class
    :var string unknown image path
    :var boolean is NOT_FOUND tag disabled?
    :return array list of all suggested tags that found in the picture 
'''


def detect_unknown_image(image_list, unknown_image_path, not_found_disabled=False):
    try:
        unknown_image = face_recognition.load_image_file(unknown_image_path)
        unknown_encodings = face_recognition.face_encodings(unknown_image)
    except FileNotFoundError:
        print('Error: unknown image can not be loaded!' + unknown_image_path)
        return []

    # loaded image has no face encodings
    if not unknown_encodings:
        return []

    return_list = []
    for unknown_encoding in unknown_encodings:
        suggested_tag = 'NOT_FOUND'
        for key, value in image_list.items():
            try:
                known_image = face_recognition.load_image_file(value)
                known_encoding = face_recognition.face_encodings(known_image)[0]
                is_matching = face_recognition.compare_faces([known_encoding], unknown_encoding)

                # no valid results
                if not is_matching or 1 != len(is_matching):
                    continue
                # we compare one by one
                if is_matching[0]:
                    parts = key.split(".")
                    if 1 <= len(parts):
                        suggested_tag = parts[0]
                        break
                    suggested_tag = key
                    break
            except IndexError:
                print('Error: one image can not be encoded! (', key, ')')

        if not_found_disabled and 'NOT_FOUND' == suggested_tag:
            continue
        # save tag in the suggestion list
        return_list.append(suggested_tag)

    # return list of all people involved in image
    return return_list


'''
    updating the count for the dataFrame based on the given token
    :var the main tagger dataFrame
    :var the current detected token array 
    ** it may be 1 or more detected tags if there are multiple people 
    on the photo that are detected
    :return the updated tagger dataFrame 
'''


def update_tagger_frame(data_frame, token):
    if 'NOT_FOUND' == token:
        return data_frame
    if data_frame.loc[data_frame['token'].isin(token)].empty:
        return data_frame

    # update the occurrence
    data_frame.loc[data_frame['token'].isin(token), ['occurrence']] += 1
    return data_frame


# actual main code>

# AJAVAHER: call Tweeter API >>>

className = 'ClassB'
if '' == className:
    print('Select Class Name:')
    className = input()
print('FaceRecognition: Initializing...')
# which class of data we want to have
dir_path = os.path.dirname(os.path.realpath(__file__))
taggedImagesDirectory = dir_path + "/data/" + className + "/"
if not os.path.exists(taggedImagesDirectory):
    print("Error: Class entered does not exist!")
    sys.exit()
if not os.path.isdir(taggedImagesDirectory):
    print("Error: Class entered does not have valid directory!")
    sys.exit()

print('FaceRecognition: Reading Class Images...')
imageList = read_all_known_images(taggedImagesDirectory)

print('FaceRecognition: Reading Class tags...')
classTaggerFrame = read_tagger(taggedImagesDirectory + "index.csv")
# adding score count

classTaggerFrame['occurrence'] = 0

# tests>

testFiles = [
    "temp_2.jpeg",
    "temp_3.jpg",
    "temp_6.jpg",
    "temp_7.jpg",
    "temp_10.jpg",
]

for tempFile in testFiles:
    unknownImagePath = dir_path + "/data/images/temp/" + tempFile
    suggestedTag = detect_unknown_image(imageList, unknownImagePath, True)
    classTaggerFrame = update_tagger_frame(classTaggerFrame, suggestedTag)

    # AJAVAHER: call hate speech detector >>>

    print(suggestedTag)

print(classTaggerFrame)
