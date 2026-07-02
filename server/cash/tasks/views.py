from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Task, CompletedTask
from .serializers import TaskSerializer, CompletedSerializer, TransactionSerializer
from accounts.models import Transactions
from accounts.models import Notifications

class TaskListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        tasks = Task.objects.filter(
            is_active=True
        )
        serializer = TaskSerializer(
            tasks,
            many=True
        )

        return Response(serializer.data)
    
class CompleteTaskView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        task_id = request.data.get('task_id')

        try:
            task = Task.objects.get(id=task_id)

        except Task.DoesNotExist:
            return Response(
                {"error": "Task not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        already_completed = CompletedTask.objects.filter(
            user=request.user,
            task=task
        ).exists()

        if already_completed:
            return Response(
                {"error": "Task already completed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        CompletedTask.objects.create(
            user=request.user,
            task=task
        )
        Transactions.objects.create(
            user=request.user,
            description = task.title,
            task_type = "task",
            amount = task.reward_points,
            status = 'completed'
                )
        Notifications.objects.create(
            title="Task Completed",
            notif_types="task",
            description=f"""You earned {task.reward_points} from {task.title}""",
            user=request.user
        )  

        request.user.points += task.reward_points
        request.user.user_wallet += task.reward_points
        request.user.save()
        

        return Response({
            "message": "Task completed",
            "earned_points": task.reward_points,
            "total_points": request.user.points,
        })
    
    def get(self, request):
        
        user = request.user
        completed = CompletedTask.objects.filter(user=user)
        
        serializers = CompletedSerializer(completed, many=True)
        
        return Response(serializers.data, status=status.HTTP_200_OK)
    
    
class TransactionsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        
        user = request.user
        transactions = Transactions.objects.filter(user=user)
        serializers = TransactionSerializer(transactions, many=True)
        
        return Response(serializers.data, status=status.HTTP_200_OK)     