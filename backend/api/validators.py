from rest_framework import serializers


def validate_unique_for_list(name, data):
    temp = set()
    for elem in data:
        if elem in temp:
            raise serializers.ValidationError(
                f'Поле {name} содержит повторяющийся элемент {elem}.')
        temp.add(elem)
