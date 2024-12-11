import asyncio
import websockets
import json
from get_loc_ip import get_ip


class RockPaperScissorsGame:
    def __init__(self, player1_ws, player2_ws):
        self.players = {player1_ws: None, player2_ws: None}
        self.player1_ws = player1_ws
        self.player2_ws = player2_ws
        self.game_over = False

    async def ask_for_rematch(self):
        await self.broadcast({"type": "rematch"})
        responses = await asyncio.gather(
            self.receive_response(self.player1_ws),
            self.receive_response(self.player2_ws),
        )
        if all(responses):
            await self.reset_game()
            await start_game(self)
        else:
            await self.broadcast({"type": "end"})
            self.game_over = True

    async def receive_response(self, websocket):
        try:
            data = await websocket.recv()
            message = json.loads(data)
            return message.get("rematch") == "да"
        except websockets.exceptions.ConnectionClosed:
            return False

    async def reset_game(self):
        self.players = {self.player1_ws: None, self.player2_ws: None}
        self.game_over = False
        
  
  
    async def receive_move(self, websocket):
        """
        Получает ход от игрока.

        Аргументы:
            websocket (websockets.WebSocketServerProtocol): Соединение WebSocket игрока.

        Возвращает:
            bool: True, если ход действителен и получен, иначе False.
        """
        try:
            data = await websocket.recv()  # Получает данные от игрока
            message = json.loads(data)  # Парсит JSON сообщение
            move = message.get("move")  # Извлекает ход
            self.players[websocket] = move  # Сохраняет ход игрока
            return True
        except websockets.exceptions.ConnectionClosed:
            # Обрабатывает случай, когда игрок отключается
            print("Соединение закрыто")
            return False
  
        


    async def determine_winner(self):
        move1 = self.players[self.player1_ws]
        move2 = self.players[self.player2_ws]
        result = self.get_result(move1, move2)
        await self.broadcast(
            {"type": "result", "move1": move1, "move2": move2, "result": result}
        )
        self.game_over = True
        await self.ask_for_rematch()

    def get_result(self, move1, move2):
        if move1 == move2:
            return "draw"
        wins = {"камень": "ножницы", "ножницы": "бумага", "бумага": "камень"}
        return "player1" if wins[move1] == move2 else "player2"

    async def broadcast(self, message):
        await self.player1_ws.send(json.dumps(message))
        await self.player2_ws.send(json.dumps(message))


async def handler(websocket):
    if waiting_players:
        opponent_ws = waiting_players.pop(0)
        game = RockPaperScissorsGame(opponent_ws, websocket)
        await start_game(game)
    else:
        waiting_players.append(websocket)
        await websocket.send(
            json.dumps({"type": "waiting", "message": "Ожидание соперника..."})
        )
        await websocket.wait_closed()


async def start_game(game):
    await game.player1_ws.send(
        json.dumps(
            {
                "type": "start",
                "player": "player1",
                "message": "Игра началась. Вы - Игрок 1",
            }
        )
    )
    await game.player2_ws.send(
        json.dumps(
            {
                "type": "start",
                "player": "player2",
                "message": "Игра началась. Вы - Игрок 2",
            }
        )
    )
    await game_loop(game)


async def game_loop(game):
    while not game.game_over:
        await game.player1_ws.send(
            json.dumps({"type": "your_move", "message": "Введите ваш ход [камень, ножницы, бумага]:"})
        )
        await game.player2_ws.send(
            json.dumps({"type": "your_move", "message": "Введите ваш ход [камень, ножницы, бумага]:"})
        )
        moves = await asyncio.gather(
            game.receive_move(game.player1_ws), game.receive_move(game.player2_ws)
        )
        
        print(moves)
        if not all(moves):
            await game.broadcast(
                {"type": "error", "message": "Один из игроков сделал неверный ход."}
            )
            break
        await game.determine_winner()


waiting_players = []

async def main():
    adress = get_ip()
    async with websockets.serve(handler, f"{adress}", 6789):
        print(f"Сервер запущен на ws://{adress}:6789")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
