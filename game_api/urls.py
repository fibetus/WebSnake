from django.urls import path
from .views import GameStateView, MoveView, StartGameView

urlpatterns = [
    path('game/start', StartGameView.as_view(), name='start_game'),
    path('game/state', GameStateView.as_view(), name='game_state'),
    path('game/move', MoveView.as_view(), name='game_move'),
]