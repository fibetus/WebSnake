from rest_framework import serializers

class GameStateSerializer(serializers.Serializer):
    snake = serializers.ListField(child=serializers.ListField(child=serializers.IntegerField(), min_length=2, max_length=2))
    food = serializers.ListField(child=serializers.IntegerField(), min_length=2, max_length=2, allow_null=True) # Food can be None if board full
    score = serializers.IntegerField()
    game_over = serializers.BooleanField()
    board_size = serializers.ListField(child=serializers.IntegerField(), min_length=2, max_length=2)
    speed = serializers.FloatField()

class MoveSerializer(serializers.Serializer):
    direction = serializers.ChoiceField(choices=["up", "down", "left", "right"])

class StartGameSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100, trim_whitespace=True) # Trim whitespace
    map_size = serializers.IntegerField(min_value=5, max_value=25)