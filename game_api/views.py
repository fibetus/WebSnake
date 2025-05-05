from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from .serializers import GameStateSerializer, MoveSerializer, StartGameSerializer
from . import game_manager
import traceback

class StartGameView(APIView):
    """
    Starts a new game session.
    Accepts POST requests with username and map_size.
    """
    def post(self, request, *args, **kwargs):
        serializer = StartGameSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            map_size = serializer.validated_data['map_size']
            print(f"Received start request: User={username}, Size={map_size}")

            print(f"DEBUG: About to call start_new_game for {username}...")
            success = game_manager.start_new_game(username, map_size)
            print(f"DEBUG: Returned from start_new_game. Value: {success} (Type: {type(success)})") # <-- ADDED/MODIFIED

            if success:
                print("DEBUG: start_new_game reported success. Attempting to get state...")
                try:
                    initial_state = game_manager.get_current_state()
                    print(f"DEBUG: Successfully got state: {initial_state}")

                    state_serializer = GameStateSerializer(initial_state)
                    print(f"DEBUG: Serialized state: {state_serializer.data}")
                    print("DEBUG: Attempting to return JsonResponse...")

                    return JsonResponse(state_serializer.data, status=status.HTTP_200_OK)

                except Exception as e:
                    print(f"ERROR: Exception occurred after successful start_new_game: {e}")
                    traceback.print_exc()
                    return JsonResponse({"error": f"Internal server error after game start: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                 print(f"DEBUG: start_new_game returned False or None ({success}). Skipping state retrieval.")
                 print("Failed to start game (e.g., DB connection issue).")
                 return JsonResponse({"error": "Failed to start game, check server logs."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            print(f"Invalid start request data: {serializer.errors}")
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GameStateView(APIView):
    """
    Returns the current state of the game.
    Accepts GET requests.
    """
    def get(self, request, *args, **kwargs):
        current_state = game_manager.get_current_state()
        serializer = GameStateSerializer(current_state)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)


class MoveView(APIView):
    """
    Processes a player's move.
    Accepts POST requests with the direction.
    Returns the updated game state.
    """
    def post(self, request, *args, **kwargs):
        serializer = MoveSerializer(data=request.data)
        if serializer.is_valid():
            direction = serializer.validated_data['direction']
            print(f"Received move request: Direction={direction}")

            try:
                print(f"DEBUG [MoveView]: Calling game_manager.process_move('{direction}')...")
                new_state = game_manager.process_move(direction)
                print(f"DEBUG [MoveView]: Returned from game_manager.process_move.")

                state_serializer = GameStateSerializer(new_state)
                print(f"DEBUG [MoveView]: Returning JsonResponse for move '{direction}'.")
                return JsonResponse(state_serializer.data, status=status.HTTP_200_OK)

            except Exception as e:
                 print(f"ERROR [MoveView]: Exception during process_move call or serialization: {e}")
                 traceback.print_exc()
                 return JsonResponse({"error": f"Internal server error processing move: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            print(f"Invalid move request data: {serializer.errors}")
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
