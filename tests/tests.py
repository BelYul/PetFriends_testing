from api import PetFriends
from settings import valid_email, valid_password, invalid_email
import os

#непосредственно моя работа начинается со стр. 89

pf = PetFriends()

""" Проверяем, что запрос api ключа возвращает статус 200 и в результате содержится слово key"""
def test_get_api_key_for_valid_user(email = valid_email, password = valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert 'key' in result


""" Проверяем, что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """
def test_get_all_pets_with_valid_key(filter=''):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0


    """Проверяем, что можно добавить питомца с корректными данными"""
def test_add_new_pet_with_valid_data(name='Мурзик', animal_type='кошак',
                                     age='1', pet_photo='images/cat1.jpg'):

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


"""Проверяем возможность обновления информации о питомце"""
def test_successful_update_self_pet_info(name='Tom', animal_type='Cat', age=2):

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


"""Проверяем возможность удаления питомца"""
def test_successful_delete_self_pet():

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


#позитивные тесты по документации к имеющимся API-методам (оставшиеся 2 метода)
"""Проверяем, что можно добавить питомца с без фото"""
def test_add_new_pet_with_valid_data(name='Кузя', animal_type='хомяк', age='1'):

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name



"""Проверяем, что можно добавить фото к питомцу без фото"""
def test_set_photo_with_valid_data(pet_photo='images/P1040103.jpg'):
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то добавляем фото к первому питомцу из списка
    if len(my_pets['pets']) > 0:
        status, result = pf.add_photo_of_pet(auth_key, my_pets['pets'][0]['id'], pet_photo)

        # Проверяем что статус ответа = 200 и изображение добавлено
        assert status == 200
        assert result['pet_photo'] != ''
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


#Негативные тесты
"""1. Проверяем, что запрос на получение ключа с невалидным email вернет ошибку 404"""
def test_get_api_key_for_invalid_email(email = invalid_email, password = valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 403


"""2. Проверяем, будет ли успешно обработан запрос на добавление питомца, где имя - цифры"""
def test_add_new_pet_with_invalid_name(name='123', animal_type='mouse', age='1'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name
    #если тест пройден успешно - в системе некорректная валидация данных, это баг


"""3. Проверяем, будет ли добавлен питомец с очень большим числом в поле возраст"""
def test_add_new_pet_with_invalid_age(name='Джерри', animal_type='хомячок', age='3465437567897643857342578'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name
    #если тест пройден успешно - в системе некорректная валидация данных, это баг


"""4. Проверяем, будет ли добавлен питомец с отрицательным числом в поле возраст"""
def test_add_new_pet_with_negative_age(name='Вася', animal_type='кролик', age='-1'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name
    #если тест пройден успешно - в системе некорректная валидация данных, это баг


"""5. Проверям, будет ли добавлен питомец с пустыми полями"""
def test_add_new_pet_with_empty_data(name='', animal_type='', age=''):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name
    #если тест пройден успешно - в системе некорректная валидация данных, это баг


"""6. Проверяем, будут ли обновлены данные о типе питомца на некорректные - спец. символы"""
def test_update_pet_info_with_invalid_data(name='Кузя', animal_type='%*&#@!)*%&%#', age='1'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        assert status == 200
        assert result['animal_type'] == animal_type
    else:
        raise Exception("There is no my pets")
    # если тест пройден успешно - в системе некорректная валидация данных, это баг


"""7. Проверяем, будут ли обновлены данные питомца на некорректные - все значения пустые"""
def test_update_pet_info_with_empty_data(name='', animal_type='', age=''):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("There is no my pets")
    # если тест пройден успешно - в системе некорректная валидация данных, это баг
    # обновления данных с этим тестом не произошло


"""8. Проверяем, будут ли обновлены данные питомца на некорректные - в возрасте - строка"""
def test_update_pet_info_with_invalid_age(name='Кузя', animal_type='кот', age='пять'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        assert status == 200
        assert result['age'] == age
    else:
        raise Exception("There is no my pets")
    # если тест пройден успешно - в системе некорректная валидация данных, это баг


"""9. Проверяем, будет ли добавлено фото некорректного формата"""
def test_set_photo_with_invalid_data(pet_photo='Словарь терминов из Практикума.pdf'):

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) > 0:
        status, result = pf.add_invalid_photo_of_pet(auth_key, my_pets['pets'][0]['id'], pet_photo)

        assert status == 200
        assert result['pet_photo'] != ''
    else:
        raise Exception("There is no my pets")
    # если тест пройден успешно - в системе некорректная валидация данных, это баг


"""10. Проверяем, можно ли удалить питомца не из списка my_pets"""
def test_delete_not_my_pet():

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, pets = pf.get_list_of_pets(auth_key, "")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список всех питомцев
    _, pets = pf.get_list_of_pets(auth_key, "")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in pets.values()
    #если тест успешно пройден - значит в системе есть нарушения в безопасности данных


"""11. Проверяем, можно ли дважды добавить питомца, где все данные одинаковые
Предусловие: необходимо, чтобы в списке my_pets был созданный питомец с данными: name="Кристофер", animal_type="рыжий кот", age= "1", pet_photo="images/cat1.jpg"""
def test_add_pet_duplicate(name='Кристофер', animal_type='рыжий кот', age='1', pet_photo='images/cat1.jpg'):

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    # сверяем, что из result имя первого питомца из списка равно имени второго питомца из списка
    assert my_pets['pets'][0]['name'] == my_pets['pets'][1]['name'] == name
    #если тест пройден успешно - в системе отсутствует проверка на дубликаты данных



