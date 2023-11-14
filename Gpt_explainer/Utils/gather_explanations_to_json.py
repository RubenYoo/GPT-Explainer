import json
import os


def sort_explanations(list_of_explanations: list) -> list:
    """
    This function sorts the list of explanations by the slide number
    :param list_of_explanations: the list of explanations with the slide number
    :return: the sorted list of explanations without the slide number
    """
    
    sorted_list = sorted(list_of_explanations, key=lambda x: x[0])
    return [slide_explanation[1] for slide_explanation in sorted_list]


def save_to_json(list_of_explanations: list, path: str) -> None:
    """
    This function saves the list of explanations to a json file
    :param list_of_explanations: the list of explanations
    :param path: the path of the pptx file
    :return: None
    """
    
    with open('../Web_api/outputs/' + os.path.splitext(os.path.basename(path))[0] + '.json', 'w') as my_file:
        json.dump(sort_explanations(list_of_explanations), my_file)
