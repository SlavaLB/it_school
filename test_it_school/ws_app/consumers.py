import json

from channels.generic.websocket import AsyncWebsocketConsumer


class SimpleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        await self.channel_layer.group_add(
            "notifications",
            self.channel_name
        )

        await self.send(json.dumps({
            'type': 'system',
            'message': 'Подключено к серверу'
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "notifications",
            self.channel_name
        )

    async def receive(self, text_data):
        await self.send(json.dumps({
            'type': 'echo',
            'message': f'Вы отправили: {text_data}'
        }))

    async def send_simple_message(self, event):
        """
        Получает сообщение из Django и отправляет клиенту
        event - это словарь с данными из Django
        """
        message_text = event.get('message', 'Пустое сообщение')

        await self.send(json.dumps({
            'type': 'notification',
            'message': message_text,
            'title': '📨 Уведомление от сервера',
            'status': 'info',
        }, ensure_ascii=False))
