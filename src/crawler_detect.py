import face_recognition
import os
import sys
import pandas as pd
import yaml

parameters = {}
print('Initializing Face Recognition...')
# read parameters:
with open("../parameters.yml", 'r') as stream:
    try:
        parameters = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

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


if __name__ == "__main__":

    className = parameters['class_name']
    if '' == className:
        print('Select Class Name: (Class___)')
        className = input()
    print('FaceRecognition: Initializing...')
    # which class of data we want to have
    # dir_path = os.path.dirname(os.path.realpath(__file__))
    # taggedImagesDirectory = dir_path + "/data/classes/" + className + "/"
    taggedImagesDirectory = parameters['class_directory'] + '/' + className + '/'
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

    checkLockerFile = open(parameters['process_directory'] + '/' + parameters['face_file'])
    current_index = checkLockerFile.read()
    csvFile = parameters['process_directory'] + '/' + parameters['parsed_file']
    print('Starting from last locked row: ' + current_index)

    rows = pd.read_csv(csvFile, sep=',')
    index = -1
    previousLink = ''
    rows['vote'] = ''
    rows['matches'] = ''
    for index, element in rows.iterrows():
        if index <= int(current_index):
            continue
        elif 0 == index % parameters['refresh_lock']:
            # update lock
            current_index = str(index)
            print('Process lock updated:' + current_index)
            lockerFile = open(parameters['process_directory'] + '/' + parameters['face_file'], 'w+')
            lockerFile.write(current_index)
            lockerFile.close()
            # save the processed data
            rows.to_csv(csvFile, index=False, sep=',', encoding='utf-8')
        suggestedTag = []
        # we skip any row un-original row or row with repeated images because vote will not change
        if 'None' == element['retweet_from_tweet_str_id'] and previousLink != element['image_url']:
            previousLink = element['image_url']
            unknownImagePath = parameters['image_directory'] + '/' + element['image_name']
            print('Scanning Tweet # ' + str(element['tweet_id']))
            suggestedTag = detect_unknown_image(imageList, unknownImagePath, True)
        vote = len(suggestedTag)
        rows.loc[index, 'vote'] = vote
        rows.loc[index, 'matches'] = '####'.join(suggestedTag)

    print('Saving CSV file...')
    rows.to_csv(csvFile, index=False, sep=',', encoding='utf-8')
    print('Operation finished')
    print('Last lock index: ' + str(index))
    lockerFile = open(parameters['process_directory'] + '/' + parameters['face_file'], 'w+')
    lockerFile.write(str(index))
    lockerFile.close()
