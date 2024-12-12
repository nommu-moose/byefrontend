def dict_null_values_to_defaults(target_dict, default_dict):
    for key, value in default_dict.items():
        if not target_dict.get(key):
            target_dict[key] = value
    return target_dict
