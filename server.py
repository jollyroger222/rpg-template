import json
import select, socket
import struct
import uuid

server = socket.socket()
# на сокет - неблокирующий
server.setblocking(0)
server.bind(('', 9090))
# ожидаем не более 5 подключений
server.listen(5)

# inputs - список соединений, который хотят что-то получить
# кладем туда сервер, т.к. он ожидает соединения
inputs = [server]

# outputs - список соединений, в которые можно записывать данные
outputs = []

# словарь "соединение:его данные"
players = {}

# пока в списке входов что-то есть
while inputs:
    # из всех соединений, выбираем те, которые в данный момент ожидают получения, отправки данных или сломались
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    print(readable, writable)
    # для каждого, кто хочет что-то отправить
    for s in readable:
        # если это сервер, то у нас новый клиент
        if s is server:
            # разрешаем подключение
            connection, client_address = s.accept()
            print("Новое подключение: ", client_address)

            # добавляем соединения во входы и выходы
            outputs.append(connection)
            inputs.append(connection)

            # создаем запись в словаре данных
            player = {
                "coins": 0,
                "x": 200,
                "y": 200,
                "xvel": 0,
                "yvel": 0,
                "id": str(uuid.uuid4()),
                "index": 0
            }
            players[connection] = player
        # если это не сервер, кто-то хочет нам что-то сказать
        else:
            try:
                # пробуем получить данные
                byte_n = s.recv(2)
                n = struct.unpack('<H', byte_n)[0]

                data = b''
                while len(data) < n:
                    data += s.recv(n)
                if data:
                    json_data = data.decode('utf-8')
                    print("Получили от клиента:", json_data)

                    player = json.loads(json_data)

                    players[s] = player

                    if s not in outputs:
                        outputs.append(s)

                else:
                    raise Exception("error")
            except Exception as e:
                print(e)
                if s in outputs:
                    outputs.remove(s)
                if s in inputs:
                    inputs.remove(s)
                try:
                    del players[s]
                except:
                    pass
                try:
                    s.close()
                except:
                    pass

    # для каждого, кто хочет что-то получить
    for s in writable:
        try:
            answer = {
                "id": players[s]['id'],
                "players": list(players.values())
            }
            data = json.dumps(answer).encode('utf-8')
            size = len(data)
            byte_size = struct.pack('<H', size)
            s.send(byte_size)
            s.send(data)
            outputs.remove(s)
        # если что-то пошло не так - отключаемся
        except Exception as e:
            print(e)
            if s in outputs:
                outputs.remove(s)
            if s in inputs:
                inputs.remove(s)
            try:
                del players[s]
            except:
                pass
            try:
                s.close()
            except:
                pass

    # для тех, кто сломался
    for s in exceptional:
        if s in outputs:
            outputs.remove(s)
        if s in inputs:
            inputs.remove(s)
        try:
            del players[s]
        except:
            pass
        try:
            s.close()
        except:
            pass
