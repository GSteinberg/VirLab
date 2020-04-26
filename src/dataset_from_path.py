#Get dataset name as string from file path
def dataset_from_path(path):
    path = str(path)
    if '/' in path:
        path_list = path.split('/')
    elif '\\' in path:
            path_list = path.split('\\')

    dataset_name = path_list[-1]
    return dataset_name
