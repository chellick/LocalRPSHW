import asyncio
import websockets
import json
from get_loc_ip import get_ip


async def play():
    """
    Подключиться к серверу и сыграть в игру.
    """
    adress = get_ip()
    uri = f"ws://{adress}:6789"  # Адрес сервера
    async with websockets.connect(uri) as websocket:
        player = None  # Будет содержать 'player1' или 'player2'
        while True:
            try:
                data = await websocket.recv()  # Получить данные от сервера
                message = json.loads(data)  # Парсить JSON сообщение

                if message["type"] == "waiting":
                    print(message["message"])

                elif message["type"] == "start":
                    player = message["player"]
                    print(message["message"])

                elif message["type"] == "your_move":
                    while True:
                        print(message["message"])
                        move = input().strip().lower()
                        if move in ["камень", "ножницы", "бумага"]:
                            await websocket.send(json.dumps({"move": move}))
                            break
                        else:
                            print("Неверный ход. Пожалуйста, введите 'камень', 'ножницы' или 'бумага'.")

                elif message["type"] == "result":
                    move1 = message["move1"]
                    move2 = message["move2"]
                    result = message["result"]
                    print(f"Игрок 1 выбрал: {move1}")
                    print(f"Игрок 2 выбрал: {move2}")
                    if result == "draw":
                        print("Ничья!")
                    elif (result == "player1" and player == "player1") or (
                        result == "player2" and player == "player2"
                    ):
                        print("Вы победили!")
                    else:
                        print("Вы проиграли.")

                elif message["type"] == "rematch":
                    while True:
                        print("Хотите сыграть ещё раз? (да/нет):")
                        answer = input().strip().lower()
                        if answer in ["да", "нет"]:
                            await websocket.send(json.dumps({"rematch": answer}))
                            break
                        else:
                            print("Пожалуйста, введите 'да' или 'нет'.")

                elif message["type"] == "end":
                    print("Игра завершена. Спасибо за игру!")
                    break

                elif message["type"] == "error":
                    print("Ошибка:", message["message"])
                    break

            except websockets.exceptions.ConnectionClosed:
                print("Соединение закрыто")
                break


if __name__ == "__main__":
    asyncio.run(play())
