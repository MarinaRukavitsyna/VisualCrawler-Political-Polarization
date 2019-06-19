import face_recognition
import os

'''
    reading all images within the directory
    base images are supposed to have only SINGLE FACE in them
    :var directory the given dir
    :return array|null
'''


def read_all_known_images(directory):
    images = os.listdir(directory)
    full_image_path = {}
    for image in images:
        full_image_path[image] = directory + image

    return full_image_path


'''
    detects an unknown image out of a list of already tagged photos
    for each encoding i.e. face it suggests one tag or NOT_FOUND
    :var array list of known image paths
    :var string unknown image path
    :var boolean is NOT_FOUND tag disabled?
    :return array list of all suggested tags that found in the picture 
'''


def detect_unknown_image(image_list, unknown_image_path, not_found_disabled = False):

    try:
        unknown_image = face_recognition.load_image_file(unknown_image_path)
        unknown_encodings = face_recognition.face_encodings(unknown_image)
    except FileNotFoundError:
        print('Error: unknown image can not be loaded!')
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


# actual main code>

dir_path = os.path.dirname(os.path.realpath(__file__))
taggedImagesDirectory = dir_path + "/data/images/known_images/"
imageList = read_all_known_images(taggedImagesDirectory)


# tests>

testFiles = [
    "temp_1.jpg",
    "temp_2.jpeg",
    "temp_3.jpg",
    "temp_5.jpeg",
    "temp_6.jpg",
    "temp_7.jpg",
]

for tempFile in testFiles:
    unknownImagePath = dir_path + "/data/images/temp/" + tempFile
    suggestedTag = detect_unknown_image(imageList, unknownImagePath, True)
    print(suggestedTag)

